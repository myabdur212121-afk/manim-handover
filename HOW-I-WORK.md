# How the work was done

Not a style guide in the abstract — these are the habits that actually
produced the working code, each with the moment it earned its place.

---

## 1. Verify, do not assert

Every claim in this project was measured before it was made. It is the
single habit that mattered most, because **being confidently wrong wastes
the user's time and trust, and he checks.**

Things that looked obvious and were not:

| assumption | what measuring showed |
| --- | --- |
| "the 4k texture downloads fine, curl says 200" | It was a 16 KB **HTML error page**. Only 2k and 8k exist. |
| "same-material duplicate faces can't z-fight, the colour is identical" | They are wound opposite ways, so one is lit and one is not. |
| "the loader works without manim, the README says so" | The package `__init__` dragged manimlib in every time. The claim was false until it was tested. |
| "Saturn takes 42 seconds to build, that needs optimising" | 41 of them were downloads. The build is 1.1 s. |
| "the topmost vertex of a globe is its pole" | A sphere's silhouette does not change when you rotate it. The pole had to be found through the UVs. |
| "`point_at(23, 13)` is the Sahara" | It was the middle of the Pacific — the map is half a turn round from the maths. |

When a probe disagrees with expectation, **suspect the probe first**. The
curl-says-200 case was a probe lying, not a server misbehaving.

## 2. Build a prototype before committing to a design

`prototypes/shapes_proto.py` was written outside the package, purely to
answer "can two functions really make a sphere and a cube?" with a picture
instead of a claim.

It cost about twenty minutes and found two bugs that would otherwise have
reached the package: `extrude` had no end caps, and a merged `Cube` kept
24 corners instead of 8, so smooth subdivision peeled it into six discs.

Prototypes go in `prototypes/`, clearly named, never imported by the
package. If the idea is dropped, deleting the folder costs nothing.

## 3. Render it and look at it

Tests pass on numbers. Some things are only visible.

The workflow, used dozens of times:

```bash
manimgl demos/x.py Scene -w -l -c "#070B14" --video_dir /tmp/d   # draft
for t in 6 12 18 25; do ffmpeg -y -ss $t -i /tmp/d/Scene.mp4 -vframes 1 /tmp/f$t.png; done
ffmpeg -y -i /tmp/f6.png -i /tmp/f12.png -filter_complex "[0:v][1:v]hstack" /tmp/sheet.png
```

Then read the contact sheet. `-l` is about six times faster than `-m` and
shows every mistake that matters except texture sharpness.

**Two real bugs survived every numeric check and were caught by a human
looking at a video.** That is not a failure of testing; it is the reason
looking is part of the job.

## 4. Read the source instead of guessing the API

ManimGL is in the workspace at `src/manimGL`. Reading it settled questions
that guessing would have got wrong:

- `textured_surface.wgsl` — `if (color.a == 0.0) { discard; }` then
  `result.a = in.opacity;`. So a hard cutout works and **partial alpha is
  thrown away**. That one line decided the whole ring design: opacity had
  to come from the vertices.
- `surface_mesh.wgsl` — `resolution.x == 0` means "these points are a
  plain triangle list". That is what lets an `.obj` use the textured
  shader at all.
- `Sphere` is `resolution=(101, 51)` with normals from `np.gradient` of
  the parametric grid — which is why it looks smooth and a loaded mesh
  does not.

Ten minutes of reading beats an hour of trial and error.

## 5. Write the symptom the way a person would see it

Every entry in a `notes.md` starts with what you would actually *see*:

> "walls speckled with two colours", not "depth buffer precision issue"
> "a cube that came apart into six discs"
> "a ring shadow nobody could see"

A symptom nobody can recognise is not worth writing down. The user found
three bugs by describing what he saw; the notes should speak the same way.

## 6. Time the parts before optimising any of them

Saturn appeared to take 42 seconds. Wrapping each stage in a timer showed
1.1 s of computation and 41 s of downloading. Optimising the mesh code
would have achieved nothing.

## 7. Prefer functions for construction, classes for knowledge

The rule that settled several design arguments:

- `Mars()` is a **class**, because it carries facts a user should not have
  to look up — radius 3,396,190 m, flattening 0.0059, which texture.
- `helix()` is a **function**, because it only builds geometry.
- A `3DObject` base class would carry neither, and `Surface` already is
  that. It was not built.

The corollary: generalise the *operation*, not the taxonomy. Two functions
(`revolve`, `extrude`) cover more shapes than a list of ten classes, and
adding a new shape needs no registration anywhere.

## 8. Do not add abstraction before you have two real cases

Asked to build a class hierarchy for shapes that might be needed later,
the answer was no — and the evidence was in the same project. Two things
already existed, models from files and bodies from formulas, and their
shared ground turned out to be **`MeshData`, a data structure**, not a
base class. That could not have been predicted; it was discovered.

Wrong abstraction is much harder to remove than missing abstraction is to
add.

## 9. Say what does not work, in the same breath

Every README and every `notes.md` has a section on limits. No shadows, one
light, no PBR, no physics. The user reached the same conclusion himself
and said so; overselling would only have cost credibility.

When something is a renderer limit rather than a missing feature, say
which. "Gas giants have no elevation data" is not a gap in the helper —
they have no surface.

## 10. Small, verifiable steps, each one checked

The pattern throughout: change one thing, run the tests, render a draft,
look, then move. Bugs were found within a minute or two of being
introduced, which is why none of them took long to fix.

## 11. Explain before building, when he asks

Several turns produced no code at all — an architecture note, a
comparison picture, an answer to "what is a spring". Those were the
deliverable. He said outright that he wants to understand the structure
because he intends to write code himself, and that understanding has
improved the design more than once.

---

## Conventions that ended up mattering

- **Tests mirror bugs.** Every check corresponds to something that was
  once broken, so a failure points at a specific entry in `notes.md`.
- **Six-section notes**: what it is · problems faced · dead ends ·
  expected numbers · hard limits · what to do first.
- **Comments explain why, never what.** `# the bigger face wins, so a
  small detail flush on a wall cannot punch a hole in it`.
- **British spelling**, plain words, no exclamation marks, no filler.
- Numbers in documents are measured, and the measurement is named.
