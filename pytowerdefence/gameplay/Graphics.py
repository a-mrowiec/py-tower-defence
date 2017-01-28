import pygame
from pygame.math import Vector2

from pytowerdefence.gameplay.Scene import Camera
from math import pi


class AttackRangeDrawer:
    def __init__(self, actor=None, color=(255, 255, 255)):
        self._actor = None
        self._color = color
        self._surface = None
        self._attack_range = None

        self.actor = actor

    @property
    def actor(self):
        return self._actor

    @actor.setter
    def actor(self, value):
        if self._actor != value:
            self._actor = value
            if self._actor is not None:
                self._attack_range = int(
                    self._actor.statistics.attack_range + self._actor.radius)
                self._surface = pygame.Surface(
                    (self._attack_range * 2, self._attack_range * 2),
                    pygame.SRCALPHA)
                self._redraw()

    def _redraw(self):
        self._surface.fill((0, 0, 0, 0))
        pygame.draw.circle(self._surface, (
        self._color[0], self._color[1], self._color[2], 128),
                           (self._attack_range, self._attack_range),
                           self._attack_range)
        pygame.draw.circle(self._surface, (
        self._color[0], self._color[1], self._color[2], 255),
                           (self._attack_range, self._attack_range),
                           self._attack_range, 4)

    def draw(self, surface):
        if self._actor is not None:
            on_screen_pos = Camera.to_screen_position(self._actor.position)
            surface.blit(self._surface,
                         [on_screen_pos.x - self._attack_range,
                          on_screen_pos.y - self._attack_range])

    @property
    def color(self):
        return self._color

    @color.setter
    def color(self, value):
        self._color = value
        self._redraw()


class HealthDrawer:
    def __init__(self, actor = None):
        self._actor = actor

    @property
    def actor(self):
        return self._actor

    @actor.setter
    def actor(self, value):
        self._actor = value

    def draw(self, surface):
        if self._actor is not None:
            rect = pygame.Rect(self.actor.rect)
            rect.width += 10
            rect.height += 10
            rect.center = Vector2(self.actor.rect.center)
            percentage = self.actor.statistics.current_health/self.actor.statistics.max_health
            end_angle = pi * percentage * 2
            pygame.draw.arc(surface, (255, 0, 0), rect, 0, end_angle, 8)