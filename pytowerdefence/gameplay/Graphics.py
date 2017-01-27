import pygame

from pytowerdefence.gameplay.Scene import Camera


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
        self._actor = value
        if self._actor is not None:
            self._attack_range = int(self._actor.statistics.attack_range + self._actor.radius)
            self._surface = pygame.Surface((self._attack_range * 2, self._attack_range * 2), pygame.SRCALPHA)
            self._surface.fill((0, 0, 0, 0))

    def draw(self, surface):
        if self._actor is not None:
            pygame.draw.circle(self._surface, (self._color[0], self._color[1], self._color[2], 128),
                               (self._attack_range, self._attack_range), self._attack_range)
            pygame.draw.circle(self._surface, (self._color[0], self._color[1], self._color[2], 255),
                               (self._attack_range, self._attack_range), self._attack_range, 4)

            on_screen_pos = Camera.to_screen_position(self._actor.position)
            surface.blit(self._surface,
                         [on_screen_pos.x - self._attack_range, on_screen_pos.y - self._attack_range])

    @property
    def color(self):
        return self._color

    @color.setter
    def color(self, value):
        self._color = value
