import pygame
from pygame.math import Vector2

from pytowerdefence.UI import UIManager, GameWindow
from pytowerdefence.gameplay.AI import StandardAI
from pytowerdefence.gameplay.Action import ActionManager, GameActionButton
from pytowerdefence.gameplay.Logic import WaveManager
from pytowerdefence.gameplay.Monsters import Bandit
from pytowerdefence.gameplay.Objects import PLAYER_TEAM
from pytowerdefence.gameplay.Scene import Level, CreaturesFactory


class App:
    def __init__(self):
        self._running = True
        self._display_surf = None
        self.size = self.width, self.height = 1024, 768
        self._wave_manager = None
        self._ui_manager = None
        self._game_window = None
        self.level = None
        self._creatures_factory = None
        self._action_manager = None

    def on_init(self):
        pygame.init()
        self._ui_manager = UIManager()

        self._display_surf = pygame.display.set_mode(self.size, pygame.HWSURFACE | pygame.DOUBLEBUF)
        self._running = True
        self.level = Level(self.size)
        self.level.load("data/maps/test.tmx")
        self._creatures_factory = CreaturesFactory(self.level)

        self._wave_manager = WaveManager(factory=self._creatures_factory)
        self._wave_manager.load("data/test_wave.json")

        self._game_window = GameWindow(self.width, self.height)
        self._action_manager = ActionManager(self._game_window, self.level, self._creatures_factory)
        self._ui_manager.add_widget(self._game_window)
        self._ui_manager.focus_widget(self._game_window)

        static_actor = Bandit()
        static_actor.position = Vector2(877, 117)
        static_actor.set_ai(StandardAI())
        static_actor.statistics.team = PLAYER_TEAM
        self.level.add(static_actor)

        add_button = GameActionButton(img=pygame.image.load("data/add-button.png"), action_name="AddTower",
                                      action_manager=self._action_manager, tower='Bandit')
        add_button.position = Vector2(900, 650)
        self._ui_manager.add_widget(add_button)

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
        self._action_manager.update(dt)

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
