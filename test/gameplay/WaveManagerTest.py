from unittest import TestCase

from src.gameplay.Logic import WaveManager
from test.TestUtils import path_to_test_data


class TestWaveManager(TestCase):
    def test_load(self):
        manager = WaveManager()
        manager.load(path_to_test_data("test_wave.json"))

        self.assertEqual(len(manager._waves), 2)

    def test_loadUnknownType_shouldRaiseError(self):
        manager = WaveManager()
        self.failUnlessRaises(RuntimeError, lambda: manager.load(path_to_test_data("test_wave_bad_type.json")))


