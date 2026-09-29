from manimlib import *

class TexTest(Scene):
    def construct(self):
        a = Tex(r"E = mc^2", font_size=72)
        b = TexText(r"Hello $x^2$ world", font_size=48)
        self.play(Write(a)); self.wait(0.3); self.play(FadeOut(a))
        self.play(Write(b)); self.wait(0.3)
