import pygame

from pygame.math import Vector2


class Widget(pygame.sprite.Sprite):
    """
    Base class for any UI widget
    """
    def __init__(self):
        self.z = 1
        self.rect = pygame.Rect(0, 0, 0, 0)
        self.position = Vector2()

    def on_mouse_event(self, event):
        """
        Invoked when widget is on top (based on Z property), and rect collides with click point
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
        self.font = pygame.font.Font(pygame.font.get_default_font(), size)
        self.surface = self.font.render(text, True, color)
        self.rect.width = self.surface.get_width()
        self.rect.height = self.surface.get_height()

    def draw(self, surface):
        surface.blit(self.surface, self.position)


class GameWindow(Widget):
    def __init__(self, level, width, height):
        super().__init__()
        self.z = 0
        self.rect.width = width
        self.rect.height = height
        self.level = level

    def on_mouse_event(self, event):
        actor_clicked = self._find_clicked_actor(event.pos)
        print("Actor clicked: ", actor_clicked)

    def _find_clicked_actor(self, pos):
        for actor in self.level.actor_iterator():
            if actor.rect.collidepoint(pos):
                return actor
        return None


def is_keyboard_event(event):
    return pygame.event.event_name(event.type).startswith("K_")


def is_mouse_event(event):
    return (event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.MOUSEBUTTONUP) and event.button == 1


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
        if is_mouse_event(event):
            clicked = self._get_colliding_widget(event.pos)
            if clicked is not None:
                clicked.on_mouse_event(event)

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