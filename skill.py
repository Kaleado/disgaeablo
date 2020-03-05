#!/usr/bin/env python
from entity import *

# A skill is assumed to:
# - Have Stats.
# - Be used by an NPC or the player.
class Skill(Usable):
    def __init__(self):
        pass

    def damage(self, source_entity):
        return None

    # Returns true if the item is meant to be removed upon use
    def use(self, entity, user_entity, mapp, menu):
        targets = self.choose_targets(entity, user_entity, mapp, menu)
        return self.use_on_targets(entity, user_entity, mapp, targets, menu)

    def choose_targets(self, entity, user_entity, mapp, menu):
        return None, None

    def use_on_targets(self, entity, user_entity, mapp, targets, menu):
        return False

class SkillDecorator(Skill):
    def __init__(self, skill):
        self._skill = skill

    def damage(self, source_entity):
        return self._skill.damage(source_entity)

    def use(self, entity, user_entity, mapp, menu):
        targets = self.choose_targets(entity, user_entity, mapp, menu)
        return self.use_on_targets(entity, user_entity, mapp, targets, menu)

    def choose_targets(self, entity, user_entity, mapp, menu):
        return self._skill.choose_targets(entity, user_entity, mapp, menu)

    def use_on_targets(self, entity, user_entity, mapp, targets, menu):
        return self._skill.use_on_targets(entity, user_entity, mapp, targets, menu)

class ConsumeSP(SkillDecorator):
    def __init__(self, sp, skill):
        super().__init__(skill)
        self._sp = sp

    def _pay_costs(self, entity, user_entity):
        user_stats = user_entity.component('Stats')
        sp_usage_heals = user_stats.get_value('sp_usage_heals') > 0
        sp_consumed = min(self._sp, user_stats.get_base('cur_sp'))
        if sp_usage_heals:
            user_stats.apply_healing(user_entity, settings.current_map, sp_consumed)
        user_stats.sub_base('cur_sp', self._sp)

    def can_pay_cost(self, entity, user_entity):
        return user_entity.component('Stats').get_value('cur_sp') >= self._sp

    def use(self, entity, user_entity, mapp, menu):
        if not self.can_pay_cost(entity, user_entity):
            return False
        self._pay_costs(entity, user_entity)
        return self._skill.use(entity, user_entity, mapp, menu)

class WithTargetMode(SkillDecorator):
    def __init__(self, targeting_mode, skill):
        super().__init__(skill)
        self._targeting_mode = targeting_mode

    def choose_targets(self, entity, user_entity, mapp, menu):
        return self._targeting_mode.choose_targets(user_entity, user_entity, mapp, menu)

class DamageTargets(SkillDecorator):
    def use_on_targets(self, entity, user_entity, mapp, targets, menu):
        if self._skill.damage(user_entity) is not None:
            targets[0].transform(lambda target: self._skill.damage(user_entity).inflict(target, mapp))
        return self._skill.use_on_targets(entity, user_entity, mapp, targets, menu)

class WithDamage(SkillDecorator):
    def __init__(self, damage, skill):
        super().__init__(skill)
        self._damage = damage

    def damage(self, source_entity):
        return self._damage(source_entity)

class ChangeDamage(SkillDecorator):
    """
    damage_applicator is a function that accepts a Damage as parameters and returns another Damage
    """
    def __init__(damage_applicator, skill):
        super().__init__(skill)
        self._damage_applicator = damage_applicator

    def damage(self, source_entity):
        damage = self._skill.damage(source_entity)
        if damage is not None:
            return self._damage_applicator(damage)

class HealTargets(SkillDecorator):
    def __init__(healing, skill):
        super().__init__(skill)
        self._healing = healing

    def use_on_targets(self, entity, user_entity, mapp, targets, menu):
        if self._healing is not None:
            targets[0].transform(lambda target: target.component('Stats').apply_healing(user_entity, mapp, self._healing))
        return self._skill.use_on_targets(entity, user_entity, mapp, targets, menu)

class RefreshTargets(SkillDecorator):
    def __init__(refreshing, skill):
        super().__init__(skill)
        self._refreshing = refreshing

    def use_on_targets(self, entity, user_entity, mapp, targets, menu):
        if self._refreshing is not None:
            targets[0].transform(lambda target: target.component('Stats').apply_refreshing(user_entity, mapp, self._refreshing))
        return self._skill.use_on_targets(entity, user_entity, mapp, targets, menu)
