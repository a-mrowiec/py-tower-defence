import pygame

from pytowerdefence.UI import Button


class GameActionButton(Button):
    def __init__(self, action_name, action_manager, text=None, img=None,
                 size=24, color=(0, 0, 0), **kwargs):
        super().__init__(text, img, size, color)
        self._action_name = action_name
        self._action_args = kwargs
        self._action_manager = action_manager
        self._action = action_manager.create_action(self._action_name, **self._action_args)
        self.click_callback = self.start_action

    def start_action(self, event):
        if event.type == pygame.MOUSEBUTTONUP:
            self._action_manager.start_action(self._action)

    def update(self, dt):
        self.disabled = self._action_manager.is_action_allowed(self._action)