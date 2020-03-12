#!/usr/bin/env python
from entity import *

class Skill(Usable):
    def __init__(self, tags=[]):
        self._tags = tags
        def default_use(self, entity, user_entity, mapp, menu):
            targets = self.choose_targets(entity, user_entity, mapp, menu)
            return self.use_on_targets(entity, user_entity, mapp, targets, menu)

        self._damage = lambda slf, s, t, i : None
        self._choose_targets = lambda slf, e, ue, m, mn : (None, None)
        self._use_on_targets = lambda slf, e, ue, m, t, mn : None
        self._use = default_use

    def damage(self, source_entity, target_entity, item_entity):
        return self._damage(self, source_entity, target_entity, item_entity)

    # Returns true if the item is meant to be removed upon use
    def use(self, entity, user_entity, mapp, menu):
        return self._use(self, entity, user_entity, mapp, menu)

    def choose_targets(self, entity, user_entity, mapp, menu):
        return self._choose_targets(self, entity, user_entity, mapp, menu)

    def use_on_targets(self, entity, user_entity, mapp, targets, menu):
        return self._use_on_targets(self, entity, user_entity, mapp, targets, menu)

    # Factory methods

    def with_sp_cost(self, sp):
        use = self._use
        def f(self, entity, user_entity, mapp, menu):
            has_blood_magic = user_entity.component('Stats').get('blood_magic') > 0
            if has_blood_magic:
                if user_entity.component('Stats').get('cur_hp') < sp:
                    return False
                else:
                    user_entity.component('Stats').deal_damage(user_entity, mapp, sp)
                    return use(self, entity, user_entity, mapp, menu)
            else:
                if user_entity.component('Stats').get('cur_sp') < sp:
                    return False
                else:
                    user_entity.component('Stats').sub_base('cur_sp', sp)
                    return use(self, entity, user_entity, mapp, menu)
        self._use = f
        return self

    def with_target_mode(self, target_mode):
        def f(self, entity, user_entity, mapp, menu):
            return target_mode.choose_targets(user_entity, user_entity, mapp, menu)
        self._choose_targets = f
        self._target_mode = target_mode
        return self

    def with_damage(self, damage):
        def f(self, source_entity, target_entity, item_entity):
            if damage is not None:
                return damage(source_entity, target_entity, item_entity)
        self._damage = f
        return self

    def override_target_mode(self, target_mode, predicate=None):
        old_target_mode = self._target_mode
        def f(self, entity, user_entity, mapp, menu):
            if predicate is None or predicate(self, entity, user_entity, mapp, menu):
                self._target_mode = target_mode
                return target_mode.choose_targets(user_entity, user_entity, mapp, menu)
            self._target_mode = old_target_mode
            return old_target_mode.choose_targets(user_entity, user_entity, mapp, menu)
        self._choose_targets = f
        # self._target_mode = target_mode
        return self

    """
    damage_applicator: func(damage, source_entity, target_entity, item_entity)
    """
    def change_damage(self, damage_applicator, predicate=None):
        damage = self._damage
        def f(self, source_entity, target_entity, item_entity):
            if predicate is None or predicate(self, entity, user_entity, mapp, targets, menu):
                return damage_applicator(damage(self, source_entity, target_entity, item_entity), source_entity, target_entity, item_entity)
            return damage
        self._damage = f
        return self

    def damage_targets(self, msg=None, predicate=None):
        use_on_targets = self._use_on_targets
        def f(self, entity, user_entity, mapp, targets, menu):
            if predicate is None or predicate(self, entity, user_entity, mapp, targets, menu):
                if targets[0] is None:
                    return False
                def g(t):
                    amt = self.damage(user_entity, t, entity).inflict(t, mapp)
                    if msg is not None:
                        colour = tcod.red if user_entity.name() == 'Player' or t.name() == 'Player' else tcod.white
                        message_panel.info(msg.format(user_entity.name(), t.name(), amt), colour)
                obstructions, mov_pos = self._target_mode.targets(group='P')
                if mov_pos is not None and len(mov_pos) > 0 and mapp.is_passable_for(user_entity, mov_pos[0]):
                    user_entity.component('Position').set(mov_pos[0][0], mov_pos[0][1])
                targets[0].transform(g)
            return use_on_targets(self, entity, user_entity, mapp, targets, menu)
        self._use_on_targets = f
        return self

    def move_to_targeted_position(self, predicate=None):
        use_on_targets = self._use_on_targets
        def f(self, entity, user_entity, mapp, targets, menu):
            if predicate is None or predicate(self, entity, user_entity, mapp, targets, menu):
                obstructions, mov_pos = self._target_mode.targets(group='P')
                if mov_pos is not None and len(mov_pos) > 0 and mapp.is_passable_for(user_entity, mov_pos[0]):
                    user_entity.component('Position').set(mov_pos[0][0], mov_pos[0][1])
            return use_on_targets(self, entity, user_entity, mapp, targets, menu)
        self._use_on_targets = f
        return self

    def melee_skill(self, predicate=None):
        use_on_targets = self._use_on_targets
        def f(self, entity, user_entity, mapp, targets, menu):
            if predicate is None or predicate(self, entity, user_entity, mapp, targets, menu):
                entities_hit, _ = self._target_mode.targets(group='x')
                if entities_hit is not None and entities_hit.size() > 0:
                    has_assault = user_entity.component('Stats').get('assault') > 0
                    if has_assault:
                        user_entity.component('Stats').inflict_status('ASSAULT', strength=1, duration=3)
            return use_on_targets(self, entity, user_entity, mapp, targets, menu)
        self._use_on_targets = f
        return self
