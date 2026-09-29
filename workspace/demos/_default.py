from manimlib import *
from manimgl_myplugin.astro import Earth

class Default(ThreeDScene):
    def construct(self):
        self.camera.frame.reorient(0, 70, 0)
        earth = Earth()                    # ← কোনো আর্গুমেন্ট নেই
        self.add(earth)
        self.wait(2)
