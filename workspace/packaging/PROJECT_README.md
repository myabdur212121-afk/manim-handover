# manim_obj

A ManimGL extension: load Wavefront `.obj` models and use them as native
mobjects.

```python
from manimlib import *
from manim_obj import OBJMobject

class Demo(ThreeDScene):
    def construct(self):
        self.camera.frame.reorient(0, 70, 0)
        self.add(OBJMobject("chair.obj", height=4))
        self.wait(2)
```

**ManimGL only** — not Manim Community Edition. See `NOTES.md` §5.

> **Read [`NOTES.md`](./NOTES.md) first.** It lists every bug that came up
> while building this, what caused it, and which directions are already
> known to be dead ends.

## Layout

```
manim_obj/
├── NOTES.md              ← problems, causes, dead ends, expected numbers
├── requirements.txt      ← this project needs ManimGL, not ManimCE
├── src/manim_obj/        ← the library (3 files, 2,308 lines)
├── tests/                ← 21 checks, ~9 s
├── demos/                ← 7 scenes
├── models/               ← 14 .obj files + Earth's texture maps
├── docs/guide_bn.md      ← the long guide, in Bengali
└── tools/                ← model fetcher, environment restore
```

## Running it

```bash
pip install -r requirements.txt
pip install git+https://github.com/3b1b/manim.git      # ManimGL
export PYTHONPATH=$PWD/src

python tests/test_manim_obj.py                         # 9 s, check it works

manimgl demos/07_minimal.py Simplest -w -l -c "#070B14" --video_dir /tmp/out
```

`MANIM_OBJ_MODELS` points at the model directory (default `~/models`), so
either copy `models/` there or set the variable.

## The scenes

No rendered video is committed — run these to get it back.

| scene | length | what it shows |
| --- | --- | --- |
| `07_minimal.py` | — | four scenes, two lines each |
| `05_obj_building.py` | 48 s | one building, nine beats |
| `06_earth_chair.py` | 40 s | two downloaded models, real texture mapping |
| `08_resolution.py` | 40 s | `decimate` / `subdivide` / `displace` |
| `09_landscape.py` | 72 s | six models, moving camera and light |
| `10_highland.py` | 90 s | eight models, QHD, placement on a mountain |

```bash
# the big one — about 13 minutes at QHD
manimgl demos/10_highland.py Highland -w -r 2560x1440 \
    -c "#05070E" --video_dir /tmp/out
```

## What it does

Loading (path, bare name, URL, raw text, or an existing `MeshData`; `.stl`,
`.ply` and `.glb` through trimesh), sizing and axis conversion, eight colour
modes, real per-pixel texture mapping from the `.mtl`, smooth/flat shading,
slicing and splitting, crease wireframes, point clouds, and a `BuildMesh`
animation that assembles a model out of its own triangles.

It also repairs the things real exports get wrong — duplicate coincident
faces that z-fight (47% of the test building), backslash line continuations
that silently drop faces, and Z-up CAD conventions.

Resolution goes both ways: `decimate(1500)`, `subdivide(2)`,
`displace("bump.jpg")`.

The clean packaged version is at
[myabdur212121-afk/manim-obj](https://github.com/myabdur212121-afk/manim-obj).
