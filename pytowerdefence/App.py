import pygame

from pytowerdefence.Game import Game
from pytowerdefence.UI import UIManager


class App:
    def __init__(self):
        self._running = True
        self._display_surf = None
        self.size = self.width, self.height = 1024, 768
        self._game = None
        self._ui_manager = None

    def on_init(self):
        pygame.init()
        self._display_surf = pygame.display.set_mode(
            self.size, pygame.HWSURFACE | pygame.DOUBLEBUF)

        self._ui_manager = UIManager(self.size)

        self._running = True
        self._game = Game(self._ui_manager)
        self._game.start("data/maps/test.tmx")

    def on_event(self, event):
        if event.type == pygame.QUIT:
            self._running = False
        else:
            self._ui_manager.process_event(event)

    def on_loop(self, dt):
        self._game.update(dt)
        self._ui_manager.update(dt)

    def on_render(self):
        self._game.draw(self._display_surf)
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
