import importlib

from pytowerdefence.gameplay.Objects import StatisticModifier, StatisticType


class LogicalEffectBase:
    def __init__(self, actor, name, is_unique):
        self._actor = actor
        self.name = name
        self.is_unique = is_unique

    def need_to_perform(self, dt, logic_manager):
        return True

    def perform(self, logic_manager):
        pass

    def is_finished(self):
        return True

    def on_remove(self, logic_manager):
        pass

    def on_merge(self, effect):
        pass


class HitEffect(LogicalEffectBase):
    def __init__(self, actor,**kwargs):
        super().__init__(actor, 'hit', False)
        self._damage = kwargs['damage']

    def perform(self, logic_manager):
        self._actor.hit(self._damage)


class TimeEffect(LogicalEffectBase):
    def __init__(self,actor, name, is_unique, time, repeat_time = None, repeat=False):
        super().__init__(actor, name, is_unique)
        self.time = time
        self._repeat = repeat
        self._first_perform = False
        if repeat_time is not None and repeat:
            self._repeat_time = repeat_time
            self._to_next_repeat = repeat_time
        else:
            self._repeat_time = None
            self._to_next_repeat = None

    def on_merge(self, effect):
        self.time = max(self.time, effect.time)

    def need_to_perform(self, dt, logic_manager):
        self.time -= dt
        if not self._first_perform:
            self._first_perform = True
            return True

        if self._repeat:
            self._to_next_repeat -= dt
            if self._to_next_repeat < 0:
                self._to_next_repeat = self._repeat_time
                return True
        return False

    def is_finished(self):
        return self.time < 0


class SlowEffect(TimeEffect):
    def __init__(self, actor,**kwargs):
        super().__init__(actor, 'slow', True, kwargs['time'])
        self.speed_modifier = StatisticModifier(StatisticType.SPEED, kwargs['percent'], True)

    def perform(self, logic_manager):
        self._actor.add_modifier(self.speed_modifier)

    def on_merge(self, effect):
        super().on_merge(effect)
        if effect.speed_modifier.value > self.speed_modifier.value:
            self._actor.remove_modifier(self.speed_modifier)
            self.speed_modifier = effect.speed_modifier
            self._actor.add_modifier(self.speed_modifier)

    def on_remove(self, logic_manager):
        super().on_remove(logic_manager)
        self._actor.remove_modifier(self.speed_modifier)


class LogicEffectManager:
    def __init__(self, level):
        self.level = level

    def update(self, dt):
        for actor in self.level.actor_iterator():
            for le in actor.logical_effects:
                if le.need_to_perform(dt, self):
                    le.perform(self)
                if le.is_finished():
                    le.on_remove(self)
                    actor.remove_effect(le)
