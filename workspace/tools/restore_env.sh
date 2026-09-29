#!/usr/bin/env bash
# ==============================================================================
# restore_env.sh — Sandbox reset হলে এক কমান্ডে পুরো Manim পরিবেশ ফেরত আনে
#
#   bash /home/user/tools/restore_env.sh
#
# কী ফেরত আসে: ManimCE 0.21.0 + ManimGL 1.7.2 + LaTeX + ffmpeg
#               + CMU Serif + Noto Serif Bengali
#
# উৎস: github.com/myabdur2121-cpu/manim-env-setup
#   - sandbox/manimce/setup_manim.sh  (ManimCE + LaTeX + font.sh)
#   - sandbox/manimgl/manimgl-e2b-sandbox.md  (ManimGL)
#
# কেন দরকার: apt আর pip দিয়ে ইনস্টল করা সবকিছু session-only, snapshot-এ থাকে না।
#            /home/user/-এর ফাইল (src/, demos/, configs/, videos/) থেকে যায়।
# ==============================================================================
set -e

# --no-latex : LaTeX স্যুট বাদ দেয় (repo তালিকার ৮৫২ MB-র ৭৭৫ MB)। Text/Pango
#              চলে, Tex/TexText চলবে না। ডিফল্ট আচরণ অপরিবর্তিত।
NO_LATEX=0
[ "${1:-}" = "--no-latex" ] && NO_LATEX=1

REPO_DIR="/home/user/manim-env-setup"
GL_DIR="/home/user/src/manimGL"

echo "############ [1/4] setup repo ############"
if [ ! -d "$REPO_DIR" ]; then
    git clone --depth 1 https://github.com/myabdur2121-cpu/manim-env-setup.git "$REPO_DIR"
fi

if [ "$NO_LATEX" = "1" ]; then
    echo "############ [2/4] ffmpeg + cairo/pango (LaTeX বাদ) ############"
    sudo apt-get update -qq
    sudo DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        libcairo2-dev libpango1.0-dev ffmpeg
    pip install --quiet manim "ipython==8.21.0"
    # ফন্ট আলাদা — LaTeX বাদ দিলেও Noto Serif Bengali দরকার হয়
    bash "$REPO_DIR/sandbox/manimce/font.sh"
else
    echo "############ [2/4] ManimCE + LaTeX + fonts ############"
    bash "$REPO_DIR/sandbox/manimce/setup_manim.sh"
fi

echo "############ [3/4] ManimGL ############"
if [ ! -d "$GL_DIR/manimlib" ]; then
    git clone --depth 1 https://github.com/3b1b/manim.git "$GL_DIR"
    rm -rf "$GL_DIR/.git"      # snapshot বাঁচাতে (~15 MB)
fi
pip install -e "$GL_DIR"
# decimate()-এর quadric backend (২৮৪ KB)
pip install --quiet fast-simplification

# Debian trixie-তে tipa.sty না থাকলে dummy (setup_manim.sh apt tipa দেয়, তাই সাধারণত লাগে না)
if [ "$NO_LATEX" = "0" ] && ! kpsewhich tipa.sty >/dev/null 2>&1; then
    echo "  -> tipa.sty missing, creating dummy"
    sudo mkdir -p /usr/share/texlive/texmf-dist/tex/latex/tipa
    printf '\\NeedsTeXFormat{LaTeX2e}\n\\ProvidesPackage{tipa}[dummy]\n\\endinput\n' \
        | sudo tee /usr/share/texlive/texmf-dist/tex/latex/tipa/tipa.sty >/dev/null
    sudo mktexlsr
fi

echo "############ [3b/4] manimgl_myplugin (helpers) on the import path ############"
# site-packages is wiped with the rest of the session, the package itself
# lives in /home/user/src and survives, so only the .pth has to come back
SITE=$(python3 -c "import site; print(site.getsitepackages()[0])")
echo "/home/user/src" | sudo tee "$SITE/manimgl_myplugin.pth" >/dev/null
python3 -c "import manimgl_myplugin; print('  manimgl_myplugin', manimgl_myplugin.__version__, 'ready')"

echo "############ [4/4] folders + black config ############"
mkdir -p /home/user/{src,demos,configs,archives,tools,logs} \
         /home/user/videos/{00_test,02_demos_black,03_glowdot,04_tex} \
         /home/user/docs/{solutions,reports}
cat > /home/user/configs/black.yml << 'YML'
camera:
  background_color: "#000000"
YML

echo "############ VERIFY ############"
manim --version
manimgl --version
ffmpeg -version | head -n1
latex --version | head -n1
dvisvgm --version | head -n1
echo -n "CMU Serif faces: ";          fc-list : family | grep -ci "cmu serif"
echo -n "Noto Serif Bengali faces: "; fc-list : family | grep -ci "noto serif bengali"
echo "================ Environment ready ================"
