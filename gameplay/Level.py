import pyscroll
from pytmx.util_pygame import load_pygame
from pyscroll.group import PyscrollGroup


class Level:
    def __init__(self, screen_size):
        self.screen_size = screen_size

    def load(self, filename):
        self.tmx_data = load_pygame(filename)
        self.map_data = pyscroll.TiledMapData(self.tmx_data)
        self.map_layer = pyscroll.BufferedRenderer(self.map_data, self.screen_size)
        self.group = PyscrollGroup(map_layer=self.map_layer)


    def update(self, dt):
        self.group.update(dt)

    def draw(self, surface):
        self.group.draw(surface)



