import pyganim

class Animation(pyganim.PygAnimation):

    def __init__(self, frames, loop=True):
        super().__init__(frames, loop)

    def blit(self, destSurface, dest=(0, 0)):
        super().blit(destSurface, dest)

    def update(self, dt):
        self.currentFrameNum = pyganim.findStartTime(self._startTimes, self.elapsed)