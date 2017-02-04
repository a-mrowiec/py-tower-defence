import pygame
from pygame.math import Vector2

from pytowerdefence.Resources import ResourceManager, ResourceClass
from pytowerdefence.UI import Button, Panel, Text, ParentAttachType, Widget
from pytowerdefence.gameplay.Objects import ActorCallback
from pytowerdefence.gameplay.Scene import Camera


class GameWindow(Widget):
    def __init__(self, width, height):
        super().__init__()
        self.z = 0
        self._rect.width = width
        self._rect.height = height
        self.mediator = None
        self.camera_movement_speed = 128

    def on_mouse_motion_event(self, event):
        if self.mediator is not None:
            self.mediator.on_mouse_motion_event(event)

    def draw(self, surface):
        if self.mediator is not None:
            self.mediator.draw(surface)

    def on_mouse_click_event(self, event):
        if self.mediator is not None:
            self.mediator.on_mouse_click_event(event)

    def on_keyboard_event(self, event):
        if event.key == pygame.K_LEFT:
            Camera.move_by((-self.camera_movement_speed, 0))
        elif event.key == pygame.K_RIGHT:
            Camera.move_by((self.camera_movement_speed, 0))
        elif event.key == pygame.K_UP:
            Camera.move_by((0, -self.camera_movement_speed))
        elif event.key == pygame.K_DOWN:
            Camera.move_by((0, self.camera_movement_speed))

    def _find_clicked_actor(self, pos):
        for actor in self.level.actor_iterator():
            if actor.rect.collidepoint(pos):
                return actor
        return None


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
    def __init__(self, logic_manager):
        super().__init__(img=ResourceManager.load_image(ResourceClass.UI, "panel.png"))
        self._actor = None
        self._logic_manager = logic_manager
        self.widget_id = "guardian_panel"
        self._upgrade_button = UpgradeButton(None, self._logic_manager)
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

        self._guardian_level = Text("", size = 48)
        self._guardian_level.parent_attach_type = ParentAttachType.CENTER
        self._guardian_level.position = Vector2(142, 77)

        self.add_child(self._guardian_name)
        self.add_child(self._guardian_level)
        self.add_child(self._upgrade_button)
        self.add_child(self._coins)
        self.add_child(self._coins_icon)

        self.visible = False

    def set_actor(self, actor):
        if self._actor is not None:
            self._actor.remove_callback(ActorCallback.EVOLVE)
        self._actor = actor
        self._on_actor_changed()

    def _on_evolve(self, actor):
        if actor != self._actor:
            print("Caching evolve event from unknown actor!")
        self._on_actor_changed()

    def _on_actor_changed(self):
        if self._actor is not None:
            self._guardian_name.text = "Bandit"
            self._guardian_level.text = "Level: {0}".format(
                self._actor.current_evolution_level + 1)
            self.visible = True
            self._actor.set_callback(ActorCallback.EVOLVE, self._on_evolve)
        else:
            self.visible = False
        self._upgrade_button.actor = self._actor


class UpgradeButton(Button):
    def __init__(self, actor, logic_manager):
        super().__init__(
            img=ResourceManager.load_image(ResourceClass.UI, "upgrade.png"),
            disabled_img=ResourceManager.load_image(ResourceClass.UI, "upgrade-disabled.png"))
        self._actor = actor
        self._logic_manager = logic_manager
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

    def update(self, dt):
        if self._actor is not None:
            self.disabled = not self._logic_manager.can_evolve(self.actor)
            print("Disabled", self.disabled)

    def clicked(self, event):
        if event.type == pygame.MOUSEBUTTONUP:
            if self._actor is not None and \
                    self._logic_manager.can_evolve(self.actor):
                self._logic_manager.evolve(self._actor)






