from enum import Enum, IntEnum

import pygame
from pygame.math import Vector2

from pytowerdefence.Resources import ResourceManager, ResourceClass
from pytowerdefence.Utils import half_size_of_rect


class PositionAttachType(Enum):
    TOP_LEFT = 0,
    CENTER = 1


class Widget(pygame.sprite.Sprite):
    """
    Base class for any UI widget
    """

    def __init__(self, widget_id=None):
        self.z = 1
        self._rect = pygame.Rect(0, 0, 0, 0)
        self._position = Vector2()
        self._relative_position = Vector2()
        self._visible = True
        self._children = []
        self._parent = None
        self.widget_id = widget_id
        self._position_attach_type = PositionAttachType.TOP_LEFT

    def remove_child(self, child):
        if child in self._children:
            self._children.remove(child)
            child.parent = None

    def add_child(self, child):
        self._children.append(child)
        child.parent = self

    @property
    def position_attach_type(self):
        return self._position_attach_type

    @position_attach_type.setter
    def position_attach_type(self, value):
        self._position_attach_type = value
        self.position_changed()

    @property
    def children(self):
        return self._children

    @property
    def rect(self):
        return self._rect

    @property
    def position(self):
        return self._position

    @property
    def parent(self):
        return self._parent

    @parent.setter
    def parent(self, value):
        self._parent = value
        self.position_changed()

    @position.setter
    def position(self, value):
        self._relative_position = value
        self.position_changed()

    def position_changed(self):
        if self._parent is not None:
            self._position = self._real_position() + self._parent.position
        else:
            self._position = self._real_position()

        self._rect.x = self._position.x
        self._rect.y = self._position.y
        for child in self.children:
            child.position_changed()

    def _real_position(self):
        if self._position_attach_type == PositionAttachType.TOP_LEFT:
            return self._relative_position
        else:
            return self._relative_position - half_size_of_rect(
                self.rect)

    @property
    def visible(self):
        return self._visible

    @visible.setter
    def visible(self, value):
        self._visible = value
        for child in self.children:
            child.visible = value

    def on_mouse_click_event(self, event):
        """
        Invoked when widget is on top (based on Z property), and rect collides
        with click point
        :param event:
        :return:
        """
        pass

    def on_mouse_motion_event(self, event):
        """
        Invoked when widget is on top (based on Z property) and mouse is moved
        over element
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
    def __init__(self, text, size=24, color=(255, 255, 255)):
        super().__init__()
        self._color = color
        self._size = size
        self._text = None
        self._font = None
        self._surface = None
        self.text = text

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, text):
        if text is not None:
            self._text = text
            self._font = pygame.font.Font(
                ResourceManager.get_path(ResourceClass.UI,
                                         "monotype-corsiva.ttf"),
                self._size)
            self._surface = self._font.render(text, True, self._color)
            self._rect.width = self._surface.get_width()
            self._rect.height = self._surface.get_height()
            self.position_changed()

    def draw(self, surface):
        if self._surface is not None:
            surface.blit(self._surface, self._position)


class Panel(Text):
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


class ButtonState(IntEnum):
    IDLE = 0,
    DISABLED = 1


class Button(Panel):
    def __init__(self, text=None, img=None, disabled_img=None, size=24,
                 color=(0, 0, 0)):
        super().__init__(text, img, size, color)
        self._click_callback = None
        self._disabled = False
        self._images = [img, disabled_img]
        self._state = ButtonState.IDLE

    @property
    def disabled(self):
        return self._state == ButtonState.DISABLED

    @disabled.setter
    def disabled(self, value):
        self._change_state(ButtonState.DISABLED if value else ButtonState.IDLE)

    def _change_state(self, value):
        if value != self._state:
            self._state = value
            if self._images[self._state] is not None:
                self.set_image(self._images[self._state])

    @property
    def click_callback(self):
        return self._click_callback

    @click_callback.setter
    def click_callback(self, value):
        self._click_callback = value

    def on_mouse_click_event(self, event):
        if self._state != ButtonState.DISABLED and self._click_callback is not None:
            self._click_callback(event)


def is_keyboard_event(event):
    return event.type == pygame.KEYDOWN


def is_mouse_click_event(event):
    return (
               event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.MOUSEBUTTONUP) and event.button == 1


def is_mouse_motion_event(event):
    return event.type == pygame.MOUSEMOTION


class UIManager(object):
    """
    Manager of any widget
    """

    def __init__(self):
        self._widgets = {}
        self._focused_widget = None

    def focus_widget(self, widget):
        self._focused_widget = widget

    def update(self, dt):
        """
        Updates every widget every frame
        :param dt:
        :return:
        """
        for _, layer in self._widgets.items():
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
            for widget in self._visible_widgets_iterator(layer):
                widget.draw(surface)

    def add_widget(self, widget):
        """
        Adds widget and all its children to update and rendering queue
        :param widget:
        :return:
        """
        if widget.z not in self._widgets:
            self._widgets[widget.z] = []

        self._widgets[widget.z].append(widget)
        for child in widget.children:
            self.add_widget(child)

    def remove_widget(self, widget):
        """
        Removes widget and all children
        :param widget:
        :return:
        """
        if widget.z in self._widgets:
            self._widgets[widget.z].remove(widget)

        for child in widget.children:
            self.remove_widget(child)

    def get_by_id(self, widget_id):
        for z in self._widgets:
            layer = self._widgets[z]
            for widget in layer:
                if widget.widget_id == widget_id:
                    return widget
        return None

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

    def _visible_widgets_iterator(self, layer):
        for widget in layer:
            if widget.visible:
                yield widget

    def _get_colliding_widget(self, pos):
        for z in sorted(self._widgets, reverse=True):
            layer = self._widgets[z]
            for widget in self._visible_widgets_iterator(layer):
                if widget.rect.collidepoint(pos):
                    return widget
        return None
