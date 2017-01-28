from pytowerdefence.Resources import ResourceClass, ResourceManager
from pytowerdefence.gameplay.AI import StandardAI
from pytowerdefence.gameplay.Controllers import PathController, DeathController, \
    RangeAttackController, AttackController
from pytowerdefence.gameplay.Objects import Actor, ActorState


class Ogre(Actor):
    def __init__(self):
        super().__init__()
        self._statistics.speed = 50

        self.set_animation(ActorState.IDLE, ResourceManager.load_animation(
            ResourceClass.CHARACTERS, 'ogre-move.json'))
        self.set_animation(ActorState.MOVE, ResourceManager.load_animation(
            ResourceClass.CHARACTERS, 'ogre-move.json'))
        self.set_animation(ActorState.ATTACK, ResourceManager.load_animation(
            ResourceClass.CHARACTERS, 'ogre-attack.json'))
        self.set_animation(ActorState.DEATH, ResourceManager.load_animation(
            ResourceClass.CHARACTERS, 'ogre-death.json'))

        self.statistics.attack_range = 2
        self.statistics.attack_damage = 1
        self.statistics.max_health = self.statistics.current_health = 100
        self.change_state(ActorState.MOVE)

        self.rect.width = 64
        self.rect.height = 64
        self.add_controller(DeathController())
        self.add_controller(AttackController())
        self.add_controller(PathController())
        self.set_ai(StandardAI())


class Bandit(Actor):
    def __init__(self):
        super().__init__()
        self._statistics.speed = 50

        self.set_animation(ActorState.MOVE, ResourceManager.load_animation(
            ResourceClass.CHARACTERS, 'bandit-move.json'))
        self.set_animation(ActorState.IDLE, ResourceManager.load_animation(
            ResourceClass.CHARACTERS, 'bandit-idle.json'))
        self.set_animation(ActorState.ATTACK, ResourceManager.load_animation(
            ResourceClass.CHARACTERS, 'bandit-attack.json'))
        self.set_animation(ActorState.DEATH, ResourceManager.load_animation(
            ResourceClass.CHARACTERS, 'bandit-death.json'))

        self.statistics.attack_range = 100
        self.statistics.attack_damage = 1
        self._play_current_animation()

        self.rect.width = 64
        self.rect.height = 64
        self.add_controller(DeathController())
        self.add_controller(RangeAttackController())
        self.add_controller(PathController())

        self.set_ai(StandardAI(debug=True))
