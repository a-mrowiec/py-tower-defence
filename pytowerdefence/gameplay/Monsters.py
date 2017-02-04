import copy

from pytowerdefence.Resources import ResourceClass, ResourceManager
from pytowerdefence.gameplay.AI import StandardAI, AttackOnlyBase
from pytowerdefence.gameplay.Controllers import PathController, DeathController, \
    RangeAttackController, AttackController, NotRotatingRangeAttackController
from pytowerdefence.gameplay.Objects import ActorState, EvolvingActor, Actor


def set_animations(actor, animation_name_prefix):
    actor.set_animation(ActorState.IDLE, ResourceManager.load_animation(
        ResourceClass.CHARACTERS, animation_name_prefix + '-idle.json'))
    actor.set_animation(ActorState.MOVE, ResourceManager.load_animation(
        ResourceClass.CHARACTERS, animation_name_prefix + '-move.json'))
    actor.set_animation(ActorState.ATTACK, ResourceManager.load_animation(
        ResourceClass.CHARACTERS, animation_name_prefix + '-attack.json'))
    actor.set_animation(ActorState.DEATH, ResourceManager.load_animation(
        ResourceClass.CHARACTERS, animation_name_prefix + '-death.json'))


class Ogre(Actor):
    PROPERTIES = {'gold_gain': 25, 'name': 'Ogre'}

    def __init__(self):
        super().__init__(Ogre.PROPERTIES)

        set_animations(self, 'ogre')

        self.base_statistics.speed = 50
        self.base_statistics.attack_range = 2
        self.base_statistics.max_health = self.hp = 100
        self.base_statistics.hit_effects = [('HitEffect', {'damage': 1})]
        self.recalculate_statistics()
        self.change_state(ActorState.MOVE)

        self.rect.width = 64
        self.rect.height = 64
        self.add_controller(DeathController())
        self.add_controller(AttackController())
        self.add_controller(PathController())
        self.set_ai(AttackOnlyBase())


class Dragon(Actor):
    PROPERTIES = {'name': 'Dragon', 'gold_gain': 500}

    def __init__(self):
        super().__init__(Dragon.PROPERTIES)

        set_animations(self, 'dragon')

        self.base_statistics.speed = 50
        self.base_statistics.attack_range = 100
        self.base_statistics.bullet_image = 'flaming-arrow.png'
        self.base_statistics.bullet_speed = 200
        self.base_statistics.hit_effects = [('HitEffect', {'damage': 1})]
        self.base_statistics.max_health = self.hp = 1000
        self.recalculate_statistics()
        self.change_state(ActorState.MOVE)

        self.rect.width = 128
        self.rect.height = 128
        self.add_controller(DeathController())
        self.add_controller(RangeAttackController())
        self.add_controller(PathController())
        self.set_ai(AttackOnlyBase())


class Base(EvolvingActor):
    PROPERTIES = {'name': 'Base'}

    def __init__(self):
        super().__init__(Base.PROPERTIES)
        set_animations(self, 'base')

        self.base_statistics.speed = 0
        self.base_statistics.attack_range = 100
        self.base_statistics.hit_effects = [('HitEffect', {'damage': 50})]
        self.base_statistics.bullet_speed = 500
        self.base_statistics.bullet_image = 'small-knife.png'
        self.base_statistics.max_health = self.hp = 1000
        self.recalculate_statistics()
        self._play_current_animation()

        self.rect.width = 64
        self.rect.height = 64

        self.add_controller(DeathController())
        self.add_controller(NotRotatingRangeAttackController())

        self.set_ai(StandardAI())

        stats = copy.deepcopy(self._base_statistics)
        stats.hit_effects = [('HitEffect', {'damage': 70}),
                             ('SlowEffect', {'time': 1, 'percent': 0.8})]
        self.add_evolution_level(stats, 1000, {ActorState.ATTACK,
                                               ResourceManager.load_animation(
                                                   ResourceClass.CHARACTERS,
                                                   'base-attack-1.json')})


class Bandit(EvolvingActor):
    PROPERTIES = {'name': 'Bandit', 'cost': 50}

    def __init__(self):
        super().__init__(Bandit.PROPERTIES)

        set_animations(self, 'bandit')

        self.base_statistics.speed = 50
        self.base_statistics.attack_range = 100
        self.base_statistics.hit_effects = [('HitEffect', {'damage': 15})]
        self.base_statistics.bullet_speed = 200
        self.base_statistics.bullet_image = 'small-knife.png'
        self.base_statistics.max_health = self.hp = 100
        self.recalculate_statistics()
        self._play_current_animation()

        self.rect.width = 64
        self.rect.height = 64
        self.add_controller(DeathController())
        self.add_controller(RangeAttackController())
        self.add_controller(PathController())

        self.set_ai(StandardAI())

        stats = copy.deepcopy(self._base_statistics)
        stats.hit_effects = [('HitEffect', {'damage': 30})]
        stats.bullet_speed = 500
        self.add_evolution_level(stats, 100, None)

        stats = copy.deepcopy(stats)
        stats.attack_range += 100
        stats.bullet_speed = 500
        stats.bullet_image = 'flaming-arrow.png'
        self.add_evolution_level(stats, 250, None)
