#!/usr/bin/env python

import tcod
import tcod.event
import random
from entitylistview import *
from util import *
from settings import *
from console import *
from formation import *
import damage
import math
import uuid
import pickle

SERIALIZED_COMPONENTS = ['Stats', 'Inventory', 'Position', 'EquipmentSlots', 'Equipment']

class GameplayException(Exception):
    pass

class Component:
    def handle_event(self, entity, event, resident_map):
        return False

    def save_subtype_string(self):
        return 'ERROR'

    def save(self):
        obj = {
            'TYPE': 'COMPONENT',
            'SUBTYPE': self.save_subtype_string(),
        }
        return obj

class Entity:
    def __init__(self, ident, components, ttype, tags=[]):
       self._ident = ident
       self._components = components
       self._disabled = False
       self._tags = tags
       self._type = ttype

    def stat(self, name):
        return self.component('Stats').get(name)

    def save(self):
        def save_components():
            cmps = {}
            for k in SERIALIZED_COMPONENTS:
                if not self.has_component(k):
                    continue
                v = self.component(k)
                cmps[k] = v.save()
            return cmps

        obj = {
            'TYPE': 'ENTITY',
            'generator_type': self._type,
            'ident': self._ident,
            'components': save_components(),
        }
        return obj

    def tags(self):
        return self._tags

    def has_tag(self, tag):
        return tag in self._tags

    def name(self):
        return self.component('NPC').name() if self.component('NPC') is not None else \
            'Player' if self.component('PlayerLogic') is not None else \
            self.component('Item').name() if self.component('Item') is not None else 'Unknown object'

    def position(self):
        return self.component('Position')

    def generate_new_ident(self):
        self._ident = str(uuid.uuid4())
        return self._ident

    def ident(self):
        return self._ident

    def disable(self):
        self._disabled = True

    def has_component(self, identifier):
        return identifier in self._components

    def component(self, identifier):
        return self._components.get(identifier)

    def set_component(self, identifier, component):
        replaced = self.component(identifier)
        self._components[identifier] = component
        return replaced

    def handle_event(self, event, resident_map):
        if self._disabled:
            return False
        for c in self._components.values():
            if c.handle_event(self, event, resident_map):
                return True

class TargetMode:
    def __init__(self):
        pass

    def targets(self, group='x'):
        return None, None

    def choose_targets(self, user_entity, used_entity, mapp, menu):
        return None, None

class PositionsOnly(TargetMode):
    def __init__(self, targeting_mode):
        self._targeting_mode = targeting_mode

    def targets(self, group='x'):
        ents, pos = self._targeting_mode.targets(group)
        return EntityListView([]), pos

    def choose_targets(self, user_entity, used_entity, mapp, menu):
        ents, pos = self._targeting_mode.choose_targets(user_entity, used_entity, mapp, menu)
        return EntityListView([]), pos

class NoFriendlyFire(TargetMode):
    def __init__(self, targeting_mode):
        self._targeting_mode = targeting_mode
        self._targets = {}

    def targets(self, group='x'):
        if group not in self._targets:
            return None, None
        return self._targets[group]

    def choose_targets(self, user_entity, used_entity, mapp, menu):
        ents, pos = self._targeting_mode.choose_targets(user_entity, used_entity, mapp, menu)
        if ents is None:
            return ents, pos
        is_player = user_entity.component('PlayerLogic') is not None
        self._targets['x'] = ents.without_components(['PlayerLogic'] if is_player else ['NPC']), pos
        return self._targets['x']

class ExcludeItems(TargetMode):
    def __init__(self, targeting_mode):
        self._targeting_mode = targeting_mode

    def targets(self, group='x'):
        if group not in self._targeting_mode._targets:
            return None, None
        ents, pos = self._targeting_mode.targets(group)
        return ents.without_components('Item'), pos

    def choose_targets(self, user_entity, used_entity, mapp, menu):
        ents, pos = self._targeting_mode.choose_targets(user_entity, used_entity, mapp, menu)
        if ents is None:
            return ents, pos
        return ents.without_components(['Item']), pos

class WithoutComponents(TargetMode):
    def __init__(self, components, targeting_mode):
        self._targeting_mode = targeting_mode
        self._components = components

    def targets(self, group='x'):
        if group not in self._targeting_mode._targets:
            return None, None
        ents, pos = self._targeting_mode.targets(group)
        return ents.without_components(self._components), pos

    def choose_targets(self, user_entity, used_entity, mapp, menu):
        ents, pos = self._targeting_mode.choose_targets(user_entity, used_entity, mapp, menu)
        if ents is None:
            return ents, pos
        return ents.without_components(self._components), pos

class WithComponents(TargetMode):
    def __init__(self, components, targeting_mode):
        self._targeting_mode = targeting_mode
        self._components = components

    def targets(self, group='x'):
        if group not in self._targeting_mode._targets:
            return None, None
        ents, pos = self._targeting_mode.targets(group)
        return ents.with_all_components(self._components), pos

    def choose_targets(self, user_entity, used_entity, mapp, menu):
        ents, pos = self._targeting_mode.choose_targets(user_entity, used_entity, mapp, menu)
        if ents is None:
            return ents, pos
        return ents.with_all_components(self._components), pos

class TargetNobody(TargetMode):
    def targets(self, group='x'):
        return EntityListView([]), []

    def choose_targets(self, user_entity, used_entity, mapp, menu):
        return EntityListView([]), []

class TargetEveryone(TargetMode):
    def __init__(self, group='x'):
        self._targets = {'x': (None, None)}
        self._group = group

    def targets(self, group='x'):
        if group not in self._targets:
            return None, None
        return self._targets[group]

    def choose_targets(self, user_entity, used_entity, mapp, menu):
        self._targets[self._group] = mapp.entities(), []
        return mapp.entities(), []

class TargetUser(TargetMode):
    def __init__(self, group='x'):
        self._targets = {'x': (None, None)}
        self._group = group

    def targets(self, group='x'):
        if group not in self._targets:
            return None, None
        return self._targets[group]
       
    def choose_targets(self, user_entity, used_entity, mapp, menu):
        self._targets[self._group] = EntityListView([user_entity]), [user_entity.component('Position').get()]
        return self._targets['x']

class TargetAnd(TargetMode):
    def __init__(self, target_mode, other_target_mode):
        self._target_mode = target_mode
        self._other_target_mode = other_target_mode

    def targets(self, group='x'):
        targets_1 = self._target_mode.targets(group)
        targets_2 = self._other_target_mode.targets(group)
        if targets_1[0] is None or targets_1[1] is None:
            return None, None
        if targets_2[0] is None or targets_2[1] is None:
            return None, None
        ents = EntityListView(list(set(targets_1[0].as_list() + targets_2[0].as_list())))
        pos = list(set(targets_1[1] + targets_2[1]))
        return ents, pos

    def choose_targets(self, user_entity, used_entity, mapp, menu):
        targets_1 = self._target_mode.choose_targets(user_entity, used_entity, mapp, menu)
        targets_2 = self._other_target_mode.choose_targets(user_entity, used_entity, mapp, menu)
        ents = EntityListView(list(set(targets_1[0].as_list() + targets_2[0].as_list())))
        pos = list(set(targets_1[1] + targets_2[1]))
        return ents, pos

class TargetRandomPositions(TargetMode):
    def __init__(self, num_positions, within_distance=None, passable_only=False, group='x'):
        self._targets = {'x': (None, None)}
        self._group = group
        self._num_positions = num_positions
        self._passable_only = passable_only
        self._within_distance = within_distance

    def targets(self, group='x'):
        if group not in self._targets:
            return None, None
        return self._targets[group]

    def _random_point_within_distance(self, pos, dim):
        import util
        x, y = pos
        w, h = dim
        dist = random.uniform(1, self._within_distance)
        angl = random.uniform(0, 2 * math.pi)
        dx, dy = round(math.sin(angl) * dist), round(math.cos(angl) * dist)
        p = (math.floor(util.clamp(x + dx, 0, w)),\
             math.floor(util.clamp(y + dy, 0, h)))
        return p

    def choose_targets(self, user_entity, used_entity, mapp, menu):
        random_positions = []
        w, h = mapp.dimensions()
        x, y = user_entity.component('Position').get()
        for _ in range(self._num_positions):
            if self._within_distance is None:
                p = (random.randint(0, w), random.randint(0, h))
            else:
                p = self._random_point_within_distance((x, y), (w, h))
            tries = 0
            while tries < 3 and self._passable_only and not mapp.is_passable_for(user_entity, p):
                p = self._random_point_within_distance((x, y), (w, h))
                tries += 1
            if self._passable_only and not mapp.is_passable_for(user_entity, p):
                continue
            random_positions.append(p)
        self._targets[self._group] = EntityListView([]), random_positions
        return self._targets['x']

class TargetFormation(TargetMode):
    def __init__(self, formation, directional=False, max_range=None, positioned_randomly=False):
        self._formation = formation
        self._directional = directional
        self._positioned_randomly = positioned_randomly
        self._max_range = max_range
        self._targets = {'x': (EntityListView([]), [])}

    def targets(self, group='x'):
        if group not in self._targets:
            return None, None
        return self._targets[group]

    def choose_targets(self, user_entity, used_entity, mapp, menu):
        if self._positioned_randomly:
            return self._choose_targets_positioned_randomly(user_entity, used_entity, mapp, menu)
        if user_entity == mapp.entity('PLAYER'):
            return self._choose_targets_player(user_entity, used_entity, mapp, menu)
        if user_entity.has_component('Ally'):
            return self._choose_targets_ally(user_entity, used_entity, mapp, menu)
        return self._choose_targets_monster(user_entity, used_entity, mapp, menu)

    def _choose_targets_positioned_randomly(self, user_entity, used_entity, mapp, menu):
        user_pos = user_entity.component('Position').get()
        formation_position = user_pos
        formation_rotation = random.randint(0,4)
        w, h = mapp.dimensions()
        if not self._directional:
            formation_position = random.randint(0, w-1), random.randint(0, h-1)
            while self._max_range is not None and util.distance(user_pos, formation_position) > self._max_range:
                formation_position = random.randint(0, w-1), random.randint(0, h-1)
        for group in self._formation.groups():
            self._targets[group] = mapp.entities().in_formation(self._formation, formation_position, formation_rotation, group=group), self._formation.positions_in_formation(formation_position, formation_rotation, group)
        return self._targets['x']

    def _choose_targets_ally(self, user_entity, used_entity, mapp, menu):
        # If the target is nearby, try to hit them, otherwise, just target randomly
        target = user_entity.component('AI').get_target()
        if target is None:
            return None, None
        user_pos = user_entity.component('Position').get()
        target_pos = mapp.entity(target).component('Position').get()
        formation_position = user_pos
        formation_rotation = random.randint(0,4)
        if not self._directional:
            if self._max_range is None or distance(user_pos, target_pos) <= self._max_range:
                formation_position = target_pos
        else:
            for rot in range(4):
                if self._formation.in_formation(formation_position, target_pos, rot):
                    formation_rotation = rot
                    break
        for group in self._formation.groups():
            self._targets[group] = mapp.entities().in_formation(self._formation, formation_position, formation_rotation, group=group), self._formation.positions_in_formation(formation_position, formation_rotation, group)
        return self._targets['x']

    def _choose_targets_monster(self, user_entity, used_entity, mapp, menu):
        # If the player is nearby, try to hit them, otherwise, just target randomly
        user_pos = user_entity.component('Position').get()
        player_pos = mapp.entity('PLAYER').component('Position').get()
        formation_position = user_pos
        formation_rotation = random.randint(0,4)
        if not self._directional:
            if self._max_range is None or distance(user_pos, player_pos) <= self._max_range:
                formation_position = player_pos
        else:
            for rot in range(4):
                if self._formation.in_formation(formation_position, player_pos, rot):
                    formation_rotation = rot
                    break
        for group in self._formation.groups():
            self._targets[group] = mapp.entities().in_formation(self._formation, formation_position, formation_rotation, group=group), self._formation.positions_in_formation(formation_position, formation_rotation, group)
        return self._targets['x']

    def _choose_targets_player(self, user_entity, used_entity, mapp, menu):
        user_position = user_entity.component('Position').get()
        map_panel_pos, old_map_panel = menu.panel('MapPanel')
        old_map_panel.unfocus()
        new_map_panel = PlaceFormationOnMapPanel(mapp, self._formation, user_position, self._directional, self._max_range, user_position)
        menu.set_panel('MapPanel', (map_panel_pos, new_map_panel))
        menu.focus('MapPanel')
        formation_position, formation_rotation = menu.run(root_console)
        menu.unresolve()
        menu.set_panel('MapPanel', (map_panel_pos, old_map_panel))
        menu.focus('MapPanel')

        if formation_position is None or formation_rotation is None:
            return None, None

        for group in self._formation.groups():
            self._targets[group] = mapp.entities().in_formation(self._formation, formation_position, formation_rotation, group=group), self._formation.positions_in_formation(formation_position, formation_rotation, group)
        return self._targets['x']

class Usable(Component):
    def __init__(self, targeting_mode):
        self._targeting_mode = targeting_mode

    def choose_targets(self, entity, user_entity, mapp, menu):
        return self._targeting_mode.choose_targets(user_entity, entity, mapp, menu)

    # Returns true if the item is meant to be removed upon use
    def use(self, entity, user_entity, mapp, menu):
        targets = self.choose_targets(entity, user_entity, mapp, menu)
        return self.use_on_targets(entity, user_entity, mapp, targets, menu)

    def use_on_targets(self, entity, user_entity, mapp, targets, menu):
        return False

    def apply_melee_damage_decorators(self, entity, target, dam):
        return entity.component('Stats').apply_melee_damage_decorators(entity, target, dam)

    def apply_spell_damage_decorators(self, entity, target, dam):
        return entity.component('Stats').apply_spell_damage_decorators(entity, target, dam)


class Cost(Usable):
    def __init__(self, sp=0, usable=None):
        self._sp = sp
        self._usable = usable

    def _pay_costs(self, entity, user_entity):
        user_stats = user_entity.component('Stats')
        user_stats.consume_sp(self._sp)

    def can_pay_cost(self, entity, user_entity):
        return user_entity.component('Stats').get_value('cur_sp') >= self._sp

    def use(self, entity, user_entity, mapp, menu):
        if not self.can_pay_cost(entity, user_entity):
            return False
        self._pay_costs(entity, user_entity)
        return self._usable.use(entity, user_entity, mapp, menu)
    
class ConsumeAfter(Usable):
    def __init__(self, usable):
        self._usable = usable

    def use(self, entity, user_entity, mapp, menu):
        # Override the return value to be True
        self._usable.use(entity, user_entity, mapp, menu)
        return True

class ReturnToTown(Usable):
    def __init__(self):
        super().__init__(targeting_mode=TargetNobody())

    def use_on_targets(self, entity, user_entity, mapp, targets, menu):
        import director
        director.map_director.return_to_town()
        return False

class Heal(Usable):
    def use_on_targets(self, entity, user_entity, mapp, targets, menu):
        stats = entity.component('Stats')
        def heal_target(target):
            amount = stats.get_value('max_hp')
            target.component('Stats').apply_healing(target, mapp, amount)
        targets[0].transform(heal_target)
        return False

class Refresh(Usable):
    def use_on_targets(self, entity, user_entity, mapp, targets, menu):
        stats = entity.component('Stats')
        def refresh_target(target):
            amount = stats.get_value('max_sp')
            target.component('Stats').apply_refreshing(target, mapp, amount)
        targets[0].transform(refresh_target)
        return False

class SkillSpell(Usable):
    def __init__(self, formation, element='phys'):
        self._element = element
        super().__init__(ExcludeItems(TargetFormation(formation, directional=False, max_range=10)))

    def get_damage(self, entity, user_entity, mapp, target, raw_damage):
        return damage.Damage(user_entity, raw_damage, self._element)

    def use_on_targets(self, entity, user_entity, mapp, targets, menu):
        global message_panel
        skill_stats = entity.component('Stats')
        user_stats = user_entity.component('Stats')
        def damage_target(target):
            attacker_name = user_entity.name()
            defender_name = target.name()
            itl_over_res = user_stats.get_value('itl') / target.component('Stats').get_value('res')
            raw_damage = math.floor(itl_over_res * skill_stats.get_value('itl'))
            colour = tcod.red if attacker_name == 'Player' or defender_name == 'Player' else tcod.white
            dam = self.get_damage(entity, user_entity, mapp, target, raw_damage)
            dam = self.apply_spell_damage_decorators(user_entity, target, dam)
            actual_damage = dam.inflict(target, mapp)
            message_panel.info("{}'s spell hits {}! ({} HP)".format(attacker_name, defender_name, str(actual_damage)), colour)
        user_is_player = mapp.entity('PLAYER') == user_entity
        targets[0].where(lambda e: e != user_entity).without_components(['NPC'] if not user_is_player else []).transform(damage_target)
        return False

class TeleportToPosition(Usable):
    def __init__(self, max_range):
        formation = Formation(formation=[['x']], origin=(0,0))
        super().__init__(TargetFormation(formation, directional=False, max_range=max_range))

    def use_on_targets(self, entity, user_entity, mapp, targets, menu):
        x, y = targets[1][0]
        user_entity.component('Position').set(x, y)

class SkillStatusSpell(Usable):
    def __init__(self, formation, status_effect, status_duration):
        super().__init__(ExcludeItems(TargetFormation(formation, directional=False, max_range=10)))
        self._status_effect = status_effect
        self._status_duration = status_duration

    def get_damage(self, entity, user_entity, mapp, target, raw_damage):
        return damage.WithStatusEffect(self._status_effect, raw_damage, self._status_duration, damage.Damage(user_entity, 0))

    def use_on_targets(self, entity, user_entity, mapp, targets, menu):
        skill_stats = entity.component('Stats')
        user_stats = user_entity.component('Stats')
        def damage_target(target):
            attacker_name = user_entity.component('NPC').name() if user_entity.component('NPC') is not None else 'Player'
            defender_name = target.component('NPC').name() if target.component('NPC') is not None else 'Player'
            itl_over_res = user_stats.get_value('itl') / max(1, target.component('Stats').get_value('res'))
            strength = math.floor(itl_over_res * skill_stats.get_value('itl'))
            dam = self.get_damage(entity, user_entity, mapp, target, strength)
            colour = tcod.red if attacker_name == 'Player' or defender_name == 'Player' else tcod.white
            message_panel.info("{} inflicts {} with {} for {} turns!".format(attacker_name, defender_name, self._status_effect, str(self._status_duration)), colour)
            dam.inflict(target, mapp)
        targets[0].transform(damage_target)
        return False

class ForceTargetSelf(Usable):
    def __init__(self, usable):
        self._usable = usable

    def use_on_targets(self, entity, user_entity, mapp, targets, menu):
        pos = user_entity.component('Position').get()
        self._usable.use_on_targets(entity, user_entity, mapp, [(user_entity, pos)], menu)

class SkillRanged(Usable):
    def __init__(self, formation, max_range):
        super().__init__(ExcludeItems(TargetFormation(formation, directional=False, max_range=max_range)))

    def get_damage(self, entity, user_entity, mapp, target, raw_damage):
        return damage.Damage(user_entity, raw_damage)

    def use_on_targets(self, entity, user_entity, mapp, targets, menu):
        global message_panel
        skill_stats = entity.component('Stats')
        user_stats = user_entity.component('Stats')
        def damage_target(target):
            attacker_name = user_entity.name()
            defender_name = target.name()
            atk_over_dfn = user_stats.get_value('atk') / max(1, target.component('Stats').get_value('dfn'))
            raw_damage = math.floor(atk_over_dfn * skill_stats.get_value('atk'))
            colour = tcod.red if attacker_name == 'Player' or defender_name == 'Player' else tcod.white
            dam = self.get_damage(entity, user_entity, mapp, target, raw_damage)
            dam = self.apply_melee_damage_decorators(user_entity, target, dam)
            actual_damage = dam.inflict(target, mapp)
            message_panel.info("{}'s attack hits {}! ({} HP)".format(attacker_name, defender_name, str(actual_damage)), colour)
        user_is_player = mapp.entity('PLAYER') == user_entity
        targets[0].where(lambda e: e != user_entity).without_components(['NPC'] if not user_is_player else []).transform(damage_target)
        obstructing_ents, mov_pos = self._targeting_mode.targets(group='P')
        if mov_pos is not None:
            new_pos = mov_pos[0]
            if mapp.is_passable_for(user_entity, new_pos):
                user_entity.component('Position').set(new_pos[0], new_pos[1])
        return False

class SkillMelee(Usable):
    def __init__(self, formation):
        super().__init__(NoFriendlyFire(ExcludeItems(TargetFormation(formation, True))))

    def get_damage(self, entity, user_entity, mapp, target, raw_damage):
        return damage.Damage(user_entity, raw_damage)

    def use_on_targets(self, entity, user_entity, mapp, targets, menu):
        global message_panel
        skill_stats = entity.component('Stats')
        user_stats = user_entity.component('Stats')
        def damage_target(target):
            attacker_name = user_entity.name()
            defender_name = target.name()
            atk_over_dfn = user_stats.get_value('atk') / max(1, target.component('Stats').get_value('dfn'))
            raw_damage = math.floor(atk_over_dfn * skill_stats.get_value('atk'))
            colour = tcod.red if attacker_name == 'Player' or defender_name == 'Player' else tcod.white
            dam = self.get_damage(entity, user_entity, mapp, target, raw_damage)
            dam = self.apply_melee_damage_decorators(user_entity, target, dam)
            actual_damage = dam.inflict(target, mapp)
            message_panel.info("{}'s attack hits {}! ({} HP)".format(attacker_name, defender_name, str(actual_damage)), colour)
        targets[0].transform(damage_target)
        obstructing_ents, mov_pos = self._targeting_mode.targets(group='P')
        if mov_pos is not None:
            new_pos = mov_pos[0]
            if mapp.is_passable_for(user_entity, new_pos):
                user_entity.component('Position').set(new_pos[0], new_pos[1])
        return False

class Mod(Component):
    def __init__(self):
        super().__init__()

class Item(Component):
    def __init__(self, name, description):
        self._name = name
        self._description = description

    def description(self):
        return self._description

    def item_world_floor(self, entity):
        return entity.component('Stats').get_base('level') + 1

    def name(self):
        return self._name

class Equipment(Component):
    def __init__(self, mod_slots=[]):
        self._mod_slots = mod_slots

    def save_subtype_string(self):
        return 'EQUIPMENT'

    def save(self):
        obj = super().save()
        obj['mod_slots'] = [i.save() if i is not None else 'None' for i in self._mod_slots]
        return obj

    def handle_event(self, entity, event, resident_map):
        for mod in self._mod_slots:
            if mod is None:
                continue
            mod.handle_event(event, resident_map)

    def attach_mod(self, item_entity, mod_entity, index, resident_map):
        if index < 0 or index >= len(self._mod_slots):
            return
        if self._mod_slots[index] is not None:
            self.detach_mod(item_entity, index, resident_map)
        mod_stats = mod_entity.component('Stats')
        item_stats = item_entity.component('Stats')
        for stat in Stats.all_stats:
            stat_value = mod_stats.get_value(stat)
            item_stats.add_additive_modifier(stat, stat_value)
        self._mod_slots[index] = mod_entity
        return

    def mod_slots(self):
        return self._mod_slots

    def detach_mod(self, item_entity, index, resident_map):
        if index < 0 or index >= len(self._mod_slots) or self._mod_slots[index] is None:
            return
        mod_entity = self._mod_slots[index]
        mod_stats = mod_entity.component('Stats')
        item_stats = item_entity.component('Stats')
        for stat in Stats.all_stats:
            stat_value = mod_stats.get_value(stat)
            item_stats.sub_additive_modifier(stat, stat_value)
        return

    def equip_to(self, item_entity, to_entity, resident_map):
        item_stats = item_entity.component('Stats')
        entity_stats = to_entity.component('Stats')
        for stat in Stats.all_stats:
            entity_stats.add_base(stat, item_stats.get_value(stat))
        resident_map.entities().transform(lambda ent: \
                                          ent.handle_event(("ITEM_EQUIPPED", (to_entity, item_entity)), resident_map))

    def unequip_from(self, item_entity, to_entity, resident_map):
        item_stats = item_entity.component('Stats')
        entity_stats = to_entity.component('Stats')
        for stat in Stats.all_stats:
            entity_stats.sub_base(stat, item_stats.get_value(stat))
        resident_map.entities().transform(lambda ent: \
                                          ent.handle_event(("ITEM_UNEQUIPPED", (to_entity, item_entity)), resident_map))

class Descendable(Component):
    def __init__(self, predicate=None):
        super().__init__()
        self._predicate = predicate
        self._can_descend = False if predicate is not None else True

    def can_descend(self):
        return self._can_descend

    def handle_event(self, entity, event, resident_map):
        if self._predicate is not None and self._predicate(entity, event, resident_map) == True:
            self._can_descend = True
        return False

class Stats(Component):
    primary_stats = set([
        'max_hp',
        'max_sp',
        'atk',
        'dfn',
        'itl',
        'res',
        'spd',
        'hit',
    ])

    cur_stats = set([
        'cur_hp',
        'cur_sp',
        'cur_exp',
    ])

    damage_stats = set([
        'fire_dam',
        'ice_dam',
        'lght_dam',
        'phys_dam',
    ])

    resistance_stats = set([
        'fire_res',
        'ice_res',
        'lght_res',
        'phys_res',
    ])

    all_stats = set([
        'max_hp',
        'cur_hp',
        'max_sp',
        'cur_sp',
        'atk',
        'dfn',
        'itl',
        'res',
        'spd',
        'hit',
        'phys_res',
        'fire_res',
        'ice_res',
        'lght_res',
        'phys_dam',
        'fire_dam',
        'ice_dam',
        'lght_dam',
        'cur_exp',
        'max_exp',
        'level',
        'deathblow',
        'lifedrain',
        'hp_regen',
        'sp_regen',
        'souldrain',
        'self_poison',
        'boost_int',
        'boost_atk',
        'poison_heal',
        'sp_usage_heals',
        'blood_magic',
        'assault',
        'improve_fire_aoe',
        'ice_souldrain',
        'lightning_lifedrain',
        'fire_assault',
        'assault_regen_hp',
        'cleave_poison',
        'ice_mind_break',
        'mindbreak_paralyzes',
        'improve_dash_length',
        'deathblow_multiplier',
        'itl_becomes_atk',
        'atk_becomes_itl',
        'max_hp_pc_penalty',
        'deathblow_multiplier_vs_paralyze',
        'exp_granted_bonus_multiplier',
    ])

    REGEN_FREQUENCY = 6
    EXP_YIELD_SCALE = 2.0

    """
    There is no need to initialise all the base_stats -- any ones left out will
    be zero by default
    """
    def __init__(self, base_stats, stats_gained_on_level=None, stat_inc_per_level=0.2):
        self._stat_inc_per_level = stat_inc_per_level
        self._regen_counter = 0
        self._stats = {}
        if stats_gained_on_level is None:
            stats_gained_on_level = list((Stats.primary_stats - set(['max_sp'])) | Stats.resistance_stats | Stats.damage_stats)
        self._stats_gained_on_level = list(stats_gained_on_level)
        self._modifiers = {}
        for stat in Stats.all_stats:
            self._stats[stat] = 0
            self._modifiers[stat] = {
                'additive': 0,
                'multiplicative': 1.0
            }
        self._status_effects = {}
        for (stat, value) in base_stats.items():
            self._stats[stat] = value
        self._base_stats = copy_dict(self._stats)

    def save_subtype_string(self):
        return 'STATS'

    def save(self):
        obj = super().save()
        obj['stats'] = self._stats
        obj['stat_inc_per_level'] = self._stat_inc_per_level
        obj['base_stats'] = self._base_stats
        obj['stats_gained_on_level'] = self._stats_gained_on_level
        obj['modifiers'] = self._modifiers
        obj['status_effects'] = self._status_effects
        return obj

    def apply_melee_damage_decorators(self, entity, target, dam):
        lifedrain = self.get_value('lifedrain')
        deathblow = self.get_value('deathblow')
        target_paralysed = target.component('Stats').has_status('PARALYZE')
        if target_paralysed:
            deathblow *= (1 if self.get('deathblow_multiplier_vs_paralyze') == 0 else self.get('deathblow_multiplier_vs_paralyze'))
        if deathblow > 0:
            dam = damage.Chance(deathblow / 100, damage.WithDeathblow(dam), dam)
        if lifedrain > 0:
            dam = damage.WithLifeDrain(dam, lifedrain / 100)
        return dam

    def apply_spell_damage_decorators(self, entity, target, dam):
        souldrain = self.get_value('souldrain')
        if souldrain > 0:
            dam = damage.WithSoulDrain(dam, souldrain / 100)
        return dam

    def exp_yield(self):
        multi = 1 + self.get('exp_granted_bonus_multiplier')
        return multi * math.floor(Stats.EXP_YIELD_SCALE * sum([self._stats[stat] for stat in Stats.primary_stats - set(['max_hp', 'max_sp'])]))

    def increase_level(self, num):
        self.add_base('max_exp', num * 90)
        self.add_base('level', num)
        for stat in self._stats_gained_on_level:
            self.add_base(stat, self._base_stats[stat] * num * self._stat_inc_per_level)

    def grant_exp(self, exp):
        message_panel.info("Gained {} EXP".format(exp), tcod.yellow)
        self.add_base('cur_exp', exp)
        levels = 0
        while self.get_base('cur_exp') >= self.get_base('max_exp'):
            excess = self.sub_base('cur_exp', self.get_base('max_exp'))
            self.set_base('cur_exp', excess)
            self.increase_level(1)
            levels += 1
        if levels > 0:
            message_panel.info("Level up!" + ("" if levels == 1 else " x{}".format(levels)), tcod.yellow)
            message_panel.info("You are now level {}".format(self.get_base('level') + 1), tcod.yellow)

    def _self_poison(self, entity, resident_map):
        ent_name = entity.component('NPC').name() if entity.component('NPC') else 'Player'
        self_poison = self.get_value('self_poison') > 0
        if self_poison and entity.component('Item') is None:
            if not self.has_status('POISON'):
                message_panel.info('{} is poisoned!'.format(ent_name))
            self.inflict_status('POISON', strength=1, duration=5)

    def handle_event(self, entity, event, resident_map):
        event_type, event_data = event
        ent_name = entity.component('NPC').name() if entity.component('NPC') else 'Player'
        removed = []
        if event_type == 'NPC_TURN':
            self._self_poison(entity, resident_map)
            sp_regen = self.get('sp_regen')
            hp_regen = self.get('hp_regen')
            if sp_regen > 0 or hp_regen > 0:
                self._regen_counter = (self._regen_counter + 1) % Stats.REGEN_FREQUENCY
                if self._regen_counter == 0:
                    if sp_regen > 0:
                        self.apply_refreshing(entity, resident_map, sp_regen)
                    if hp_regen > 0:
                        self.apply_healing(entity, resident_map, hp_regen)
            assault_regen_hp = self.get('assault_regen_hp')
            if assault_regen_hp > 0 and self.has_status('ASSAULT'):
                self.apply_healing(entity, resident_map, 0.01 * assault_regen_hp * self.get_value('max_hp'))
            if self.has_status('REGEN'):
                self.apply_healing(entity, resident_map, 0.05 * self.get_value('max_hp'))
            if self.has_status('POISON'):
                psn_dam_amt = math.floor(0.05 * self.get_value('max_hp'))
                psn_dam_threshold = 0.05 # Poison can only deal damage until the affected reaches 5% HP
                poison_heal = self.get_value('poison_heal') > 0
                if poison_heal:
                    colour = tcod.green if ent_name == 'Player' else tcod.white
                    self.apply_healing(entity, resident_map, psn_dam_amt / 50)
                else:
                    # Only damage the character if they wouldn't have less than the poison damage threshold
                    if self.get_value('cur_hp') / self.get_value('max_hp') - 0.05 >= psn_dam_threshold:
                        colour = tcod.red if ent_name == 'Player' else tcod.white
                        message_panel.info("{} takes damage from poison ({} HP)".format(ent_name, psn_dam_amt), colour)
                        self.deal_damage(entity, resident_map, psn_dam_amt)
            for status_effect in self._status_effects.keys():
                self._status_effects[status_effect] -= 1
                if self._status_effects[status_effect] == 0:
                    removed.append(status_effect)
            for status_effect in removed:
                self._status_effects.pop(status_effect, None)
                self._lost_status(entity, resident_map, status_effect)
                status_lost_event = ('LOST_STATUS_EFFECT', {'status_effect': status_effect, 'entity_ident': entity.ident()})
                resident_map.entities().transform(lambda ent: ent.handle_event(status_lost_event, resident_map))

    def _lost_status(self, entity, resident_map, status):
        ent_name = entity.component('NPC').name() if entity.component('NPC') else 'Player'
        colour = tcod.red if ent_name == 'Player' else tcod.white
        if status == 'WEAKEN':
            message_panel.info("{} is no longer weakened".format(ent_name), colour)
            self.add_multiplicative_modifier('atk', 0.5)
        elif status == 'GUARD_BREAK':
            message_panel.info("{} is no longer guard-broken".format(ent_name), colour)
            self.add_multiplicative_modifier('dfn', 0.3)
        elif status == 'MIND_BREAK':
            message_panel.info("{} is no longer mind-broken".format(ent_name), colour)
            self.add_multiplicative_modifier('res', 0.3)
        elif status == 'STONESKIN':
            message_panel.info("{} no longer has stoneskin".format(ent_name), colour)
            self.sub_multiplicative_modifier('dfn', 0.5)
        elif status == 'ASSAULT':
            message_panel.info("{} no longer has assault".format(ent_name), colour)
            self.sub_additive_modifier('phys_dam', 20)
            self.sub_additive_modifier('fire_dam', 20)
            self.sub_additive_modifier('ice_dam', 20)
            self.sub_additive_modifier('lght_dam', 20)
            self.add_additive_modifier('phys_res', 20)
            self.add_additive_modifier('fire_res', 20)
            self.add_additive_modifier('ice_res', 20)
            self.add_additive_modifier('lght_res', 20)
        elif status == 'INVINCIBLE':
            message_panel.info("{} is no longer invincible".format(ent_name), colour)
            self.sub_multiplicative_modifier('res', 3)
        elif status == 'UNSTOPPABLE':
            message_panel.info("{} is no longer unstoppable".format(ent_name), colour)
            self.sub_multiplicative_modifier('dfn', 3)
        else:
            message_panel.info("{} no longer has {}".format(ent_name, status), colour)

    def status_effects(self):
        return self._status_effects.keys()

    def has_status(self, status):
        return status in self._status_effects

    def inflict_status(self, status, strength, duration):
        abort = status in self._status_effects
        self._status_effects[status] = duration
        if abort:
            return
        if status == 'WEAKEN':
            self.sub_multiplicative_modifier('atk', 0.5)
        if status == 'GUARD_BREAK':
            self.sub_multiplicative_modifier('dfn', 0.3)
        if status == 'MIND_BREAK':
            self.sub_multiplicative_modifier('res', 0.3)
        if status == 'STONESKIN':
            self.add_multiplicative_modifier('dfn', 0.5)
        if status == 'ASSAULT':
            self.add_additive_modifier('phys_dam', 20)
            self.add_additive_modifier('fire_dam', 20)
            self.add_additive_modifier('ice_dam', 20)
            self.add_additive_modifier('lght_dam', 20)
            self.sub_additive_modifier('phys_res', 20)
            self.sub_additive_modifier('fire_res', 20)
            self.sub_additive_modifier('ice_res', 20)
            self.sub_additive_modifier('lght_res', 20)
        if status == 'INVINCIBLE':
            self.add_multiplicative_modifier('res', 3)
        if status == 'UNSTOPPABLE':
            self.add_multiplicative_modifier('dfn', 3)

    def apply_healing(self, entity, resident_map, amount):
        amount = min(math.floor(amount), self.get_value('max_hp') - self.get_value('cur_hp'))
        self.add_base('cur_hp', amount)

    def apply_refreshing(self, entity, resident_map, amount):
        amount = min(math.floor(amount), self.get_value('max_sp') - self.get_value('cur_sp'))
        self.add_base('cur_sp', amount)

    def consume_sp(self, entity, resident_map, amount):
        if self.sub_base('cur_sp', amount) <= 0:
            sp_usage_heals = self.get_value('sp_usage_heals') > 0
            sp_consumed = min(self._sp, self.get_base('cur_sp'))
            if sp_usage_heals:
                self.apply_healing(user_entity, settings.current_map, sp_consumed)

    def deal_damage(self, entity, resident_map, damage):
        resident_map.entities().transform(lambda ent: ent.handle_event(("DEALT_DAMAGE", (entity, damage)), resident_map))
        player = resident_map.entity('PLAYER')
        if self.sub_base('cur_hp', damage) <= 0:
            player.component('Stats').grant_exp(self.exp_yield())
            resident_map.entities().transform(lambda ent: ent.handle_event(("ENTITY_KILLED", entity), resident_map))
            resident_map.remove_entity(entity.ident())

    """
    Just for convenience
    """
    def get(self, stat):
        return self.get_value(stat)

    def get_value(self, stat):
        if stat in ['atk', 'itl']:
            atk_becomes_itl = self.get('atk_becomes_itl') > 0
            itl_becomes_atk = self.get('itl_becomes_atk') > 0
            if not (atk_becomes_itl and itl_becomes_atk):
                if stat == 'atk' and atk_becomes_itl:
                    return self.get('itl')
                if stat == 'itl' and itl_becomes_atk:
                    return self.get('atk')
        if stat in ['level', 'cur_exp', 'max_exp', 'cur_hp', 'cur_sp']:
            return self.get_base(stat)
        boost_stat = self._stats.get('boost_{}'.format(stat))
        boost_factor = (boost_stat if boost_stat is not None else 0) * 1.333
        if stat == 'spd' and self.has_status('PARALYZE'):
            return 0
        deathblow_mult = 1 if stat != 'deathblow' else 1 + self.get('deathblow_multiplier')
        max_hp_mult = 1 if stat != 'max_hp' else (100 - self.get('max_hp_pc_penalty'))/100
        return int((self.get_base(stat) * (1 + boost_factor) + self._modifiers[stat]['additive'])
                   * self._modifiers[stat]['multiplicative'] * deathblow_mult * max_hp_mult)

    def get_additive_modifier(self, stat):
        return self._modifiers[stat]['additive']

    def get_multiplicative_modifier(self, stat):
        return self._modifiers[stat]['multiplicative']

    def get_base(self, stat):
        return self._stats[stat]

    def set_base(self, stat, value):
        self._stats[stat] = value
        return self._stats[stat]

    def add_base(self, stat, value):
        return self.set_base(stat, self._stats[stat] + value)

    def sub_base(self, stat, value):
        return self.set_base(stat, self._stats[stat] - value)

    def set_additive_modifier(self, stat, value):
        self._modifiers[stat]['additive'] = value
        return self._modifiers[stat]['additive']

    def add_additive_modifier(self, stat, value):
        return self.set_additive_modifier(stat, self._modifiers[stat]['additive'] + value)

    def sub_additive_modifier(self, stat, value):
        return self.set_additive_modifier(stat, self._modifiers[stat]['additive'] - value)

    def set_multiplicative_modifier(self, stat, value):
        self._modifiers[stat]['multiplicative'] = value
        return self._modifiers[stat]['multiplicative']

    def add_multiplicative_modifier(self, stat, value):
        return self.set_multiplicative_modifier(stat, self._modifiers[stat]['multiplicative'] + value)

    def sub_multiplicative_modifier(self, stat, value):
        return self.set_multiplicative_modifier(stat, self._modifiers[stat]['multiplicative'] - value)

class Position(Component):
    def __init__(self, x, y):
        self._x = x
        self._y = y

    def save_subtype_string(self):
        return 'POSITION'

    def save(self):
        obj = super().save()
        obj['x'] = self._x
        obj['y'] = self._y
        return obj

    def get(self):
        return (self._x, self._y)

    def set(self, x=None, y=None):
        if x is not None:
            self._x = x
        if y is not None:
            self._y = y

    def add(self, x=None, y=None):
        if x is not None:
            self._x += x
        if y is not None:
            self._y += y

    def sub(self, x=None, y=None):
        if x is not None:
            self._x -= x
        if y is not None:
            self._y -= y

class Render(Component):
    def __init__(self, character, colour=tcod.white):
        self._character = character
        self._colour = colour
        self._status_render_idx = -1

    def character(self):
        return self._character

    def colour(self):
        return self._colour

    def _status_chars(self, entity):
        stats = entity.component('Stats')
        if not stats:
            return []
        return [eff[0] for eff in stats.status_effects()]

    def render(self, entity, console, origin):
        x, y = origin
        old_fg = console.default_fg
        console.default_fg = self.colour()
        self._status_render_idx = -1 if self._status_render_idx >= len(self._status_chars(entity)) else self._status_render_idx
        if self._status_render_idx == -1:
            console.print_(x=x, y=y, string=self.character())
        else:
            console.print_(x=x, y=y, string=self._status_chars(entity)[self._status_render_idx])
        self._status_render_idx += 1
        if self._status_render_idx >= len(self._status_chars(entity)):
            self._status_render_idx = -1
        console.default_fg = old_fg

'''
if_true and if_false are of the form (char, tcod_colour)
if trigger_once is false, the render state will match that of the predicate
'''
class ConditionalRender(Render):
    def __init__(self, if_true, if_false, predicate, trigger_once=True):
        self._if_true = if_true
        self._if_false = if_false
        self._predicate = predicate
        self._flag = False
        self._trigger_once = trigger_once

    def character(self):
        if self._flag:
            return self._if_true[0]
        return self._if_false[0]

    def colour(self):
        if self._flag:
            return self._if_true[1]
        return self._if_false[1]

    def handle_event(self, entity, event, resident_map):
        predicate_value = self._predicate(entity, event, resident_map)
        if predicate_value == True:
            self._flag = True
        if not self._trigger_once and predicate_value == False:
            self._flag = False
        return False


class Inventory(Component):
    def __init__(self, items=[]):
        self._items = items

    def save_subtype_string(self):
        return 'INVENTORY'

    def save(self):
        def save_items():
            return [i.save() for i in self._items]

        obj = super().save()
        obj['items'] = save_items()
        return obj

    def items(self):
        return EntityListView(self._items)

    def add(self, item):
        self._items.append(item)

    def remove(self, item):
        self._items.remove(item)

    def pick_up(self, entity, item, resident_map):
        def pick_up_item(itm):
            self.add(itm)
            resident_map.remove_entity(itm.ident())
        resident_map.entities().with_component('Item').where(lambda itm: itm == item).transform(pick_up_item)

    def drop(self, entity, item, resident_map, position):
        def drop_item(itm):
            x, y = position
            itm.component('Position').set(x, y)
            resident_map.add_entity(itm)
            self.remove(item)
        self.items().where(lambda itm: itm == item).transform(drop_item)


class EquipmentSlots(Component):
    def __init__(self, slots):
        self._slots = {}
        for slot in slots:
            if self._slots.get(slot) is None:
                self._slots[slot] = []
            self._slots[slot].append(None)

    def save_subtype_string(self):
        return 'EQUIPMENTSLOTS'

    def save(self):
        obj = super().save()
        obj['slots'] = {}
        for k, v in self._slots.items():
            obj['slots'][k] = [i.save() if i is not None else 'None' for i in self._slots[k]]
        return obj

    def slots(self):
        return self._slots

    def equip(self, entity, item_entity, slot, resident_map):
        slot_type, slot_index = slot
        item = item_entity.component('Equipment')
        equipped_item = self._slots[slot_type][slot_index]
        if equipped_item is not None:
            self.unequip(entity, equipped_item, slot, resident_map)
        item.equip_to(item_entity, entity, resident_map)
        self._slots[slot_type][slot_index] = item_entity
        inventory = entity.component('Inventory')
        inventory.remove(item_entity)

    def unequip(self, entity, item_entity, slot, resident_map):
        slot_type, slot_index = slot
        item = item_entity.component('Equipment')
        if self._slots[slot_type][slot_index] is None:
            return
        self._slots[slot_type][slot_index] = None
        item.unequip_from(item_entity, entity, resident_map)
        inventory = entity.component('Inventory')
        inventory.add(item_entity)

    def handle_event(self, entity, event, resident_map):
        for items_in_slot in self._slots.values():
            for item in items_in_slot:
                if item is None:
                    continue
                if item.handle_event(event, resident_map):
                    return True
        return False

class Combat(Component):
    def __init__(self):
        pass

    def attack(self, entity, resident_map, position):
        def do_attack(ent):
            attacker_name = 'Player'
            defender_name = 'Player'
            npc = entity.component('NPC')
            ent_npc = ent.component('NPC')
            if npc is not None:
                attacker_name = npc.name()
            if ent_npc is not None:
                defender_name = ent_npc.name()
            stats = ent.component('Stats')
            my_stats = entity.component('Stats')
            raw_amount = math.floor(20 * my_stats.get_value('atk') / stats.get_value('dfn'))
            dam = damage.Damage(entity, raw_amount)
            dam = entity.component('Stats').apply_melee_damage_decorators(entity, ent, dam)
            amount = dam.inflict(ent, resident_map)
            colour = tcod.red if attacker_name == 'Player' or defender_name == 'Player' else tcod.white
            settings.message_panel.info("{} attacks {}! ({} HP)".format(attacker_name, defender_name, str(int(amount))), colour)

        resident_map.entities().without_components(['Item']).with_all_components(['Stats', 'Position']).where(lambda ent : ent.component('Position').get() == position).transform(do_attack)

class NPC(Component):
    def __init__(self, name):
        self._name = name

    def name(self):
        return self._name

class AI(Component):
    def __init__(self):
        self._delayed_attack = None
        self._delayed_targets = None
        self._delay = None

    def _handle_delayed_attack(self, entity, resident_map):
        self._delay -= 1
        if self._delay > 0:
            return False
        targeted_positions = self._delayed_targets[1]
        targets = resident_map.entities().without_components(['Item']).with_component('Position')\
                                            .where(lambda ent: ent.component('Position').get() in targeted_positions), targeted_positions
        self._delayed_attack.use_on_targets(entity, entity, resident_map, targets, None)
        self._delay = None
        self._delayed_attack = None
        return False

    def handle_event(self, entity, event, resident_map):
        event_type, event_data = event
        is_paralyzed = entity.component('Stats').has_status('PARALYZE')
        if event_type == 'ENTITY_KILLED' and event_data == entity and self._delayed_targets is not None:
            targeted_positions = self._delayed_targets[1]
            resident_map.remove_threatened_positions(entity.ident())
            return False
        if event_type == 'NPC_TURN':
            if is_paralyzed:
                return False
            elif self._delayed_attack is not None:
                if self._handle_delayed_attack(entity, resident_map) is False:
                    return False
        return self._handle_event(entity, event, resident_map)

    def _handle_event(self, entity, event, resident_map):
        return False

    def _step_towards_player(self, entity, resident_map):
        passmap = resident_map.passability_map_for(entity)
        player = resident_map.entity('PLAYER')
        player_pos = player.component('Position').get()
        ent_pos = entity.component('Position').get()
        path = find_path(passmap, ent_pos, player_pos)
        if len(path) > 1 and not player_pos == path[1]:
            entity.component('Position').set(path[1][0], path[1][1])

    def _step_away_from_player(self, entity, resident_map):
        passmap = resident_map.passability_map_for(entity)
        player = resident_map.entity('PLAYER')
        player_pos = player.component('Position').get()
        ent_pos = entity.component('Position').get()
        (x, y) = ent_pos
        dx, dy = (player_pos[0] - ent_pos[0], player_pos[1] - ent_pos[1])
        dx, dy = (-1 if dx < 0 else 1 if dx > 0 else 0, -1 if dy < 0 else 1 if dy > 0 else 0)
        if resident_map.is_passable_for(entity, (x-dx, y-dy)):
            entity.component('Position').sub(x=dx, y=dy)

    def _step_randomly(self, entity, resident_map):
        x, y = entity.component('Position').get()
        possible_steps = [(dx, dy) for dx in range(-1, 2) for dy in range(-1, 2) \
                          if resident_map.is_passable_for(entity, (x+dx, y+dy))]
        if len(possible_steps) != 0:
            dx, dy = random.choice(possible_steps)
            entity.component('Position').add(x=dx, y=dy)

    def _distance_to_player(self, entity, resident_map):
        player = resident_map.entity('PLAYER')
        my_position = entity.component('Position').get()
        player_position = player.component('Position').get()
        return distance(player_position, my_position)

    def _perform_attack_against(self, entity, target, resident_map):
        my_combat = entity.component('Combat')
        my_combat.attack(entity, resident_map, target.component('Position').get())

    def _perform_delayed_attack_against(self, entity, target, resident_map, usable, delay):
        self._delayed_attack = usable
        self._delay = delay
        self._delayed_targets = usable.choose_targets(entity, entity, resident_map, None)
        resident_map.add_threatened_positions(self._delayed_targets[1], delay, entity.ident())

class Neutral(AI):
    def __init__(self, on_chat=None, on_attacked=None):
        super().__init__()
        self._on_chat = on_chat
        self._on_attacked = on_attacked

    def _handle_event(self, entity, event, resident_map):
        event_type, event_data = event
        if event_type == 'PLAYER_CHAT_WITH' and event_data == entity.ident() and self._on_chat is not None:
            self._on_chat(self, entity, event, resident_map)
            return True
        if event_type == 'ENTITY_DAMAGED_BY' and event_data[0] == entity.ident() and self._on_attacked is not None:
            self._on_attacked(self, entity, event, resident_map)
            return False

class Shopkeeper(Neutral):
    def __init__(self):
        super().__init__(on_chat=Shopkeeper.on_chat, on_attacked=Shopkeeper.on_attacked)
        self._times_attacked = 0

    def Apocalypse():
        return SkillSpell(formation=Formation(origin=(10,10), formation=[
            ['x' for _ in range(20)] for __ in range(20)
        ]))

    def on_attacked(self, entity, event, resident_map):
        self._times_attacked += 1
        if self._times_attacked >= 3:
            settings.message_panel.info('\"You\'ve REALLY done it now...\"', tcod.green)
            entity.set_component('AI', Hostile(primary_skill=Shopkeeper.Apocalypse(), primary_skill_range=9999))
        else:
            settings.message_panel.info(random.choice(['\"Ouch!\"', '\"Stop it!\"', '\"Hey!\"']), tcod.green)

    def _choose_item_to_buy(self, entity):
        choose_item_menu = Menu({
            'ChooseItemPanel': ((0,0), ChooseItemPanel(entity, [], title="\"What'll it be today?\" (Each item costs 1 town portal)"))
        }, ['ChooseItemPanel'])
        chosen_item = choose_item_menu.run(settings.root_console)
        return chosen_item

    def _choose_town_portal(self, entity):
        choose_item_menu = Menu({
            'ChooseItemPanel': ((0,0), ChooseItemPanel(entity, ["TownPortal"], title="\"That'll be one town portal\""))
        }, ['ChooseItemPanel'])
        chosen_item = choose_item_menu.run(settings.root_console)
        return chosen_item

    def on_chat(self, entity, event, resident_map):
        import director
        player = resident_map.entity('PLAYER')
        bought_item = self._choose_item_to_buy(entity)
        if bought_item is None:
            settings.message_panel.info("\"Aww, gimme a break...\"", tcod.green)
            return
        town_portal = self._choose_town_portal(player)
        if town_portal is None:
            settings.message_panel.info("\"Aww, gimme a break...\"", tcod.green)
            return
        item_name = bought_item.component('Item').name()
        entity.component('Inventory').remove(bought_item)
        player.component('Inventory').remove(town_portal)
        player.component('Inventory').add(bought_item)
        settings.message_panel.info("\"Thank you for your patronage!\"", tcod.green)
        settings.message_panel.info("\"...sucker.\"", tcod.green)

class UptierShopkeeper(Neutral):
    def __init__(self):
        super().__init__(on_chat=UptierShopkeeper.on_chat, on_attacked=UptierShopkeeper.on_attacked)
        self._times_attacked = 0

    def Apocalypse():
        return SkillSpell(formation=Formation(origin=(10,10), formation=[
            ['x' for _ in range(20)] for __ in range(20)
        ]))

    def on_attacked(self, entity, event, resident_map):
        self._times_attacked += 1
        if self._times_attacked >= 3:
            settings.message_panel.info('\"You\'ve REALLY done it now...\"', tcod.green)
            entity.set_component('AI', Hostile(primary_skill=UptierShopkeeper.Apocalypse(), primary_skill_range=9999))
        else:
            settings.message_panel.info(random.choice(['\"Ouch!\"', '\"Stop it!\"', '\"Hey!\"']), tcod.green)

    def _choose_charred_skull(self, entity):
        title = "Give a charred skull to:\n - Reset your dungeon progression, and\n - Uptier all loot and enemies\n\"Your charred skull, please... hehehe...\""
        choose_item_menu = Menu({
            'ChooseItemPanel': ((0,0), ChooseItemPanel(entity, ["CharredSkull"], title=title))
        }, ['ChooseItemPanel'])
        chosen_item = choose_item_menu.run(settings.root_console)
        return chosen_item

    def on_chat(self, entity, event, resident_map):
        import director
        player = resident_map.entity('PLAYER')
        charred_skull = self._choose_charred_skull(player)
        if charred_skull is None:
            settings.message_panel.info("\"Aww, gimme a break...\"", tcod.green)
            return
        player.component('Inventory').remove(charred_skull)
        settings.loot_tier += 1
        settings.monster_tier += 1
        settings.main_dungeon_lowest_floor = 1
        settings.message_panel.info("\"Good luck, traveller...\"", tcod.green)

class Mailman(Neutral):
    def __init__(self):
        super().__init__(on_chat=Mailman.on_chat, on_attacked=Mailman.on_attacked)
        self._times_attacked = 0

    def Apocalypse():
        return SkillSpell(formation=Formation(origin=(10,10), formation=[
            ['x' for _ in range(20)] for __ in range(20)
        ]))

    def on_attacked(self, entity, event, resident_map):
        self._times_attacked += 1
        if self._times_attacked >= 3:
            settings.message_panel.info('\"You\'ve REALLY done it now...\"', tcod.green)
            entity.set_component('AI', Hostile(primary_skill=Mailman.Apocalypse(), primary_skill_range=9999))
        else:
            settings.message_panel.info(random.choice(['\"Ouch!\"', '\"Stop it!\"', '\"Hey!\"']), tcod.green)

    def _handle_event(self, entity, event, resident_map):
        import load
        super()._handle_event(entity, event, resident_map)

    def on_chat(self, entity, event, resident_map):
        import director
        player = resident_map.entity('PLAYER')
        settings.message_panel.info('\"Let me see if there are any deliveries for you...\"', tcod.green)
        if settings.pending_items_received == []:
            settings.message_panel.info('\"Nope, nothing for you at the moment\"', tcod.green)
        else:
            settings.message_panel.info('\"Here you go!\"', tcod.green)
        # Receive and handle network-sourced events
        for item in settings.pending_items_received:
            px, py = resident_map.entity('PLAYER').component('Position').get()
            item.component('Position').set(px, py)
            # item.generate_new_ident() # this might not work if we have mods, etc.
            resident_map.add_entity(item)
        settings.pending_items_received = []

class ItemWorldClerk(Neutral):
    def __init__(self):
        super().__init__(on_chat=ItemWorldClerk.on_chat, on_attacked=ItemWorldClerk.on_attacked)
        self._times_attacked = 0

    def Apocalypse():
        return SkillSpell(formation=Formation(origin=(10,10), formation=[
            ['x' for _ in range(20)] for __ in range(20)
        ]))

    def on_attacked(self, entity, event, resident_map):
        self._times_attacked += 1
        if self._times_attacked >= 3:
            settings.message_panel.info('\"You\'ve REALLY done it now...\"', tcod.green)
            entity.set_component('AI', Hostile(primary_skill=ItemWorldClerk.Apocalypse(), primary_skill_range=9999))
        else:
            settings.message_panel.info(random.choice(['\"Ouch!\"', '\"Stop it!\"', '\"Hey!\"']), tcod.green)

    def on_chat(self, entity, event, resident_map):
        import director
        player = resident_map.entity('PLAYER')
        choose_item_menu = Menu({
            'ChooseItemPanel': ((0,0), ChooseItemPanel(player, []))
        }, ['ChooseItemPanel'])
        chosen_item = choose_item_menu.run(settings.root_console)
        if chosen_item is None:
            return True
        item_name = chosen_item.component('Item').name()
        settings.message_panel.info("The item world clerk opens a portal to the {} item world".format(item_name), tcod.green)
        settings.message_panel.info('\"Have fun -- and try not to die!\"'.format(item_name), tcod.green)
        settings.set_item_world(chosen_item)
        director.map_director.descend()

class Slow(AI):
    def __init__(self, ai, period=2):
        super().__init__()
        self._ai = ai
        self._turn_count = 0
        self._period = period

    def _handle_event(self, entity, event, resident_map):
        event_type, _ = event
        if event_type == 'NPC_TURN':
            if self._ai._delayed_attack is not None:
                res = self._ai._handle_delayed_attack(entity, resident_map)
                if res is not None:
                    return res
            self._turn_count = (self._turn_count + 1) % self._period
            if self._turn_count == 0:
                return self._ai._handle_event(entity, event, resident_map)
            return False
        return self._ai._handle_event(entity, event, resident_map)

class Hostile(AI):
    def __init__(self, aggro_range=5, primary_skill=None, primary_skill_range=None, immobile=False, keep_at_range=0, primary_skill_delay=1):
        super().__init__()
        self._ai_status = "IDLE"
        self._aggro_range = aggro_range
        self._primary_skill = primary_skill
        self._primary_skill_range = primary_skill_range
        self._primary_skill_delay = primary_skill_delay
        self._immobile = immobile
        self._keep_at_range = keep_at_range

    def _handle_aggro(self, entity, event, resident_map):
        player = resident_map.entity('PLAYER')
        attack_range = 2 if self._primary_skill_range is None else self._primary_skill_range
        if self._primary_skill is None and self._distance_to_player(entity, resident_map) < attack_range:
            self._perform_attack_against(entity, player, resident_map)
        elif not self._immobile and self._distance_to_player(entity, resident_map) < self._keep_at_range:
                self._step_away_from_player(entity, resident_map)
        elif self._primary_skill is not None and \
             (self._primary_skill_range is None or self._distance_to_player(entity, resident_map) <= self._primary_skill_range):
            self._perform_delayed_attack_against(entity, player, resident_map, self._primary_skill, self._primary_skill_delay)
        elif not self._immobile:
            self._step_towards_player(entity, resident_map)

    def _handle_idle(self, entity, event, resident_map):
        player = resident_map.entity('PLAYER')
        my_position = entity.component('Position').get()
        player_position = player.component('Position').get()
        if player is not None and distance(player_position, my_position) <= self._aggro_range:
            self._ai_status = 'AGGRO'
            self._handle_aggro(entity, event, resident_map)
        elif not self._immobile:
            self._step_randomly(entity, resident_map)

    def _handle_event(self, entity, event, resident_map):
        event_type, event_data = event
        if event_type == 'NPC_TURN':
            if self._ai_status == 'IDLE':
                self._handle_idle(entity, event, resident_map)
            elif self._ai_status == 'AGGRO':
                self._handle_aggro(entity, event, resident_map)
        return False

class PlayerLogic(Component):
    def __init__(self):
        self._chat_mode = False
        self._sending_to_net_name = None

    def _prompt_for_net_name(self):
        text_input_menu = Menu({
            'TextInputPanel': ((0,0), TextInputPanel("Net name of receiver:"))
        }, ['TextInputPanel'])
        net_name = text_input_menu.run(settings.root_console)
        return net_name

    def _prompt_for_message(self):
        import director
        if self._sending_to_net_name is None:
            self._sending_to_net_name = self._prompt_for_net_name()
            if self._sending_to_net_name is None:
                return False
       
        text_input_menu = Menu({
            'TextInputPanel': ((0,0), TextInputPanel("To {}:".format(self._sending_to_net_name)))
        }, ['TextInputPanel'])
        message = text_input_menu.run(settings.root_console)
        if message is not None:
            director.net_director.queue_events([('NET_RECEIVED_MESSAGE', {
                'sender': director.net_director.net_name(),
                'receiver': self._sending_to_net_name,
                'message': message,
            })])
            director.net_director.send_events()
            message_panel.info("To {}: {}".format(self._sending_to_net_name, message), tcod.cyan)
            return True
        return None

    def handle_event(self, entity, event, resident_map):
        import director, load
        event_type, event_data = event
        if event_type == 'NET_RECEIVED_MESSAGE':
            settings.message_panel.info('From {}: {}'.format(event_data['sender'], event_data['message']), tcod.cyan)
            return False
        elif event_type == 'NET_RECEIVED_ITEM':
            settings.message_panel.info('{} sent you an item!'.format(event_data['sender']), tcod.cyan)
            item_obj = event_data['item']
            item_ent = load.load_entity(item_obj)
            settings.pending_items_received.append(item_ent)
            return False
        elif event_type == 'ENTITY_KILLED' and event_data == entity:
            print("Player was killed!")
            raise GameplayException("Player died")
        elif event_type == 'TCOD' and event_data.type == 'KEYDOWN':
            position = entity.component('Position')
            combat = entity.component('Combat')
            is_paralyzed = entity.component('Stats').has_status('PARALYZE')
            x, y = position.get()
            lshift_held = event_data.mod & tcod.event.KMOD_LSHIFT == 1
            target_position = (x, y)
            has_acted = False
            if event_data.sym == tcod.event.K_c:
                self._chat_mode = not self._chat_mode
                return True
            elif event_data.sym in [tcod.event.K_n]:
                self._sending_to_net_name = self._prompt_for_net_name()
                return True
            elif event_data.sym in [tcod.event.K_m]:
                return self._prompt_for_message()
            elif event_data.sym in [tcod.event.K_t]:
                inventory = entity.component('Inventory')
                item = inventory.items().as_list()[0].save()
                receiver = self._prompt_for_net_name()
                director.net_director.queue_events([('NET_RECEIVED_ITEM', {
                    'receiver': receiver,
                    'sender': director.net_director.net_name(),
                    'item': item,
                })])
                inventory.remove(inventory.items().as_list()[0])
                director.net_director.send_events()
                message_panel.info("Item sent!", tcod.cyan)
            elif event_data.sym in [tcod.event.K_o]:
                import load
                m = load.load_save_file('save.json')
                settings.current_map = None
                settings.set_current_map(m)
            elif event_data.sym in [tcod.event.K_s]:
                if not settings.current_map.can_save():
                    message_panel.info("You can only save in town", tcod.cyan)
                    return False
                save = {
                    'current_map': settings.current_map.save(),
                    'main_dungeon_lowest_floor': settings.main_dungeon_lowest_floor,
                    'loot_tier': settings.loot_tier,
                    'monster_tier': settings.monster_tier,
                }
                strg = json.dump(save, open('save.json', mode='w'))
                message_panel.info("Game saved to save.json", tcod.cyan)
            elif event_data.sym in [tcod.event.K_KP_8, tcod.event.K_i]:
                target_position = (x, y-1)
                has_acted = True
            elif event_data.sym == tcod.event.K_KP_7:
                target_position = (x-1, y-1)
                has_acted = True
            elif event_data.sym == tcod.event.K_KP_9:
                target_position = (x+1, y-1)
                has_acted = True
            elif event_data.sym == tcod.event.K_KP_1:
                target_position = (x-1, y+1)
                has_acted = True
            elif event_data.sym == tcod.event.K_KP_3:
                target_position = (x+1, y+1)
                has_acted = True
            elif event_data.sym in [tcod.event.K_KP_4, tcod.event.K_j]:
                target_position = (x-1, y)
                has_acted = True
            elif event_data.sym in [tcod.event.K_KP_2, tcod.event.K_k]:
                target_position = (x, y+1)
                has_acted = True
            elif event_data.sym in [tcod.event.K_KP_6, tcod.event.K_l]:
                target_position = (x+1, y)
                has_acted = True
            elif event_data.sym == tcod.event.K_g:
                inventory = entity.component('Inventory')
                resident_map.entities().with_all_components(['Position', 'Item'])\
                                       .where(lambda itm: itm.component('Position').get() == position.get())\
                                       .transform(lambda itm: inventory.pick_up(entity, itm, resident_map))
                resident_map.end_turn()
                return True
            elif event_data.sym == tcod.event.K_PERIOD and event_data.mod & tcod.event.KMOD_LSHIFT == 1:
                if resident_map.is_descendable((x, y)):
                    director.map_director.descend()
                return True
            elif event_data.sym == tcod.event.K_PERIOD:
                resident_map.end_turn()
                return True

            if has_acted:
                if self._chat_mode:
                    resident_map.entities()\
                                .at_position(target_position)\
                                .transform(lambda ent: ent.handle_event(('PLAYER_CHAT_WITH', ent.ident()), resident_map))
                    self._chat_mode = False
                    return True
                elif lshift_held:
                    combat.attack(entity, resident_map, target_position)
                elif not is_paralyzed and resident_map.is_passable_for(entity, target_position):
                    position.set(target_position[0], target_position[1])
                resident_map.end_turn()
                return True
        return False
