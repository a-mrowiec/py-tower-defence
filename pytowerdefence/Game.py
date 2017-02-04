from pygame.math import Vector2

from pytowerdefence.Resources import ResourceManager, ResourceClass
from pytowerdefence.UI import PositionAttachType
from pytowerdefence.gameplay.Action import ActionManager
from pytowerdefence.gameplay.Logic import LogicManager, WaveManager
from pytowerdefence.gameplay.LogicalEffects import LogicEffectManager
from pytowerdefence.gameplay.Scene import Level, CreaturesFactory
from pytowerdefence.gameplay.Widgets import GameWindow, GameActionButton, \
    GuardianPanel, PlayerInfoPanel, PlayerHealthPanel


class Game:
    def __init__(self, ui_manager):
        self._ui_manager = ui_manager
        self._wave_manager = None
        self._game_window = None
        self.level = None
        self._creatures_factory = None
        self._action_manager = None
        self._logic_manager = None
        self._logical_effect_manager = None

    def start(self, map_file):
        self._logic_manager = LogicManager()
        self.level = Level(self._ui_manager.window_size, self._logic_manager)
        self.level.load(map_file)
        self._creatures_factory = CreaturesFactory(self.level)

        self._wave_manager = WaveManager(factory=self._creatures_factory)
        self._wave_manager.load("data/test_wave.json")

        self._game_window = GameWindow(self._ui_manager.window_size.x,
                                       self._ui_manager.window_size.y)
        self._action_manager = ActionManager(self._game_window, self.level,
                                             self._creatures_factory,
                                             self._logic_manager,
                                             self._ui_manager)
        self._ui_manager.add_widget(self._game_window)
        self._ui_manager.focus_widget(self._game_window)

        self._logical_effect_manager = LogicEffectManager(self.level)

        add_button = GameActionButton(
            img=ResourceManager.load_image(ResourceClass.UI, 'add-button.png'),
            action_name="AddTower",
            action_manager=self._action_manager, tower='Bandit')
        add_button.position = Vector2(900, 650)
        self._ui_manager.add_widget(add_button)

        panel = GuardianPanel(self._logic_manager)
        panel.position = Vector2(375, 536)
        self._ui_manager.add_widget(panel)
        self._ui_manager.add_widget(PlayerInfoPanel(self._logic_manager))
        health_panel = PlayerHealthPanel(self.level.base)
        health_panel.position_attach_type = PositionAttachType.CENTER
        health_panel.position = Vector2(self._ui_manager.window_size.x / 2, 35)
        self._ui_manager.add_widget(health_panel)

    def update(self, dt):
        if self._wave_manager is not None:
            self._wave_manager.update(dt)
        self.level.update(dt)
        self._logic_manager.update(dt)
        self._action_manager.update(dt)
        self._logical_effect_manager.update(dt)

    def draw(self, surface):
        self.level.draw(surface)
