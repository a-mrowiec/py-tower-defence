import json
import importlib

from src.gameplay.Controllers import PathController


class StandardWave:
    def __init__(self, json_object):
        self._objects = json_object["objects"]
        self._start_time = json_object["start_time"]
        self._object_creation_interval = json_object["creation_interval"]
        self._number_of_created_objects = 0
        self._number_of_objects = json_object["number_of_objects"]

    def should_run(self, time_elapsed):
        return self._start_time <= time_elapsed and self._number_of_created_objects < self._number_of_objects

    def get_objects_to_create(self, time_elapsed):
        objects_to_create = []
        while self._number_of_created_objects * self._object_creation_interval + self._start_time < time_elapsed and self._number_of_created_objects < self._number_of_objects:
            objects_to_create.append(self._get_object_template(self._number_of_created_objects))
            self._number_of_created_objects += 1
        return objects_to_create

    def _get_object_template(self, index):
        return self._objects[0]


class WaveManager:
    def __init__(self, level):
        self._waves = []
        self._data = None
        self._time_elapsed = 0.
        self._last_wave_index = 0
        self._level = level

    def load(self, filename):
        with open(filename) as file_data:
            self._data = json.load(file_data)
            self._load_waves()
            self._last_wave_index = 0

    def update(self, dt):
        self._time_elapsed += dt

        for wave in self._waves:
            if wave.should_run(self._time_elapsed):
                objects_to_create = wave.get_objects_to_create(self._time_elapsed)
                for obj_template in objects_to_create:
                    self._create_object(obj_template)

    def _create_object(self, object_template):
        monsters_module=importlib.import_module("src.gameplay.Monsters")
        monster=getattr(monsters_module, object_template["name"])()

        path_controller=monster.get_controller(PathController)
        if path_controller is not None:
            path_controller.set_path(self._level.paths[object_template["path"]])

        self._level.add(monster)

    def _load_waves(self):
        self._waves = []
        sorted_waves = sorted(self._data["waves"], key=lambda x: x["start_time"])
        for wave in sorted_waves:
            if wave["type"] == "standard":
                self._waves.append(StandardWave(wave))
            else:
                raise RuntimeError("Unknown wave type!")
