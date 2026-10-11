"""
Solar -- সৌরজালের এক প্রদক্ষিণ: জ্বলন্ত সূর্য, কক্ষপথে ঘোরা আট গ্রহ,
আর সবচেয়ে জরুরি, চলমান ক্যামেরা।

    manimgl our-work/scenes/solar.py Solar -w -m -c "#070B14" \
        --video_dir our-work/videos

নকশা: পুরো ভিডিওটা একটানা আপডেটারে চলে -- ঘড়ি-ট্র্যাকার প্রতি ফ্রেমে
সময় বাড়ায়, গ্রহের অবস্থান আর ক্যামেরার ভঙ্গি সবাই সেই সময় থেকে
হিসেব হয়, তাই কোনো বিটে গতি থেমে থাকে না। ক্যামেরা তিন রকম চলে:
থিটা অবিরাম ধীরে ঘোরে (তারার প্যারালাক্স), ফাই ক্রমে বেঁকে কক্ষগুলোকে
ডিম্বাকৃত করে, আর উচ্চতা তিন পর্বে শ্বাস নেয় -- ভেতরে ঢুকে ভেতরের
জগৎ দেখে, পিছিয়ে গিয়ে বাইরের গ্রহগুলো প্রকাশ করে, শেষে থামে।
এটি our-work-এর ডেমো দৃশ্য; কোরোনাটি এখন প্লাগইনেও আছে -- astro.Sun()।
মাপ ও সীমা README-তে।
"""

import numpy as np
from manimlib import *

from manimgl_myplugin.astro import (
    Body, Mercury, Venus, Earth, Moon, Mars,
    Jupiter, Saturn, Uranus, Neptune,
)

INK, DIM = "#EAF0F8", "#7E93AC"
BN = "Noto Serif Bengali"


class Solar(ThreeDScene):

    # ------------------------------------------------------------ pieces --

    def corona(self, pos, r):
        """
        সূর্যের আভা -- সত্যিকারের ত্রিমাত্রিক। সাঁটানো স্প্রাইট নয়:
        সূর্যকে বেষ্টন করা গোলক-স্তর, যাদের আলো ফ্রেনেল-সূত্রে
        দৃশ্য-দিকের ওপর নির্ভর করে। বাইরের স্তরগুলো বিপরীত-ফ্রেনেল
        (পিণ্ডমুখী সর্বোচ্চ, নিজ-প্রান্তে শূন্য) -- তাই আভাটা প্রান্ত থেকে
        মসৃণভাবে ক্ষয় যায়; ওপাসিটিগুলো লক্ষ্য-প্রোফাইলের বিপরীতে একক-শেল রেন্ডার করে মাপা প্রকৃত প্রতিক্রিয়ার বিপরীতে nnls-এ মেলানো
        (৪৮৭→৩১৩→২০৯→১০৫, প্রান্ত থেকে ৩.৩R পর্যন্ত)। গভীরতা-
        পরীক্ষা চালু থাকে: সামনে আসা গ্রহ আভাকে কেটে যায়, পেছনের গ্রহ
        আভার নিচে ঢাকা পড়ে -- সমতল স্প্রাইটে এই আচরণ অসম্ভব।
        স্তরগুলো ক্রমবর্ধমান z-index-এ আঁকা যায় বলে গভীরতা-লেখনের
        সংঘর্ষও নেই: প্রতিটি পরের স্তর ক্যামেরার দিকে বেশি ফুলে থাকে,
        তাই সবসময় পরীক্ষা পাস করে।
        """
        # (প্রতি গুণিতক, ঘাত, rgb, ওপাসিটি) -- লিফট + ৫টি বিপরীত-ফ্রেনেল শেল
        shells = [
            (1.019, None, (1.000, 0.914, 0.753), 0.42),   # ফটোস্ফিয়ার-লিফট, সমতল
            (1.45, 1.4, (1.000, 0.822, 0.548), 0.231),
            (1.80, 1.1, (1.000, 0.774, 0.472), 0.149),
            (2.20, 0.9, (1.000, 0.723, 0.415), 0.111),
            (2.70, 0.75, (1.000, 0.671, 0.359), 0.120),
            (3.30, 0.60, (1.000, 0.620, 0.302), 0.052),
        ]
        out = []
        for i, (mult, power, rgb, op) in enumerate(shells):
            s = Sphere(radius=mult * r, resolution=(128, 64))
            s.move_to(pos)
            s.set_shading(0.0, 0.0, 0.0)   # আলো এটাকে চালায় না, এ নিজেই আলো
            r_, g_, b_ = (f"{x:.3f}" for x in rgb)
            if power is None:
                code = f"color = vec4f(vec3f({r_}, {g_}, {b_}), {op});"
            else:
                code = (
                    "let to_cam = normalize(frame.camera_position - point);"
                    f"let f = pow(abs(dot(normal, to_cam)), {power});"
                    f"color = vec4f(vec3f({r_}, {g_}, {b_}), {op} * f);"
                )
            s.set_color_by_code(code)
            s.blend_mode = "add"          # আলো যোগ হয়, ঢেকে দেয় না
            s.depth_write = False         # স্তরে স্তরে গভীরতা-প্রত্যাখ্যান নয়
            out.append(s)
        return Group(*out)

    def starfield(self):
        """
        দূরের তারা -- স্থির বিন্দু, নড়ে না; ক্যামেরা ঘুরলে এদের দিক বদলায়,
        আর সেই বদলই ঘোরার প্রমাণ। তিন স্তরে ভাগ (মিহল / উজ্জ্বল / কদাচিৎ
        বড়) যাতে আকাশ সমতল না লাগে।
        """
        rng = np.random.default_rng(11)
        out = []
        for count, radius, opacity, color in (
                (340, 0.028, 0.40, "#C9D6EE"),
                (180, 0.036, 0.70, "#E8EEF9"),
                (50, 0.055, 0.90, "#FFF3E0"),
        ):
            v = rng.normal(size=(count, 3))
            v /= np.linalg.norm(v, axis=1, keepdims=True)
            pts = 38.0 * v
            out.append(DotCloud(pts, radius=radius, color=color,
                                opacity=opacity, glow_factor=1.0))
        return Group(*out)

    # ---------------------------------------------------------- helpers --

    @staticmethod
    def seg(t, keys, vals):
        """কী-ফ্রেমের মাঝে smoothstep -- প্রতি পর্বের শুরু-শেষে মৃদু থামা।"""
        if t <= keys[0]:
            return vals[0]
        for i in range(len(keys) - 1):
            if t < keys[i + 1]:
                u = (t - keys[i]) / (keys[i + 1] - keys[i])
                u = u * u * (3.0 - 2.0 * u)
                return vals[i] + u * (vals[i + 1] - vals[i])
        return vals[-1]

    @staticmethod
    def orbit(R, a0, w):
        """কক্ষপথের অবস্থান: xy-সমতলে কোণ a0 থেকে w ডিগ্রি/সেকেন্ডে।"""
        return lambda t: np.array([
            R * np.cos((a0 + w * t) * DEG),
            R * np.sin((a0 + w * t) * DEG),
            0.0,
        ])

    # ------------------------------------------------------------- scene --

    def construct(self):
        frame = self.camera.frame

        # ঘড়ি সবার আগে যোগ -- প্রতি ফ্রেমে এটাই আগে টিক করে, বাকিরা পড়ে
        clock = ValueTracker(0.0)
        clock.add_updater(lambda m, dt: m.increment_value(dt))
        self.add(clock)

        # ---- আকাশ, কক্ষরেখা, সূর্য --------------------------------------
        self.add(self.starfield())

        for R, op in ((3.0, 0.16), (4.4, 0.14), (5.8, 0.13), (7.2, 0.12),
                      (9.6, 0.11), (11.8, 0.10), (13.6, 0.09), (15.4, 0.08)):
            ring = Circle(radius=R, color="#3A4A66")
            ring.set_stroke(width=1, opacity=op)
            self.add(ring)

        sun = Body(radius=1.6, texture="sun", light=np.array([0.0, 0, 0]))
        sun.globe.set_shading(0.0, 0.0, 0.0)
        self.camera.light_source.move_to(ORIGIN)
        self.add(sun)

        # ---- গ্রহ: কক্ষার্ধ, শুরুর কোণ, কৌণিক গতি (ডিগ্রি/সে) ---------
        spec = [
            (Mercury(0.24), 3.0, 40.0, 16.0),
            (Venus(0.55),   4.4, 200.0, 10.0),
            (Earth(0.58),   5.8, 320.0, 7.0),
            (Mars(0.36),    7.2, 120.0, 4.7),
            (Jupiter(1.35), 9.6, 250.0, 2.5),
            (Saturn(1.15), 11.8, 30.0, 1.8),
            (Uranus(0.70), 13.6, 160.0, 1.3),
            (Neptune(0.68), 15.4, 90.0, 1.0),
        ]
        earth_pos = self.orbit(5.8, 320.0, 7.0)
        for planet, R, a0, w in spec:
            pos = self.orbit(R, a0, w)
            planet.move_to(pos(0.0))
            planet.add_updater(lambda m, dt, pos=pos: m.move_to(pos(clock.get_value())))
            self.add(planet)

        moon = Moon(0.16)
        moon_pos = lambda t: earth_pos(t) + np.array([
            1.05 * np.cos((140.0 + 60.0 * t) * DEG),
            1.05 * np.sin((140.0 + 60.0 * t) * DEG),
            0.0,
        ])
        moon.move_to(moon_pos(0.0))
        moon.add_updater(lambda m, dt: m.move_to(moon_pos(clock.get_value())))
        self.add(moon)

        self.add(self.corona(ORIGIN, 1.6))

        # ---- ক্যামেরা: তিন পর্বের শ্বাস --------------------------------
        KEYS = (0.0, 12.0, 24.0, 30.0)
        HS = (13.5, 10.2, 17.5, 14.5)
        PHIS = (-24.0, -32.0, -44.0, -50.0)

        def fly(m, dt):
            t = clock.get_value()
            m.set_height(self.seg(t, KEYS, HS))
            # তিন কোণই পরম মানে reorient-এ বসানো -- জমানো increment_theta
            # আর প্রতি ফ্রেমের set_phi মেশালে অয়লার-প্রতিনিধিত্ব ফ্লিপ করে
            # (মাপা: ৬৯০ ধাপে theta ১০০°-র বদলে ৮°, phi-র চিহ্ন উল্টে)
            m.reorient(self.seg(t, KEYS, PHIS), 68.0 + 1.4 * t, 0)

        frame.set_height(13.5).reorient(-24, 68, 0)
        frame.add_updater(fly)

        # ---- শিরোনাম আর সৎ স্বীকারোক্তি -------------------------------
        title = Text("সৌরজাল", font=BN, font_size=40,
                     fill_color=INK, stroke_width=0)
        sub = Text("জ্বলন্ত সূর্য থেকে নেপচুন — এক প্রদক্ষিণ",
                   font=BN, font_size=22, fill_color=DIM, stroke_width=0)
        card = VGroup(title, sub).arrange(DOWN, buff=0.35)
        card.fix_in_frame()

        note = Text("দূরত্ব ও আকার সংকুচিত — ছন্দের খাতিরে",
                    font=BN, font_size=18, fill_color=DIM, stroke_width=0)
        note.fix_in_frame()
        note.to_corner(DL, buff=0.45)

        self.play(FadeIn(card, shift=0.2 * UP), run_time=0.8)
        self.wait(1.5)
        self.play(FadeOut(card), run_time=1.0)
        self.wait(0.9)
        self.play(FadeIn(note, shift=0.2 * UP), run_time=0.5)
        self.wait(1.3)
        self.play(FadeOut(note), run_time=0.5)
        self.wait(23.5)
