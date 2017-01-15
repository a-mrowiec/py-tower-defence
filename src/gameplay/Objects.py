import pygame
from pygame.math import Vector2


class GameObject(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self._position = Vector2(0, 0)
        self._prev_position = Vector2(0, 0)
        self._velocity = Vector2(0, 0)
        self._rect = pygame.Rect(0, 0, 0, 0)

    def update(self, dt):
        self._prev_position = Vector2(self._position)
        self._position += (self._velocity * dt)
        self._rect.center = self._position

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

    def rotate_to_direction(self, direction):
        self._angle = direction.angle_to(Vector2(0, -1))
