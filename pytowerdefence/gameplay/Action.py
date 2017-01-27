from pygame.math import Vector2


class BaseAction:
    def perform(self, action_manager):
        pass

    def is_continuous(self):
        return False


class BaseContinuousAction(BaseAction):
    def is_continuous(self):
        return True

    def is_finished(self):
        return True


class AddTowerAction(BaseContinuousAction):
    def __init__(self, tower):
        self._tower = tower
        self._action_manager = None
        self._finished = False

    def perform(self, action_manager):
        self._action_manager = action_manager
        self._action_manager.set_window_mediator(self)

    def is_finished(self):
        return self._finished

    def on_break(self):
        self._action_manager.set_window_mediator(None)

    def on_mouse_click_event(self, event):
        pass

    def on_mouse_motion_event(self, event):
        self._tower.position = Vector2(event.pos)
        if self._action_manager.level.is_rectangle_colliding(self._tower.rect):
            print("Colliding")

    def draw(self, surface):
        if self._tower is not None:
            surface.blit(self._tower.image, [self._tower.rect.x, self._tower.rect.y])


class ActionManager:

    def __init__(self, game_window, level):
        self.game_window = game_window
        self._current_action = None
        self.level = level

    def set_window_mediator(self, mediator):
        self.game_window.mediator = mediator

    def start_action(self, name, **kwargs):
        if self._current_action is not None:
            self._current_action.on_break()
            self._current_action = None
        action_created = self._create_action(name, **kwargs)
        action_created.perform(self)
        if action_created.is_continuous():
            self._current_action = action_created

    def update(self, dt):
        if self._current_action is not None and self._current_action.is_finished():
            self._current_action = None

    def _create_action(self, name, **kwargs):
        return AddTowerAction(kwargs['tower'])