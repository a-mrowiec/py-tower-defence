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
        self.attack_range = 0


class ActorState(Enum):
    IDLE = 0
    MOVE = 1
    ATTACK = 2
    DEATH = 3


class Actor(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self._position = Vector2(0, 0)
        self._prev_position = Vector2(0, 0)
        self._velocity = Vector2(0, 0)
        self._rect = pygame.Rect(0, 0, 0, 0)
        self._animations = {}
        self._current_animation = None
        self.controllers = []
        self._team = 0
        self._state = ActorState.IDLE
        self._statistics = ActorStatistics()
        self._angle = 0
        self._actors_in_attack_range = []
        self.image = None

    def update(self, dt):
        for controller in self.controllers:
            controller.update(dt)

        self._prev_position = Vector2(self._position)
        self._position += (self._velocity * dt)
        self._rect.center = self._position
        if self._current_animation is not None:
            self.image = pygame.transform.rotate(self._current_animation.getCurrentFrame(), self._angle)
            if self._current_animation.isFinished():
                for controller in self.controllers:
                    controller.on_animation_end()
                self._change_state(ActorState.IDLE)

    def hit(self, damage):
        self._statistics.current_health -= damage
        if self._statistics.current_health < 0:
            self.on_death()

    def add_controller(self, controller):
        controller.set_actor(self)
        self.controllers.append(controller)

    def on_death(self):
        self._stop_controllers()
        self._velocity = Vector2()
        self._change_state(ActorState.DEATH)

    def stop(self):
        self._change_state(ActorState.IDLE)

    def add_animation(self, state, animation):
        self._animations[state] = animation

    def create_and_add_animation(self, images_path, rects, state, **kwargs):
        images = pyganim.getImagesFromSpriteSheet(images_path, rects=rects)
        speed = kwargs.get('speed', [100])
        frames = list(zip(images, speed * len(images)))
        animation = pyganim.PygAnimation(frames)
        animation.loop = kwargs.get('loop', True)
        self.add_animation(state, animation)

    def _change_state(self, new_state):
        if self._state != new_state:
            self._stop_current_animation()
            self._state = new_state
            self._play_current_animation()

    def _stop_controllers(self):
        for controller in self.controllers:
            controller.stop()

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

    @property
    def velocity(self):
        return self._velocity

    @property
    def angle(self):
        return self._angle

    @property
    def rect(self):
        return self._rect

    @rect.setter
    def rect(self, value):
        self._rect = value

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

    @property
    def radius(self):
        return max(self._rect.width, self._rect.height)

    @position.setter
    def position(self, value):
        self._position = value
        self._rect.center = self._position

    @property
    def actors_in_attack_range(self):
        return self._actors_in_attack_range

    @actors_in_attack_range.setter
    def actors_in_attack_range(self, value):
        self._actors_in_attack_range = value


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

ogre_death_rects = [(0, 0, 64, 64),
                     (64, 0, 64, 64),
                     (128, 0, 64, 64),
                     (192, 0, 64, 64),
                     (0, 64, 64, 64),
                     (64, 64, 64, 64),
                     (128, 64, 64, 64),
                     (192, 64, 64, 64),
                     (0, 128, 64, 64),
                     (64, 128, 64, 64),
                     (128, 128, 64, 64),
                     (192, 128, 64, 64),
                     (0, 192, 64, 64),
                     (64, 192, 64, 64),
                     (128, 192, 64, 64),
                     (192, 192, 64, 64),
                     (0, 256, 64, 64),
                     (64, 256, 64, 64),
                     (128, 256, 64, 64),
                     (192, 256, 64, 64),
                     (0, 320, 64, 64),
                     (64, 320, 64, 64),
                     (128, 320, 64, 64),
                     (192, 320, 64, 64),
                     (0, 384, 64, 64),
                     (64, 384, 64, 64),
                     (128, 384, 64, 64),
                     (192, 384, 64, 64),
                     (0, 448, 64, 64),
                     (64, 448, 64, 64),
                     (128, 448, 64, 64),
                     (192, 448, 64, 64)]


class OgreActor(Actor):
    def __init__(self):
        super().__init__()
        self._statistics.speed = 50

        self.create_and_add_animation('data/ogre-move.png', ogre_move_rects, ActorState.MOVE)
        self.create_and_add_animation('data/ogre-move.png', ogre_idle_rects, ActorState.IDLE)
        self.create_and_add_animation('data/ogre-attack.png', ogre_move_rects, ActorState.ATTACK, loop=False)
        self.create_and_add_animation('data/ogre-death.png', ogre_death_rects, ActorState.DEATH, loop=False, speed=[20])

        self.statistics.attack_range = 100
        self._change_state(ActorState.MOVE)

        self.rect.width = 64
        self.rect.height = 64


class BanditActor(Actor):
    def __init__(self):
        super().__init__()
        self._statistics.speed = 50

        self.create_and_add_animation('data/bandit-move.png', ogre_move_rects, ActorState.MOVE)
        self.create_and_add_animation('data/bandit-move.png', ogre_idle_rects, ActorState.IDLE)
        self.create_and_add_animation('data/bandit-attack.png', ogre_move_rects, ActorState.ATTACK, loop=False)
        self.create_and_add_animation('data/bandit-death.png', ogre_death_rects, ActorState.DEATH, loop=False)

        self.statistics.attack_range = 100
        self.statistics.attack = 5
        self._play_current_animation()

        self.rect.width = 64
        self.rect.height = 64
