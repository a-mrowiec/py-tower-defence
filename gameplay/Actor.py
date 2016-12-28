from enum import Enum

import pygame
from pygame.math import Vector2


class ActorStatistics:
    def __init__(self):
        self.current_health = 0
        self.max_health = 0
        self.speed = 0
        self.attack = 0
        self.attack_speed = 0


class ActorState(Enum):
    IDLE = 0
    MOVE = 1
    ATTACK = 2


class Actor(pygame.sprite.Sprite):
    _position = Vector2(0, 0)
    _prev_position = Vector2(0, 0)
    _velocity = Vector2(0, 0)
    rect = pygame.Rect(0, 0, 0, 0)
    _animations = {}
    _current_animation = None
    controllers = []
    _state = ActorState.IDLE
    _statistics = ActorStatistics()
    _angle = 0
    image = None

    def __init__(self):
        pygame.sprite.Sprite.__init__(self)

    def update(self, dt):
        for controller in self.controllers:
            controller.update(dt)

        self._prev_position = Vector2(self._position)
        self._position += (self._velocity * dt)
        self.rect.center = self._position
        if self._current_animation is not None:
            self.image = pygame.transform.rotate(self._current_animation.getCurrentFrame(), self._angle)
            if self._current_animation.isFinished():
                self._change_state(ActorState.IDLE)

    def hit(self, damage):
        self._statistics.current_health -= damage
        if self._statistics.current_health < 0:
            self.on_death()

    def add_controller(self, controller):
        controller.set_actor(self)
        self.controllers.append(controller)

    def on_death(self):
        pass

    def stop(self):
        self._change_state(ActorState.IDLE)

    def add_animation(self, state, animation):
        self._animations[state] = animation

    def _change_state(self, new_state):
        if self._state != new_state:
            if self._current_animation is not None:
                self._current_animation.stop()
            self._state = new_state
            self._current_animation = self._animations.get(self._state, None)
            if self._current_animation is not None:
                self._current_animation.play()

    @property
    def statistics(self):
        return self._statistics

    @property
    def velocity(self):
        return self._velocity

    def go_to_direction(self, direction):
        self._velocity = direction.normalize() * self._statistics.speed
        self._angle = self._velocity.angle_to(Vector2(0, -1))
        self._change_state(ActorState.MOVE)

    def stop(self):
        self._velocity = Vector2()
        self._change_state(ActorState.IDLE)

    @property
    def position(self):
        return self._position

    @position.setter
    def position(self, value):
        self._position = value
        self.rect.center = self._position


import pyganim

rects = [(0, 154, 94, 77),
         (94, 154, 94, 77),
         (188, 154, 94, 77),
         (282, 154, 94, 77),
         (376, 154, 94, 77),
         (470, 154, 94, 77),
         (564, 154, 94, 77),
         (658, 154, 94, 77),
         (752, 154, 94, 77), ]

ogre_move_rects = [(0, 0, 64, 64),
                   (64, 0, 64, 64),
                   (128, 0, 64, 64),
                   (192, 0, 64, 64),
                   (256, 0, 64, 64),
                   (320, 0, 64, 64),
                   (384, 0, 64, 64),
                   (448, 0, 64, 64), ]

ogre_idle_rects = [(0, 0, 64, 64)]


class TestAnimatedActor(Actor):
    def __init__(self):
        super().__init__()
        self._statistics.speed = 50
        move_images = pyganim.getImagesFromSpriteSheet('data/ogre-move.png', rects=ogre_move_rects)
        move_frames = list(zip(move_images, [100] * len(move_images)))
        self.add_animation(ActorState.MOVE, pyganim.PygAnimation(move_frames))

        idle_images = pyganim.getImagesFromSpriteSheet('data/ogre-move.png', rects=ogre_idle_rects)
        idle_frames = list(zip(idle_images, [100] * len(idle_images)))
        self.add_animation(ActorState.IDLE, pyganim.PygAnimation(idle_frames))

        attack_images = pyganim.getImagesFromSpriteSheet('data/ogre-attack.png', rects=ogre_move_rects)
        attack_frames = list(zip(attack_images, [100] * len(attack_images)))
        attack_animation = pyganim.PygAnimation(attack_frames)
        attack_animation.loop = False
        self.add_animation(ActorState.ATTACK, attack_animation)
