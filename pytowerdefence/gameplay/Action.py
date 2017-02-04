import pygame

from pytowerdefence.gameplay.Graphics import AttackRangeDrawer, HealthDrawer
from pytowerdefence.gameplay.Objects import PLAYER_TEAM
from pytowerdefence.gameplay.Scene import Camera, is_actor_in_player_team


class BaseAction:
    def __init__(self, action_manager):
        self._action_manager = action_manager

    def perform(self):
        pass

    def is_continuous(self):
        return False

    def is_allowed(self):
        return True


class BaseContinuousAction(BaseAction):
    def is_continuous(self):
        return True

    def is_finished(self):
        return True

    def on_break(self):
        pass


class ScrollingAction(BaseContinuousAction):
    def __init__(self, action_manager):
        super().__init__(action_manager)
        self._attack_range_drawer = AttackRangeDrawer()
        self._health_drawer = HealthDrawer()

    def is_finished(self):
        return False

    def perform(self):
        self._action_manager.set_window_mediator(self)

    def on_break(self):
        self._action_manager.set_window_mediator(None)

    def on_mouse_click_event(self, event):
        if event.type == pygame.MOUSEBUTTONUP:
            if self._attack_range_drawer.actor is not None:
                self._action_manager.\
                    create_and_start_action("TowerManaging",
                                            attack_range_drawer=self._attack_range_drawer)

    def on_mouse_motion_event(self, event):
        actor = self._action_manager.level.get_actor_on_position(
            Camera.to_world_position(event.pos))
        if actor is not None and is_actor_in_player_team(actor):
            self._attack_range_drawer.actor = actor
            self._health_drawer.actor = None
        elif actor is None:
            self._attack_range_drawer._actor = None
        else:
            self._health_drawer.actor = actor

    def draw(self, surface):
        self._attack_range_drawer.draw(surface)
        self._health_drawer.draw(surface)


class TowerManagingAction(BaseContinuousAction):
    def __init__(self, action_manager, **kwargs):
        super().__init__(action_manager)
        self._attack_range_drawer = kwargs["attack_range_drawer"]

    def is_finished(self):
        return self._attack_range_drawer.actor is None

    def perform(self):
        self._action_manager.set_window_mediator(self)
        self._action_manager.ui_manager.get_by_id("guardian_panel").set_actor(self._attack_range_drawer.actor)

    def on_break(self):
        self._action_manager.set_window_mediator(None)
        self._action_manager.ui_manager.get_by_id("guardian_panel").set_actor(None)

    def draw(self, surface):
        self._attack_range_drawer.draw(surface)

    def on_mouse_click_event(self, event):
        if event.type == pygame.MOUSEBUTTONUP:
            world_pos = Camera.to_world_position(event.pos)
            clicked_actor = self._action_manager.level.get_actor_on_position(
                world_pos, is_actor_in_player_team)
            self._marked_actor_changed(clicked_actor)

    def _marked_actor_changed(self, actor):
        self._action_manager.ui_manager.get_by_id("guardian_panel").set_actor(actor)
        self._attack_range_drawer.actor = actor

    def on_mouse_motion_event(self, event):
        pass


class AddTowerAction(BaseContinuousAction):
    def __init__(self, action_manager, tower, **kwargs):
        super().__init__(action_manager)
        self._tower_template_name = tower
        self._finished = False
        self._colliding = True
        self._tower = None
        self._attack_range_drawer = None

    def perform(self):
        self._finished = False
        self._tower = self._action_manager.creatures_factory.create(
            self._tower_template_name)
        self._tower.update(0.0)
        self._action_manager.set_window_mediator(self)
        self._attack_range_drawer = AttackRangeDrawer(self._tower)

    def is_allowed(self):
        return False

    def is_finished(self):
        return self._finished

    def on_break(self):
        self._action_manager.set_window_mediator(None)

    def on_mouse_click_event(self, event):
        if not self._colliding:
            self._action_manager.level.add(self._tower)
            self._action_manager.level.add_obstacle(self._tower)
            self._tower.team = PLAYER_TEAM
            self._tower = None
            self._finished = True
            self._action_manager.set_window_mediator(None)

    def on_mouse_motion_event(self, event):
        self._tower.position = Camera.to_world_position(event.pos)
        self._colliding = self._action_manager.level.is_rectangle_colliding(
            self._tower.rect)

    def draw(self, surface):
        if self._tower is not None:
            self._attack_range_drawer.color = (255, 0, 0) if \
                self._colliding else (255, 255, 255)
            self._attack_range_drawer.draw(surface)
            surface.blit(self._tower.image, Camera.to_screen_position(
                [self._tower.rect.x, self._tower.rect.y]))


class ActionManager:
    def __init__(self, game_window, level, creatures_factory, logic_manager, ui_manager):
        self.game_window = game_window
        self._current_action = None
        self.level = level
        self.creatures_factory = creatures_factory
        self.logic_manager = logic_manager
        self.ui_manager = ui_manager
        self.create_and_start_action("Scrolling")

    def set_window_mediator(self, mediator):
        self.game_window.mediator = mediator

    def create_and_start_action(self, name, **kwargs):
        action_created = self.create_action(name, **kwargs)
        return self.start_action(action_created)

    def start_action(self, action):
        if self.is_action_allowed(action):
            self._stop_other_action()
            self._perform_action(action)
            return True
        return False

    def is_action_allowed(self, action):
        return action.is_allowed()

    def update(self, dt):
        if self._current_action is not None and \
                self._current_action.is_finished():
            self.create_and_start_action("Scrolling")

    def _perform_action(self, action):
        action.perform()
        if action.is_continuous():
            self._current_action = action

    def _stop_other_action(self):
        if self._current_action is not None:
            self._current_action.on_break()
            self._current_action = None

    def create_action(self, name, **kwargs):
        if name == 'Scrolling':
            return ScrollingAction(self)
        elif name == 'TowerManaging':
            return TowerManagingAction(self, **kwargs)
        else:
            return AddTowerAction(self, kwargs['tower'])
