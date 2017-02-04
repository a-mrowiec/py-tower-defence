from pygame.math import Vector2

from pytowerdefence.Phase import Phase
from pytowerdefence.UI import Button, PositionAttachType


class MainMenuPhase(Phase):
    def __init__(self, app, ui_manager):
        self._app = app
        self._ui_manager = ui_manager

    def initialise(self, **kwargs):
        start_button = Button("Start Game", color=(255, 255, 255), size=44)
        start_button._click_callback = self.start_game
        start_button.position_attach_type = PositionAttachType.CENTER
        start_button.position = Vector2(self._ui_manager.window_size.x / 2,
                                        self._ui_manager.window_size.y / 2)
        self._ui_manager.add_widget(start_button)

    def start_game(self, event):
        self._app.set_phase('game', map_file='data/maps/test.tmx')

    def on_destroy(self):
        self._ui_manager.clear_all_widgets()
