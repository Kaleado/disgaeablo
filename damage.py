#!/usr/bin/env python
import settings

class Damage:
    def __init__(self, source_entity, amount):
        self._source_entity = source_entity
        self._amount = amount

    def inflict(self, destination_entity, mapp):
        stats = destination_entity.component('Stats')
        if stats is not None:
            if self._amount > 0:
                stats.deal_damage(destination_entity, mapp, self._amount)
            return self._amount
        return None

class WithStatusEffect:
    def __init__(self, status_effect, strength, duration, damage):
        self._damage = damage
        self._status_effect = status_effect
        self._strength = strength
        self._duration = duration
        self._source_entity = damage._source_entity

    def inflict(self, destination_entity, mapp):
        stats = destination_entity.component('Stats')
        if stats is not None:
            stats.inflict_status(self._status_effect, self._strength, self._duration)
        return self._damage.inflict(destination_entity, mapp)

class WithDeathblow:
    def __init__(self, damage):
        self._damage = damage
        self._source_entity = damage._source_entity

    def inflict(self, destination_entity, mapp):
        inflicted = self._damage.inflict(destination_entity, mapp)
        stats = destination_entity.component('Stats')
        if stats is not None and inflicted > 0:
            stats.deal_damage(destination_entity, mapp, stats.get_value('cur_hp'))
            settings.message_panel.info("DEATHBLOW!")

class WithLifesteal:
    def __init__(self, damage):
        self._damage = damage
        self._source_entity = damage._source_entity

    def inflict(self, destination_entity, mapp):
        inflicted = self._damage.inflict(destination_entity, mapp)
        stats = self._source_entity.component('Stats')
        stats.apply_healing(source_entity, mapp, inflicted)
        return inflicted
