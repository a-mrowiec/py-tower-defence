import pygame
from pygame.math import Vector2

from pytowerdefence.UI import Button


class GameActionButton(Button):
    def __init__(self, action_name, action_manager, text=None, img=None, size=24, color=(0,0,0), **kwargs):
        super().__init__(text, img, size, color)
        self._action_name = action_name
        self._action_args = kwargs
        self._action_manager = action_manager

    def on_mouse_click_event(self, event):
        if event.type == pygame.MOUSEBUTTONUP:
            self._action_manager.start_action(self._action_name, **self._action_args)


class BaseAction:
    def perform(self, action_manager):
        pass

    def is_continuous(self):
        return False


class BaseContinuousAction(BaseAction):
    def is_continuous(self):
        return True

    def is_finished(self):
        return True


class AddTowerAction(BaseContinuousAction):
    def __init__(self, tower, **kwargs):
        self._tower_template_name = tower
        self._action_manager = None
        self._finished = False
        self._colliding = True
        self._tower = None

    def perform(self, action_manager):
        self._action_manager = action_manager
        self._tower = self._action_manager.creatures_factory.create(self._tower_template_name)
        self._tower.update(0.0)
        self._action_manager.set_window_mediator(self)

    def is_finished(self):
        return self._finished

    def on_break(self):
        self._action_manager.set_window_mediator(None)

    def on_mouse_click_event(self, event):
        if not self._colliding:
            self._action_manager.level.add(self._tower)
            self._action_manager.level.add_obstacle(self._tower)
            self._tower.statistics.team = 1
            self._tower = None
            self._finished = True
            self._action_manager.set_window_mediator(None)

    def on_mouse_motion_event(self, event):
        self._tower.position = Vector2(event.pos)
        self._colliding = self._action_manager.level.is_rectangle_colliding(self._tower.rect)

    def draw(self, surface):
        if self._tower is not None:
            surface.blit(self._tower.image, [self._tower.rect.x, self._tower.rect.y])


class ActionManager:

    def __init__(self, game_window, level, creatures_factory):
        self.game_window = game_window
        self._current_action = None
        self.level = level
        self.creatures_factory = creatures_factory

    def set_window_mediator(self, mediator):
        self.game_window.mediator = mediator

    def start_action(self, name, **kwargs):
        self._stop_other_action()
        action_created = self.create_action(name, **kwargs)
        self._perform_action(action_created)

    def update(self, dt):
        if self._current_action is not None and self._current_action.is_finished():
            self._current_action = None

    def _perform_action(self, action):
        action.perform(self)
        if action.is_continuous():
            self._current_action = action

    def _stop_other_action(self):
        if self._current_action is not None:
            self._current_action.on_break()
            self._current_action = None

    def create_action(self, name, **kwargs):
        return AddTowerAction(kwargs['tower'])