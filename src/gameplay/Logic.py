import json


class StandardWave:
    def __init__(self, json_object):
        self._objects = json_object["objects"]
        self._start_time = json_object["start_time"]
        self._number_of_objects = json_object["number_of_objects"]
        self._object_creation_interval = json_object["creation_interval"]
        self._number_of_created_objects = 0

    def should_run(self, time_elapsed):
        return self._start_time >= time_elapsed >= self._number_of_objects * self._object_creation_interval + self._start_time

    def get_objects_to_create(self, time_elapsed):
        objects_to_create = []
        while self._number_of_created_objects * self._object_creation_interval + self._start_time < time_elapsed:
            objects_to_create.append(self._create_object(self._number_of_created_objects))
            self._number_of_created_objects += 1

    def _create_object(self, index):
        return self._objects[index]


class WaveManager:
    def __init__(self):
        self._waves = []
        self._data = None
        self._time_elapsed = 0.
        self._last_wave_index = 0

    def load(self, filename):
        with open(filename) as file_data:
            self._data = json.load(file_data)
            self._load_waves()
            self._last_wave_index = 0

    def update(self, dt):
        self._time_elapsed += dt
        # TODO: get list of objects to create from waves

    def _load_waves(self):
        self._waves = []
        sorted_waves = sorted(self._data["waves"], key=lambda x: x.start_time)
        for wave in sorted_waves:
            self._waves.append(StandardWave(wave))
