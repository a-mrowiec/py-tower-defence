from enum import Enum

import pygame
from pygame.math import Vector2

from pytowerdefence.Resources import ResourceClass
from pytowerdefence.Resources import ResourceManager
from pytowerdefence.Utils import rot_center

ENEMY_TEAM = 0
PLAYER_TEAM = 1


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
        self._kill_callback = None
        self._team = ENEMY_TEAM

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

    @property
    def kill_callback(self):
        return self._kill_callback

    @kill_callback.setter
    def kill_callback(self, value):
        self._kill_callback = value

    def rotate_to_direction(self, direction):
        self._angle = direction.angle_to(Vector2(0, -1))

    def kill(self):
        self.alive = False
        if self._kill_callback is not None:
            self._kill_callback(self)
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
        self._speed = 500
        self.sprite = ResourceManager.load_image(ResourceClass.BULLETS,
                                                 'small-knife.png')

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
        self._target.hit(self._owner.statistics.attack_damage)
        self._owner.change_state(ActorState.IDLE)
        self.kill()


class ActorState(Enum):
    IDLE = 0
    MOVE = 1
    ATTACK = 2
    DEATH = 3


class ActorStatistics:
    def __init__(self):
        self.current_health = 0
        self.max_health = 0
        self.speed = 0
        self.attack_damage = 0
        self.attack_speed = 0
        self.attack_range = 0


class Actor(GameObject):
    def __init__(self):
        super().__init__()
        self._animations = {}
        self._current_animation = None
        self._controllers = []
        self._state = ActorState.IDLE
        self._statistics = ActorStatistics()
        self._actors_in_attack_range = []
        self._ai = None
        self._prev_updated_controller = None

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
                if self._prev_updated_controller != controller and self._prev_updated_controller is not None:
                    self._prev_updated_controller.on_update_end()
                controller.update(dt)
                self._prev_updated_controller = controller

    def hit(self, damage):
        self._statistics.current_health -= damage
        if self._statistics.current_health < 0:
            self.on_death()

    def add_controller(self, controller):
        controller.set_actor(self)
        self._controllers.append(controller)

    @property
    def controllers(self):
        return self._controllers

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


class EvolvingActor(Actor):
    def __init__(self):
        super().__init__()
        self._current_evolution_level = 0
        self._evolution_statistics = []
        self._evolution_animations = []

    def add_evolution_level(self, statistics, animations=None):
        self._evolution_statistics.append(statistics)
        self._evolution_animations.append(animations)

    @property
    def current_evolution_level(self):
        return self._current_evolution_level

    def evolve(self):
        i = self._current_evolution_level
        self._current_evolution_level += 1

        self._statistics = self._evolution_statistics[i]
        animations = self._evolution_animations[i]
        if animations is not None:
            for state, animation in animations:
                self.set_animation(state, animation)

    def can_evolve(self):
        return self._current_evolution_level < len(
            self._evolution_statistics)
