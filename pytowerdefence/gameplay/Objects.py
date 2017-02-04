import copy
import importlib
from collections import defaultdict
from enum import Enum, IntEnum
from functools import reduce

import pygame
from pygame.math import Vector2

from pytowerdefence.Resources import ResourceClass
from pytowerdefence.Resources import ResourceManager
from pytowerdefence.Utils import rot_center

ENEMY_TEAM = 0
PLAYER_TEAM = 1


class ActorCallback(Enum):
    KILL = 0,
    EVOLVE = 1


class GameObject(pygame.sprite.Sprite):
    """
    Base class for any game object, which can be drawed and updated
    """
    _objects_to_create = []

    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self._position = Vector2(0, 0)
        self._prev_position = Vector2(0, 0)
        self._velocity = Vector2(0, 0)
        self._rect = pygame.Rect(0, 0, 0, 0)
        self.alive = True
        self.image = None
        self._sprite = None
        self._angle = 0
        self._team = ENEMY_TEAM
        self._callbacks = {}

    def update(self, dt):
        """
        Update method, updated every frame
        :param dt:
        :return:
        """
        self._prev_position = Vector2(self._position)
        self._position += (self._velocity * dt)
        self._rect.center = self._position
        if self._sprite is not None:
            self.image = rot_center(self._sprite, self._angle)

    @property
    def team(self):
        return self._team

    @team.setter
    def team(self, value):
        self._team = value

    @property
    def sprite(self):
        """
        Getter
        :return:
        """
        return self._sprite

    @sprite.setter
    def sprite(self, value):
        """
        Sets sprite
        :param value:
        :return:
        """
        self._sprite = value
        self.image = rot_center(self._sprite, self._angle)

    @property
    def velocity(self):
        return self._velocity

    @velocity.setter
    def velocity(self, val):
        self._velocity = val
        self.rotate_to_direction(val)

    @property
    def angle(self):
        return self._angle

    @property
    def rect(self):
        return self._rect

    @rect.setter
    def rect(self, value):
        self._rect = value

    @property
    def position(self):
        return self._position

    @property
    def radius(self):
        return max(self._rect.width / 2.0, self._rect.height / 2.0)

    @position.setter
    def position(self, value):
        self._position = Vector2(value)
        self._rect.center = self._position

    def set_callback(self, type, callback):
        self._callbacks[type] = callback

    def remove_callback(self, type):
        del self._callbacks[type]

    def rotate_to_direction(self, direction):
        self._angle = direction.angle_to(Vector2(0, -1))

    def kill(self):
        self.alive = False
        if ActorCallback.KILL in self._callbacks:
            self._callbacks[ActorCallback.KILL](self)
        super().kill()


class Bullet(GameObject):
    """
    Class that represents bullet
    """

    def __init__(self, owner):
        super().__init__()
        self._target = None
        self._owner = owner
        self._start_position = Vector2(owner.position)
        self._speed = owner.statistics.bullet_speed
        self.sprite = ResourceManager.load_image(ResourceClass.BULLETS,
                                                 owner.statistics.bullet_image)

    @property
    def target(self):
        """
        Target is an actor
        :return: target
        """
        return self._target

    @target.setter
    def target(self, val):
        """
        Setter
        :param val:
        :return:
        """
        self._target = val

    def update(self, dt):
        super().update(dt)
        projection_vector = self._position - self._start_position
        to_goal_vector = self._target.position - self._position
        self.velocity = to_goal_vector.normalize() * self._speed
        dot = projection_vector.dot(to_goal_vector)
        if dot < 0:
            self._on_hit()

    def _on_hit(self):
        add_effects_to_actor(self._target, self._owner.statistics.hit_effects)
        self._owner.change_state(ActorState.IDLE)
        self.kill()


class ActorState(Enum):
    IDLE = 0
    MOVE = 1
    ATTACK = 2
    DEATH = 3


class StatisticType(IntEnum):
    MAX_HEALTH = 0,
    SPEED = 1,
    ATTACK_DAMAGE = 2,
    ATTACK_SPEED = 3,
    ATTACK_RANGE = 4,
    BULLET_SPEED = 5,
    BULLET_IMAGE = 6,
    HIT_EFFECTS = 7


class StatisticModifier:
    def __init__(self, statistic_type, value, multiply=False):
        self.statistic_type = statistic_type
        self.value = value
        self.multiply = multiply


class ActorStatistics:
    def __init__(self, readonly=False):
        self._values = [None] * len(StatisticType)
        self._readonly = readonly

    def readonly(self, value):
        self._readonly = value

    def set_value(self, type, value):
        if not self._readonly:
            self._values[type] = value

    def _categorized_modifiers(self, modifiers):
        d = defaultdict(list)
        modifiers_with_type = list(
            (m.statistic_type, m) for m in modifiers)
        for k, v in modifiers_with_type:
            d[k].append(v)
        return d

    def modify_stat(self, statistic_type, modifiers):
        s = sum(map(lambda m: m.value,
                    filter(lambda m: not m.multiply, modifiers)))
        mul = reduce(lambda x, y: x * y, map(lambda m: m.value,
                                             filter(lambda m: m.multiply,
                                                    modifiers)))

        self._values[statistic_type] += s
        self._values[statistic_type] *= mul

    def get_modified_statistics(self, modifiers):
        new_statistics = copy.deepcopy(self)
        new_statistics.readonly(False)
        categorized_modifiers = self._categorized_modifiers(modifiers)
        for statistic_type, mods in categorized_modifiers.items():
            new_statistics.modify_stat(statistic_type, mods)
        new_statistics.readonly(True)
        return new_statistics

    @property
    def max_health(self):
        return self._values[StatisticType.MAX_HEALTH]

    @max_health.setter
    def max_health(self, value):
        self.set_value(StatisticType.MAX_HEALTH, value)

    @property
    def speed(self):
        return self._values[StatisticType.SPEED]

    @speed.setter
    def speed(self, value):
        self.set_value(StatisticType.SPEED, value)

    @property
    def attack_speed(self):
        return self._values[StatisticType.ATTACK_SPEED]

    @attack_speed.setter
    def attack_speed(self, value):
        self.set_value(StatisticType.ATTACK_SPEED, value)

    @property
    def attack_damage(self):
        return self._values[StatisticType.ATTACK_DAMAGE]

    @attack_damage.setter
    def attack_damage(self, value):
        self.set_value(StatisticType.ATTACK_DAMAGE, value)

    @property
    def attack_range(self):
        return self._values[StatisticType.ATTACK_RANGE]

    @attack_range.setter
    def attack_range(self, value):
        self.set_value(StatisticType.ATTACK_RANGE, value)

    @property
    def bullet_speed(self):
        return self._values[StatisticType.BULLET_SPEED]

    @bullet_speed.setter
    def bullet_speed(self, value):
        self.set_value(StatisticType.BULLET_SPEED, value)

    @property
    def bullet_image(self):
        return self._values[StatisticType.BULLET_IMAGE]

    @bullet_image.setter
    def bullet_image(self, value):
        self.set_value(StatisticType.BULLET_IMAGE, value)

    @property
    def hit_effects(self):
        return self._values[StatisticType.HIT_EFFECTS]

    @hit_effects.setter
    def hit_effects(self, value):
        self.set_value(StatisticType.HIT_EFFECTS, value)


class Actor(GameObject):
    def __init__(self):
        super().__init__()
        self._animations = {}
        self._current_animation = None
        self._controllers = []
        self._statistic_modifiers = []
        self._state = ActorState.IDLE
        self._base_statistics = ActorStatistics()
        self._statistics = ActorStatistics(readonly=True)
        self._modifiers = []
        self._actors_in_attack_range = []
        self._ai = None
        self._prev_updated_controller = None
        self._hp = 0
        self._logical_effects = []

    def update(self, dt):
        if self._ai is not None:
            self._ai.update(dt)

        self._update_controllers(dt)

        super().update(dt)
        if self._current_animation is not None and self._sprite is None:
            self.image = rot_center(self._current_animation.getCurrentFrame(),
                                    self._angle)
            if self._current_animation.isFinished():
                for controller in self._controllers:
                    controller.on_animation_end()

    def _update_controllers(self, dt):
        for controller in self._controllers:
            need_update = controller.need_update()
            if need_update:
                if self._prev_updated_controller != controller \
                        and self._prev_updated_controller is not None:
                    self._prev_updated_controller.on_update_end()
                controller.update(dt)
                self._prev_updated_controller = controller

    def hit(self, damage):
        self._hp -= damage
        if self._hp < 0:
            self.on_death()

    def recalculate_statistics(self):
        self._statistics = \
            self._base_statistics.get_modified_statistics(self._modifiers)

        self._statistics.readonly(True)

    def add_controller(self, controller):
        controller.set_actor(self)
        self._controllers.append(controller)

    @property
    def controllers(self):
        return self._controllers

    @property
    def hp(self):
        return self._hp

    @hp.setter
    def hp(self, value):
        self._hp = value

    @property
    def base_statistics(self):
        return self._base_statistics

    def on_death(self):
        self.stop_controllers()
        self._velocity = Vector2()
        self.change_state(ActorState.DEATH)

    def stop(self):
        self.change_state(ActorState.IDLE)

    def set_animation(self, state, animation):
        self._animations[state] = animation

    def change_state(self, new_state):
        if self._state != new_state:
            self._stop_current_animation()
            self._state = new_state
            self._play_current_animation()

    def stop_controllers(self):
        for controller in self._controllers:
            controller.stop()

    def get_controller(self, type):
        for c in self._controllers:
            if isinstance(c, type):
                return c
        return None

    def _stop_current_animation(self):
        if self._current_animation is not None:
            self._current_animation.stop()

    def _play_current_animation(self):
        self._current_animation = self._animations.get(self._state, None)
        if self._current_animation is not None:
            self._current_animation.play()

    @property
    def statistics(self):
        return self._statistics

    @property
    def state(self):
        return self._state

    def set_ai(self, value):
        value.set_actor(self)
        self._ai = value

    def go_to_direction(self, direction):
        self.velocity = direction.normalize() * self._statistics.speed
        self.change_state(ActorState.MOVE)

    def stop(self):
        self.zero_velocity()
        self.change_state(ActorState.IDLE)

    def zero_velocity(self):
        self._velocity = Vector2()

    @property
    def actors_in_attack_range(self):
        return self._actors_in_attack_range

    @actors_in_attack_range.setter
    def actors_in_attack_range(self, value):
        self._actors_in_attack_range = value

    def statistics_changed(self):
        self.recalculate_statistics()
        if self.velocity.length() != 0:
            self.velocity = self.velocity.normalize() * self._statistics.speed

    def add_modifier(self, modifier):
        self._modifiers.append(modifier)
        self.statistics_changed()

    @property
    def logical_effects(self):
        return self._logical_effects

    def find_logical_effect_by_name(self, name):
        for le in self._logical_effects:
            if le.name == name:
                return le
        return None

    def remove_effect(self, effect):
        self._logical_effects.remove(effect)

    def add_logical_effect(self, effect):
        if effect.is_unique:
            prev_effect = self.find_logical_effect_by_name(effect.name)
            if prev_effect is not None:
                prev_effect.on_merge(effect)
            else:
                self._logical_effects.append(effect)
        else:
            self._logical_effects.append(effect)


class EvolvingActor(Actor):
    def __init__(self):
        super().__init__()
        self._current_evolution_level = 0
        self._evolution_statistics = []
        self._evolution_animations = []
        self._evolution_costs = []

    def add_evolution_level(self, statistics, evolution_cost, animations=None):
        self._evolution_statistics.append(statistics)
        self._evolution_animations.append(animations)
        self._evolution_costs.append(evolution_cost)

    @property
    def current_evolution_level(self):
        return self._current_evolution_level

    def evolve(self):
        i = self._current_evolution_level
        self._current_evolution_level += 1

        self._base_statistics = self._evolution_statistics[i]
        self.recalculate_statistics()
        animations = self._evolution_animations[i]
        if animations is not None:
            for state, animation in animations:
                self.set_animation(state, animation)

        if ActorCallback.EVOLVE in self._callbacks:
            self._callbacks[ActorCallback.EVOLVE](self)

    def get_current_evolution_cost(self):
        return self._evolution_costs[self._current_evolution_level]

    def has_max_level(self):
        return self._current_evolution_level >= len(
            self._evolution_statistics)


def create_effect(name, actor, **kwargs):
    effects_module = importlib.import_module(
        "pytowerdefence.gameplay.LogicalEffects")
    return getattr(effects_module, name)(actor, **kwargs)


def add_effect_to_actor(name, actor, **kwargs):
    effect = create_effect(name, actor, **kwargs)
    actor.add_logical_effect(effect)


def add_effects_to_actor(actor, effect_list):
    for ed in effect_list:
        add_effect_to_actor(ed[0], actor, **ed[1])
