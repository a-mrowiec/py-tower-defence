"""
Main menu phase
"""
import pygame
from pygame.math import Vector2

from pytowerdefence.Phase import Phase
from pytowerdefence.Resource import ResourceManager, ResourceClass
from pytowerdefence.UI import Button, PositionAttachType, Panel


class MainMenuPhase(Phase):
    """
    Main menu phase
    """

    def __init__(self, app, ui_manager):
        self._app = app
        self._ui_manager = ui_manager

    def initialise(self, **kwargs):
        image = ResourceManager.load_image(ResourceClass.UI, 'main-menu-bg.jpg')
        panel = Panel(img=pygame.transform.scale(image, (1024, 768)))
        start_button = Button("Start Game", color=(255, 255, 255), size=44)
        start_button.click_callback = self.start_game
        start_button.position_attach_type = PositionAttachType.CENTER
        start_button.position = Vector2(self._ui_manager.window_size.x / 2,
                                        self._ui_manager.window_size.y / 2)
        start_button.z = 1
        panel.z = 0
        self._ui_manager.add_widget(start_button)
        self._ui_manager.add_widget(panel)

    def start_game(self, _):
        """
        Starts game
        :param _:
        :return:
        """
        self._app.set_phase('game', filename='data/maps/1.json')

    def on_destroy(self):
        self._ui_manager.clear_all_widgets()
