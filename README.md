# Handover

**If you are an assistant starting a fresh conversation with this user —
read this repository first. It exists so you do not have to be told
everything again.**

The previous conversation ran long enough to be slow to load, so it was
ended deliberately and everything worth keeping was written down here.
Nothing below is a summary of chat; it is the working state.

---

## Read in this order

| file | what it gives you |
| --- | --- |
| [`HANDOVER.md`](HANDOVER.md) | who the user is, what was built, where it stopped, what is next |
| [`HOW-I-WORK.md`](HOW-I-WORK.md) | the working method that produced it — worth matching |
| [`DEBUGGING.md`](DEBUGGING.md) | the specific techniques that found the real bugs |
| [`ENVIRONMENT.md`](ENVIRONMENT.md) | the sandbox, what survives a reset, how to get back to work |
| [`DECISIONS.md`](DECISIONS.md) | every consequential choice and the reason for it |
| `workspace/` | every file from the working directory |

Five minutes on the first two is enough to continue without asking the
user to repeat himself.

---

## The thirty-second version

The user is building **`manimgl_myplugin`**, a plugin for ManimGL. Three
helpers work today:

| helper | what it does |
| --- | --- |
| `obj` | Wavefront `.obj` models as native ManimGL mobjects |
| `shapes` | meshes from formulas — revolve, extrude, or borrow any ManimGL surface |
| `astro` | planets, moons, rings, with geography and orbits |

**60+ tests pass in about a minute.** Two live repositories:

- [`manimgl-myplugin`](https://github.com/myabdur212121-afk/manimgl-myplugin) — the clean package
- [`manim-projects`](https://github.com/myabdur212121-afk/manim-projects) — the archive, under `2026/manimgl_myplugin/`

Next on the list: **the Sun** — it emits light rather than receiving it, so
it needs different handling, and the corona is the hard part.

---

## Before you do anything

```bash
cd workspace
bash tools/restore_env.sh --no-latex      # ~45 s, the toolchain is not persistent
python3 tests/test_obj.py                 # 21
python3 tests/test_shapes.py              # 18
python3 tests/test_astro.py               # 29
```

If those pass, the library is intact and you can start. If one fails, the
matching `docs/<helper>/notes.md` says what that check was protecting.

---

## The one thing to get right

This user does not want code handed to him. He wants to **understand the
structure well enough to write it himself**, and he says so. Several times
he stopped work to ask how something fits together, and each time the
answer improved the design.

So: explain before building, show the reasoning, and when he proposes
something that will not work, say so and say why. He responds well to
being disagreed with when there is evidence behind it. He responds badly
to being handed a wall of code.

He also asked, in as many words, that the next assistant should already
know all this — which is why this repository exists.
