import pyscroll
import pygame
from pytmx.util_pygame import load_pygame
from pyscroll.group import PyscrollGroup

from gameplay.Actor import Actor, ActorState


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
        for o in self.group.sprites():
            if isinstance(o, Actor):
                if o.state != ActorState.DEATH:
                    visible = pygame.sprite.spritecollide(o, self.group.sprites(), False, is_visible)
                    o.actors_in_attack_range = visible

    def draw(self, surface):
        self.group.draw(surface)


def is_visible(left, right):
    if not isinstance(left, Actor) or not isinstance(right, Actor):
        return False

    if left == right:
        return False

    return right.state != ActorState.DEATH and (left.position - right.position).length() < left.statistics.attack_range + left.radius + right.radius

