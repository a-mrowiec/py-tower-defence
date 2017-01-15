import pygame
from src.gameplay.AI import StandardAI
from src.gameplay.Controllers import PathController, AttackController, DeathController
from src.gameplay.Logic import WaveManager
from src.gameplay.Scene import Level
from pygame.math import Vector2

from src.gameplay.Monsters import Ogre, Bandit


class App:
    def __init__(self):
        self._running = True
        self._display_surf = None
        self.size = self.width, self.height = 1024, 768
        self._wave_manager = None

    def on_init(self):
        pygame.init()
        self._display_surf = pygame.display.set_mode(self.size, pygame.HWSURFACE | pygame.DOUBLEBUF)
        self._running = True
        self.level = Level(self.size)
        self.level.load("data/maps/test.tmx")

        self._wave_manager = WaveManager(level=self.level)
        self._wave_manager.load("data/test_wave.json")

        actor = Ogre()
        actor.position = Vector2(10, 10)
        path_controller=PathController()
        path_controller.set_path(self.level.paths[0])
        actor.add_controller(path_controller)
        actor.add_controller(DeathController())


        static_actor = Bandit()
        static_actor.position = Vector2(350, 400)
        attack_controller=AttackController()
        static_actor.add_controller(attack_controller)
        static_actor.add_controller(DeathController())
        static_actor.set_ai(StandardAI())
        static_actor.statistics.team = 1
        self.level.add(static_actor)
        self.level.add(actor)

    def on_event(self, event):
        if event.type == pygame.QUIT:
            self._running = False

    def on_loop(self, dt):
        if self._wave_manager is not None:
            self._wave_manager.update(dt)
        self.level.update(dt)

    def on_render(self):
        self.level.draw(self._display_surf)

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