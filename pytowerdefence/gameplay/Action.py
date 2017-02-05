"""
Action module
"""
import pygame

from pytowerdefence.gameplay.Graphics import AttackRangeDrawer, HealthDrawer
from pytowerdefence.gameplay.Objects import PLAYER_TEAM
from pytowerdefence.gameplay.Scene import Camera, is_actor_in_player_team


class BaseAction:
    """
    Base class for action
    """
    def __init__(self, action_manager):
        self._action_manager = action_manager

    def perform(self, **kwargs):
        """
        Perform action
        :param kwargs:
        :return:
        """
        pass

    def is_continuous(self):
        """
        Returns true if action is continuous
        :return:
        """
        return False

    def is_allowed(self):
        """
        Return True if action is currently allowed
        :return:
        """
        return True


class BaseContinuousAction(BaseAction):
    """
    Base class for continuous actions
    """
    def is_continuous(self):
        return True

    def is_finished(self):
        """
        Returns true if action is finished
        :return:
        """
        return True

    def on_break(self):
        """
        Called when action is break
        :return:
        """
        pass


class ScrollingAction(BaseContinuousAction):
    """
    Default pending scrolling action
    """
    def __init__(self, action_manager):
        super().__init__(action_manager)
        self._attack_range_drawer = AttackRangeDrawer()
        self._health_drawer = HealthDrawer()

    def is_finished(self):
        return False

    def perform(self, **kwargs):
        self._action_manager.set_window_mediator(self)

    def on_break(self):
        self._action_manager.set_window_mediator(None)

    def on_mouse_click_event(self, event):
        """
        On mouse click event
        :param event:
        :return:
        """
        if event.type == pygame.MOUSEBUTTONUP:
            if self._attack_range_drawer.actor is not None:
                self._action_manager. \
                    create_and_start_action("GuardManaging",
                                            attack_range_drawer=self._attack_range_drawer)

    def on_mouse_motion_event(self, event):
        """
        On mouse motion event
        :param event:
        :return:
        """
        actor = self._action_manager.level.get_actor_on_position(
            Camera.to_world_position(event.pos))
        if actor is not None and is_actor_in_player_team(actor):
            self._attack_range_drawer.actor = actor
            self._health_drawer.actor = None
        elif actor is None:
            self._attack_range_drawer.actor = None
        else:
            self._health_drawer.actor = actor

    def draw(self, surface):
        """
        Draw
        :param surface:
        :return:
        """
        self._attack_range_drawer.draw(surface)
        self._health_drawer.draw(surface)


class GuardManagingAction(BaseContinuousAction):
    """
    Creating guard action
    """

    def __init__(self, action_manager, **kwargs):
        super().__init__(action_manager)
        self._attack_range_drawer = kwargs["attack_range_drawer"]

    def is_finished(self):
        return self._attack_range_drawer.actor is None

    def perform(self, **kwargs):
        self._action_manager.set_window_mediator(self)
        self._action_manager.ui_manager.get_by_id("guardian_panel").set_actor(
            self._attack_range_drawer.actor)

    def on_break(self):
        self._action_manager.set_window_mediator(None)
        self._action_manager.ui_manager.get_by_id("guardian_panel").set_actor(
            None)

    def draw(self, surface):
        """
        Draw needed elements
        :param surface:
        :return:
        """
        self._attack_range_drawer.draw(surface)

    def on_mouse_click_event(self, event):
        """
        On mouse click event
        :param event:
        :return:
        """
        if event.type == pygame.MOUSEBUTTONUP:
            world_pos = Camera.to_world_position(event.pos)
            clicked_actor = self._action_manager.level.get_actor_on_position(
                world_pos, is_actor_in_player_team)
            self._marked_actor_changed(clicked_actor)

    def _marked_actor_changed(self, actor):
        self._action_manager.ui_manager.get_by_id("guardian_panel").set_actor(
            actor)
        self._attack_range_drawer.actor = actor

    def on_mouse_motion_event(self, event):
        """
        On mouse motion event
        :param event:
        :return:
        """
        pass


class AddTowerAction(BaseContinuousAction):
    """
    Add tower action
    """

    def __init__(self, action_manager, tower):
        super().__init__(action_manager)
        self._tower_template_name = tower
        self._tower_cost = self._get_cost()
        self._finished = False
        self._colliding = True
        self._tower = None
        self._attack_range_drawer = None

    def perform(self, **kwargs):
        world_pos = Camera.to_world_position(kwargs['mouse_pos'])
        self._finished = False
        self._tower = self._action_manager.creatures_factory.create(
            self._tower_template_name)
        self._tower.update(0.0)
        self._tower.position = world_pos
        self._action_manager.set_window_mediator(self)
        self._attack_range_drawer = AttackRangeDrawer(self._tower)

    def _get_cost(self):
        factory = self._action_manager.creatures_factory
        properties = factory.get_creature_type_properties(
            self._tower_template_name)
        return properties['cost']

    def is_allowed(self):
        current_gold = self._action_manager.logic_manager.game_state.player_gold
        return current_gold >= self._tower_cost

    def is_finished(self):
        return self._finished

    def on_break(self):
        self._action_manager.set_window_mediator(None)

    def on_mouse_click_event(self, event):
        """
        On mouse click event
        :param event:
        :return:
        """
        if not self._colliding:
            self._action_manager.logic_manager.game_state.player_gold -= self._tower_cost
            self._action_manager.level.add(self._tower)
            self._action_manager.level.add_obstacle(self._tower)
            self._tower.team = PLAYER_TEAM
            self._tower = None
            self._finished = True
            self._action_manager.set_window_mediator(None)

    def on_mouse_motion_event(self, event):
        """
        On mouse motion event
        :param event:
        :return:
        """
        self._tower.position = Camera.to_world_position(event.pos)
        self._colliding = self._action_manager.level.is_rectangle_colliding(
            self._tower.rect)

    def draw(self, surface):
        """
        Draw needed elements
        :param surface:
        :return:
        """
        if self._tower is not None:
            self._attack_range_drawer.color = (255, 0, 0) if \
                self._colliding else (255, 255, 255)
            self._attack_range_drawer.draw(surface)
            surface.blit(self._tower.image, Camera.to_screen_position(
                [self._tower.rect.x, self._tower.rect.y]))


class ActionManager:
    """
    Action Manager
    """

    def __init__(self, game_window, level, creatures_factory, logic_manager,
                 ui_manager):
        self.game_window = game_window
        self._current_action = None
        self.level = level
        self.creatures_factory = creatures_factory
        self.logic_manager = logic_manager
        self.ui_manager = ui_manager
        self.create_and_start_action("Scrolling")

        self.game_window.action_manager = self

    def set_window_mediator(self, mediator):
        """
        Changes game window mediator
        :param mediator:
        :return:
        """
        self.game_window.mediator = mediator

    def create_and_start_action(self, name, **kwargs):
        """
        Creates and start action
        :param name:
        :param kwargs:
        :return:
        """
        action_created = self.create_action(name, **kwargs)
        return self.start_action(action_created)

    def start_action(self, action, **kwargs):
        """
        Start performing of action instance
        :param action:
        :param kwargs:
        :return:
        """
        if self.is_action_allowed(action):
            self.cancel_current_action()
            self._perform_action(action, **kwargs)
            return True
        return False

    def is_action_allowed(self, action):
        """
        Returns true if action is allowed
        :param action:
        :return:
        """
        return action.is_allowed()

    def update(self, dt):
        """
        Update action manager
        :param dt:
        :return:
        """
        if self._current_action is not None and \
                self._current_action.is_finished():
            self.create_and_start_action("Scrolling")

    def _perform_action(self, action, **kwargs):
        action.perform(**kwargs)
        if action.is_continuous():
            self._current_action = action

    def set_default_action(self):
        """
        Sets action to default
        :return:
        """
        self.cancel_current_action()
        self.create_and_start_action("Scrolling")

    def cancel_current_action(self):
        """
        Cancel current action
        :return:
        """
        if self._current_action is not None:
            self._current_action.on_break()
            self._current_action = None

    def create_action(self, name, **kwargs):
        """
        Create and return action instance
        :param name:
        :param kwargs:
        :return:
        """
        if name == 'Scrolling':
            return ScrollingAction(self)
        elif name == 'GuardManaging':
            return GuardManagingAction(self, **kwargs)
        else:
            return AddTowerAction(self, kwargs['tower'])
