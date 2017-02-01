import pygame
from pygame.math import Vector2

from pytowerdefence.Resources import ResourceManager, ResourceClass
from pytowerdefence.UI import Button, Panel, Text
from pytowerdefence.gameplay.Scene import Camera


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
        self.disabled = not self._action_manager.is_action_allowed(self._action)


class GuardianPanel(Panel):
    def __init__(self):
        super().__init__(img=ResourceManager.load_image(ResourceClass.UI, "panel.png"))
        self._upgrade_button = UpgradeButton(None)
        self._guardian_name = Text("Ogre", size=16)
        self.add_child(self._guardian_name)
        self._guardian_name.center_position(Vector2(139, 18))


class UpgradeButton(Button):
    def __init__(self, actor):
        super().__init__(img=ResourceManager.load_image(ResourceClass.UI, "upgrade.png"))
        self._actor = actor
        self._update()
        self.z = 2
        self._click_callback = self.clicked

    @property
    def actor(self):
        return self._actor

    @actor.setter
    def actor(self, value):
        self._actor = value
        self._update()

    def update(self, dt):
        super().update(dt)
        self._update()

    def _update(self):
        if self._actor is not None:
            rect = self._actor.rect
            self.position = Camera.to_screen_position([rect.right, rect.top])

    def on_mouse_click_event(self, event):
        super().on_mouse_click_event(event)

    def clicked(self, event):
        print("Clicked")






