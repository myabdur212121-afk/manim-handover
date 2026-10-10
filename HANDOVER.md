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
| this one | the handover documents only — the old `workspace/` tree was dissolved when the work moved to the live workspace |

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
| `sun` | 24.8 s | the emissive body, light at its centre, additive sprite corona (round 2, below) |
| `solar` | 30.0 s | the whole system, camera flying a keyed schedule, the shell corona (round 3) |

---

## 3. Where it stopped

*Updated 2026-10-11; earlier stopping points are preserved in git history.*

**The Sun's glow was settled, in three measured rounds.**

- **Round 1 — translucent dot-shells.** Rejected by the user outright:
  dot-art is not glow.
- **Round 2 — additive glow sprites.** The renderer (a local 3b1b/manim
  checkout at `src/manimGL`, never upstream) gained an opt-in
  `mobject.blend_mode = "add"` — (SRC_ALPHA, ONE) for colour, so light
  accumulates; the naive (ONE, ONE) was tried first and gives a flat
  disc because the falloff is ignored. `sun.py` wore five sprite layers:
  profile 675 → 330 → 231 → 159 → 103 out to 3R, verified against an
  isolated scene. But sprites face the camera: no depth behaviour. The
  user's verdict, in his words: *"make a glow effect perfectly in 3d
  not 2d"*.
- **Round 3 — fresnel shells, the current answer.** Six true spheres
  around the sun: one flat photosphere lift (1.019r) plus five
  inverse-fresnel shells (1.45r…3.3r, powers 1.4…0.6, `depth_write
  = False`). The WGSL goes in through `set_color_by_code` — the
  renderer needed no change for the fresnel itself. Opacities are not
  hand-tuned: each shell was rendered alone, its measured response
  became the basis, and nnls solved the opacities against the target
  profile. Result (frame height 10): 684 → 596 → 534 → 377 → 311 →
  234 → 154 → 121 → 71, decaying smoothly to 3.1R, and the same inside
  the full scene within ±5%.

**The 3D claim is proven with Mercury, not asserted.** Found by
single-planet stills (the only reliable way — bright patches near the
centre turned out to be corona light and sunspots, not planets):
in front of the disc the glow is cut — 403 vs 658 around it, 39%;
behind the disc Mercury is fully hidden, no dot at all; behind the rim
it shows as a veiled smudge, 106–130 under a 300–600 ring. None of
these three behaviours is possible with a camera-facing sprite.

**`Solar.mp4`** — 30.000 s, eight planets plus the Moon, 570 stars,
orbit rings, and a camera flying a keyed schedule (theta +1.4°/s,
phi −24°→−50°, height 13.5 → 10.2 → 17.5 → 14.5). Verified by a
full-scene replica rendered at the same clock and diffed pixel by
pixel: mean|Δ| 1.67 with zero missing regions at t=24.

**Two renderer laws found on the way** (see DEBUGGING.md for the
methods):

- **The euler flip.** Mixing a per-frame `set_phi` with accumulated
  `increment_theta` drifts into a flipped representation — measured at
  23 s: theta 8.2°, phi +43.8° where 100.2°, −43.8° was meant, planets
  "vanished" because they were elsewhere. Cure: set all three angles
  absolutely with `reorient` every frame; 900 steps of that leave the
  orientation matrix exact.
- **Depth write is poison for additive layers.** A shell's front
  surface writes depth and rejects the next shell's back hemisphere, so
  the composite falls short of its parts. Cure: a `depth_write` opt-out
  in the renderer — test on, write off. Both patches live as one diff
  at `our-work/patches/manimgl-glow-renderer.patch` in the live
  workspace; the plugin's 94 tests pass with them applied.

**Pending his verdict, unchanged:** whether the corona becomes plugin
API (a `Sun` preset, an emission parameter, or nothing), whether
`sun.py` is re-rendered with the shell corona, and the older question
of re-rendering the first videos' colours.

Still open, unchanged from before:

- Whether `MeshData` should move out of the `obj` helper. Two helpers
  use it; a third would settle it.
- Presets download textures on first use; no offline story yet.
- No DEM is bundled for any body.

A sandbox law worth knowing: workspace snapshots strip `.git/config`
(credential hygiene), so **every reset removes the remotes from all
local repos** — and this time the whole of `manim-handover/.git` went
with it. Re-init, fetch, update-ref, then push; the URLs are in
`our-work/remotes.md` in the live workspace.

---

## 4. Known gaps, stated plainly

- **No shadows in the renderer.** The two Saturn shadows are solved for
  that one geometry. Nothing else casts anything.
- **One light source**, no PBR, no normal maps, no transparency sorting.
- **The corona is shells, not a true volume.** Beyond ~2.7R the faint
  tail's shell surface can sit nearer the camera than a planet, so the
  veil there is an approximation, not a line integral.
- **No physics, no rigging.** This is an illustration toolkit, not a
  renderer. For photorealism or simulation, model in Blender, export
  `.obj` or `.glb`, and bring the result here for the explaining.
- `decimate()` transfers UVs and materials by nearest neighbour — a texture
  slides slightly.
- `subdivide(smooth=True)` rounds sharp corners. Wrong for architecture.
- Not on PyPI.

The user understands all of this; it was discussed at length and he
reached the same conclusion independently. Do not oversell.
