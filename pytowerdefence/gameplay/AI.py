from pytowerdefence.gameplay.Controllers import AttackController
from pytowerdefence.gameplay.Objects import ActorState


class BaseAI:
    def __init__(self):
        self._actor = None

    def set_actor(self, actor):
        self._actor = actor

    def update(self, dt):
        pass


class StandardAI(BaseAI):
    def __init__(self, debug=False):
        super().__init__()
        self._debug = debug

    def update(self, dt):
        if self._actor.state != ActorState.ATTACK:
            for t in self._actor.actors_in_attack_range:
                if t.statistics.team != self._actor.statistics.team and \
                                t.state != ActorState.DEATH:
                    controller = self._actor.get_controller(AttackController)
                    if controller is not None:
                        if self._debug:
                            print("Setting controller target to", t)
                        controller.target = t
                        break
