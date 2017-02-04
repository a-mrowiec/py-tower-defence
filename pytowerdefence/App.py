import pygame

from pytowerdefence.UI import UIManager
from pytowerdefence.gameplay.GamePhase import GamePhase
from pytowerdefence.mainmenu.MainMenuPhase import MainMenuPhase


class App:
    def __init__(self):
        self._running = True
        self._display_surf = None
        self.size = self.width, self.height = 1024, 768
        self._current_phase = None
        self._ui_manager = None

    def on_init(self):
        pygame.init()
        self._display_surf = pygame.display.set_mode(
            self.size, pygame.HWSURFACE | pygame.DOUBLEBUF)

        self._ui_manager = UIManager(self.size)

        self._running = True
        self.set_phase('main_menu')

    def on_event(self, event):
        if event.type == pygame.QUIT:
            self._running = False
        else:
            self._ui_manager.process_event(event)

    def set_phase(self, type, **kwargs):
        if self._current_phase is not None:
            self._current_phase.on_destroy()

        if type == 'game':
            self._current_phase = GamePhase(self, self._ui_manager)
        elif type == 'main_menu':
            self._current_phase = MainMenuPhase(self, self._ui_manager)

        self._current_phase.initialise(**kwargs)

    def on_loop(self, dt):
        self._current_phase.update(dt)
        self._ui_manager.update(dt)

    def on_render(self):
        self._current_phase.draw(self._display_surf)
        self._ui_manager.draw(self._display_surf)

    def on_cleanup(self):
        pygame.quit()

    def on_execute(self):
        clock = pygame.time.Clock()
        if self.on_init() == False:
            self._running = False

        while self._running:
            for event in pygame.event.get():
                self.on_event(event)

            dt = clock.tick(60) / 1000.

            self.on_loop(dt)
            self.on_render()
            pygame.display.flip()

        self.on_cleanup()


if __name__ == "__main__":
    app = App()
    app.on_execute()
