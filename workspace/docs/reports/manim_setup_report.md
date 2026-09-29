# Manim Environment Setup — রিপোর্ট

**তারিখ:** ২৮ সেপ্টেম্বর ২০২৬
**উৎস রেপো:** [myabdur2121-cpu/manim-env-setup](https://github.com/myabdur2121-cpu/manim-env-setup)
**পদ্ধতি:** রেপোর ইনস্ট্রাকশন হুবহু অনুসরণ করা হয়েছে — কোনো ধাপ বাদ দেওয়া বা বদলানো হয়নি।
**ফল:** ✅ ManimCE, ManimGL, LaTeX, ffmpeg, দুটো ফন্ট — সব ইনস্টল ও রেন্ডার-পরীক্ষিত

---

## ১. স্যান্ডবক্স পরিবেশ

রেপোর `sandbox/manimgl/manimgl-e2b-sandbox.md` §1-এ যা লেখা আছে, পরিবেশ তার সাথে **হুবহু মিলেছে**:

| বিষয় | রেপোতে লেখা | এখানে পাওয়া গেছে | |
|---|---|---|---|
| OS | Debian 13 trixie | Debian 13 trixie, x86_64 | ✅ |
| Python | 3.13.14 | 3.13.14 | ✅ |
| pip | 26.x | 26.1.2 | ✅ |
| CPU / RAM | 2 CPU, 1 GB | 2 CPU, 1.9 GB | ✅ |
| Disk | ~20 GB free | 20 GB free | ✅ |
| sudo | পাসওয়ার্ড ছাড়া | কাজ করে | ✅ |

---

## ২. কী কী ইনস্টল হয়েছে

### ২.১ ManimCE — `sandbox/manimce/setup_manim.sh`

স্ক্রিপ্টটা যেভাবে আছে সেভাবেই চালানো হয়েছে (`FONT_USER_COPY` বন্ধ রাখা হয়েছে, README-র পরামর্শ অনুযায়ী — জায়গা বাঁচাতে)।

| | ভার্সন |
|---|---|
| **ManimCE** | v0.21.0 |
| **IPython** | 8.21.0 (pin করা, README-র সতর্কতা অনুযায়ী) |
| **ffmpeg** | 7.1.5 |
| **dvisvgm** | 3.4.4 |
| **LaTeX** | pdfTeX 3.141592653 (TeX Live 2025/Debian) |

apt প্যাকেজ: `libcairo2-dev`, `libpango1.0-dev`, `ffmpeg`, `dvisvgm`, `texlive`, `texlive-latex-extra`, `texlive-fonts-extra`, `texlive-latex-recommended`, `texlive-science`, `tipa` — মোট ~৮৯৩ MB ডাউনলোড।

### ২.২ ManimGL — `sandbox/manimgl/manimgl-e2b-sandbox.md`

গাইডের **§2.2 Option B** (recommended, editable install):

```
git clone --depth 1 https://github.com/3b1b/manim.git /home/user/src/manimGL
pip install -e /home/user/src/manimGL
```

| | |
|---|---|
| **ManimGL** | v1.7.2 ✅ (গাইডে যা লেখা ছিল, হুবহু) |
| **manimlib path** | `/home/user/src/manimGL/manimlib/__init__.py` ✅ |
| নতুন dependency | glfw, wgpu, rendercanvas, trimesh, pywavefront, diskcache, colour, addict, validators, appdirs, pyperclip |

> **কোনো dependency conflict হয়নি** — ManimCE (`manim`) আর ManimGL (`manimgl`/`manimlib`) একই Python env-এ পাশাপাশি চলছে। কমান্ড দুটো আলাদা: `manim` বনাম `manimgl`।

### ২.৩ ফন্ট — `sandbox/manimce/font.sh`

| ফন্ট | উৎস | ফল |
|---|---|---|
| **CMU Serif** | Debian প্যাকেজ `fonts-cmu` (Option A, SourceForge fallback লাগেনি) | ৩টি family ✅ |
| **Noto Serif Bengali** | notofonts GitHub release v3.000 | ৩২টি family/variant ✅ |

ইনস্টল হয়েছে `/usr/local/share/fonts/truetype/{cmu-serif,noto-serif-bengali}/`-এ, `fc-cache -fv` চালানো হয়েছে।

---

## ৩. ভেরিফিকেশন — সব পাস

### ৩.১ LaTeX প্যাকেজ (গাইড §2.4, §8)

| ফাইল | অবস্থা |
|---|---|
| `tipa.sty` | ✅ **আসলটাই পাওয়া গেছে** `/usr/share/texmf/tex/latex/tipa/` — dummy বানাতে হয়নি |
| `standalone.cls` | ✅ |
| `physics.sty` | ✅ |
| `wasysym.sty` | ✅ |
| `dsfont.sty` | ✅ |
| `babel.sty`, `amsmath.sty` | ✅ |

> গাইডে Debian trixie-র যে tipa বাগের কথা বলা আছে, সেটা এখানে হয়নি — কারণ `setup_manim.sh` স্ক্রিপ্টটা apt দিয়ে `tipa` প্যাকেজ ইনস্টল করে। তবুও `restore_env.sh`-এ fallback রাখা আছে।

### ৩.২ ManimCE রেন্ডার টেস্ট

```
cd /home/user/videos/00_test && manim -ql test_scene.py SetupCheck
```

রেপোর নিজের `test_scene.py` চালানো হয়েছে — বাংলা `Text`, `CMU Serif` `Text`, আর `MathTex` একসাথে:

- ✅ `Text("বাংলা ফন্ট ঠিক আছে", font="Noto Serif Bengali")` — যুক্তাক্ষর সহ ঠিকমতো রেন্ডার
- ✅ `Text("CMU Serif works", font="CMU Serif")`
- ✅ `MathTex(r"(A+B)^n=\sum_{r=0}^{n}\binom{n}{r}A^{n-r}B^r")`
- আউটপুট: `videos/00_test/media/videos/test_scene/480p15/SetupCheck.mp4`
- প্রমাণ ফ্রেম: `videos/00_test/manimce_font_check.png`

### ৩.৩ ManimGL রেন্ডার টেস্ট

```
manimgl demos/00_hello.py Hello -w -l -c "#000000" --video_dir videos/00_test
manimgl demos/04_tex_test.py TexTest -w -l --config_file configs/black.yml --video_dir videos/04_tex
```

| টেস্ট | ফল |
|---|---|
| হেডলেস `-w` রেন্ডার (X11 ছাড়া) | ✅ |
| `GlowDot(glow_factor=2.5)` | ✅ |
| `Tex(r"E = mc^2")` — pure math | ✅ |
| `TexText(r"Hello $x^2$ world")` — text+math | ✅ |
| ব্ল্যাক BG (`-c "#000000"` ফ্ল্যাগ) | ✅ পিক্সেল `(0,0,0)` |
| ব্ল্যাক BG (`--config_file black.yml`) | ✅ পিক্সেল `(0,0,0)` |

গাইড §5-এর পিক্সেল-চেক পদ্ধতিতেই যাচাই করা — ডিফল্ট ধূসর `(51,51,51)` হয়নি।

---

## ৪. ফোল্ডার স্ট্রাকচার (গাইড §3 অনুযায়ী)

```
/home/user/
├── src/manimGL/                    # ManimGL 1.7.2 (editable, .git মোছা)
├── demos/
│   ├── 00_hello.py                 # GlowDot টেস্ট
│   └── 04_tex_test.py              # Tex / TexText টেস্ট
├── configs/black.yml               # true black #000000
├── videos/
│   ├── 00_test/Hello.mp4           # ManimGL
│   ├── 00_test/media/.../SetupCheck.mp4  # ManimCE (বাংলা+CMU+MathTex)
│   ├── 00_test/manimce_font_check.png
│   ├── 04_tex/TexTest.mp4
│   ├── 02_demos_black/  03_glowdot/
├── docs/reports/manim_setup_report.md   # এই ফাইল
├── tools/restore_env.sh            # ⭐ reset হলে এক কমান্ডে সব ফেরত
├── logs/                           # setup লগ
├── archives/
└── manim-env-setup/                # ক্লোন করা রেপো
```

**Snapshot:** ৪.৬ MB, ৩৬১ ফাইল — লিমিট (128 MB / 10,000) থেকে অনেক নিচে ✅

---

## ৫. ⚠️ পরের session-এ কী করতে হবে

রেপোর README-তে যেটা বলা আছে সেটাই সত্যি: **apt আর pip দিয়ে ইনস্টল করা সব কিছু session-only** — snapshot-এ যায় না। `/home/user`-এর ফাইলগুলো (src, demos, configs, videos) থেকে যাবে, কিন্তু manim/ffmpeg/TeX মুছে যাবে।

তাই sandbox reset হলে শুধু একটা কমান্ড:

```bash
bash /home/user/tools/restore_env.sh
```

এটা নিজেই রেপোর `setup_manim.sh` + `font.sh` চালায়, ManimGL `pip install -e` করে, tipa fallback দেখে, ফোল্ডার আর `black.yml` বানায়, শেষে verify করে। সময় লাগে ~৩-৫ মিনিট।

---

## ৬. ব্যবহারের চিটশিট

```bash
# ── ManimCE (Cairo) — বাংলা লেখা + MathTex-এর জন্য সবচেয়ে ভালো ──
manim -ql  scene.py MyScene          # 480p ড্রাফট
manim -qm  scene.py MyScene          # 720p
manim -qh  scene.py MyScene          # 1080p
#   Text("বাংলা", font="Noto Serif Bengali")
#   Text("English", font="CMU Serif")
#   MathTex(r"\frac{a}{b}")

# ── ManimGL (3b1b, OpenGL) — GlowDot / 3D / সিনেম্যাটিক ──
manimgl demos/x.py MyScene -w -l  -c "#000000" --video_dir videos   # 480p
manimgl demos/x.py MyScene -w -m  -c "#000000" --video_dir videos   # 720p
manimgl demos/x.py MyScene -w --hd -c "#000000" --video_dir videos  # 1080p
#   -w সবসময় লাগবে (হেডলেস, X11 নেই)
#   GlowDot থাকলে VGroup নয় → Group ব্যবহার করো
#   Tex = শুধু math,  TexText = text+math,  Text = LaTeX ছাড়া
```

**পারফরম্যান্স নোট (README থেকে):** ২ CPU / ১ GB RAM-এ `-qm`-এ ৩৩ মিনিটের ভিডিও রেন্ডার করতে ~২৫ মিনিট লেগেছিল। লম্বা রেন্ডার ব্যাকগ্রাউন্ড প্রসেসে চালাতে হবে।

**জায়গা বাঁচাতে:** রেন্ডারের পর `media/`, `partial_movie_files/`, `__pycache__` মুছে দিতে হবে।

---

## ৭. GitHub টোকেন

- টোকেন সেভ করা আছে: `/home/user/secrets/github_token.md` (পারমিশন `600`)
- অ্যাকাউন্ট: `myabdur212121-afk` | স্কোপ: `repo, delete_repo, project, write:packages`
- টোকেনটা শুধু রেপোর মেটাডেটা পড়তে ব্যবহার হয়েছে — রেপো পাবলিক, তাই ক্লোন anonymous-ই হয়েছে
- **কোনো কিছু লেখা/বদলানো/ডিলিট করা হয়নি**

### 🔴 এখন করণীয়: https://github.com/settings/tokens → টোকেন **revoke** করো

বলে দিও, ফাইলটা আমি মুছে দেব।
