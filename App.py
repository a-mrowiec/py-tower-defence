import pygame
from pygame.math import Vector2

from gameplay.Actor import OgreActor, BanditActor
from gameplay.Controllers import PathController, AttackController
from gameplay.Scene import Level


class App:
    def __init__(self):
        self._running = True
        self._display_surf = None
        self.size = self.width, self.height = 1024, 768

    def on_init(self):
        pygame.init()
        self._display_surf = pygame.display.set_mode(self.size, pygame.HWSURFACE | pygame.DOUBLEBUF)
        self._running = True
        self.level = Level(self.size)
        self.level.load("data/maps/test.tmx")
        actor = OgreActor()
        actor.position = Vector2(10, 10)
        path_controller=PathController()
        path_controller.set_path(self.level.paths[0])
        actor.add_controller(path_controller)


        static_actor = BanditActor()
        static_actor.position = Vector2(350, 400)
        attack_controller=AttackController()
        attack_controller.target = actor
        static_actor.add_controller(attack_controller)

        self.level.add(static_actor)
        self.level.add(actor)

    def on_event(self, event):
        if event.type == pygame.QUIT:
            self._running = False

    def on_loop(self, dt):
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