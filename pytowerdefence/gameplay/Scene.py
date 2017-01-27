import pygame
import pyscroll
import importlib

from contextlib import contextmanager
from pyscroll.group import PyscrollGroup
from pytmx.util_pygame import load_pygame

from pytowerdefence.gameplay.Objects import GameObject, Actor, ActorState


class Level:
    def __init__(self, screen_size):
        self.screen_size = screen_size
        self.tmx_data = None
        self.map_data = None
        self.map_layer = None
        self.group = None
        self.paths = []

    def load(self, filename):
        self.tmx_data = load_pygame(filename)
        self.map_data = pyscroll.TiledMapData(self.tmx_data)
        self.map_layer = pyscroll.BufferedRenderer(self.map_data, self.screen_size)
        self.group = PyscrollGroup(map_layer=self.map_layer)

        for obj in self.tmx_data.get_layer_by_name("paths"):
            self.paths.append(obj.points)

        for obstacle in self.obstacle_iterator():
            obstacle.rect = pygame.Rect(obstacle.x, obstacle.y, obstacle.width, obstacle.height)

    def add(self, sprite):
        self.group.add(sprite, layer=self.get_layer_index("actors"))

    def add_obstacle(self, obstacle):
        self.tmx_data.get_layer_by_name("obstacles").append(obstacle)

    def actor_iterator(self):
        for o in self.group.sprites():
            if isinstance(o, Actor):
                yield o

    def obstacle_iterator(self):
        for obstacle in self.tmx_data.get_layer_by_name("obstacles"):
            yield obstacle

    def get_layer_index(self, layer_name):
        for i, layer in enumerate(self.tmx_data.layers):
            if layer.name == layer_name:
                return i
        return -1

    def is_rectangle_colliding(self, rectangle):
        for obstacle in self.obstacle_iterator():
            if rectangle.colliderect(obstacle.rect):
                return True
        return False

    def update(self, dt):
        self.group.update(dt)
        for o in self.actor_iterator():
            if o.state != ActorState.DEATH:
                visible = pygame.sprite.spritecollide(o, self.group.sprites(), False, is_visible)
                o.actors_in_attack_range = visible

        for new_object in GameObject._objects_to_create:
            self.add(new_object)

        GameObject._objects_to_create.clear()

    def draw(self, surface):
        self.group.draw(surface)


class CreaturesFactory:
    def __init__(self, level):
        self._level = level

    @contextmanager
    def create_on_scene(self, name, **kwargs):
        monster = self.create(name, **kwargs)
        yield monster, self._level
        self._level.add(monster)

    def create(self, name, **kwargs):
        monsters_module = importlib.import_module("pytowerdefence.gameplay.Monsters")
        return getattr(monsters_module, name)()


def is_visible(left, right):
    if not isinstance(left, Actor) or not isinstance(right, Actor):
        return False

    if left == right:
        return False

    return right.state != ActorState.DEATH and (left.position - right.position).length() \
                                               < left.statistics.attack_range + left.radius + right.radius
