from pygame.math import Vector2


class BaseController:
    _actor = None

    def set_actor(self, actor):
        self._actor = actor

    def update(self, dt):
        pass


class PathController(BaseController):
    path = []
    current_path_point = 0
    path_vector = Vector2()

    def set_path(self, path):
        self.path = path
        self.current_path_point = 0

    def update(self, dt):
        super().update(dt)
        if self.path:
            self._actor.velocity = self.path[self.current_path_point] - self._actor.position
            to_goal_vector = self._actor.position - self.path[self.current_path_point]
            dot = self.path_vector.dot(to_goal_vector)
            if dot < 0:
                self.current_path_point = (self.current_path_point+1) % len(self.path)
                self._on_path_point_change()

    def set_actor(self, actor):
        super().set_actor(actor)
        self._on_path_point_change()

    def _on_path_point_change(self):
        self.path_vector = self._actor.position - self.path[self.current_path_point]