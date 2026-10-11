"""
Sun -- নিঃসরণকারী বস্তুর প্রথম প্রোটোটাইপ, corona-প্রার্থীদের রায়সহ।

    manimgl our-work/scenes/sun.py Sun -w -m -c "#070B14" \
        --video_dir our-work/videos

যা মাপা হয়েছে (S1/S2 প্রোব, README-তে সংখ্যা): শেডিং শূন্য করলে গোলক
নিজেই জ্বলে (কোনো আলো তাকে চালায় না); দৃশ্যের আলো কেন্দ্রে বসালে গ্রহ
সূর্য থেকেই আলো পায় (উজ্জ্বল অর্ধ উল্টে যায়: −২.৪ px বনাম +৪.০ px)।
corona: বড় আভা-ডট মসৃণ রিম দেয়, ছোট ডটের শেল লম্বা লেজ — দুটো স্তরে।
এটি প্লাগইনে নয়, our-work-এর প্রোটোটাইপ; রায়ের পর ঠিক হবে কী যাবে।
"""

import numpy as np
from manimlib import *

from manimgl_myplugin.astro import Body, Venus

INK, DIM, CYAN, GOLD = "#EAF0F8", "#7E93AC", "#6FE3C4", "#F2B33D"
WARM = "#FFC266"
MONO = "DejaVu Sans Mono"
BN = "Noto Serif Bengali"


class Sun(ThreeDScene):
    # -------------------------------------------------------------- hud --

    def hud(self, text, *, corner=DL, font=None, size=20, color=CYAN, buff=0.45):
        mob = Text(text, font=font or MONO, font_size=size,
                   fill_color=color, stroke_width=0)
        mob.fix_in_frame()
        mob.to_corner(corner, buff=buff)
        return mob

    def swap_hud(self, old, new, run_time=0.5):
        if old is None:
            self.play(FadeIn(new, shift=0.2 * UP), run_time=run_time)
        else:
            self.play(FadeOut(old, shift=0.2 * UP),
                      FadeIn(new, shift=0.2 * UP), run_time=run_time)
        return new

    def clear_hud(self, *huds, run_time=0.5):
        huds = [h for h in huds if h is not None]
        if huds:
            self.play(*[FadeOut(h, shift=0.2 * UP) for h in huds],
                      run_time=run_time)

    # ------------------------------------------------------------ pieces --

    def corona(self, pos, r):
        """
        Light that adds, not tints -- the classic glow-sprite method.
        Three camera-facing sprites with soft falloffs (DotCloud dots,
        whose shader fades each as (1 - r)^glow_factor), tight and bright
        near the limb, wide and faint far out; overlapping layers
        accumulate, which is what makes the halo read as light coming
        out of the disc. A faint shell of glowing dots adds the wispy
        structure real coronas have. All drawn additively (the
        renderer's blend_mode="add"), with the depth test off so the
        glow wraps round the disc instead of hiding behind it.
        """
        from manimgl_myplugin.astro.bodies import _apply_occlusion
        rng = np.random.default_rng(7)
        n = 1200
        v = rng.normal(size=(n, 3))
        v /= np.linalg.norm(v, axis=1, keepdims=True)
        rr = 1.08 + 1.25 * rng.random(n) ** 2      # dense near, sparse far
        # A sprite's bright centre falls behind the disc, so what the halo
        # shows is each falloff's tail read from the limb outward: gentle
        # exponents, not steep ones, are what make the light reach
        layers = [
            # a blown-out core, lifting the disc itself
            DotCloud([pos], radius=0.9 * r, color="#FFF3D6",
                     glow_factor=2.0, opacity=0.35),
            # the intense halo hugging the limb
            DotCloud([pos], radius=1.35 * r, color="#FFE9B8",
                     glow_factor=1.2, opacity=0.9),
            # the mid reach
            DotCloud([pos], radius=2.3 * r, color="#FFC873",
                     glow_factor=1.0, opacity=0.5),
            # the wide faint tail
            DotCloud([pos], radius=3.4 * r, color="#FF9E4D",
                     glow_factor=0.5, opacity=0.28),
            # wisps of structure over the smooth light
            DotCloud(pos + v * (rr * r)[:, None],
                     radius=0.045 * (r / 1.1) * 1.4, color="#FFC873",
                     opacity=0.30, glow_factor=1.5),
        ]
        for layer in layers:
            layer.blend_mode = "add"       # light accumulates, see S4/smoke
            _apply_occlusion(layer, True)  # x-ray: wrap the disc, z above it
        return Group(*layers)

    # ------------------------------------------------------------ scene --

    def construct(self):
        frame = self.camera.frame
        frame.set_height(10.0).reorient(-14, 72, 0)

        head = self.hud("সূর্য — নিঃসরণকারী বস্তু", corner=UL,
                        font=BN, size=24, color=INK)
        self.play(FadeIn(head, shift=0.2 * UP), run_time=0.5)

        # ---- 1. it emits: nothing lights it -----------------------------
        code = self.hud('Body(radius=1.6, texture="sun")\n'
                        'sun.globe.set_shading(0, 0, 0)')
        sun = Body(radius=1.6, texture="sun", light=np.array([0.0, 0, 0]))
        sun.globe.set_shading(0.0, 0.0, 0.0)
        self.play(FadeIn(code, shift=0.2 * UP),
                  FadeIn(sun, scale=0.9), run_time=1.4)
        self.camera.light_source.move_to(sun.get_center())
        frame.add_updater(lambda m, dt: m.increment_theta(0.10 * dt))
        note = self.hud("শেডিং শূন্য — একে আলো চালায় না, এ নিজেই আলো",
                        corner=UR, font=BN, size=20, color=DIM)
        self.play(FadeIn(note), run_time=0.5)
        self.wait(1.6)

        # ---- 2. the corona, two measured layers --------------------------
        code = self.swap_hud(code, self.hud(
            "for s in glow_sprites:\n"
            "    s.blend_mode = \"add\"   # light that adds, not tints"))
        note2 = self.hud("আলো এখন যোগ হয় — স্তরগুলো জমে,\n"
                         "প্রান্ত থেকে বাইরে ক্রমশ ম্লান",
                         corner=UR, font=BN, size=20, color=DIM)
        self.clear_hud(note)
        halo = self.corona(sun.get_center(), sun.radius)
        self.play(FadeIn(halo[0]), FadeIn(note2), run_time=1.2)
        self.play(*[FadeIn(h, lag_ratio=0.2) for h in halo[1:]], run_time=2.0)
        self.wait(2.0)

        # ---- 3. a planet lit from it, and only from it -------------------
        code = self.swap_hud(code, self.hud(
            "venus = Venus(radius=0.55)\n"
            "self.camera.light_source.move_to(sun.get_center())"))
        note3 = self.hud("শুক্রের দিনের দিকটা সূর্যের দিকে",
                         corner=UR, font=BN, size=20, color=DIM)
        self.clear_hud(note2)
        venus = Venus(radius=0.55)
        venus.move_to(np.array([5.6, 1.1, 0.8]))
        self.play(FadeIn(venus, scale=0.8), FadeIn(note3), run_time=1.2)
        self.wait(1.4)

        # the camera swings round; the lit side stays sun-ward
        note4 = self.hud("ক্যামেরা ঘুরলেও আলোর দিক বদলায় না",
                         corner=UR, font=BN, size=20, color=DIM)
        self.play(Transform(note3, note4), run_time=0.5)
        self.play(frame.animate.increment_theta(70 * DEG), run_time=4.0)
        self.wait(1.2)
        self.play(frame.animate.increment_theta(-20 * DEG), run_time=1.6)

        # ---- end ---------------------------------------------------------
        self.clear_hud(code, note3, head)
        one = Text("prototypes, not the package -- রায়ের পরে ঠিক হবে",
                   font=BN, font_size=26, fill_color=INK, stroke_width=0)
        two = Text("emit: shading 0  ·  light: at the centre  ·  "
                   "corona: rim + tail", font=MONO, font_size=20,
                   fill_color=GOLD, stroke_width=0)
        card = VGroup(one, two).arrange(DOWN, buff=0.35)
        card.fix_in_frame()
        self.play(FadeIn(card, shift=0.3 * UP), run_time=0.9)
        self.wait(1.6)
        self.play(FadeOut(card), run_time=0.7)
