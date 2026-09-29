# Debugging, concretely

The techniques below each found a real bug in this project. They are
written as recipes because that is how they were used.

---

## Numbers first, pictures second

Before rendering anything, ask the mesh what it thinks.

```python
mesh = load_mesh("building.obj")
print(mesh.num_faces, mesh.size, mesh.material_names)
print(len(mesh.coincident_pairs(cross_material_only=False)))
```

That last line turned "the walls look wrong" into "6,417 pairs of
triangles occupy the same space", which is a fixable statement. A
histogram, a count or a min/max is usually enough to locate a problem
before a single frame is rendered.

## Contact sheets

The main loop. Draft render, pull frames, stack, look.

```bash
manimgl demos/x.py Scene -w -l -c "#070B14" --video_dir /tmp/d
cd /tmp/d && for t in 6 12 18 25 31; do
  ffmpeg -y -v error -ss $t -i Scene.mp4 -vframes 1 f$t.png; done
ffmpeg -y -v error -i f6.png -i f12.png -i f18.png \
  -filter_complex "[0:v]scale=520:-1[a];[1:v]scale=520:-1[b];[2:v]scale=520:-1[c];[a][b][c]hstack=3" sheet.png
```

Sample times must miss the transitions or you photograph a fade. If a
panel looks half-dissolved, move the timestamp, do not assume a bug.

## A/B with exactly one variable changed

The only reliable way to show a fix worked.

```python
for label, value in [("dedupe=False", False), ('dedupe="auto"', "auto")]:
    model = OBJMobject("building.obj", dedupe=value)
    ...render both, stack side by side...
```

This produced `dedupe_before_after.png`, `texture_sharpness.png` and
`sphere_vs_obj.png`. Each settled an argument that words could not.

## Zoom in with nearest-neighbour

Soft artefacts vanish when an image is scaled down. Crop and magnify
without smoothing:

```bash
ffmpeg -y -i frame.png -vf "crop=180:300:420:40,scale=720:-1:flags=neighbor" zoom.png
```

That is how the checkerboard on the roof slabs became visible.

## Watch memory during a long render

The box has 2 GB and no swap. A render that dies silently is usually OOM.

```bash
( manimgl ... > /tmp/r.log 2>&1 ) &
RP=$!
while kill -0 $RP 2>/dev/null; do
  echo "$(date +%H:%M:%S) rss=$(ps -eo rss= --ppid $RP -p $RP | awk '{s+=$1} END{print int(s/1024)}')MB \
avail=$(free -m | awk '/^Mem:/{print $7}')MB" >> /home/user/logs/mem.log
  sleep 10
done
```

The QHD render peaked at **1,804 MB of 1,984** with 78 MB to spare. That
number is the ceiling; anything heavier needs `decimate` first.

## Time the stages before optimising

```python
orig = Body._build_globe
def timed(*a, **k):
    t = time.time(); r = orig(*a, **k); print(time.time() - t); return r
Body._build_globe = timed
```

Saturn's "42 seconds" was 1.1 s of work and 41 s of downloading.

## Check the MIME type, not the status code

```bash
curl -sL -o t.jpg "$URL"
file -b --mime-type t.jpg        # text/html means it is an error page
```

`curl -L` followed a redirect to an HTML 404 and reported **200**. The
file was 16 KB of markup. `urllib` was right to raise.

## Simulate a missing package properly

To prove the loader does not need manim, block the import for real:

```python
from importlib.abc import MetaPathFinder
class Block(MetaPathFinder):
    def find_spec(self, name, path=None, target=None):
        if name == "manimlib" or name.startswith("manimlib."):
            raise ImportError("simulated")
sys.meta_path.insert(0, Block())
```

An earlier attempt used the removed `find_module` API, silently did
nothing, and produced a passing test that proved nothing. If a negative
test never fails, it is not a test.

## Beware the always-true shell check

```bash
if grep -rl "$TOKEN" . | head -3; then echo "LEAK"; fi      # always fires
```

A pipeline's status is the *last* command's, and `head` always succeeds.
Capture first, then test:

```bash
hits=$(grep -rl "$TOKEN" . || true)
[ -n "$hits" ] && echo "LEAK: $hits"
```

## When geometry hides the answer

A sphere's silhouette does not change when it rotates, and its topmost
vertex is not its pole. Symmetry destroys evidence. Find the feature
through the **UVs** instead, or sample the texture at a place you can name:

```python
assert not is_sea(23, 13),  "the Sahara came out wet"
assert is_sea(0, -150),     "the Pacific came out dry"
```

That test caught a 180° longitude offset that looked perfectly fine on
screen.

## Turn each bug into a test named after the symptom

```python
def test_spin_leaves_the_pole_alone_but_rotate_does_not(): ...
def test_a_welded_cube_subdivides_into_one_blob(): ...
def test_point_at_agrees_with_the_texture(): ...
```

A failure then reads like a sentence and points straight at the entry in
`notes.md` that explains it.

---

## Sandbox habits

- `bash tools/restore_env.sh --no-latex` after every reset — 45 s.
- `bash tools/trace_boot.sh` writes one line per turn, so a reset that
  happened between turns is visible rather than mysterious.
- Long renders go through a background process, not a foreground command
  that a timeout can kill.
- Scratch files in `/tmp`, which is never snapshotted. Anything worth
  keeping goes under `/home/user`.
