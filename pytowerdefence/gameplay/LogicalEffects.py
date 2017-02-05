"""
Logical effects module
"""
from pytowerdefence.gameplay.Objects import StatisticModifier, StatisticType


class LogicalEffectBase:
    """
    Base class for any logical effect
    """
    def __init__(self, actor, name, is_unique):
        self._actor = actor
        self.name = name
        self.is_unique = is_unique

    def need_to_perform(self, dt, logic_manager):
        """
        Returns true when effect must be performed
        :param dt:
        :param logic_manager:
        :return:
        """
        return True

    def perform(self, logic_manager):
        """
        Performs effect
        :param logic_manager:
        :return:
        """
        pass

    def is_finished(self):
        """
        If True effect will be removed in nearest frame tick
        :return:
        """
        return True

    def on_remove(self, logic_manager):
        """
        Called before removing effect
        :param logic_manager:
        :return:
        """
        pass

    def on_merge(self, effect):
        """
        Called only for unique effect
        :param effect:
        :return:
        """
        pass


class HitEffect(LogicalEffectBase):
    """
    Simply hit effect
    """
    def __init__(self, actor, **kwargs):
        super().__init__(actor, 'hit', False)
        self._damage = kwargs['damage']

    def perform(self, logic_manager):
        self._actor.hit(self._damage)


class TimeEffect(LogicalEffectBase):
    """
    Base class for time lasting effects
    """
    def __init__(self, actor, name, is_unique, time, repeat_time=None,
                 repeat=False):
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
    """
    Slows actor speed
    """
    def __init__(self, actor, **kwargs):
        super().__init__(actor, 'slow', True, kwargs['time'])
        self.speed_modifier = StatisticModifier(StatisticType.SPEED,
                                                kwargs['percent'], True)

    def perform(self, logic_manager):
        self._actor.add_modifier(self.speed_modifier)

    def on_merge(self, effect):
        super().on_merge(effect)
        if effect.speed_modifier.value < self.speed_modifier.value:
            self._actor.remove_modifier(self.speed_modifier)
            self.speed_modifier = effect.speed_modifier
            self._actor.add_modifier(self.speed_modifier)

    def on_remove(self, logic_manager):
        super().on_remove(logic_manager)
        self._actor.remove_modifier(self.speed_modifier)


class LogicEffectManager:
    """
    Manages logical effects
    """
    def __init__(self, level):
        self.level = level

    def update(self, dt):
        """
        Update logical effects
        :param dt:
        :return:
        """
        for actor in self.level.actor_iterator():
            for logical_effect in actor.logical_effects:
                if logical_effect.need_to_perform(dt, self):
                    logical_effect.perform(self)
                if logical_effect.is_finished():
                    logical_effect.on_remove(self)
                    actor.remove_effect(logical_effect)
