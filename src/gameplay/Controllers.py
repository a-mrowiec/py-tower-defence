from pygame.math import Vector2

from src.gameplay.Actor import ActorState


class BaseController:
    def __init__(self):
        self._actor = None

    def set_actor(self, actor):
        self._actor = actor

    def update(self, dt):
        pass

    def on_animation_end(self):
        pass

    def stop(self):
        pass


class PathController(BaseController):
    def __init__(self):
        super().__init__()
        self.path = []
        self.current_path_point = 0
        self.finished = False
        self.path_vector = Vector2()

    def set_path(self, path):
        self.path = path
        self.current_path_point = 0
        self.finished = False

    def update(self, dt):
        super().update(dt)
        if self.path and not self.finished:
            self._actor.go_to_direction(self.path[self.current_path_point] - self._actor.position)
            to_goal_vector = self._actor.position - self.path[self.current_path_point]
            dot = self.path_vector.dot(to_goal_vector)
            if dot < 0:
                self.current_path_point += 1
                if self.current_path_point >= len(self.path):
                    self.finished = True
                    self._actor.stop()
                else:
                    self._on_path_point_change()

    def set_actor(self, actor):
        super().set_actor(actor)
        self._on_path_point_change()

    def stop(self):
        super().stop()
        self.finished = True

    def _on_path_point_change(self):
        self.path_vector = self._actor.position - self.path[self.current_path_point]


class AttackController(BaseController):
    def __init__(self):
        super().__init__()
        self._target = None

    @property
    def target(self):
        return self._target

    @target.setter
    def target(self, value):
        self._target = value

    def update(self, dt):
        super().update(dt)
        if self._actor._state != ActorState.ATTACK:
            if self._target in self._actor.actors_in_attack_range:
                self._actor._change_state(ActorState.ATTACK)

    def on_animation_end(self):
        if self._target is not None:
            self._target.hit(self._actor.statistics.attack)


class DeathController(BaseController):
    def on_animation_end(self):
        if self._actor._state == ActorState.DEATH:
            self._actor.kill()