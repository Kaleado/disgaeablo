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

class Component:
    def handle_event(self, entity, event, resident_map):
        return False

class Entity:
    def __init__(self, ident, components):
       self._ident = ident
       self._components = components
       self._disabled = False

    def ident(self):
        return self._ident

    def disable(self):
        self._disabled = True

    def has_component(self, identifier):
        return identifier in self._components

    def component(self, identifier):
        return self._components.get(identifier)

    def handle_event(self, event, resident_map):
        if self._disabled:
            return False
        print(event)
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
        return [], pos

    def choose_targets(self, user_entity, used_entity, mapp, menu):
        ents, pos = self._targeting_mode.choose_targets(user_entity, used_entity, mapp, menu)
        return [], pos

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

class TargetNobody(TargetMode):
    def targets(self, group='x'):
        return [], []

    def choose_targets(self, user_entity, used_entity, mapp, menu):
        return [], []

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

class TargetFormation(TargetMode):
    def __init__(self, formation, directional=False, max_range=None):
        self._formation = formation
        self._directional = directional
        self._max_range = max_range
        self._targets = {}

    def targets(self, group='x'):
        if group not in self._targets:
            return None, None
        return self._targets[group]

    def choose_targets(self, user_entity, used_entity, mapp, menu):
        if user_entity == mapp.entity('PLAYER'):
            return self._choose_targets_player(user_entity, used_entity, mapp, menu)
        return self._choose_targets_monster(user_entity, used_entity, mapp, menu)

    def _choose_targets_monster(self, user_entity, used_entity, mapp, menu):
        # If the player is nearby, try to hit them, otherwise, just target north
        user_pos = user_entity.component('Position').get()
        player_pos = mapp.entity('PLAYER').component('Position').get()
        formation_position = user_pos
        formation_rotation = 0
        if not self._directional:
            if self._max_range is None or distance(user_pos, player_pos) <= self._max_range:
                formation_position = player_pos
        else:
            for rot in range(4):
                if self._formation.in_formation(user_pos, formation_position, rot):
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

class Cost(Usable):
    def __init__(self, sp=0, usable=None):
        self._sp = sp
        self._usable = usable

    def _pay_costs(self, entity, user_entity):
        user_stats = user_entity.component('Stats')
        user_stats.sub_base('cur_sp', self._sp)

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
    def __init__(self, formation):
        super().__init__(ExcludeItems(TargetFormation(formation, directional=False, max_range=10)))

    def use_on_targets(self, entity, user_entity, mapp, targets, menu):
        global message_panel
        skill_stats = entity.component('Stats')
        user_stats = user_entity.component('Stats')
        def damage_target(target):
            attacker_name = user_entity.component('NPC').name() if user_entity.component('NPC') is not None else 'Player'
            defender_name = target.component('NPC').name() if target.component('NPC') is not None else 'Player'
            itl_over_res = user_stats.get_value('itl') / target.component('Stats').get_value('res')
            amount = math.floor(itl_over_res * skill_stats.get_value('itl'))
            message_panel.info("{}'s spell hits {}! ({} HP)".format(attacker_name, defender_name, str(amount)))
            dam = damage.Damage(user_entity, amount)
            dam.inflict(target, mapp)
        targets[0].transform(damage_target)
        return False

class TeleportToPosition(Usable):
    def __init__(self, max_range):
        formation = Formation(formation=[['x']], origin=(0,0))
        super().__init__(TargetFormation(formation, directional=False, max_range=max_range))

    def use_on_targets(self, entity, user_entity, mapp, targets, menu):
        global message_panel
        x, y = targets[1][0]
        user_entity.component('Position').set(x, y)

class SkillStatusSpell(Usable):
    def __init__(self, formation, status_effect, status_duration):
        super().__init__(ExcludeItems(TargetFormation(formation, directional=False, max_range=10)))
        self._status_effect = status_effect
        self._status_duration = status_duration

    def use_on_targets(self, entity, user_entity, mapp, targets, menu):
        global message_panel
        skill_stats = entity.component('Stats')
        user_stats = user_entity.component('Stats')
        def damage_target(target):
            attacker_name = user_entity.component('NPC').name() if user_entity.component('NPC') is not None else 'Player'
            defender_name = target.component('NPC').name() if target.component('NPC') is not None else 'Player'
            itl_over_res = user_stats.get_value('itl') / max(1, target.component('Stats').get_value('res'))
            strength = math.floor(itl_over_res * skill_stats.get_value('itl'))
            dam = damage.WithStatusEffect(self._status_effect, strength, self._status_duration, damage.Damage(user_entity, 0))
            message_panel.info("{} inflicts {} with {} for {} turns!".format(attacker_name, defender_name, self._status_effect, str(self._status_duration)))
            dam.inflict(target, mapp)
        targets[0].transform(damage_target)
        return False

class ForceTargetSelf(Usable):
    def __init__(self, usable):
        self._usable = usable

    def use_on_targets(self, entity, user_entity, mapp, targets, menu):
        pos = user_entity.component('Position').get()
        self._usable.use_on_targets(entity, user_entity, mapp, [(user_entity, pos)], menu)

class SkillMelee(Usable):
    def __init__(self, formation):
        super().__init__(ExcludeItems(TargetFormation(formation, True)))

    def use_on_targets(self, entity, user_entity, mapp, targets, menu):
        global message_panel
        skill_stats = entity.component('Stats')
        user_stats = user_entity.component('Stats')
        def damage_target(target):
            attacker_name = user_entity.component('NPC').name() if user_entity.component('NPC') is not None else 'Player'
            defender_name = target.component('NPC').name() if target.component('NPC') is not None else 'Player'
            atk_over_dfn = user_stats.get_value('atk') / max(1, target.component('Stats').get_value('dfn'))
            amount = math.floor(atk_over_dfn * skill_stats.get_value('atk'))
            message_panel.info("{}'s attack hits {}! ({} HP)".format(attacker_name, defender_name, str(amount)))
            dam = damage.Damage(user_entity, amount)
            dam.inflict(target, mapp)
        targets[0].transform(damage_target)
        obstructing_ents, mov_pos = self._targeting_mode.targets(group='U')
        if mov_pos is not None:
            new_pos = mov_pos[0]
            if mapp.is_passable_for(user_entity, new_pos):
                user_entity.component('Position').set(new_pos[0], new_pos[1])
        return False
   
class Item(Component):
    def __init__(self, name):
        self._name = name

    def name(self):
        return self._name

class Equipment(Component):
    def __init__(self, mods=[]):
        self._mods = mods

    def handle_event(self, entity, event, resident_map):
        for mod in self._mods:
            if mod is None:
                continue
            mod.handle_event(mod, event, resident_map)

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

    resistance_stats = set([
        'fire_res',
        'ice_res',
        'lght_res',
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
        'fire_res',
        'ice_res',
        'lght_res',
        'cur_exp',
        'max_exp',
        'level',
    ])

    """
    There is no need to initialise all the base_stats -- any ones left out will
    be zero by default
    """
    def __init__(self, base_stats):
        self._stats = {}
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

    def exp_yield(self):
        return sum([self._stats[stat] for stat in Stats.primary_stats - set(['max_hp', 'max_sp'])])

    def increase_level(self, num):
        self.add_base('max_exp', num * 100)
        for stat in Stats.primary_stats:
            print(self.add_base(stat, self._base_stats[stat] * num * 0.2))

    def grant_exp(self, exp):
        message_panel.info("Gained {} EXP".format(exp))
        self.add_base('cur_exp', exp)
        levels = 0
        while self.get_base('cur_exp') >= self.get_base('max_exp'):
            excess = self.sub_base('cur_exp', self.get_base('max_exp'))
            self.set_base('cur_exp', excess)
            self.increase_level(1)
            levels += 1
        if levels > 0:
            message_panel.info("Level up!" + ("" if levels == 1 else " x{}".format(levels)))
            message_panel.info("You are now level {}".format(self.get_base('level')))

    def handle_event(self, entity, event, resident_map):
        event_type, event_data = event
        removed = []
        if event_type == 'NPC_TURN':
            if self.has_status('REGEN'):
                self.apply_healing(entity, resident_map, 0.02 * self.get_value('max_hp'))
            if self.has_status('POISON'):
                self.deal_damage(entity, resident_map, 0.05 * self.get_value('max_hp'))
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
        if status == 'WEAKEN':
            self.add_multiplicative_modifier('atk', 0.5)
        if status == 'GUARD_BREAK':
            self.add_multiplicative_modifier('dfn', 0.3)
        if status == 'MIND_BREAK':
            self.add_multiplicative_modifier('res', 0.3)
        if status == 'STONESKIN':
            self.sub_multiplicative_modifier('dfn', 0.5)

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

    def apply_healing(self, entity, resident_map, amount):
        amount = min(amount, self.get_value('max_hp') - self.get_value('cur_hp'))
        self.add_base('cur_hp', amount)

    def apply_refreshing(self, entity, resident_map, amount):
        amount = min(amount, self.get_value('max_sp') - self.get_value('cur_sp'))
        self.add_base('cur_sp', amount)

    def deal_damage(self, entity, resident_map, damage):
        if self.sub_base('cur_hp', damage) <= 0:
            player = resident_map.entity('PLAYER')
            player.component('Stats').grant_exp(self.exp_yield())
            resident_map.entities().transform(lambda ent: ent.handle_event(("ENTITY_KILLED", entity), resident_map))
            resident_map.remove_entity(entity.ident())

    def get_value(self, stat):
        if stat == 'spd' and self.has_status('PARALYZE'):
            return 0
        return int((self._stats[stat] + self._modifiers[stat]['additive']) * self._modifiers[stat]['multiplicative'])

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
        print(self._stats)
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

    def character(self):
        return self._character

    def colour(self):
        return self._colour

    def render(self, entity, console, origin):
        x, y = origin
        old_fg = console.default_fg
        console.default_fg = self._colour
        console.print_(x=x, y=y, string=self._character)
        console.default_fg = old_fg

class Inventory(Component):
    def __init__(self):
        self._items = []

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
            dam = damage.Damage(entity, 20 * my_stats.get_value('atk') / stats.get_value('dfn'))
            amount = dam.inflict(ent, resident_map)
            settings.message_panel.info("{} lunges at {}! ({} HP)".format(attacker_name, defender_name, str(int(amount))))

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

    def handle_event(self, entity, event, resident_map):
        event_type, event_data = event
        is_paralyzed = entity.component('Stats').has_status('PARALYZE')
        if event_type == 'ENTITY_KILLED' and event_data == entity and self._delayed_targets is not None:
            targeted_positions = self._delayed_targets[1]
            resident_map.remove_threatened_positions(targeted_positions)
            return False
        if event_type == 'NPC_TURN':
            if is_paralyzed:
                return False
            elif self._delayed_attack is not None:
                self._delay -= 1
                if self._delay > 0:
                    return False
                targeted_positions = self._delayed_targets[1]
                targets = resident_map.entities().without_components(['Item']).with_component('Position')\
                                                 .where(lambda ent: ent.component('Position').get() in targeted_positions), targeted_positions
                self._delayed_attack.use_on_targets(entity, entity, resident_map, targets, None)
                resident_map.remove_threatened_positions(targeted_positions)
                self._delay = None
                self._delayed_attack = None
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
        resident_map.add_threatened_positions(self._delayed_targets[1])

class Slow(AI):
    def __init__(self, ai, period=2):
        self._ai = ai
        self._turn_count = 0
        self._period = period

    def handle_event(self, entity, event, resident_map):
        event_type, _ = event
        if event_type == 'NPC_TURN':
            self._turn_count = (self._turn_count + 1) % self._period
            if self._turn_count == 0:
                return self._ai.handle_event(entity, event, resident_map)
            return False
        return self._ai.handle_event(entity, event, resident_map)

class Hostile(AI):
    def __init__(self, aggro_range=5, primary_skill=None, primary_skill_range=None):
        super().__init__()
        self._ai_status = "IDLE"
        self._aggro_range = aggro_range
        self._primary_skill = primary_skill
        self._primary_skill_range = primary_skill_range

    def _handle_aggro(self, entity, event, resident_map):
        player = resident_map.entity('PLAYER')
        if self._primary_skill is None and self._distance_to_player(entity, resident_map) < 2:
            self._perform_attack_against(entity, player, resident_map)
        elif self._primary_skill is not None and \
             (self._primary_skill_range is None or self._distance_to_player(entity, resident_map) <= self._primary_skill_range):
            self._perform_delayed_attack_against(entity, player, resident_map, self._primary_skill, 1)
        else:
            self._step_towards_player(entity, resident_map)

    def _handle_idle(self, entity, event, resident_map):
        player = resident_map.entity('PLAYER')
        my_position = entity.component('Position').get()
        player_position = player.component('Position').get()
        if player is not None and distance(player_position, my_position) <= self._aggro_range:
            self._ai_status = 'AGGRO'
            self._handle_aggro(entity, event, resident_map)
        else:
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
        pass

    def handle_event(self, entity, event, resident_map):
        import director
        event_type, event_data = event
        if event_type == 'TCOD' and event_data.type == 'KEYDOWN':
            position = entity.component('Position')
            combat = entity.component('Combat')
            is_paralyzed = entity.component('Stats').has_status('PARALYZE')
            x, y = position.get()
            lshift_held = event_data.mod & tcod.event.KMOD_LSHIFT == 1
            if event_data.sym == tcod.event.K_KP_8:
                if lshift_held:
                    combat.attack(entity, resident_map, (x, y-1))
                elif not is_paralyzed and resident_map.is_passable_for(entity, (x, y-1)):
                    position.sub(y=1)
                resident_map.end_turn()
                return True
            elif event_data.sym == tcod.event.K_KP_7:
                if lshift_held:
                    combat.attack(entity, resident_map, (x-1, y-1))
                elif not is_paralyzed and resident_map.is_passable_for(entity, (x-1, y-1)):
                    position.sub(x=1,y=1)
                resident_map.end_turn()
                return True
            elif event_data.sym == tcod.event.K_KP_9:
                if lshift_held:
                    combat.attack(entity, resident_map, (x+1, y-1))
                elif not is_paralyzed and resident_map.is_passable_for(entity, (x+1, y-1)):
                    position.add(x=1,y=-1)
                resident_map.end_turn()
                return True
            elif event_data.sym == tcod.event.K_KP_1:
                if lshift_held:
                    combat.attack(entity, resident_map, (x-1, y+1))
                elif not is_paralyzed and resident_map.is_passable_for(entity, (x-1, y+1)):
                    position.add(x=-1,y=1)
                resident_map.end_turn()
                return True
            elif event_data.sym == tcod.event.K_KP_3:
                if lshift_held:
                    combat.attack(entity, resident_map, (x+1, y+1))
                elif not is_paralyzed and resident_map.is_passable_for(entity, (x+1, y+1)):
                    position.add(x=1,y=1)
                resident_map.end_turn()
                return True
            elif event_data.sym == tcod.event.K_KP_4:
                if lshift_held:
                    combat.attack(entity, resident_map, (x-1, y))
                elif not is_paralyzed and resident_map.is_passable_for(entity, (x-1, y)):
                    position.sub(x=1)
                resident_map.end_turn()
                return True
            elif event_data.sym == tcod.event.K_KP_2:
                if lshift_held:
                    combat.attack(entity, resident_map, (x, y+1))
                elif not is_paralyzed and resident_map.is_passable_for(entity, (x, y+1)):
                    position.add(y=1)
                resident_map.end_turn()
                return True
            elif event_data.sym == tcod.event.K_KP_6:
                if lshift_held:
                    combat.attack(entity, resident_map, (x+1, y))
                elif not is_paralyzed and resident_map.is_passable_for(entity, (x+1, y)):
                    position.add(x=1)
                resident_map.end_turn()
                return True
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
        return False
