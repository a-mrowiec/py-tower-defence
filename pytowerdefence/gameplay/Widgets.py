import pygame
from pygame.math import Vector2

from pytowerdefence.Resources import ResourceManager, ResourceClass
from pytowerdefence.UI import Button, Panel, Text, ParentAttachType


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
        self.widget_id = "guardian_panel"
        self._upgrade_button = UpgradeButton(None)
        self._upgrade_button.parent_attach_type = ParentAttachType.CENTER
        self._upgrade_button.position = Vector2(55, 164)

        self._coins = Text(text="50")
        self._coins.parent_attach_type = ParentAttachType.CENTER
        self._coins.position = Vector2(150, 164)

        self._coins_icon = Panel(img=ResourceManager.load_image(ResourceClass.UI, "coins.png"))
        self._coins_icon.parent_attach_type = ParentAttachType.CENTER
        self._coins_icon.position = Vector2(200, 164)

        self._guardian_name = Text("", size=16)
        self._guardian_name.parent_attach_type = ParentAttachType.CENTER
        self._guardian_name.position = Vector2(142, 18)

        self._guardian_level = Text("Level: 1", size = 48)
        self._guardian_level.parent_attach_type = ParentAttachType.CENTER
        self._guardian_level.position = Vector2(142, 77)

        self.add_child(self._guardian_name)
        self.add_child(self._guardian_level)
        self.add_child(self._upgrade_button)
        self.add_child(self._coins)
        self.add_child(self._coins_icon)

        self.visible = False

    def set_actor(self, actor):
        if actor is not None:
            self._guardian_name.text = "Bandit"
            self.visible = True
        else:
            self.visible = False
        self._upgrade_button.actor = actor


class UpgradeButton(Button):
    def __init__(self, actor):
        super().__init__(img=ResourceManager.load_image(ResourceClass.UI, "upgrade.png"))
        self._actor = actor
        self.z = 2
        self._click_callback = self.clicked

    @property
    def actor(self):
        return self._actor

    @actor.setter
    def actor(self, value):
        self._actor = value

    def on_mouse_click_event(self, event):
        super().on_mouse_click_event(event)

    def clicked(self, event):
        print("Clicked")






