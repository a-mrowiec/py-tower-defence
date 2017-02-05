"""
Objects module
"""
import copy
import importlib
from collections import defaultdict
from enum import Enum, IntEnum
from functools import reduce

import pygame
from pygame.math import Vector2

from pytowerdefence.Resource import ResourceClass
from pytowerdefence.Resource import ResourceManager
from pytowerdefence.Utils import rot_center

ENEMY_TEAM = 0
PLAYER_TEAM = 1


class ActorCallback(Enum):
    """
    Callback type. Is executed when specified event occurs
    """
    KILL = 0,
    EVOLVE = 1


class GameObject(pygame.sprite.Sprite):
    """
    Base class for any game object, which can be drawed and updated
    """
    objects_to_create = []

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
        """
        Team of object
        :return:
        """
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
        """
        Velocity of object
        :return:
        """
        return self._velocity

    @velocity.setter
    def velocity(self, val):
        self._velocity = val
        self.rotate_to_direction(val)

    @property
    def angle(self):
        """
        Rotation of object in radians
        :return:
        """
        return self._angle

    @property
    def rect(self):
        """
        Rectangle of object
        :return:
        """
        return self._rect

    @rect.setter
    def rect(self, value):
        self._rect = value

    @property
    def position(self):
        """
        Position
        :return:
        """
        return self._position

    @property
    def radius(self):
        """
        Radius
        :return:
        """
        return max(self._rect.width / 2.0, self._rect.height / 2.0)

    @position.setter
    def position(self, value):
        self._position = Vector2(value)
        self._rect.center = self._position

    def set_callback(self, callback_type, callback):
        """
        Set callback triggered on specific time, determined by callback_type
        :param callback_type:
        :param callback:
        :return:
        """
        self._callbacks[callback_type] = callback

    def remove_callback(self, callback_type):
        """
        Removes specified callback
        :param callback_type:
        :return:
        """
        del self._callbacks[callback_type]

    def rotate_to_direction(self, direction):
        """
        Rotate object to specified direction
        :param direction:
        :return:
        """
        self._angle = direction.angle_to(Vector2(0, -1))

    def kill(self):
        """
        Kill actor
        :return:
        """
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
        """
        Update bullet
        :param dt:
        :return:
        """
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
    """
    Actor state
    """
    IDLE = 0
    MOVE = 1
    ATTACK = 2
    DEATH = 3


class StatisticType(IntEnum):
    """
    Types of statistics
    """
    MAX_HEALTH = 0,
    SPEED = 1,
    ATTACK_DAMAGE = 2,
    ATTACK_RANGE = 3,
    BULLET_SPEED = 4,
    BULLET_IMAGE = 5,
    HIT_EFFECTS = 6


class StatisticModifier:
    """
    Modifer of statistics
    """
    def __init__(self, statistic_type, value, multiply=False):
        self.statistic_type = statistic_type
        self.value = value
        self.multiply = multiply


def categorized_modifiers(modifiers):
    """
    Returns dictionary of list modifiers. Key is modifier type
    :param modifiers:
    :return:
    """
    d = defaultdict(list)
    modifiers_with_type = list(
        (m.statistic_type, m) for m in modifiers)
    for k, v in modifiers_with_type:
        d[k].append(v)
    return d


class ActorStatistics:
    """
    Actor statistics class.
    """
    def __init__(self, readonly=False):
        self._values = [None] * len(StatisticType)
        self._readonly = readonly

    def readonly(self, value):
        """
        Readonly blocks any value changes
        :param value:
        :return:
        """
        self._readonly = value

    def set_value(self, statistic_type, value):
        """
        Set value of statistic
        :param statistic_type:
        :param value:
        :return:
        """
        if not self._readonly:
            self._values[statistic_type] = value

    def modify_stat(self, statistic_type, modifiers):
        """
        Internally modifies statistics value
        :param statistic_type:
        :param modifiers:
        :return:
        """
        s = sum(map(lambda m: m.value,
                    filter(lambda m: not m.multiply, modifiers)))
        mul = reduce(lambda x, y: x * y, map(lambda m: m.value,
                                             filter(lambda m: m.multiply,
                                                    modifiers)))

        self._values[statistic_type] += s
        self._values[statistic_type] *= mul

    def get_modified_statistics(self, modifiers):
        """
        Returns modified statistics
        :param modifiers:
        :return:
        """
        new_statistics = copy.deepcopy(self)
        new_statistics.readonly(False)
        categorized = categorized_modifiers(modifiers)
        for statistic_type, mods in categorized.items():
            new_statistics.modify_stat(statistic_type, mods)
        new_statistics.readonly(True)
        return new_statistics

    @property
    def max_health(self):
        """
        Max health
        :return:
        """
        return self._values[StatisticType.MAX_HEALTH]

    @max_health.setter
    def max_health(self, value):
        self.set_value(StatisticType.MAX_HEALTH, value)

    @property
    def speed(self):
        """
        Walk speed
        :return:
        """
        return self._values[StatisticType.SPEED]

    @speed.setter
    def speed(self, value):
        self.set_value(StatisticType.SPEED, value)

    @property
    def attack_damage(self):
        """
        Attack damage
        :return:
        """
        return self._values[StatisticType.ATTACK_DAMAGE]

    @attack_damage.setter
    def attack_damage(self, value):
        self.set_value(StatisticType.ATTACK_DAMAGE, value)

    @property
    def attack_range(self):
        """
        Attack range
        :return:
        """
        return self._values[StatisticType.ATTACK_RANGE]

    @attack_range.setter
    def attack_range(self, value):
        self.set_value(StatisticType.ATTACK_RANGE, value)

    @property
    def bullet_speed(self):
        """
        Bullet speed
        :return:
        """
        return self._values[StatisticType.BULLET_SPEED]

    @bullet_speed.setter
    def bullet_speed(self, value):
        self.set_value(StatisticType.BULLET_SPEED, value)

    @property
    def bullet_image(self):
        """
        Bullet image
        :return:
        """
        return self._values[StatisticType.BULLET_IMAGE]

    @bullet_image.setter
    def bullet_image(self, value):
        self.set_value(StatisticType.BULLET_IMAGE, value)

    @property
    def hit_effects(self):
        """
        Hit effects are used when attack is performed on enemy actor
        :return:
        """
        return self._values[StatisticType.HIT_EFFECTS]

    @hit_effects.setter
    def hit_effects(self, value):
        self.set_value(StatisticType.HIT_EFFECTS, value)


class Actor(GameObject):
    """
    Base class for any oactor on scene
    """
    def __init__(self, class_properties):
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
        self._class_properties = class_properties

    @property
    def class_properties(self):
        """
        Class properties that holds information about Monster/Tower type
        :return:
        """
        return self._class_properties

    def update(self, dt):
        """
        Update actor
        :param dt:
        :return:
        """
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
                break

    def hit(self, damage):
        """
        Hit actor with specified damage
        :param damage:
        :return:
        """
        self._hp -= damage
        if self._hp < 0:
            self.on_death()

    def recalculate_statistics(self):
        """
        Recalculate statistics
        :return:
        """
        self._statistics = \
            self._base_statistics.get_modified_statistics(self._modifiers)

        self._statistics.readonly(True)

    def add_controller(self, controller):
        """
        Add actor controller
        :param controller:
        :return:
        """
        controller.set_actor(self)
        self._controllers.append(controller)

    @property
    def controllers(self):
        """
        Actor controllers
        :return:
        """
        return self._controllers

    @property
    def hp(self):
        """
        Health Points
        :return:
        """
        return self._hp

    @hp.setter
    def hp(self, value):
        self._hp = value

    @property
    def base_statistics(self):
        """
        Base statistics
        :return:
        """
        return self._base_statistics

    def get_hp_percentage(self):
        """
        Return percentage value of HP
        :return:
        """
        return self._hp/self._statistics.max_health

    def on_death(self):
        """
        Called when actor is dead
        :return:
        """
        self.stop_controllers()
        self._velocity = Vector2()
        self.change_state(ActorState.DEATH)

    def set_animation(self, state, animation):
        """
        Set current animation
        :param state:
        :param animation:
        :return:
        """
        self._animations[state] = animation

    def change_state(self, new_state):
        """
        Change state of actor and update animation
        :param new_state:
        :return:
        """
        if self._state != new_state:
            self._stop_current_animation()
            self._state = new_state
            self._play_current_animation()

    def stop_controllers(self):
        """
        Stop all controllers
        :return:
        """
        for controller in self._controllers:
            controller.stop()

    def get_controller(self, controller_type):
        """
        Returns controller of specified type
        :param controller_type:
        :return:
        """
        for c in self._controllers:
            if isinstance(c, controller_type):
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
        """
        Current calculated statistics
        :return:
        """
        return self._statistics

    @property
    def state(self):
        """
        Actor state. See @ActorState
        :return:
        """
        return self._state

    def set_ai(self, value):
        """
        Sets AI
        :param value:
        :return:
        """
        value.set_actor(self)
        self._ai = value

    def go_to_direction(self, direction):
        """
        Rotate and set velocity
        :param direction:
        :return:
        """
        self.velocity = direction.normalize() * self._statistics.speed
        self.change_state(ActorState.MOVE)

    def stop(self):
        """
        Stop performing of any action
        :return:
        """
        self.zero_velocity()
        self.change_state(ActorState.IDLE)

    def zero_velocity(self):
        """
        Zero velocity
        :return:
        """
        self._velocity = Vector2()

    @property
    def actors_in_attack_range(self):
        """
        Property that holds reference to any visible enemy
        :return:
        """
        return self._actors_in_attack_range

    @actors_in_attack_range.setter
    def actors_in_attack_range(self, value):
        self._actors_in_attack_range = value

    def statistics_changed(self):
        """
        Recalculate statistics
        :return:
        """
        self.recalculate_statistics()
        if self.velocity.length() != 0:
            self.velocity = self.velocity.normalize() * self._statistics.speed

    def add_modifier(self, modifier):
        """
        Adds statistics modifier
        :param modifier:
        :return:
        """
        self._modifiers.append(modifier)
        self.statistics_changed()

    def remove_modifier(self, modifier):
        """
        Removes statistics modifier
        :param modifier:
        :return:
        """
        self._modifiers.remove(modifier)
        self.statistics_changed()

    @property
    def logical_effects(self):
        """
        Holds any logical effect applied to actor
        :return:
        """
        return self._logical_effects

    def find_logical_effect_by_name(self, name):
        """
        Returns effect with specified id
        :param name:
        :return:
        """
        for le in self._logical_effects:
            if le.name == name:
                return le
        return None

    def remove_effect(self, effect):
        """
        Remove effect from actor
        :param effect:
        :return:
        """
        self._logical_effects.remove(effect)

    def add_logical_effect(self, effect):
        """
        Adds logical effect to actor
        :param effect:
        :return:
        """
        if effect.is_unique:
            prev_effect = self.find_logical_effect_by_name(effect.name)
            if prev_effect is not None:
                prev_effect.on_merge(effect)
            else:
                self._logical_effects.append(effect)
        else:
            self._logical_effects.append(effect)


class EvolvingActor(Actor):
    """
    Actor which can be evolved/upgraded
    """
    def __init__(self, class_properties):
        super().__init__(class_properties)
        self._current_evolution_level = 0
        self._evolution_statistics = []
        self._evolution_animations = []
        self._evolution_costs = []

    def add_evolution_level(self, statistics, evolution_cost, animations=None):
        """
        Adds evolution level
        :param statistics:
        :param evolution_cost:
        :param animations:
        :return:
        """
        self._evolution_statistics.append(statistics)
        self._evolution_animations.append(animations)
        self._evolution_costs.append(evolution_cost)

    @property
    def current_evolution_level(self):
        """
        Current level
        :return:
        """
        return self._current_evolution_level

    def evolve(self):
        """
        Evolve actor
        :return:
        """
        i = self._current_evolution_level
        self._current_evolution_level += 1

        self._base_statistics = self._evolution_statistics[i]
        self.recalculate_statistics()
        animations = self._evolution_animations[i]
        if animations is not None:
            for state, animation in animations.items():
                self.set_animation(state, animation)

        if ActorCallback.EVOLVE in self._callbacks:
            self._callbacks[ActorCallback.EVOLVE](self)

    def get_current_evolution_cost(self):
        """
        Returns cost of evolution
        :return:
        """
        return self._evolution_costs[self._current_evolution_level]

    def has_max_level(self):
        """
        Returns true if reached max level
        :return:
        """
        return self._current_evolution_level >= len(
            self._evolution_statistics)


def create_effect(name, actor, **kwargs):
    """
    Creates effect from arguments
    :param name:
    :param actor:
    :param kwargs:
    :return:
    """
    effects_module = importlib.import_module(
        "pytowerdefence.gameplay.LogicalEffects")
    return getattr(effects_module, name)(actor, **kwargs)


def add_effect_to_actor(name, actor, **kwargs):
    """
    Add effect to actor by its definition
    :param name:
    :param actor:
    :param kwargs:
    :return:
    """
    effect = create_effect(name, actor, **kwargs)
    actor.add_logical_effect(effect)


def add_effects_to_actor(actor, effect_list):
    """
    Add logical effects list
    :param actor:
    :param effect_list:
    :return:
    """
    for ed in effect_list:
        add_effect_to_actor(ed[0], actor, **ed[1])
