import pygame

from pytowerdefence.Resources import ResourceManager, ResourceClass
from pytowerdefence.Utils import half_size_of_rect
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
        if self._actor != value:
            self._actor = value
            self._refresh()

    def _refresh(self):
        if self._actor is not None:
            self._attack_range = self._compute_attack_range()
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

    def _compute_attack_range(self):
        return int(self._actor.statistics.attack_range + self._actor.radius)

    def draw(self, surface):
        if self._actor is not None:
            if self._attack_range != self._compute_attack_range():
                self._refresh()

            on_screen_pos = Camera.to_screen_position(self._actor.position)
            surface.blit(self._surface,
                         [on_screen_pos.x - self._attack_range,
                          on_screen_pos.y - self._attack_range])
            surface.blit(self._actor.image,
                         Camera.to_screen_position(self._actor.rect.topleft))

    @property
    def color(self):
        return self._color

    @color.setter
    def color(self, value):
        self._color = value
        self._redraw()


class ProgressBarDrawer:
    def __init__(self, progress_image):
        self._progress_image = progress_image

    def draw(self, surface, rect, percentage):
        crop_rect = self._progress_image.get_rect()
        crop_rect.width = crop_rect.width * percentage
        surface.blit(self._progress_image.subsurface(crop_rect), rect)


class HealthDrawer:
    def __init__(self, actor=None):
        self._actor = actor
        self._background = ResourceManager.load_image(
            ResourceClass.UI, 'health-bar-background.png')
        self._progress = ProgressBarDrawer(ResourceManager.load_image(
            ResourceClass.UI, 'health-bar.png'))

    @property
    def actor(self):
        return self._actor

    @actor.setter
    def actor(self, value):
        self._actor = value

    def draw(self, surface):
        if self._actor is not None:
            statistics = self.actor.statistics
            percentage = self.actor.hp / statistics.max_health

            rect = self._background.get_rect()
            rect.center = Camera.to_screen_position(
                self.actor.position) - half_size_of_rect(
                self.actor.rect) + half_size_of_rect(
                self._background.get_rect()) - (0, 10)

            surface.blit(self._background, rect)
            self._progress.draw(surface, rect, percentage)
