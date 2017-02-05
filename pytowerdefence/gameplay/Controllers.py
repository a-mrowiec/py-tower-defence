"""
Controller module
"""
from pygame.math import Vector2

from pytowerdefence.gameplay.Objects import Bullet, ActorState, \
    add_effects_to_actor


class BaseController:
    """
    Base class for any controller
    """

    def __init__(self):
        self._actor = None

    def need_update(self):
        """
        Returns True if controller need update
        :return:
        """
        return False

    def on_update_end(self):
        """
        Called when higher priority controller take control of actor
        :return:
        """
        pass

    def set_actor(self, actor):
        """
        Set actor
        :param actor:
        :return:
        """
        self._actor = actor

    def update(self, dt):
        """
        Update controller
        :param dt:
        :return:
        """
        pass

    def on_animation_end(self):
        """
        Called when animation is ended
        :return:
        """
        pass

    def stop(self):
        """
        Stop updating controller
        :return:
        """
        pass


class PathController(BaseController):
    """
    Controller which drives monster at specific path
    """

    def __init__(self):
        super().__init__()
        self.path = []
        self._current_path_point = 0
        self.finished = False
        self.path_vector = Vector2()

    def set_path(self, path):
        """
        Set path
        :param path:
        :return:
        """
        self.path = path
        self._current_path_point = 0
        self.finished = False
        self._on_path_point_change()

    @property
    def current_path_point(self):
        """
        Current path point which is the target
        :return:
        """
        return self._current_path_point

    @current_path_point.setter
    def current_path_point(self, value):
        self._current_path_point = value
        self._on_path_point_change()

    def need_update(self):
        return self.path and not self.finished

    def update(self, dt):
        self._actor.go_to_direction(
            self.path[self._current_path_point] - self._actor.position)
        to_goal_vector = self._actor.position - self.path[
            self._current_path_point]
        dot = self.path_vector.dot(to_goal_vector)
        if dot < 0:
            self._current_path_point += 1
            if self._current_path_point >= len(self.path):
                self.finished = True
                self._actor.stop()
            else:
                self._on_path_point_change()

    def on_update_end(self):
        self._actor.zero_velocity()

    def set_actor(self, actor):
        super().set_actor(actor)
        self._on_path_point_change()

    def stop(self):
        super().stop()
        self.finished = True

    def _on_path_point_change(self):
        if len(self.path) > 0:
            self.path_vector = self._actor.position - self.path[
                self._current_path_point]


class AttackController(BaseController):
    """
    Standard attack controller
    """

    def __init__(self):
        super().__init__()
        self._target = None

    @property
    def target(self):
        """
        Target
        :return:
        """
        return self._target

    @target.setter
    def target(self, value):
        self._target = value
        if self._actor.state != ActorState.ATTACK:
            if self._target in self._actor.actors_in_attack_range:
                self._on_target_in_range()

    def _on_target_in_range(self):
        self._actor.rotate_to_direction(
            self._target.position - self._actor.position)
        self._actor.change_state(ActorState.ATTACK)
        self._actor.zero_velocity()

    def need_update(self):
        return self._actor.state == ActorState.ATTACK

    def _process_animation_end(self):
        add_effects_to_actor(self._target, self._actor.statistics.hit_effects)
        self._actor.change_state(ActorState.IDLE)

    def on_animation_end(self):
        if self._target is not None:
            self._process_animation_end()


class RangeAttackController(AttackController):
    """
    Controller for range attack
    """

    def __init__(self):
        super().__init__()
        self._bullet = None

    def _process_animation_end(self):
        if self._bullet is None or not self._bullet.alive:
            self._bullet = Bullet(self._actor)
            self._bullet.position = self._actor.position
            self._bullet.target = self._target
            self._actor.objects_to_create.append(self._bullet)


class NotRotatingRangeAttackController(RangeAttackController):
    """
    Range attack controller, which won't turn toward target
    """

    def _on_target_in_range(self):
        self._actor.change_state(ActorState.ATTACK)


class DeathController(BaseController):
    """
    Death controller
    """

    def need_update(self):
        return self._actor.state == ActorState.DEATH

    def on_animation_end(self):
        if self._actor.state == ActorState.DEATH:
            self._actor.kill()
