import pygame
from pygame.math import Vector2

from pytowerdefence.UI import UIManager, Text, GameWindow
from pytowerdefence.gameplay.AI import StandardAI
from pytowerdefence.gameplay.Controllers import PathController
from pytowerdefence.gameplay.Logic import WaveManager
from pytowerdefence.gameplay.Monsters import Ogre, Bandit
from pytowerdefence.gameplay.Scene import Level


class App:
    def __init__(self):
        self._running = True
        self._display_surf = None
        self.size = self.width, self.height = 1024, 768
        self._wave_manager = None
        self._ui_manager = None

    def on_init(self):
        pygame.init()
        self._ui_manager = UIManager()
        self._ui_manager.add_widget(Text("Testowy tekst"))
        self._display_surf = pygame.display.set_mode(self.size, pygame.HWSURFACE | pygame.DOUBLEBUF)
        self._running = True
        self.level = Level(self.size)
        self.level.load("data/maps/test.tmx")

        self._wave_manager = WaveManager(level=self.level)
        self._wave_manager.load("data/test_wave.json")

        self._ui_manager.add_widget(GameWindow(self.level, self.width, self.height))

        actor = Ogre()
        actor.position = Vector2(10, 10)
        path_controller = actor.get_controller(PathController)
        path_controller.set_path(self.level.paths[0])

        static_actor = Bandit()
        static_actor.position = Vector2(350, 400)
        static_actor.set_ai(StandardAI())
        static_actor.statistics.team = 1
        self.level.add(static_actor)
        self.level.add(actor)

    def on_event(self, event):
        if event.type == pygame.QUIT:
            self._running = False
        else:
            self._ui_manager.process_event(event)

    def on_loop(self, dt):
        if self._wave_manager is not None:
            self._wave_manager.update(dt)
        self.level.update(dt)
        self._ui_manager.update(dt)

    def on_render(self):
        self.level.draw(self._display_surf)
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
