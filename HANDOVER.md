# The project, and where it stopped

---

## 1. The user

Writes in **Bengali**, sometimes Banglish. Replies have been in Bengali
throughout and that is clearly the right register — keep it unless he
switches.

What he is like to work with, from a long collaboration:

- **He wants to understand, not just receive.** His words: he wants to
  grasp the structure because later he will write code himself. When an
  explanation was too dense he said so and asked for it simpler.
- **He asks to talk before building.** "lets talk" came up repeatedly.
  Respect it — when he said "no work yet, explain", the explanation was
  the deliverable.
- **He notices things in the rendered output.** Three real bugs were found
  because he looked at a video and said something was wrong: zig-zag walls
  on a building, a still-speckled roof, a blurry Earth. He was right every
  time.
- **He proposes designs and expects an honest verdict.** He suggested a
  `3DObject` base class; the reasoned disagreement was welcome. He
  suggested `Planet → Earth, Moon`; that was adopted with one correction
  (a moon is not a planet, so the base is `Body`).
- **He worries about wasting your effort.** He asked more than once
  whether his questions were breaking the plan and said not to do things
  just because he suggested them. Answer honestly.
- **He gives permission clearly** — "start", "I give you permission" — and
  then expects you to decide the details yourself.

### Standing instructions he has given

- The GitHub token file must contain **only the token string**.
- For the environment setup, follow the `manim-env-setup` repo **exactly**,
  not an improvised alternative. *(That task is complete.)*
- **No rendered video in the repositories.** Scenes and input assets only,
  so anything can be re-rendered. He confirmed this twice.
- The root README of a repo is its **identity**, not a class reference.
  Detail belongs inside, per component.
- Each project carries a `NOTES.md`: problems hit, causes, dead ends,
  expected numbers.
- He will revoke the GitHub token himself.

---

## 2. What exists

### `manimgl_myplugin` — a ManimGL plugin, ~4,500 lines plus ~1,500 of tests

**ManimGL only.** It subclasses ManimGL's `Surface`, writes its wgsl
buffers directly and uses `camera.light_source`. ManimCE's renderer is a
different thing; a port would be a second backend, not a patch.

But the mesh half is renderer-free: `obj/loader.py` imports only numpy,
scipy, trimesh and Pillow, and the package imports the mobject side lazily
(PEP 562), so `from manimgl_myplugin import load_mesh` works with no manim
installed. There is a test for that.

#### `obj` — models from files

Loading from a path, a bare name, a URL, raw text or a `MeshData`; `.stl`,
`.ply` and `.glb` through trimesh. Axis conversion. Eight colour modes.
Real per-pixel texture mapping via `TexturedSurface`. Slicing, splitting,
crease wireframes, point clouds, a `BuildMesh` animation. Mesh surgery:
`dedupe`, `decimate`, `subdivide`, `displace`, `weld`.

#### `shapes` — meshes from formulas

Three builders only:

```python
from_surface(mob)        # anything ManimGL already draws
revolve(profile)         # spin an outline — a potter's wheel
extrude(path, profile)   # sweep a cross-section — toothpaste from a nozzle
```

There is deliberately **no `sphere()` or `cube()`**. ManimGL has those;
`from_surface` borrows all of them in one function. The plan started at
ten shape functions and ended at three, which was an improvement.

#### `astro` — planets, moons, rings

Nine bodies, each carrying only measured facts. `Body` for anything else.

```python
Earth()                            # every default is a real value
Saturn(radius=3, quality="4k")
Mars(radius=3, dem="mola.img", exaggeration=25)

earth.spin(0.3)                    # its own axis, not the scene's
earth.turn(PI, rate_func=smooth)   # a playable Rotating
earth.point_at(23.8, 90.4)         # Dhaka, in scene coordinates
earth.marker(23.8, 90.4)
earth.arc_between((23.8, 90.4), (51.5, -0.1))
earth.graticule(30)
earth.axis_line()
moon.orbit(earth, radius=5.2, period=9, tilt=12)
```

Both Saturn shadows are solved analytically and painted in, because the
renderer has none at all.

### Repositories

| | |
| --- | --- |
| [`manimgl-myplugin`](https://github.com/myabdur212121-afk/manimgl-myplugin) | the package: code, docs, examples, tests |
| [`manim-projects`](https://github.com/myabdur212121-afk/manim-projects) | his archive; this lives at `2026/manimgl_myplugin/` |
| this one | the handover, plus the whole workspace |

`manim-projects` has its own house style — projects by year, each in a
folder, an index table in the README, **no rendered output**. Respect it;
only two lines were added to its root README.

### Videos rendered (kept out of the repos on purpose)

| scene | length | shows |
| --- | --- | --- |
| `05_obj_building` | 48 s | one building, nine beats |
| `06_earth_chair` | 40 s | two downloaded models, real texture mapping |
| `08_resolution` | 40 s | decimate / subdivide / displace |
| `09_landscape` | 72 s | six models, moving camera and light |
| `10_highland` | 90 s | eight models, **2560×1440** |
| `11_shapes` | 40 s | the three builders |
| `12_planets` | 57 s | nine bodies, Saturn's rings and shadows |
| `13_spin` | 21 s | spin() vs rotate() side by side |
| `14_geography` | 23 s | markers, arcs, graticule, orbit |

The demos of the current phase (2026-10-10) live in `our-work/videos/` in
the live workspace, not in any repo, and supersede the list above for
ongoing work:

| scene | length | shows |
| --- | --- | --- |
| `tour` | 47 s | the whole plugin in one pass |
| `api2` | 55 s | the surface family: place_on_surface, surface_text, surface_mathtex, cell_note, marker |
| `features` | 29 s | graticule highlights, labels, see_through (probe: +51% grid visible through the globe) |
| `bncurve` | 26 s | Bengali surface_text — the bend measured, tangent-plane and naive flats for contrast |
| `sun` | 24 s | the emissive body, light at its centre, corona rim + tail |

---

## 3. Where it stopped

*Updated 2026-10-10; the previous stopping point (the Sun named but not
started) is preserved in git history.*

**The Sun was started, measured, and filmed — but not put in the plugin.**
A prototype lives in `our-work/scenes/sun.py` (never imported by the
package). What the probes settled:

- The emissive body works: `Body(texture="sun")` with
  `globe.set_shading(0, 0, 0)` renders direction-independent (halves
  401/376 and 353/424 of 765; the rest is the texture's own sunspots).
  Texture `2k_sun.jpg` from Solar System Scope (CC BY 4.0), now in
  `~/models`.
- Moving `camera.light_source` to the sun's centre makes planets lit
  from it and nothing else: with the light flipped to the antipode the
  bright half of Venus flipped with it (centroid pull -2.4 px vs
  +4.0 px).
- The corona, three candidates measured side by side: a `DotCloud` shell
  of small dots is the only one with a tail (1.5–2R at about twice the
  background luminance); nested translucent spheres render perfectly
  cleanly (the sorting fear was wrong) but stop hard at 1.3R; one big
  glowing `DotCloud` dot is a smooth rim with a short tail. The demo
  layers rim + tail: 392 -> 88 -> 62 -> 51 -> 35 out to 2.5R.
- **Pending his verdict:** whether any of this becomes a `Sun` preset,
  an emission parameter, or a corona helper in the package. Nothing was
  committed to the plugin for it.

**The surface family grew up.** Since the handover the astro API gained
`place_on_surface`, `surface_text` (any script — Bengali measured: all
474 points on the r(1+h) shell within 0.002, edge slope 18.09 deg
against a longitude span of 18.07 deg, so the bend is geometry, not
font), `surface_tex`, `surface_mathtex`, `surface_cell_note`,
`surface_point`, `label`, and the pinned `cell_note`; the graticule
gained highlights, value labels and `see_through`; bodies gained
`shed_overlays`. `flat_map` was proposed and dropped — the minimal-API
rule held. Notes 2.13–2.19 record the laws found on the way, including
2.19: manimlib's `Text`/`Tex` take `color` to Pango but the glyph fills
come back white, so the plugin carries the colour over with `set_fill`
— every coloured caption in every video before 2026-10-10 was silently
monochrome, and the plugin's tests now guard against it (94 green).

Still open, unchanged from before:

- Whether `MeshData` should move out of the `obj` helper. Two helpers
  use it; a third would settle it.
- Presets download textures on first use; no offline story yet.
- No DEM is bundled for any body.

A sandbox law worth knowing: workspace snapshots strip `.git/config`
(credential hygiene), so **every reset removes the remotes from all
local repos**. Re-add them from the account before pushing; the URLs
are in `our-work/remotes.md` in the live workspace.

---

## 4. Known gaps, stated plainly

- **No shadows in the renderer.** The two Saturn shadows are solved for
  that one geometry. Nothing else casts anything.
- **One light source**, no PBR, no normal maps, no transparency sorting.
- **No physics, no rigging.** This is an illustration toolkit, not a
  renderer. For photorealism or simulation, model in Blender, export
  `.obj` or `.glb`, and bring the result here for the explaining.
- `decimate()` transfers UVs and materials by nearest neighbour — a texture
  slides slightly.
- `subdivide(smooth=True)` rounds sharp corners. Wrong for architecture.
- Not on PyPI.

The user understands all of this; it was discussed at length and he
reached the same conclusion independently. Do not oversell.
