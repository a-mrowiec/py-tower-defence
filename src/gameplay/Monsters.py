
from src.gameplay.Actor import ActorState, Actor

rects = [(0, 154, 94, 77),
         (94, 154, 94, 77),
         (188, 154, 94, 77),
         (282, 154, 94, 77),
         (376, 154, 94, 77),
         (470, 154, 94, 77),
         (564, 154, 94, 77),
         (658, 154, 94, 77),
         (752, 154, 94, 77), ]

ogre_move_rects = [(0, 0, 64, 64),
                   (64, 0, 64, 64),
                   (128, 0, 64, 64),
                   (192, 0, 64, 64),
                   (256, 0, 64, 64),
                   (320, 0, 64, 64),
                   (384, 0, 64, 64),
                   (448, 0, 64, 64), ]

ogre_idle_rects = [(0, 0, 64, 64)]

ogre_death_rects = [(0, 0, 64, 64),
                     (64, 0, 64, 64),
                     (128, 0, 64, 64),
                     (192, 0, 64, 64),
                     (0, 64, 64, 64),
                     (64, 64, 64, 64),
                     (128, 64, 64, 64),
                     (192, 64, 64, 64),
                     (0, 128, 64, 64),
                     (64, 128, 64, 64),
                     (128, 128, 64, 64),
                     (192, 128, 64, 64),
                     (0, 192, 64, 64),
                     (64, 192, 64, 64),
                     (128, 192, 64, 64),
                     (192, 192, 64, 64),
                     (0, 256, 64, 64),
                     (64, 256, 64, 64),
                     (128, 256, 64, 64),
                     (192, 256, 64, 64),
                     (0, 320, 64, 64),
                     (64, 320, 64, 64),
                     (128, 320, 64, 64),
                     (192, 320, 64, 64),
                     (0, 384, 64, 64),
                     (64, 384, 64, 64),
                     (128, 384, 64, 64),
                     (192, 384, 64, 64),
                     (0, 448, 64, 64),
                     (64, 448, 64, 64),
                     (128, 448, 64, 64),
                     (192, 448, 64, 64)]


class Ogre(Actor):
    def __init__(self):
        super().__init__()
        self._statistics.speed = 50

        self.create_and_add_animation('data/ogre-move.png', ogre_move_rects, ActorState.MOVE)
        self.create_and_add_animation('data/ogre-move.png', ogre_idle_rects, ActorState.IDLE)
        self.create_and_add_animation('data/ogre-attack.png', ogre_move_rects, ActorState.ATTACK, loop=False)
        self.create_and_add_animation('data/ogre-death.png', ogre_death_rects, ActorState.DEATH, loop=False, speed=[20])

        self.statistics.attack_range = 100
        self.change_state(ActorState.MOVE)

        self.rect.width = 64
        self.rect.height = 64


class Bandit(Actor):
    def __init__(self):
        super().__init__()
        self._statistics.speed = 50

        self.create_and_add_animation('data/bandit-move.png', ogre_move_rects, ActorState.MOVE)
        self.create_and_add_animation('data/bandit-move.png', ogre_idle_rects, ActorState.IDLE)
        self.create_and_add_animation('data/bandit-attack.png', ogre_move_rects, ActorState.ATTACK, loop=False)
        self.create_and_add_animation('data/bandit-death.png', ogre_death_rects, ActorState.DEATH, loop=False)

        self.statistics.attack_range = 100
        self.statistics.attack = 5
        self._play_current_animation()

        self.rect.width = 64
        self.rect.height = 64
