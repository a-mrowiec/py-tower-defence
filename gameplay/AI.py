from gameplay.Actor import ActorState
from gameplay.Controllers import AttackController


class BaseAI:
    def __init__(self):
        self._actor = None

    def set_actor(self, actor):
        self._actor = actor

    def update(self, dt):
        pass


class StandardAI(BaseAI):
    def __init__(self):
        super().__init__()

    def update(self, dt):
        if self._actor.state != ActorState.ATTACK:
            for t in self._actor.actors_in_attack_range:
                if t.statistics.team != self._actor.statistics.team:
                    controller = self._actor.get_controller(AttackController)
                    if controller is not None:
                        controller.target = t
                        break