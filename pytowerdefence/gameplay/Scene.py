"""
Scene module
"""
import importlib
from contextlib import contextmanager

import pygame
from pygame.math import Vector2
from pygame.rect import Rect
from pyscroll import BufferedRenderer, TiledMapData
from pyscroll.group import PyscrollGroup
from pytmx.util_pygame import load_pygame

from pytowerdefence.gameplay.Monsters import Base
from pytowerdefence.gameplay.Objects import GameObject, Actor, ActorState, \
    PLAYER_TEAM


class Camera:
    """
    Game camera
    """
    _position = Vector2(0, 0)
    _group = None
    _map_layer = None
    _half_screen_size = None

    @classmethod
    def set_up(cls, group, map_layer, screen_size):
        """
        Initialise camera
        :param group:
        :param map_layer:
        :param screen_size:
        :return:
        """
        cls._group = group
        cls._map_layer = map_layer
        cls._half_screen_size = Vector2(screen_size) / 2
        cls._position = Vector2(cls._half_screen_size)

    @classmethod
    def set_position(cls, value):
        """
        Set camera position
        :param value:
        :return:
        """
        cls._group.center(value)
        cls._position = cls._half_screen_size - cls._map_layer.get_center_offset()

    @classmethod
    def move_by(cls, value):
        """
        Move camera by vector
        :param value:
        :return:
        """
        cls.set_position(cls._position + value)

    @classmethod
    def to_world_position(cls, screen_position):
        """
        Returns world position
        :param screen_position:
        :return:
        """
        return screen_position + cls._position - cls._half_screen_size

    @classmethod
    def to_screen_position(cls, world_position):
        """
        Returns screen position
        :param world_position:
        :return:
        """
        return world_position - cls._position + cls._half_screen_size


class Level:
    """
    Class that holds map, and any game object that should be rendered or updated
    """
    def __init__(self, screen_size, logic_manager):
        self._logic_manager = logic_manager
        self.screen_size = screen_size
        self.tmx_data = None
        self.map_data = None
        self.map_layer = None
        self.group = None
        self.paths = []
        self.base = None

    def load(self, filename):
        """
        Loads map
        :param filename:
        :return:
        """
        self.tmx_data = load_pygame(filename)
        self.map_data = TiledMapData(self.tmx_data)
        self.map_layer = BufferedRenderer(self.map_data,
                                          self.screen_size, alpha=True)
        self.group = PyscrollGroup(map_layer=self.map_layer)
        Camera.set_up(self.group, self.map_layer, self.screen_size)
        for obj in self.tmx_data.get_layer_by_name("paths"):
            self.paths.append(obj.points)

        for obstacle in self.obstacle_iterator():
            obstacle.rect = Rect(obstacle.x, obstacle.y, obstacle.width,
                                 obstacle.height)

        for actor in self.tmx_data.get_layer_by_name("actors"):
            if actor.name == 'base':
                self.base = Base()
                self.base.position = Vector2(actor.x, actor.y)
                self.base.team = PLAYER_TEAM
                self.add(self.base)

    def add(self, obj):
        """
        Add actor
        :param obj:
        :return:
        """
        self.group.add(obj, layer=self.get_layer_index("actors"))
        self._logic_manager.on_object_added_to_scene(obj)

    def add_obstacle(self, obstacle):
        """
        Add obstacle
        :param obstacle:
        :return:
        """
        self.tmx_data.get_layer_by_name("obstacles").append(obstacle)

    def actor_iterator(self):
        """
        Returns iterator that goe through actors
        :return:
        """
        for o in self.group.sprites():
            if isinstance(o, Actor):
                yield o

    def obstacle_iterator(self):
        """
        Returns iterator that goes through obstacles
        :return:
        """
        for obstacle in self.tmx_data.get_layer_by_name("obstacles"):
            yield obstacle

    def get_layer_index(self, layer_name):
        """
        Returns index of layer by name
        :param layer_name:
        :return:
        """
        for i, layer in enumerate(self.tmx_data.layers):
            if layer.name == layer_name:
                return i
        return -1

    def is_rectangle_colliding(self, rectangle):
        """
        Checks if rect is colliding with any obstacle
        :param rectangle:
        :return:
        """
        for obstacle in self.obstacle_iterator():
            if rectangle.colliderect(obstacle.rect):
                return True
        return False

    def get_actor_on_position(self, position, lambda_filter=None):
        """
        Checks if given position collides with any actor and returns it
        :param position:
        :param lambda_filter:
        :return:
        """
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
        """
        Updates level
        :param dt:
        :return:
        """
        self.group.update(dt)
        for obj in self.actor_iterator():
            if obj.state != ActorState.DEATH:
                visible = pygame.sprite.spritecollide(obj, self.group.sprites(),
                                                      False, is_visible)
                obj.actors_in_attack_range = visible

        for new_object in GameObject.objects_to_create:
            self.add(new_object)

        GameObject.objects_to_create.clear()

    def draw(self, surface):
        """
        Draw level objects
        :param surface:
        :return:
        """
        self.group.draw(surface)


class CreaturesFactory:
    """
    Factory to create any type of creature/actor
    """

    def __init__(self, level):
        self._level = level

    @contextmanager
    def create_on_scene(self, name, **kwargs):
        """
        Create, set up, and add creature to scene
        :param name:
        :param kwargs:
        :return:
        """
        monster = self.create(name, **kwargs)
        yield monster, self._level
        self._level.add(monster)

    def get_creature_type_properties(self, name):
        """
        Returns creature class properties
        :param name:
        :return:
        """
        return self._get_monster_class(name).PROPERTIES

    @staticmethod
    def _get_monster_class(name):
        monsters_module = importlib.import_module(
            "pytowerdefence.gameplay.Monsters")
        return getattr(monsters_module, name)

    def create(self, name, **kwargs):
        """
        Create creature
        :param name:
        :param kwargs:
        :return:
        """
        return self._get_monster_class(name)(**kwargs)


def is_actor_in_player_team(actor):
    """
    Checks if player has same team as player
    :param actor:
    :return:
    """
    return actor.team == PLAYER_TEAM


def is_visible(left, right):
    """
    Checks if one actor see other actor
    :param left:
    :param right:
    :return:
    """
    if not isinstance(left, Actor) or not isinstance(right, Actor):
        return False

    if left == right:
        return False

    is_alive = right.state != ActorState.DEATH
    radius = left.statistics.attack_range + left.radius + right.radius
    real_distance = (left.position - right.position).length()
    return is_alive and real_distance < radius
