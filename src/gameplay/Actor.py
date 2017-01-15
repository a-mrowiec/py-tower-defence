from enum import Enum

import pyganim
from pygame.math import Vector2

from src.Utils import rot_center
from src.gameplay.Objects import GameObject


class ActorStatistics:
    def __init__(self):
        self.team = 0
        self.current_health = 0
        self.max_health = 0
        self.speed = 0
        self.attack = 0
        self.attack_speed = 0
        self.attack_range = 0


class ActorState(Enum):
    IDLE = 0
    MOVE = 1
    ATTACK = 2
    DEATH = 3


class Actor(GameObject):
    def __init__(self):
        super().__init__()
        self._animations = {}
        self._current_animation = None
        self._controllers = []
        self._state = ActorState.IDLE
        self._statistics = ActorStatistics()
        self._angle = 0
        self._actors_in_attack_range = []
        self._ai = None

    def update(self, dt):
        if self._ai is not None:
            self._ai.update(dt)

        for controller in self._controllers:
            controller.update(dt)

        super().update(dt)
        if self._current_animation is not None:
            self.image = rot_center(self._current_animation.getCurrentFrame(), self._angle)
            if self._current_animation.isFinished():
                for controller in self._controllers:
                    controller.on_animation_end()
                self.change_state(ActorState.IDLE)

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

    def add_animation(self, state, animation):
        self._animations[state] = animation

    def create_and_add_animation(self, images_path, rects, state, **kwargs):
        images = pyganim.getImagesFromSpriteSheet(images_path, rects=rects)
        speed = kwargs.get('speed', [100])
        frames = list(zip(images, speed * len(images)))
        animation = pyganim.PygAnimation(frames)
        animation.loop = kwargs.get('loop', True)
        self.add_animation(state, animation)

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
        self._velocity = direction.normalize() * self._statistics.speed
        self.rotate_to_direction(direction)
        self.change_state(ActorState.MOVE)

    def stop(self):
        self._velocity = Vector2()
        self.change_state(ActorState.IDLE)

    @property
    def actors_in_attack_range(self):
        return self._actors_in_attack_range

    @actors_in_attack_range.setter
    def actors_in_attack_range(self, value):
        self._actors_in_attack_range = value
