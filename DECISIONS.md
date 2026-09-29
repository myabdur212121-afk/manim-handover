# Decisions, and why

Consequential choices, so nobody relitigates them by accident. Where the
user decided, that is marked.

---

## Scope and identity

**This is an illustration toolkit, not a renderer.** It exists to explain
things with models — exploded views, labelled parts, cutaways, build-up
animations. Not photorealism, not simulation. The user reached this
conclusion independently and stated it; the documents say it plainly
rather than overselling.

**ManimGL only.** The mobject side subclasses ManimGL's `Surface` and
writes wgsl buffers directly. CE's renderer is a different thing; a port
would be a second backend, not a patch. The mesh half is deliberately
kept renderer-free so it could be reused.

**Named `manimgl_myplugin`** *(user's choice)*. It was briefly
`manim-obj`, then renamed once it was clear the `.obj` work was one helper
among several. GitHub keeps the old URL redirecting.

## Architecture

**No `3DObject` base class** *(user proposed it; declined with reasons)*.
`Surface` and `Mobject` already mean "a 3D thing", and the real shared
ground between models-from-files and bodies-from-formulas turned out to be
`MeshData` — a data structure, not a hierarchy. That was discovered, not
predicted, which is the argument against designing hierarchies early.

**Classes carry knowledge, functions carry construction.** `Mars()` is a
class because it knows its radius and which texture. `helix()` is a
function because it only builds geometry.

**Helpers are subpackages, registered in one dict.** `_HELPERS` in the
top-level `__init__` maps a helper to the names it contributes; they are
imported lazily so the mesh side needs no manim.

**`MeshData` still lives in `obj/`.** It is really shared ground, and
`shapes` importing it from there is a small smell. Two helpers use it; if
a third does, move it. Noted rather than fixed, deliberately.

## The `shapes` helper

**Three builders, not ten** *(the user's question forced this)*. ManimGL
already ships `Sphere`, `Torus`, `Cylinder`, `Cone`, `Cube`, `Prism`,
`Disk3D` and `ParametricSurface`. `from_surface` borrows all of them, so
`revolve` and `extrude` only had to cover what manim has no answer for.
Less code, more shapes.

**`revolve` spins about z only.** Rotate the result for another axis.

**`from_surface` welds by default.** A `Cube` is six separate faces; 24
corners instead of 8 makes smooth subdivision peel it apart.

## The `astro` helper

**Base class is `Body`, not `Planet`** *(user proposed `Planet`; corrected)*.
A moon is not a planet, and neither is Ceres.

**Presets are thin subclasses generated from a table.** Discoverable,
short to type, and all the facts live in `data.py`.

**The Cassini Division is a real hole in the geometry**, not a transparent
patch. Forced by the shader: it discards fully transparent pixels but
overwrites partial alpha with the vertex opacity, so soft transparency
from a texture does not survive.

**Ring colour and opacity are per-vertex**, sampled from the ring strip.
Same reason, and it also makes the rings darkenable for the planet's
shadow.

**Both Saturn shadows are solved analytically.** The renderer has none.
Planet-on-rings is per-vertex; rings-on-planet is painted into a copy of
the texture, because a textured surface has no vertex colour to darken.

**`quality="4k"` is derived from the 8k.** Solar System Scope publishes 2k
and 8k only; asking for 4k returns an HTML error page that looks like a
success.

**`spin()` uses the body's own axis, `rotate()` stays on the scene's**
*(the user asked for exactly this distinction)*. `turn()` returns a
playable `Rotating`. It is **not** called `apply_rotation`: manim's
`apply_*` family applies functions to points and returns `self`, so the
name would mislead.

**`point_at` adds 180° to the longitude.** The texture's left edge is
longitude −180 and `revolve` starts its sweep on +x. Without it, the
Sahara comes out in the Pacific.

## Repositories and documents

**No rendered video in any repository** *(user's instruction, twice)*.
Scenes and input assets only, so anything can be re-rendered.

**Root README is identity, not reference** *(user's correction)*. What the
thing is for, a table of helpers, what it deliberately cannot do. Class
detail lives in `docs/<helper>/reference.md`.

**Every helper carries a six-section `notes.md`** *(user's request)*:
what it is, problems faced with symptom → cause → fix → guard, dead ends,
expected numbers, hard limits, what to do first.

**The sandbox story is kept out of the project notes** *(user's
correction)*. It is an artefact of the working environment, not of the
project. It lives in `ENVIRONMENT.md` here instead.

**`manim-projects` house style is respected.** Only two lines were added
to its root README: one index row, one bullet.

## Rejected outright

| idea | why |
| --- | --- |
| vertex welding to cure z-fighting | twins are triangulated along opposite diagonals; caught 153 of ~4,800 |
| O(k²) overlap test | 13 s; the per-plane grid does it in 1 s |
| `sphere()`, `cube()` in `shapes` | ManimGL has them |
| `smooth_subdivide` on architecture | Loop subdivision melts sharp corners |
| a Frenet frame for `extrude` | flips where the path straightens |
| alpha for soft ring transparency | the shader overwrites it |
| rebaking the globe shadow every frame | ~1 s per bake |
| `apply_rotation` as a name | collides with manim's `apply_*` meaning |
