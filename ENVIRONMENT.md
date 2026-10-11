# The environment

Everything here was measured, not assumed.

---

## What survives and what does not

Only **`/home/user`** is saved between sessions.

| | where it lives | survives? |
| --- | --- | --- |
| project files | `/home/user` | ✅ |
| `pip install` | `/usr/local/lib/python3.13/site-packages` | ❌ |
| `apt install` | `/usr/bin`, `/usr/lib` | ❌ |
| repo remotes (`.git/config`) | inside `/home/user`, but stripped | ❌ |

So `manimlib`, `ffmpeg` and LaTeX disappear regularly, while the code
stays. One row deserves its own sentence: `.git/config` is stripped from
snapshots (credential hygiene), so **every reset silently removes the
remotes from all local repos** — re-add them before any push; the URLs
are in `our-work/remotes.md` in the live workspace. This is normal platform behaviour, not a fault, and not caused by
anything the assistant does — one turn began with the machine 21 seconds
old, before a single command had run.

Other chats do not notice because nothing is installed in them. The base
image already has Python, numpy, scipy, matplotlib and node. Of ManimGL's
31 dependencies, **14 are already present**; 17 are not.

## Getting back to work

The old `tools/restore_env.sh` went with the workspace reorganisation;
the recipe now lives in `manim-env-setup`, and amounts to this:

```bash
pip install -e src/manimGL -e manimgl-myplugin "setuptools<81" \
    trimesh fast-simplification av        # ~40 s
sudo apt-get install -y -q ffmpeg
bash manim-env-setup/sandbox/manimce/font.sh   # Bengali + CMU fonts
```

LaTeX (~775 MB) is only needed for `Tex` / `TexText`; the scenes all
use `Text`, which goes through Pango. Skipping the fonts once turned
every Bengali caption into boxes.

The glow patches in `src/manimGL` survive resets with the workspace —
the editable install picks them up again on the next `pip install -e`,
and the same diff is carried in this repository at
`patches/manimgl-glow-renderer.patch` (and at `our-work/patches/` in the
live workspace).

## The machine

| | |
| --- | --- |
| CPU | 2 cores |
| RAM | **1,984 MB, no swap** |
| disk | 25 GB, ~17 GB free |
| GPU | software (wgpu/lavapipe) |

### Measured render cost

| scene | resolution | triangles | time | peak RSS |
| --- | --- | --- | --- | --- |
| one building, 48 s | 1280×720 | 7,938 | 2.5 min | 1,132 MB |
| eight models, 90 s | **2560×1440** | ~70,000 | 13 min | **1,804 MB** |
| solar system, 30 s | 1280×720 | ~60,000 | 6–10 min | (not yet measured) |

QHD with that much geometry is the ceiling — 78 MB of headroom. For 4K,
cut geometry first.

## Command notes

```bash
manimgl demos/x.py Scene -w -l  -c "#070B14" --video_dir /tmp/out   # 854×480 draft
manimgl demos/x.py Scene -w -m  -c "#070B14" --video_dir videos/x   # 1280×720
manimgl demos/x.py Scene -w -r 2560x1440 -c "#070B14" --video_dir videos/x
```

- `-w` is required; without it manimgl opens a window there is none of.
- **`-c` on the command line** sets the background.
  `self.camera.background_color` does nothing in `construct()`.
- `-l` renders smaller but still at **30 fps** — divide frames by 30 for
  the real duration, not by the frame count.

## Traps that cost time

| | |
| --- | --- |
| `manimlib/typing.py` shadows the standard library | never run Python from inside `src/manimGL/manimlib` |
| `which x && y` truncates when `which` fails | use `;` or `|| true` |
| `start_process` piping to `tee` in a missing directory | reports exit 1 on success; create the directory first |
| `.cache`, `build`, `dist`, `node_modules`, `__pycache__` | excluded from the snapshot — never keep anything there |
| snapshot cap | roughly 128 MB; the workspace sits near 90 MB, so large files need thought |

## Layout

```
/home/user/
├── manimgl-myplugin/       the library, its own git repo
├── src/manimGL/            3b1b checkout + glow patches (uncommitted; diff kept in our-work/patches/)
├── our-work/               non-repo: scenes/, videos/, patches/, remotes.md, README
├── manim-env-setup/        environment recipes (other account, read-only)
├── manim-handover/         this repository; carries the sun scenes and the glow patch too
├── models/                 .obj files and textures
└── secrets/                the GitHub token — never commit this
```

## GitHub

The token is at `secrets/github_token.md`, token string only, `600`.
Account `myabdur212121-afk`, scopes `repo`, `delete_repo`, `project`,
`write:packages`.

**The user has been asked repeatedly to revoke it and may already have
done so.** Check before relying on it. Note also that
`myabdur2121-cpu/manim-env-setup` is a *different account* — read access
only.

GitHub is **not** an available connector; drive it with `curl` and the
token, or `git` with the token in the remote URL. Always confirm no
tracked file contains the token before committing.
