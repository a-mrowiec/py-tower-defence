import importlib
from contextlib import contextmanager

import pygame
import pyscroll
from pygame.math import Vector2
from pyscroll.group import PyscrollGroup
from pytmx.util_pygame import load_pygame

from pytowerdefence.gameplay.Objects import GameObject, Actor, ActorState, \
    PLAYER_TEAM


class Camera:
    _position = Vector2(0, 0)
    _group = None
    _map_layer = None
    _half_screen_size = None

    @classmethod
    def set_up(cls, group, map_layer, screen_size):
        cls._group = group
        cls._map_layer = map_layer
        cls._half_screen_size = Vector2(screen_size) / 2
        cls._position = Vector2(cls._half_screen_size)

    @classmethod
    def set_position(cls, value):
        cls._group.center(value)
        cls._position = cls._half_screen_size - cls._map_layer.get_center_offset()

    @classmethod
    def move_by(cls, value):
        cls.set_position(cls._position + value)

    @classmethod
    def to_world_position(cls, screen_position):
        return screen_position + cls._position - cls._half_screen_size

    @classmethod
    def to_screen_position(cls, world_position):
        return world_position - cls._position + cls._half_screen_size


class Level:
    def __init__(self, screen_size, logic_manager):
        self._logic_manager = logic_manager
        self.screen_size = screen_size
        self.tmx_data = None
        self.map_data = None
        self.map_layer = None
        self.group = None
        self.paths = []

    def load(self, filename):
        self.tmx_data = load_pygame(filename)
        self.map_data = pyscroll.TiledMapData(self.tmx_data)
        self.map_layer = pyscroll.BufferedRenderer(self.map_data,
                                                   self.screen_size, alpha=True)
        self.group = PyscrollGroup(map_layer=self.map_layer)
        Camera.set_up(self.group, self.map_layer, self.screen_size)
        for obj in self.tmx_data.get_layer_by_name("paths"):
            self.paths.append(obj.points)

        for obstacle in self.obstacle_iterator():
            obstacle.rect = pygame.Rect(obstacle.x, obstacle.y, obstacle.width,
                                        obstacle.height)

    def add(self, object):
        self.group.add(object, layer=self.get_layer_index("actors"))
        self._logic_manager.on_object_added_to_scene(object)

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

    def get_actor_on_position(self, position, lambda_filter=None):
        if lambda_filter is not None:
            for actor in self.actor_iterator():
                if actor.rect.collidepoint(position.x,
                                           position.y) and lambda_filter(actor):
                    return actor
        else:
            for actor in self.actor_iterator():
                if actor.rect.collidepoint(position.x, position.y):
                    return actor
        return None

    def update(self, dt):
        self.group.update(dt)
        for o in self.actor_iterator():
            if o.state != ActorState.DEATH:
                visible = pygame.sprite.spritecollide(o, self.group.sprites(),
                                                      False, is_visible)
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
        monsters_module = importlib.import_module(
            "pytowerdefence.gameplay.Monsters")
        return getattr(monsters_module, name)()


def is_actor_in_player_team(actor):
    return actor.statistics.team == PLAYER_TEAM


def is_visible(left, right):
    if not isinstance(left, Actor) or not isinstance(right, Actor):
        return False

    if left == right:
        return False

    return right.state != ActorState.DEATH and (
                                               left.position - right.position).length() \
                                               < left.statistics.attack_range + left.radius + right.radius
