import pyscroll
from pytmx.util_pygame import load_pygame
from pyscroll.group import PyscrollGroup


class Level:
    paths = []
    def __init__(self, screen_size):
        self.screen_size = screen_size

    def load(self, filename):
        self.tmx_data = load_pygame(filename)
        self.map_data = pyscroll.TiledMapData(self.tmx_data)
        self.map_layer = pyscroll.BufferedRenderer(self.map_data, self.screen_size)
        self.group = PyscrollGroup(map_layer=self.map_layer)

        for obj in self.tmx_data.get_layer_by_name("paths"):
            self.paths.append(obj.points)

    def add(self, sprite):
        self.tmx_data.get_layer_by_name("actors")
        self.group.add(sprite, layer=self.get_layer_index("actors"))

    def get_layer_index(self, layer_name):
        for i, layer in enumerate(self.tmx_data.layers):
            if layer.name == layer_name:
                return i
        return -1

    def update(self, dt):
        self.group.update(dt)

    def draw(self, surface):
        self.group.draw(surface)



