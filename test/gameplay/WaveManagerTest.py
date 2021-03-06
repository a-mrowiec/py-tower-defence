from unittest import TestCase

import mock

from pytowerdefence.gameplay.Logic import WaveManager
from test.TestUtils import path_to_test_data


class TestWaveManager(TestCase):
    def test_load(self):
        manager = WaveManager(mock.Mock())
        manager.load(path_to_test_data("test_wave.json"))

        self.assertEqual(len(manager._waves), 2)

    def test_loadUnknownType_shouldRaiseError(self):
        manager = WaveManager(mock.Mock())
        self.failUnlessRaises(RuntimeError, lambda: manager.load(path_to_test_data("test_wave_bad_type.json")))

    def test_update(self):
        manager = WaveManager(mock.Mock())
        manager._create_object = mock.Mock()
        manager.load(path_to_test_data("test_wave.json"))

        manager.update(0.4)
        self.assertEqual(manager._create_object.call_count, 1)
        manager.update(0.5)
        manager.update(0.3)
        self.assertEqual(manager._create_object.call_count, 3)
        manager.update(0.5)
        self.assertEqual(manager._create_object.call_count, 3)

        manager.update(5.0)
