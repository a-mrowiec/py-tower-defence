"""
Common game logic module
"""
import json

from pytowerdefence.gameplay.Controllers import PathController
from pytowerdefence.gameplay.Objects import Actor, ActorCallback, EvolvingActor
from pytowerdefence.gameplay.Scene import is_actor_in_player_team


class StandardWave:
    """
    Standard wave
    """

    def __init__(self, json_object):
        self._objects = json_object["objects"]
        self._start_time = json_object["start_time"]
        self._object_creation_interval = json_object["creation_interval"]
        self._number_of_created_objects = 0
        self._number_of_objects = json_object["number_of_objects"]

    def should_run(self, time_elapsed):
        """
        returns True if should create actors
        :param time_elapsed:
        :return:
        """
        return self._start_time <= time_elapsed \
               and self._number_of_created_objects < self._number_of_objects

    def get_objects_to_create(self, time_elapsed):
        """
        Returns list of actors templates to create
        :param time_elapsed:
        :return:
        """
        objects_to_create = []
        while self._should_create(time_elapsed) \
                and self._still_need_create_objects():
            objects_to_create.append(
                self._get_object_template(self._number_of_created_objects))
            self._number_of_created_objects += 1
        return objects_to_create

    def _should_create(self, time_elapsed):
        return self._number_of_created_objects * self._object_creation_interval \
               + self._start_time < time_elapsed

    def _still_need_create_objects(self):
        return self._number_of_created_objects < self._number_of_objects

    def _get_object_template(self, index):
        return self._objects[0]


class WaveManager:
    """
    Create monster waves
    """

    def __init__(self, factory):
        self._waves = []
        self._data = None
        self._time_elapsed = 0.
        self._last_wave_index = 0
        self._creatures_factory = factory

    def load(self, filename):
        """
        Load waves from json file
        :param filename:
        :return:
        """
        with open(filename) as file_data:
            self._data = json.load(file_data)
            self._load_waves()
            self._last_wave_index = 0

    def update(self, dt):
        """
        Update wave manager
        :param dt:
        :return:
        """
        self._time_elapsed += dt

        for wave in self._waves:
            if wave.should_run(self._time_elapsed):
                objects_to_create = wave.get_objects_to_create(
                    self._time_elapsed)
                for obj_template in objects_to_create:
                    self._create_object(obj_template)

    def _create_object(self, object_template):
        with self._creatures_factory.create_on_scene(object_template["name"]) \
                as (monster, level):
            path_controller = monster.get_controller(PathController)
            path = level.paths[object_template["path"]]
            if path_controller is not None and path is not None:
                monster.position = path[0]

                path_controller.set_path(path)
                path_controller.current_path_point = 1

    def _load_waves(self):
        self._waves = []
        sorted_waves = sorted(self._data["waves"],
                              key=lambda x: x["start_time"])
        for wave in sorted_waves:
            if wave["type"] == "standard":
                self._waves.append(StandardWave(wave))
            else:
                raise RuntimeError("Unknown wave type!")


class GameState:
    """
    Game state
    """

    def __init__(self):
        self.player_gold = 0
        self.monsters_killed = 0
        self.time_elapsed = 0


class LogicManager:
    """
    Logic manager
    """

    def __init__(self, start_properties):
        self.game_state = GameState()
        self.game_state.player_gold = start_properties['player_gold']

    def on_object_added_to_scene(self, actor_object):
        """
        Called when actor is added to scene
        :param actor_object:
        :return:
        """
        if isinstance(actor_object, Actor) and not is_actor_in_player_team(
                actor_object):
            actor_object.set_callback(ActorCallback.KILL,
                                      self.on_monster_killed)

    def on_monster_killed(self, actor):
        """
        Called when monster is killed
        :param actor:
        :return:
        """
        self.game_state.monsters_killed += 1
        self.game_state.player_gold += actor.class_properties['gold_gain']

    def can_evolve(self, actor):
        """
        Checks if actor can be evolved
        :param actor:
        :return:
        """
        if isinstance(actor, EvolvingActor):
            if not actor.has_max_level():
                return actor.get_current_evolution_cost() <= self.game_state.player_gold
        return False

    def evolve(self, actor):
        """
        Evolve specified actor
        :param actor:
        :return:
        """
        self.game_state.player_gold -= actor.get_current_evolution_cost()
        actor.evolve()

    def update(self, dt):
        """
        Update logic
        :param dt:
        :return:
        """
        self.game_state.time_elapsed += dt
