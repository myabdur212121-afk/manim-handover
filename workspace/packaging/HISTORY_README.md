# manim-obj-history

The complete working state of the `manim_obj` project — library, demos,
rendered videos, models, tooling and notes. Nothing trimmed.

The clean, installable package lives at
**[manim-obj](https://github.com/myabdur212121-afk/manim-obj)**. This
repository is the archive: it keeps the things a package should not carry,
so the work can be picked up again exactly where it stopped.

---

## What is here

| path | contents |
| --- | --- |
| `src/manim_obj/` | the library, 2,308 lines (same code as the package repo) |
| `demos/` | every scene written along the way, including throwaway ones |
| `videos/` | the rendered output — see the table below |
| `models/` | the eight `.obj` test models and the Earth textures |
| `docs/manim_obj_guide.md` | the long guide, in Bengali, 16 chapters |
| `docs/reports/` | the environment setup report |
| `tools/` | `restore_env.sh`, model fetcher, boot tracer |
| `packaging/` | README, licence and `pyproject.toml` for the package repo |
| `logs/` | environment restores, memory traces from the big renders |
| `manim-env-setup/` | the setup repository this was built against |

## The videos

| file | length | resolution | what it shows |
| --- | --- | --- | --- |
| `videos/05_obj/BuildingDemo.mp4` | 48 s | 1280×720 | one building, nine beats |
| `videos/06_earth_chair/EarthAndChair.mp4` | 40 s | 1280×720 | two downloaded models, real texture mapping |
| `videos/08_resolution/Resolution.mp4` | 40 s | 1280×720 | `decimate` / `subdivide` / `displace` |
| `videos/09_landscape/Landscape.mp4` | 72 s | 1280×720 | six models, moving camera and light |
| `videos/10_highland/Highland.mp4` | 90 s | **2560×1440** | eight models, QHD, placement on a mountain |

Also `dedupe_before_after.png`, `texture_sharpness.png` and
`sphere_vs_obj.png` — the measurements that drove three of the fixes.

## Running it again

The sandbox this was built in is recreated between sessions, and anything
installed with `apt` or `pip` lives outside the saved directory and is lost.
Only the files here survive. To get back to a working toolchain:

```bash
bash tools/restore_env.sh --no-latex     # ~45 s
bash tools/restore_env.sh                # ~2 min, adds the LaTeX suite
```

`--no-latex` skips 775 MB of TeX that none of these scenes need — they all
use `Text`, which goes through Pango.

Then:

```bash
manimgl demos/07_minimal.py Simplest -w -l -c "#070B14" --video_dir /tmp/out
```

## What was fixed along the way

Each of these was found by rendering something and looking at it.

1. **11,346 triangles instead of 15,024** — the exporter wrapped long `f`
   lines with a backslash and splitting on newlines dropped the rest.
2. **Walls speckled with two colours** — 47% of the building's faces were
   exact duplicates on a second material layer, z-fighting. A vertex weld
   could not find them because the twins are triangulated along opposite
   diagonals; a geometric coplanar-overlap test could.
3. **Roofs still speckled after that** — same-material twins, left in place
   on the assumption that identical colours cannot fight. They can: opposite
   winding means one is lit and one is not.
4. **`color=` ignored** — the `.mtl` was winning against an explicit
   argument, against what the docstring promised.
5. **Texture vanishing after `Transform`** — shading read from a cached copy
   of the colours that `Transform` had already overwritten.
6. **Blurry Earth** — colours were being sampled once per vertex and
   interpolated. ManimGL has a real textured-surface shader; feeding it the
   `.obj`'s own `vt` coordinates gives a per-pixel lookup instead.

## Known gaps

- No automated test suite. Everything was checked by rendering and looking.
- `decimate()` transfers UVs and materials by nearest neighbour, which is an
  approximation.
- Not on PyPI.

See the package repository's README for the full list of what the renderer
itself cannot do — shadows, multiple lights, PBR, physics.
