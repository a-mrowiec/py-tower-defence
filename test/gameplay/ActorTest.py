import unittest

from pygame.math import Vector2

from src.gameplay.Actor import Actor


class TestActor(Actor):
    def __init__(self):
        super().__init__()
        self.statistics.speed = 1
        self.statistics.attack = 5
        self.statistics.attack_range = 5


class ActorTests(unittest.TestCase):
    def test_updateForNotConfiguredActor_shouldWork(self):
        actor = TestActor()
        actor.go_to_direction(Vector2(1,0))
        actor.update(1.0)

        self.assertEqual(actor.position, Vector2(1, 0))


if __name__ == '__main__':
    unittest.main()