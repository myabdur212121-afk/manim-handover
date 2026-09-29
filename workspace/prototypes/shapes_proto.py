"""
Prototype: building meshes from formulas instead of files.

Not part of the package yet -- this exists to answer one question with a
picture rather than a claim: how much can two general functions actually
make?

    revolve(profile)          spin a 2D outline around the z axis
    extrude(path, profile)    sweep a cross-section along a 3D path
    box(w, d, h)              the one primitive not worth routing through
                              either of the above

Everything returns a MeshData with proper UVs, so subdivide / decimate /
displace / textured / wireframe / point_cloud all work on the result.
"""

from __future__ import annotations

import sys

import numpy as np

sys.path.insert(0, "/home/user/src")
from manimgl_myplugin.obj.loader import MeshData          # noqa: E402


# ------------------------------------------------------------- plumbing --

def _grid_mesh(points, uvs, nu, nv, wrap_u=False, wrap_v=False, name="shape"):
    """
    Turn an (nu x nv) grid of points into a triangle mesh.

    Degenerate quads -- the ones that collapse to a line at a pole, say --
    are dropped rather than emitted as zero-area triangles.
    """
    points = np.asarray(points, dtype=np.float32).reshape(nu, nv, 3)
    uvs = np.asarray(uvs, dtype=np.float32).reshape(nu, nv, 2)

    idx = np.arange(nu * nv).reshape(nu, nv)
    iu = np.arange(nu if wrap_u else nu - 1)
    iv = np.arange(nv if wrap_v else nv - 1)
    a = idx[np.ix_(iu, iv)]
    b = idx[np.ix_((iu + 1) % nu, iv)]
    c = idx[np.ix_((iu + 1) % nu, (iv + 1) % nv)]
    d = idx[np.ix_(iu, (iv + 1) % nv)]

    quads = np.stack([a, b, c, d], axis=-1).reshape(-1, 4)
    tris = np.concatenate([quads[:, [0, 1, 2]], quads[:, [0, 2, 3]]])

    flat = points.reshape(-1, 3)
    edge1 = flat[tris[:, 1]] - flat[tris[:, 0]]
    edge2 = flat[tris[:, 2]] - flat[tris[:, 0]]
    area = np.linalg.norm(np.cross(edge1, edge2), axis=1)
    tris = tris[area > 1e-12]                       # drop the collapsed ones

    return MeshData(
        vertices=flat,
        tri_v=tris.astype(np.int32),
        tri_vt=tris.astype(np.int32),               # same layout as vertices
        tri_vn=np.full_like(tris, -1, dtype=np.int32),
        tri_material=np.zeros(len(tris), dtype=np.int32),
        tri_group=np.zeros(len(tris), dtype=np.int32),
        tri_object=np.zeros(len(tris), dtype=np.int32),
        material_names=[name], group_names=[name], object_names=[name],
        uvs=uvs.reshape(-1, 2),
        normals=np.zeros((0, 3), dtype=np.float32),
        source=f"<{name}>",
    )


# -------------------------------------------------------------- shapes --

def revolve(profile, segments=96, name="revolve"):
    """
    Spin a 2D outline around the z axis.

    ``profile`` is an ``(N, 2)`` array of ``(radius, height)`` points. Any
    surface with an axis of symmetry is one of these.
    """
    profile = np.asarray(profile, dtype=np.float64).reshape(-1, 2)
    theta = np.linspace(0, 2 * np.pi, segments, endpoint=False)

    r, z = profile[:, 0], profile[:, 1]
    pts = np.stack([
        np.outer(np.cos(theta), r),
        np.outer(np.sin(theta), r),
        np.tile(z, (segments, 1)),
    ], axis=-1)

    u = np.linspace(0, 1, segments, endpoint=False)
    v = np.linspace(0, 1, len(profile))
    uvs = np.stack(np.meshgrid(u, v, indexing="ij"), axis=-1)

    return _grid_mesh(pts, uvs, segments, len(profile), wrap_u=True, name=name)


def extrude(path, profile, closed_path=False, caps=False, name="extrude"):
    """
    Sweep a closed cross-section along a 3D path.

    ``path`` is ``(M, 3)``, ``profile`` an ``(K, 2)`` loop in the plane
    perpendicular to it. The frame is carried along by rotation-minimising
    transport, so the cross-section does not spin as the path curves.
    """
    path = np.asarray(path, dtype=np.float64).reshape(-1, 3)
    profile = np.asarray(profile, dtype=np.float64).reshape(-1, 2)
    m, k = len(path), len(profile)

    tangents = np.gradient(path, axis=0)
    tangents /= np.maximum(np.linalg.norm(tangents, axis=1, keepdims=True), 1e-12)

    # Start with any vector not parallel to the first tangent, then carry it
    # along by projecting out the tangent at each step -- a Frenet frame
    # would flip wherever the curve straightens out.
    seed = np.array([0.0, 0.0, 1.0])
    if abs(seed @ tangents[0]) > 0.9:
        seed = np.array([1.0, 0.0, 0.0])
    normals = np.empty_like(path)
    n = seed - (seed @ tangents[0]) * tangents[0]
    normals[0] = n / np.linalg.norm(n)
    for i in range(1, m):
        n = normals[i - 1] - (normals[i - 1] @ tangents[i]) * tangents[i]
        norm = np.linalg.norm(n)
        normals[i] = n / norm if norm > 1e-9 else normals[i - 1]
    binormals = np.cross(tangents, normals)

    pts = (path[:, None, :]
           + profile[None, :, 0, None] * normals[:, None, :]
           + profile[None, :, 1, None] * binormals[:, None, :])

    u = np.linspace(0, 1, m)
    v = np.linspace(0, 1, k, endpoint=False)
    uvs = np.stack(np.meshgrid(u, v, indexing="ij"), axis=-1)

    mesh = _grid_mesh(pts, uvs, m, k, wrap_u=closed_path, wrap_v=True, name=name)
    if caps and not closed_path:
        mesh = _add_caps(mesh, pts[0], pts[-1], k, name)
    return mesh


def _add_caps(mesh, first_ring, last_ring, k, name):
    """Close the two open ends with a triangle fan around each centre."""
    verts = [mesh.vertices]
    uvs = [mesh.uvs]
    tris = [mesh.tri_v]
    base = len(mesh.vertices)
    for ring, flip in ((first_ring, True), (last_ring, False)):
        centre = ring.mean(axis=0)
        verts.append(np.vstack([ring, centre]).astype(np.float32))
        disc = np.zeros((k + 1, 2), dtype=np.float32) + 0.5
        uvs.append(disc)
        hub = base + k
        fan = [[hub, base + i, base + (i + 1) % k] for i in range(k)]
        fan = np.array(fan, dtype=np.int32)
        tris.append(fan[:, ::-1] if flip else fan)
        base += k + 1
    tris = np.concatenate(tris).astype(np.int32)
    mesh.vertices = np.concatenate(verts).astype(np.float32)
    mesh.uvs = np.concatenate(uvs).astype(np.float32)
    mesh.tri_v = tris
    mesh.tri_vt = tris.copy()
    mesh.tri_vn = np.full_like(tris, -1)
    for f in ("tri_material", "tri_group", "tri_object"):
        setattr(mesh, f, np.zeros(len(tris), dtype=np.int32))
    return mesh


def box(width=1.0, depth=1.0, height=1.0, name="box"):
    """
    A rectangular block.

    Could be an extrude with end caps, but eight vertices written out are
    clearer than the machinery, and every face gets its own UV square.
    """
    w, d, h = width / 2, depth / 2, height / 2
    corner = np.array([[-w, -d, -h], [w, -d, -h], [w, d, -h], [-w, d, -h],
                       [-w, -d, h], [w, -d, h], [w, d, h], [-w, d, h]])
    faces = [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4),
             (2, 3, 7, 6), (1, 2, 6, 5), (3, 0, 4, 7)]
    square = np.array([[0, 0], [1, 0], [1, 1], [0, 1]], dtype=np.float32)

    verts, uvs, tris = [], [], []
    for n, quad in enumerate(faces):
        base = 4 * n
        verts.append(corner[list(quad)])
        uvs.append(square)
        tris += [[base, base + 1, base + 2], [base, base + 2, base + 3]]
    tris = np.array(tris, dtype=np.int32)

    return MeshData(
        vertices=np.concatenate(verts).astype(np.float32),
        tri_v=tris, tri_vt=tris.copy(),
        tri_vn=np.full_like(tris, -1),
        tri_material=np.zeros(len(tris), dtype=np.int32),
        tri_group=np.zeros(len(tris), dtype=np.int32),
        tri_object=np.zeros(len(tris), dtype=np.int32),
        material_names=[name], group_names=[name], object_names=[name],
        uvs=np.concatenate(uvs).astype(np.float32),
        normals=np.zeros((0, 3), dtype=np.float32),
        source=f"<{name}>",
    )


# ------------------------------------------------- profiles and paths --

def circle_profile(radius=1.0, sides=32):
    t = np.linspace(0, 2 * np.pi, sides, endpoint=False)
    return np.stack([radius * np.cos(t), radius * np.sin(t)], axis=-1)


def square_profile(size=1.0):
    h = size / 2
    return np.array([[-h, -h], [h, -h], [h, h], [-h, h]])


def helix_path(turns=4.0, radius=1.0, pitch=0.35, samples=400):
    t = np.linspace(0, turns * 2 * np.pi, samples)
    return np.stack([radius * np.cos(t), radius * np.sin(t),
                     pitch * t / (2 * np.pi)], axis=-1)


def line_path(start, end, samples=2):
    return np.linspace(np.asarray(start, float), np.asarray(end, float), samples)


# ---------------------------------------- the shapes people ask about --

def sphere(radius=1.0, resolution=(96, 48)):
    """A semicircle, spun. The poles collapse and those quads are dropped."""
    segments, rings = resolution
    t = np.linspace(0, np.pi, rings)
    return revolve(np.stack([radius * np.sin(t), -radius * np.cos(t)], -1),
                   segments, name="sphere")


def ellipsoid(radii=(1.0, 1.0, 1.0), resolution=(96, 48)):
    mesh = sphere(1.0, resolution)
    mesh.vertices = (mesh.vertices * np.asarray(radii, np.float32)).astype(np.float32)
    return mesh


def torus(major=1.0, minor=0.3, resolution=(96, 32)):
    """A circle spun about an axis it does not touch."""
    segments, ring = resolution
    t = np.linspace(0, 2 * np.pi, ring, endpoint=False)
    profile = np.stack([major + minor * np.cos(t), minor * np.sin(t)], -1)
    return revolve(np.concatenate([profile, profile[:1]]), segments, name="torus")


def cylinder(radius=1.0, height=2.0, segments=96):
    """Capped: the profile runs in from the axis, up, and back in again."""
    return revolve([[0, -height / 2], [radius, -height / 2],
                    [radius, height / 2], [0, height / 2]],
                   segments, name="cylinder")


def cone(radius=1.0, height=2.0, segments=96):
    return revolve([[0, 0], [radius, 0], [0, height]], segments, name="cone")


def vase(height=2.0, segments=96):
    """The point of revolve: any outline at all, not a fixed menu."""
    z = np.linspace(0, height, 60)
    r = 0.25 + 0.42 * np.sin(np.pi * z / height) ** 1.6 + 0.10 * np.cos(4 * z)
    return revolve(np.stack([r, z], -1), segments, name="vase")


def spring(turns=4.0, radius=1.0, pitch=0.35, thickness=0.09):
    return extrude(helix_path(turns, radius, pitch),
                   circle_profile(thickness, 16), name="spring")


def square_duct(turns=3.0, radius=1.0, pitch=0.5, size=0.22):
    """Same call as the spring, a different cross-section."""
    return extrude(helix_path(turns, radius, pitch),
                   square_profile(size), name="duct")


def prism(sides=6, radius=0.8, height=2.0):
    return extrude(line_path([0, 0, -height / 2], [0, 0, height / 2]),
                   circle_profile(radius, sides), caps=True, name="prism")


if __name__ == "__main__":
    for label, mesh in [
        ("sphere", sphere()), ("ellipsoid", ellipsoid((1, 1, 0.6))),
        ("torus", torus()), ("cylinder", cylinder()), ("cone", cone()),
        ("vase", vase()), ("box", box(1.4, 1.4, 1.4)),
        ("spring", spring()), ("square duct", square_duct()),
        ("hex prism", prism()),
    ]:
        print(f"  {label:12s} {mesh.num_faces:>6,} tris   "
              f"{len(mesh.vertices):>6,} verts   uv={mesh.tri_vt.max() >= 0}")


# ----------------------------------------------- the bridge from manim --

def from_surface(mob, name=None):
    """
    Turn anything ManimGL already knows how to draw into a MeshData.

    ManimGL ships Sphere, Torus, Cylinder, Cone, Cube, Prism, Disk3D,
    Dodecahedron and ParametricSurface -- there is no reason to write those
    again. This reads the grid of points a Surface already holds and hands
    it over, so every one of them can then be subdivided, decimated,
    displaced, textured, wireframed or built up triangle by triangle.

    Groups (Cube is six Square3D faces) are merged into one mesh.
    """
    from manimlib.mobject.types.surface import Surface

    name = name or type(mob).__name__.lower()

    if not isinstance(mob, Surface):
        parts = [from_surface(s, name) for s in mob.submobjects
                 if isinstance(s, Surface) or s.submobjects]
        if not parts:
            raise TypeError(f"{type(mob).__name__} holds no Surface to read")
        # A Cube is six separate squares; without welding the shared corners
        # the faces stay disconnected and smooth subdivision pulls them apart.
        return weld(_merge(parts, name))

    nu, nv = mob.get_resolution()
    pts = np.asarray(mob.get_points(), dtype=np.float32)
    if nu * nv != len(pts):
        raise ValueError(f"{name}: resolution {nu}x{nv} does not match "
                         f"{len(pts)} points")

    u = np.linspace(0, 1, nu)
    v = np.linspace(0, 1, nv)
    uvs = np.stack(np.meshgrid(u, v, indexing="ij"), axis=-1)
    return _grid_mesh(pts, uvs, nu, nv, name=name)


def weld(mesh, tol=1e-5):
    """
    Fuse vertices that sit on top of each other.

    Separate surfaces joined into one mesh still have two copies of every
    shared corner, so the mesh is watertight to look at but not to walk:
    smooth subdivision reads each face as having a free edge and curls it
    away from its neighbours. Rounding the coordinates and keeping one
    vertex per cell puts the surface back together.
    """
    quantised = np.round(np.asarray(mesh.vertices) / tol).astype(np.int64)
    _, keep, inverse = np.unique(quantised, axis=0,
                                 return_index=True, return_inverse=True)
    mesh.vertices = np.asarray(mesh.vertices)[keep].astype(np.float32)
    mesh.tri_v = inverse[mesh.tri_v].astype(np.int32)
    return mesh


def _merge(meshes, name):
    verts, uvs, tris, offset, uv_offset = [], [], [], 0, 0
    for m in meshes:
        verts.append(m.vertices)
        uvs.append(m.uvs)
        tris.append(m.tri_v + offset)
        offset += len(m.vertices)
        uv_offset += len(m.uvs)
    tris = np.concatenate(tris).astype(np.int32)
    return MeshData(
        vertices=np.concatenate(verts).astype(np.float32),
        tri_v=tris, tri_vt=tris.copy(),
        tri_vn=np.full_like(tris, -1),
        tri_material=np.zeros(len(tris), dtype=np.int32),
        tri_group=np.zeros(len(tris), dtype=np.int32),
        tri_object=np.zeros(len(tris), dtype=np.int32),
        material_names=[name], group_names=[name], object_names=[name],
        uvs=np.concatenate(uvs).astype(np.float32),
        normals=np.zeros((0, 3), dtype=np.float32),
        source=f"<{name}>",
    )
