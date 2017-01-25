from enum import Enum

import pygame

from pygame.math import Vector2


class Widget(pygame.sprite.Sprite):
    """
    Base class for any UI widget
    """
    def __init__(self):
        self.z = 1
        self._rect = pygame.Rect(0, 0, 0, 0)
        self._position = Vector2()

    @property
    def rect(self):
        return self._rect

    @property
    def position(self):
        return self._position

    @position.setter
    def position(self, value):
        self._position = value
        self._rect.x = value.x
        self._rect.y = value.y

    def on_mouse_click_event(self, event):
        """
        Invoked when widget is on top (based on Z property), and rect collides with click point
        :param event:
        :return:
        """
        pass

    def on_mouse_motion_event(self, event):
        """
        Invoked when widget is on top (based on Z property) and mouse is moved over element
        :param event:
        :return:
        """
        pass

    def on_keyboard_event(self, event):
        """
        Invoked when widget is focused
        :param event:
        :return:
        """
        pass

    def draw(self, surface):
        """
        Draw widget
        :param surface:
        :return:
        """
        pass

    def update(self, dt):
        """
        Update widget every frame
        :param dt:
        :return:
        """
        pass


class Text(Widget):
    def __init__(self, text, size=24, color=(0, 0, 0)):
        super().__init__()
        self._color = color
        self._size = size
        self._text = None
        self._font = None
        self._surface = None
        self.set_text(text)

    def set_text(self, text):
        if text is not None:
            self._text = text
            self._font = pygame.font.Font(pygame.font.get_default_font(), self._size)
            self._surface = self.font.render(text, True, self._color)
            self._rect.width = self.surface.get_width()
            self._rect.height = self.surface.get_height()

    def draw(self, surface):
        if self._surface is not None:
            surface.blit(self.surface, self.position)


class Button(Text):
    def __init__(self, text=None, img=None, size=24, color=(0, 0, 0)):
        super().__init__(text, size, color)
        self._img = None
        self.set_image(img)

    def set_image(self, img):
        self._img = img
        if self._img is not None:
            rect = self._img.get_rect()
            self._rect.width = rect.width
            self._rect.height = rect.height

    def draw(self, surface):
        if self._img is not None:
            surface.blit(self._img, self.position)
        super().draw(surface)


class GameWindowState(Enum):
    IDLE = 0,
    ADDING_TOWER = 1


class GameWindow(Widget):
    def __init__(self, level, width, height):
        super().__init__()
        self.z = 0
        self._rect.width = width
        self._rect.height = height
        self.level = level
        self.state = GameWindowState.IDLE
        self._tower = None

    def start_adding_tower(self, tower):
        if self.state == GameWindowState.IDLE:
            self._tower = tower
            self.state = GameWindowState.ADDING_TOWER

    def on_mouse_motion_event(self, event):
        if self.state == GameWindowState.ADDING_TOWER:
            self._tower.position = Vector2(event.pos)
            if self.level.is_rectangle_colliding(self._tower.rect):
                print("Colliding")

    def draw(self, surface):
        if self.state == GameWindowState.ADDING_TOWER and self._tower is not None:
            surface.blit(self._tower.image, [self._tower.rect.x, self._tower.rect.y])

    def on_mouse_click_event(self, event):
        if self.state == GameWindowState.ADDING_TOWER:
            self._tower = None
            self.state = GameWindowState.IDLE

        actor_clicked = self._find_clicked_actor(event.pos)
        print("Actor clicked: ", actor_clicked)

    def _find_clicked_actor(self, pos):
        for actor in self.level.actor_iterator():
            if actor.rect.collidepoint(pos):
                return actor
        return None


def is_keyboard_event(event):
    return pygame.event.event_name(event.type).startswith("K_")


def is_mouse_click_event(event):
    return (event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.MOUSEBUTTONUP) and event.button == 1

def is_mouse_motion_event(event):
    return event.type == pygame.MOUSEMOTION


class UIManager(object):
    """
    Manager of any widget
    """
    def __init__(self):
        self._widgets = {}
        self._focused_widget = None

    def update(self, dt):
        """
        Updates every widget every frame
        :param dt:
        :return:
        """
        for _ , layer in self._widgets.items():
            for widget in layer:
                widget.update(dt)

    def draw(self, surface):
        """
        Draws widget in appropriate Z order
        :param surface:
        :return:
        """
        for z in sorted(self._widgets):
            layer = self._widgets[z]
            for widget in layer:
                widget.draw(surface)

    def add_widget(self, widget):
        """
        Adds widget to update and rendering queue
        :param widget:
        :return:
        """
        if widget.z not in self._widgets:
            self._widgets[widget.z] = []

        self._widgets[widget.z].append(widget)

    def process_event(self, event):
        """
        Process any input event. Delegates event to proper widget when needed
        :param event:
        :return:
        """
        if is_mouse_click_event(event):
            clicked = self._get_colliding_widget(event.pos)
            if clicked is not None:
                clicked.on_mouse_click_event(event)
        elif is_mouse_motion_event(event):
            moved_over = self._get_colliding_widget(event.pos)
            if moved_over is not None:
                moved_over.on_mouse_motion_event(event)
        elif is_keyboard_event(event):
            if self._focused_widget is not None:
                self._focused_widget.on_keyboard_event(event)

    def _get_colliding_widget(self, pos):
        for z in sorted(self._widgets, reverse=True):
            layer = self._widgets[z]
            for widget in layer:
                if widget.rect.collidepoint(pos):
                    return widget
        return None