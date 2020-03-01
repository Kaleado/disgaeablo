#!/usr/bin/env python
import settings
import random
import math
import tcod

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
            cur_hp = stats.get_value('cur_hp')
            stats.deal_damage(destination_entity, mapp, cur_hp)
            settings.message_panel.info("DEATHBLOW!", tcod.crimson)
            return cur_hp

class WithLifeDrain:
    def __init__(self, damage, heal_proportion=1.0):
        self._damage = damage
        self._heal_proportion = heal_proportion
        self._source_entity = damage._source_entity

    def inflict(self, destination_entity, mapp):
        inflicted = self._damage.inflict(destination_entity, mapp)
        stats = self._source_entity.component('Stats')
        healed_amount = math.floor(inflicted * self._heal_proportion)
        stats.apply_healing(self._source_entity, mapp, math.floor(healed_amount))
        attacker_name = "Player" if self._source_entity.component('NPC') is None else \
                        self._source_entity.component('NPC').name()
        defender_name = "Player" if destination_entity.component('NPC') is None else \
                        destination_entity.component('NPC').name()
        colour = tcod.red if attacker_name == "Player" or defender_name == "Player" else tcod.white
        settings.message_panel.info("{} drained {} HP from {}".format(attacker_name, healed_amount, defender_name), colour)
        return inflicted

class Chance:
    def __init__(self, chance_success, damage_success, damage_failure):
        self._chance_success = chance_success
        self._damage_success = damage_success
        self._damage_failure = damage_failure
        self._source_entity = damage_success._source_entity

    def inflict(self, destination_entity, mapp):
        roll = random.randint(0, 100)
        if roll < 100 * self._chance_success:
            return self._damage_success.inflict(destination_entity, mapp)
        else:
            return self._damage_failure.inflict(destination_entity, mapp)
