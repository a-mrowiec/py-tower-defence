import copy
from pytowerdefence.Resources import ResourceClass, ResourceManager
from pytowerdefence.gameplay.AI import StandardAI
from pytowerdefence.gameplay.Controllers import PathController, DeathController, \
    RangeAttackController, AttackController
from pytowerdefence.gameplay.Objects import Actor, ActorState, EvolvingActor


class Ogre(Actor):
    def __init__(self):
        super().__init__()

        self.set_animation(ActorState.IDLE, ResourceManager.load_animation(
            ResourceClass.CHARACTERS, 'ogre-move.json'))
        self.set_animation(ActorState.MOVE, ResourceManager.load_animation(
            ResourceClass.CHARACTERS, 'ogre-move.json'))
        self.set_animation(ActorState.ATTACK, ResourceManager.load_animation(
            ResourceClass.CHARACTERS, 'ogre-attack.json'))
        self.set_animation(ActorState.DEATH, ResourceManager.load_animation(
            ResourceClass.CHARACTERS, 'ogre-death.json'))

        self.base_statistics.speed = 50
        self.base_statistics.attack_range = 2
        self.base_statistics.attack_damage = 1
        self.base_statistics.max_health = self.hp = 100
        self.recalculate_statistics()
        self.change_state(ActorState.MOVE)

        self.rect.width = 64
        self.rect.height = 64
        self.add_controller(DeathController())
        self.add_controller(AttackController())
        self.add_controller(PathController())
        self.set_ai(StandardAI())


class Dragon(Actor):
    def __init__(self):
        super().__init__()

        self.set_animation(ActorState.IDLE, ResourceManager.load_animation(
            ResourceClass.CHARACTERS, 'dragon-move.json'))
        self.set_animation(ActorState.MOVE, ResourceManager.load_animation(
            ResourceClass.CHARACTERS, 'dragon-move.json'))
        self.set_animation(ActorState.ATTACK, ResourceManager.load_animation(
            ResourceClass.CHARACTERS, 'dragon-attack.json'))
        self.set_animation(ActorState.DEATH, ResourceManager.load_animation(
            ResourceClass.CHARACTERS, 'dragon-death.json'))

        self.base_statistics.speed = 50
        self.base_statistics.attack_range = 2
        self.base_statistics.attack_damage = 1
        self.base_statistics.max_health = self.hp = 1000
        self.recalculate_statistics()
        self.change_state(ActorState.MOVE)

        self.rect.width = 128
        self.rect.height = 128
        self.add_controller(DeathController())
        self.add_controller(AttackController())
        self.add_controller(PathController())
        self.set_ai(StandardAI())


class Bandit(EvolvingActor):
    def __init__(self):
        super().__init__()

        self.set_animation(ActorState.MOVE, ResourceManager.load_animation(
            ResourceClass.CHARACTERS, 'bandit-move.json'))
        self.set_animation(ActorState.IDLE, ResourceManager.load_animation(
            ResourceClass.CHARACTERS, 'bandit-idle.json'))
        self.set_animation(ActorState.ATTACK, ResourceManager.load_animation(
            ResourceClass.CHARACTERS, 'bandit-attack.json'))
        self.set_animation(ActorState.DEATH, ResourceManager.load_animation(
            ResourceClass.CHARACTERS, 'bandit-death.json'))

        self.base_statistics.speed = 50
        self.base_statistics.attack_range = 100
        self.base_statistics.attack_damage = 15
        self.base_statistics.bullet_speed = 1000
        self.base_statistics.bullet_image = 'small-knife.png'
        self.base_statistics.max_health = self.hp = 100
        self.recalculate_statistics()
        self._play_current_animation()

        self.rect.width = 64
        self.rect.height = 64
        self.add_controller(DeathController())
        self.add_controller(RangeAttackController())
        self.add_controller(PathController())

        self.set_ai(StandardAI(debug=True))

        stats=copy.deepcopy(self._base_statistics)
        stats.attack_damage += 15
        self.add_evolution_level(stats,None)

        stats=copy.deepcopy(stats)
        stats.attack_range += 200
        self.add_evolution_level(stats, None)
