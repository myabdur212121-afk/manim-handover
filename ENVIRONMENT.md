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

So `manimlib`, `ffmpeg` and LaTeX disappear regularly, while the code
stays. This is normal platform behaviour, not a fault, and not caused by
anything the assistant does — one turn began with the machine 21 seconds
old, before a single command had run.

Other chats do not notice because nothing is installed in them. The base
image already has Python, numpy, scipy, matplotlib and node. Of ManimGL's
31 dependencies, **14 are already present**; 17 are not.

## Getting back to work

```bash
bash tools/restore_env.sh --no-latex      # ~45 s  ← use this
bash tools/restore_env.sh                 # ~2 min, adds the LaTeX suite
```

`--no-latex` skips **775 MB of the 852 MB** apt list. None of the scenes
need it — they all use `Text`, which goes through Pango. Use the full form
only for `Tex` / `TexText`.

Fonts are installed either way; skipping them once turned every Bengali
caption into boxes.

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
├── src/manimgl_myplugin/   the library
├── src/manimGL/            ManimGL checkout — read it when unsure
├── demos/                  scenes
├── tests/                  three files, ~60 checks
├── models/                 .obj files and textures
├── videos/                 renders (never committed)
├── docs/                   guide, architecture note, reports
├── packaging/              the README / notes that go to the repos
├── prototypes/             throwaway experiments and their stills
├── tools/                  restore_env.sh, trace_boot.sh, fetchers
├── logs/                   restore logs, memory traces, boot trace
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
