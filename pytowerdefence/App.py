"""
Start module
"""
import pygame

from pytowerdefence.UI import UIManager
from pytowerdefence.gameplay.GamePhase import GamePhase
from pytowerdefence.mainmenu.MainMenuPhase import MainMenuPhase


class App:
    """
    Main starting class
    """
    def __init__(self):
        self._running = True
        self._display_surf = None
        self.size = self.width, self.height = 1024, 768
        self._current_phase = None
        self._ui_manager = None

    def on_init(self):
        """
        Initialize pygame
        :return:
        """
        pygame.init()
        self._display_surf = pygame.display.set_mode(
            self.size, pygame.HWSURFACE | pygame.DOUBLEBUF)

        self._ui_manager = UIManager(self.size)

        self._running = True
        self.set_phase('main_menu')
        return True

    def on_event(self, event):
        """
        Process input events
        :param event:
        :return:
        """
        if event.type == pygame.QUIT:
            self._running = False
        else:
            self._ui_manager.process_event(event)

    def set_phase(self, phase_type, **kwargs):
        """
        Change current phase
        :param phase_type:
        :param kwargs:
        :return:
        """
        if self._current_phase is not None:
            self._current_phase.on_destroy()

        if phase_type == 'game':
            self._current_phase = GamePhase(self, self._ui_manager)
        elif phase_type == 'main_menu':
            self._current_phase = MainMenuPhase(self, self._ui_manager)

        self._current_phase.initialise(**kwargs)

    def on_loop(self, dt):
        """
        Update GUI and phase
        :param dt:
        :return:
        """
        self._current_phase.update(dt)
        self._ui_manager.update(dt)

    def on_render(self):
        """
        Render GUI and current phase
        :return:
        """
        self._current_phase.draw(self._display_surf)
        self._ui_manager.draw(self._display_surf)

    def on_cleanup(self):
        """
        Cleanup resources
        :return:
        """
        self._ui_manager.clear_all_widgets()
        pygame.quit()

    def on_execute(self):
        """
        Starts main loop
        :return:
        """
        clock = pygame.time.Clock()
        if not self.on_init():
            self._running = False

        while self._running:
            for event in pygame.event.get():
                self.on_event(event)

            delta_time = clock.tick(60) / 1000.

            self.on_loop(delta_time)
            self.on_render()
            pygame.display.flip()

        self.on_cleanup()


if __name__ == "__main__":
    application = App()
    application.on_execute()
