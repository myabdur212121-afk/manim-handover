from manimlib import *

class Hello(Scene):
    def construct(self):
        self.play(Write(Text("Hello Kushtia!", color=YELLOW)))
        self.play(GrowFromCenter(GlowDot(color=RED, radius=0.4, glow_factor=2.5)))
        self.wait()
