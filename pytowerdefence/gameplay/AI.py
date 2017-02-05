"""
AI module
"""
from pytowerdefence.gameplay.Controllers import AttackController
from pytowerdefence.gameplay.Objects import ActorState


class BaseAI:
    """
    Base class for AI
    """
    def __init__(self):
        self._actor = None

    def set_actor(self, actor):
        """
        Set actor
        :param actor:
        :return:
        """
        self._actor = actor

    def update(self, dt):
        """
        Update AI
        :param dt:
        :return:
        """
        pass


class StandardAI(BaseAI):
    """
    Standard AI which attacks first visible enemy
    """
    def __init__(self, debug=False):
        super().__init__()
        self._debug = debug

    def update(self, dt):
        if self._actor.state != ActorState.DEATH:
            for target in self._actor.actors_in_attack_range:
                if self._target_filter(target):
                    controller = self._actor.get_controller(AttackController)
                    if controller is not None:
                        if self._debug:
                            print("Setting controller target to", target)
                        controller.target = target
                        break

    def _target_filter(self, target):
        return target.team != self._actor.team \
               and target.state != ActorState.DEATH


class AttackOnlyBase(StandardAI):
    """
    Monster attacks only base
    """

    def _target_filter(self, target):
        return super()._target_filter(target) \
               and target.class_properties['name'] == 'Base'
