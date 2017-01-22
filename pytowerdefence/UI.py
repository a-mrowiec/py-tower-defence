import pygame

from pygame.math import Vector2


class Widget(pygame.sprite.Sprite):
    def __init__(self):
        self.z = 0
        self.rect = pygame.Rect(0, 0, 0, 0)
        self.position = Vector2()

    def on_mouse_event(self, event):
        pass

    def on_keyboard_event(self, event):
        pass

    def draw(self, surface):
        pass

    def update(self, dt):
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


class UIManager(object):
    def __init__(self):
        self._widgets = {}
        self._focused_widget = None

    def update(self, dt):
        for _ , layer in self._widgets.items():
            for widget in layer:
                widget.update(dt)

    def draw(self, surface):
        for z in sorted(self._widgets):
            layer = self._widgets[z]
            for widget in layer:
                widget.draw(surface)

    def add_widget(self, widget):
        if widget.z not in self._widgets:
            self._widgets[widget.z] = []

        self._widgets[widget.z].append(widget)

    def process_event(self, event):
        if (event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.MOUSEBUTTONUP) and event.button == 1:
            clicked = self._get_colliding_widget(event.pos)
            if clicked is not None:
                clicked.on_mouse_event(event)

        elif self._is_keyboard_event(event):
            if self._focused_widget is not None:
                self._focused_widget.on_keyboard_event(event)

    def _is_keyboard_event(self, event):
        return pygame.event.event_name(event.type).startswith("K_")

    def _get_colliding_widget(self, pos):
        for z in sorted(self._widgets, reverse=True):
            layer = self._widgets[z]
            for widget in layer:
                if widget.rect.collidepoint(pos):
                    return widget
        return None