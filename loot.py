#!/usr/bin/env python

from formation import *
import util
import entity
import uuid
import tcod
import math
import random
import skill_factory
import damage

LEVEL_PC_STAT_INC = 0.4
TIER_PC_STAT_INC = 10

##################################################### CONSUMABLES

def CharredSkull(position):
    x, y = position
    return entity.Entity(str(uuid.uuid4()), components={
        'Stats': entity.Stats({}, stat_inc_per_level=LEVEL_PC_STAT_INC),
        'Position': entity.Position(x, y),
        'Render': entity.Render(character='+', colour=tcod.red),
        'Item': entity.Item("Charred skull", 'Someone strange might want this...'),
        'CharredSkull': entity.Component()
    })

def TownPortal(position):
    x, y = position
    return entity.Entity(str(uuid.uuid4()), components={
        'Stats': entity.Stats({}, stat_inc_per_level=LEVEL_PC_STAT_INC),
        'Position': entity.Position(x, y),
        'Render': entity.Render(character='+', colour=tcod.lighter_blue),
        'Item': entity.Item("Town portal", 'Takes you back to town, fully healing your HP and SP'),
        'Usable': entity.ConsumeAfter(entity.ReturnToTown()),
        'TownPortal': entity.Component()
    })

class Healing:
    base_stats = {
        'max_hp': 175,
        'cur_hp': 175,
    }
    names = ['Rosemary', 'Sage', 'Daffodil', 'Ginseng', 'Valerian']
    colours = [tcod.cyan, tcod.blue, tcod.gold, tcod.silver, tcod.green, tcod.magenta, tcod.red]

    def generator(tier=1, level=1):
        actual_stats = util.copy_dict(Healing.base_stats)
        for stat in Healing.base_stats:
            actual_stats[stat] = (Healing.base_stats[stat] + Healing.base_stats[stat] * (tier - 1) * TIER_PC_STAT_INC)
            actual_stats[stat] += math.floor(LEVEL_PC_STAT_INC * actual_stats[stat]) * (level-1)
        def gen(position):
            x, y = position
            return entity.Entity(str(uuid.uuid4()), components={
                'Stats': entity.Stats(actual_stats, stat_inc_per_level=LEVEL_PC_STAT_INC),
                'Position': entity.Position(x, y),
                'Render': entity.Render(character='"', colour=Healing.colours[tier-1]),
                'Item': entity.Item(Healing.names[tier-1], 'Heals some HP'),
                'Usable': entity.ConsumeAfter(entity.Heal(entity.TargetUser()))
            })
        return gen

class Refreshing:
    base_stats = {
        'max_sp': 25,
        'cur_sp': 25,
    }
    names = ['Spring water', 'Apple juice', 'Rosewater', 'Nectar', 'Morning dew']
    colours = [tcod.cyan, tcod.blue, tcod.gold, tcod.silver, tcod.green]

    def generator(tier=1, level=1):
        actual_stats = util.copy_dict(Refreshing.base_stats)
        for stat in Refreshing.base_stats:
            actual_stats[stat] = (Refreshing.base_stats[stat] + Refreshing.base_stats[stat] * (tier - 1) * TIER_PC_STAT_INC)
            actual_stats[stat] += math.floor(LEVEL_PC_STAT_INC * actual_stats[stat]) * (level-1)
        def gen(position):
            x, y = position
            return entity.Entity(str(uuid.uuid4()), components={
                'Stats': entity.Stats(actual_stats, stat_inc_per_level=LEVEL_PC_STAT_INC),
                'Position': entity.Position(x, y),
                'Render': entity.Render(character='!', colour=Refreshing.colours[tier-1]),
                'Item': entity.Item(Refreshing.names[tier-1], 'Heals some SP'),
                'Usable': entity.ConsumeAfter(entity.Refresh(entity.TargetUser()))
            })
        return gen

##################################################### EQUIPMENT

class DfnArmour:
    base_stats = {
        'dfn': 30,
    }
    names = ['Tunic', 'Leather armour', 'Splint mail', 'Chainmail', 'Platemail', 'Glorious armour', 'Nephilim guard']
    colours = [tcod.brass, tcod.dark_orange, tcod.gold, tcod.silver, tcod.green, tcod.magenta, tcod.dark_red]

    def generator(tier=1, level=1):
        actual_stats = util.copy_dict(DfnArmour.base_stats)
        for stat in DfnArmour.base_stats:
            actual_stats[stat] = (DfnArmour.base_stats[stat] + DfnArmour.base_stats[stat] * (tier - 1) * TIER_PC_STAT_INC)
            actual_stats[stat] += math.floor(LEVEL_PC_STAT_INC * actual_stats[stat]) * (level-1)
        def gen(position):
            x, y = position
            return entity.Entity(str(uuid.uuid4()), components={
                'Stats': entity.Stats(actual_stats, stat_inc_per_level=LEVEL_PC_STAT_INC),
                'Position': entity.Position(x, y),
                'Equipment': entity.Equipment(mod_slots=[None] * random.randint(0,4)),
                'Render': entity.Render(character='[', colour=DfnArmour.colours[tier-1]),
                'Item': entity.Item(DfnArmour.names[tier-1], 'Raises DFN'),
            })
        return gen

class ResArmour:
    base_stats = {
        'res': 30,
    }
    names = ['Loincloth', 'Cloth sash', 'Linen robe', 'Silken gown', 'Sorceror\'s gown', 'Arcane robe', 'Flowing garb']
    colours = [tcod.brass, tcod.dark_orange, tcod.gold, tcod.silver, tcod.green, tcod.magenta, tcod.dark_red]

    def generator(tier=1, level=1):
        actual_stats = util.copy_dict(ResArmour.base_stats)
        for stat in ResArmour.base_stats:
            actual_stats[stat] = (ResArmour.base_stats[stat] + ResArmour.base_stats[stat] * (tier - 1) * TIER_PC_STAT_INC)
            actual_stats[stat] += math.floor(LEVEL_PC_STAT_INC * actual_stats[stat]) * (level-1)
        def gen(position):
            x, y = position
            return entity.Entity(str(uuid.uuid4()), components={
                'Stats': entity.Stats(actual_stats, stat_inc_per_level=LEVEL_PC_STAT_INC),
                'Position': entity.Position(x, y),
                'Equipment': entity.Equipment(mod_slots=[None] * random.randint(0,4)),
                'Render': entity.Render(character='{', colour=ResArmour.colours[tier-1]),
                'Item': entity.Item(ResArmour.names[tier-1], 'Raises RES'),
            })
        return gen

class ResItlArmour:
    base_stats = {
        'res': 18,
        'itl': 12,
    }
    names = ['Bandana', 'Plain circlet', 'Cloth hat', 'Mitre', 'Wizard\'s hat', 'Feather cap', 'Majestic crown']
    colours = [tcod.brass, tcod.dark_orange, tcod.gold, tcod.silver, tcod.green, tcod.magenta, tcod.dark_red]

    def generator(tier=1, level=1):
        actual_stats = util.copy_dict(ResItlArmour.base_stats)
        for stat in ResItlArmour.base_stats:
            actual_stats[stat] = (ResItlArmour.base_stats[stat] + ResItlArmour.base_stats[stat] * (tier - 1) * TIER_PC_STAT_INC)
            actual_stats[stat] += math.floor(LEVEL_PC_STAT_INC * actual_stats[stat]) * (level-1)
        def gen(position):
            x, y = position
            return entity.Entity(str(uuid.uuid4()), components={
                'Stats': entity.Stats(actual_stats, stat_inc_per_level=LEVEL_PC_STAT_INC),
                'Position': entity.Position(x, y),
                'Equipment': entity.Equipment(mod_slots=[None] * random.randint(0,4)),
                'Render': entity.Render(character=']', colour=ResItlArmour.colours[tier-1]),
                'Item': entity.Item(ResItlArmour.names[tier-1], 'Raises RES and ITL'),
            })
        return gen

class DfnAtkArmour:
    base_stats = {
        'dfn': 18,
        'atk': 12,
    }
    names = ['Leather shield', 'Targe', 'Kite shield', 'Square shield', 'Spiked shield', 'Berserker shield', 'Angel aegis']
    colours = [tcod.brass, tcod.dark_orange, tcod.gold, tcod.silver, tcod.green, tcod.magenta, tcod.dark_red]

    def generator(tier=1, level=1):
        actual_stats = util.copy_dict(DfnAtkArmour.base_stats)
        for stat in DfnAtkArmour.base_stats:
            actual_stats[stat] = (DfnAtkArmour.base_stats[stat] + DfnAtkArmour.base_stats[stat] * (tier - 1) * TIER_PC_STAT_INC)
            actual_stats[stat] += math.floor(LEVEL_PC_STAT_INC * actual_stats[stat]) * (level-1)
        def gen(position):
            x, y = position
            return entity.Entity(str(uuid.uuid4()), components={
                'Stats': entity.Stats(actual_stats, stat_inc_per_level=LEVEL_PC_STAT_INC),
                'Position': entity.Position(x, y),
                'Equipment': entity.Equipment(mod_slots=[None] * random.randint(0,4)),
                'Render': entity.Render(character=')', colour=DfnAtkArmour.colours[tier-1]),
                'Item': entity.Item(DfnAtkArmour.names[tier-1], 'Raises DFN and ATK'),
            })
        return gen

class Sword:
    base_stats = {
        'atk': 45,
    }
    names = ['Rusted sword', 'Shortsword', 'Broadsword', 'Estoc', 'Claymore', 'Flamberge', 'Zanbato']
    colours = [tcod.cyan, tcod.blue, tcod.gold, tcod.silver, tcod.green, tcod.magenta, tcod.red]

    def generator(tier=1, level=1):
        actual_stats = util.copy_dict(Sword.base_stats)
        for stat in Sword.base_stats:
            actual_stats[stat] = (Sword.base_stats[stat] + Sword.base_stats[stat] * (tier - 1) * TIER_PC_STAT_INC)
            actual_stats[stat] += math.floor(LEVEL_PC_STAT_INC * actual_stats[stat]) * (level-1)
        def gen(position):
            x, y = position
            return entity.Entity(str(uuid.uuid4()), components={
                'Stats': entity.Stats(actual_stats, stat_inc_per_level=LEVEL_PC_STAT_INC),
                'Position': entity.Position(x, y),
                'Equipment': entity.Equipment(mod_slots=[None] * random.randint(0,4)),
                'Render': entity.Render(character='/', colour=Sword.colours[tier-1]),
                'Item': entity.Item(Sword.names[tier-1], 'Boost physical attacks'),
            })
        return gen

class Staff:
    base_stats = {
        'itl': 45,
    }
    names = ['Bent staff', 'Apprentice staff', 'Novice rod', 'Battlestaff', 'Angel\'s cane', 'Greatstaff', 'Yggdrasil branch']
    colours = [tcod.cyan, tcod.blue, tcod.gold, tcod.silver, tcod.green, tcod.magenta, tcod.red]

    def generator(tier=1, level=1):
        actual_stats = util.copy_dict(Staff.base_stats)
        for stat in Staff.base_stats:
            actual_stats[stat] = (Staff.base_stats[stat] + Staff.base_stats[stat] * (tier - 1) * TIER_PC_STAT_INC)
            actual_stats[stat] += math.floor(LEVEL_PC_STAT_INC * actual_stats[stat]) * (level-1)
        def gen(position):
            x, y = position
            return entity.Entity(str(uuid.uuid4()), components={
                'Stats': entity.Stats(actual_stats, stat_inc_per_level=LEVEL_PC_STAT_INC),
                'Position': entity.Position(x, y),
                'Equipment': entity.Equipment(mod_slots=[None] * random.randint(0,4)),
                'Render': entity.Render(character='|', colour=Staff.colours[tier-1]),
                'Item': entity.Item(Staff.names[tier-1], 'Boost magical attacks'),
            })
        return gen

##################################################### SKLLS

def Cleave(position):
    formation = Formation(origin=(1,2), formation=[['x','x','x'],
                                                   ['x','x','x'],
                                                   ['.','.','.']])
    x, y = position
    return entity.Entity(str(uuid.uuid4()), components={
        'Stats': entity.Stats({'atk': 35}, stat_inc_per_level=LEVEL_PC_STAT_INC),
        'Position': entity.Position(x, y),
        'Render': entity.Render(character='&', colour=tcod.lighter_green),
        'Item': entity.Item('Skill: Cleave', 'Deals high physical damage in an area in front'),
        'Usable': skill_factory.Skill(tags=['skill_cleave', 'attack', 'offensive'])\
        .melee_skill()\
        .with_target_mode(entity.ExcludeItems(entity.TargetFormation(formation, directional=True)))\
        .damage_targets("{}'s cleave hits {}! ({} HP)")\
        .with_sp_cost(3)\
        .with_damage(damage.AttackDamage(1, 'phys'))
        .change_damage(lambda d, s, t, i : damage.WithStatusEffect('POISON', strength=1, duration=4, damage=d),
                       lambda s, s_e, t_e, i_e : s_e.component('Stats').get('cleave_poison') > 0)
    })

def Pierce(position):
    formation = Formation(origin=(0,4), formation=[['x'],
                                                   ['x'],
                                                   ['x'],
                                                   ['x'],
                                                   ['.']])
    x, y = position
    return entity.Entity(str(uuid.uuid4()), components={
        'Stats': entity.Stats({'atk': 35}, stat_inc_per_level=LEVEL_PC_STAT_INC),
        'Position': entity.Position(x, y),
        'Render': entity.Render(character='&', colour=tcod.lighter_green),
        'Item': entity.Item('Skill: Pierce', 'Deals high physical damage in a line'),
        'Usable': skill_factory.Skill(tags=['skill_pierce', 'attack', 'offensive'])\
        .melee_skill()\
        .with_target_mode(entity.ExcludeItems(entity.TargetFormation(formation, directional=True)))\
        .damage_targets("{}'s pierce hits {}! ({} HP)")\
        .with_sp_cost(3)\
        .with_damage(damage.AttackDamage(1, 'phys'))
    })

def Bypass(position):
    formation = Formation(origin=(0,3), formation=[['x','.'],
                                                   ['x','P'],
                                                   ['x','.'],
                                                   ['.','.']])
    x, y = position
    return entity.Entity(str(uuid.uuid4()), components={
        'Stats': entity.Stats({'atk': 25}, stat_inc_per_level=LEVEL_PC_STAT_INC),
        'Position': entity.Position(x, y),
        'Render': entity.Render(character='&', colour=tcod.lighter_green),
        'Item': entity.Item('Skill: Bypass', 'Attack in a line whilst moving diagonally forwards'),
        'Usable': skill_factory.Skill(tags=['skill_bypass', 'attack', 'movement', 'offensive'])\
        .melee_skill()\
        .with_target_mode(entity.ExcludeItems(entity.TargetFormation(formation, directional=True)))\
        .damage_targets("{}'s bypass hits {}! ({} HP)")\
        .with_sp_cost(3)\
        .with_damage(damage.AttackDamage(1, 'phys'))
    })

def WhipSlash(position):
    formation = Formation(origin=(1,1), formation=[['x','x','x'],
                                                   ['x','.','x'],
                                                   ['.','P','.',]])
    x, y = position
    return entity.Entity(str(uuid.uuid4()), components={
        'Stats': entity.Stats({'atk': 25}, stat_inc_per_level=LEVEL_PC_STAT_INC),
        'Position': entity.Position(x, y),
        'Render': entity.Render(character='&', colour=tcod.lighter_green),
        'Item': entity.Item('Skill: Crescent slash', 'Deal damage in an arc whilst sidestepping danger'),
        'Usable': skill_factory.Skill(tags=['skill_whip_slash', 'attack', 'movement', 'offensive'])\
        .melee_skill()\
        .with_target_mode(entity.ExcludeItems(entity.TargetFormation(formation, directional=True)))\
        .damage_targets("{}'s crescent slash hits {}! ({} HP)")\
        .with_sp_cost(3)\
        .with_damage(damage.AttackDamage(1, 'phys'))
    })

def Dash(position):
    formation = Formation(origin=(0,2), formation=[['P'],
                                                   ['.'],
                                                   ['.']])

    improved_formation = Formation(origin=(0,3), formation=[['P'],
                                                            ['.'],
                                                            ['.'],
                                                            ['.']])
    x, y = position
    return entity.Entity(str(uuid.uuid4()), components={
        'Stats': entity.Stats({}, stat_inc_per_level=LEVEL_PC_STAT_INC),
        'Position': entity.Position(x, y),
        'Render': entity.Render(character='&', colour=tcod.green),
        'Item': entity.Item('Skill: Dash', 'Cheap mobility skill, good for evading attacks'),
        'Usable': skill_factory.Skill(tags=['skill_dash', 'movement'])\
        .with_target_mode(entity.ExcludeItems(entity.TargetFormation(formation, directional=True)))\
        .override_target_mode(entity.ExcludeItems(entity.TargetFormation(improved_formation, directional=True)),
                              lambda s, e, u, m, mn : u.component('Stats').get('improve_dash_length') > 0)
        .move_to_targeted_position()\
        .with_sp_cost(2)
    })

def RollingStab(position):
    formation = Formation(origin=(0,3), formation=[['P'],
                                                   ['x'],
                                                   ['x'],
                                                   ['.']])
    x, y = position
    return entity.Entity(str(uuid.uuid4()), components={
        'Stats': entity.Stats({'atk': 20}, stat_inc_per_level=LEVEL_PC_STAT_INC),
        'Position': entity.Position(x, y),
        'Render': entity.Render(character='&', colour=tcod.lighter_green),
        'Item': entity.Item('Skill: Rolling stab', 'Good for rolling out of the way of incoming attacks'),
        'Usable': skill_factory.Skill(tags=['skill_rolling_stab', 'attack', 'movement', 'offensive'])\
        .melee_skill()\
        .with_target_mode(entity.ExcludeItems(entity.TargetFormation(formation, directional=True)))\
        .damage_targets("{} deftly rolls whilst piercing {}! ({} HP)")\
        .with_sp_cost(7)\
        .with_damage(damage.AttackDamage(1, 'phys'))
    })

def AerialDrop(position):
    formation = Formation(origin=(1,1), formation=[['x','x','x'],
                                                   ['x','P','x'],
                                                   ['x','x','x']])
    x, y = position
    return entity.Entity(str(uuid.uuid4()), components={
        'Stats': entity.Stats({'atk': 20}, stat_inc_per_level=LEVEL_PC_STAT_INC),
        'Position': entity.Position(x, y),
        'Render': entity.Render(character='&', colour=tcod.lighter_green),
        'Item': entity.Item('Skill: Aerial drop', 'Pierce your foes from the sky!'),
        'Usable': skill_factory.Skill(tags=['skill_aerial_drop', 'attack', 'movement', 'offensive'])\
        .melee_skill()\
        .with_target_mode(entity.ExcludeItems(entity.TargetFormation(formation, max_range=5)))\
        .damage_targets("{} plunges down on to {}! ({} HP)")\
        .with_sp_cost(15)\
        .with_damage(damage.AttackDamage(1, 'phys'))\
    })

def Combustion(position):
    formation = Formation(origin=(0,2), formation=[['x'],
                                                   ['x'],
                                                   ['.']])
    x, y = position
    return entity.Entity(str(uuid.uuid4()), components={
        'Stats': entity.Stats({'itl': 45}, stat_inc_per_level=LEVEL_PC_STAT_INC),
        'Position': entity.Position(x, y),
        'Render': entity.Render(character='&', colour=tcod.lighter_purple),
        'Item': entity.Item('Spell: Combustion', 'Deals high fire damage in front'),
        'Usable': skill_factory.Skill(tags=['spell_fire', 'spell', 'offensive'])\
        .with_target_mode(entity.ExcludeItems(entity.TargetFormation(formation, directional=True)))\
        .damage_targets("{} emits a blast of fire at {}! ({} HP)")\
        .with_sp_cost(5)\
        .with_damage(damage.SpellDamage(1, 'fire'))
        .apply_status_to_user('ASSAULT', 2,
                              lambda s, e, u, m, t, mn : u.component('Stats').get('fire_assault') > 0)
    })

def Fire(position):
    formation = Formation(origin=(0,0), formation=[['x']])
    improved_formation = Formation(origin=(1,1), formation=[['x','x','x'],
                                                            ['x','x','x'],
                                                            ['x','x','x']])
    x, y = position
    return entity.Entity(str(uuid.uuid4()), components={
        'Stats': entity.Stats({'itl': 35}, stat_inc_per_level=LEVEL_PC_STAT_INC),
        'Position': entity.Position(x, y),
        'Render': entity.Render(character='&', colour=tcod.lighter_purple),
        'Item': entity.Item('Spell: Fire', 'Deals fire damage in a single tile'),
        'Usable': skill_factory.Skill(tags=['spell_fire', 'spell', 'offensive'])\
        .with_target_mode(entity.ExcludeItems(entity.TargetFormation(formation, max_range=10)))\
        .damage_targets("{} shoots a fireball at {}! ({} HP)")\
        .with_sp_cost(5)\
        .override_target_mode(entity.ExcludeItems(entity.TargetFormation(improved_formation, max_range=10)),
                              lambda s, e, u, m, mn : u.component('Stats').get('improve_fire_aoe') > 0)
        .with_damage(damage.SpellDamage(1, 'fire'))
        .apply_status_to_user('ASSAULT', 2,
                              lambda s, e, u, m, t, mn : u.component('Stats').get('fire_assault') > 0)
    })

def PoisonDetonation(position):
    formation = Formation(origin=(1,1), formation=[['.','x','.'],
                                                   ['x','x','x'],
                                                   ['.','x','.']])
    x, y = position
    return entity.Entity(str(uuid.uuid4()), components={
        'Stats': entity.Stats({'itl': 20}, stat_inc_per_level=LEVEL_PC_STAT_INC),
        'Position': entity.Position(x, y),
        'Render': entity.Render(character='&', colour=tcod.lighter_purple),
        'Item': entity.Item('Spell: Poison Detonation', 'Deals a small amount of fire damage, or a massive amount of fire damage on poisoned targets'),
        'Usable': skill_factory.Skill(tags=['spell_fire', 'spell', 'offensive'])\
        .with_target_mode(entity.ExcludeItems(entity.TargetFormation(formation, max_range=10)))\
        .damage_targets("{} detonates toxins at {}! ({} HP)")\
        .with_sp_cost(5)\
        .with_damage(damage.SpellDamage(1, 'fire'))
        .change_damage(lambda d, s, t, i : damage.AndDamage(damage.SpellDamage(3, 'fire')(s,t,i), d),
                       lambda s, s_e, t_e, i_e : t_e.component('Stats').has_status('POISON'))
        .apply_status_to_user('ASSAULT', 2,
                              lambda s, e, u, m, t, mn : u.component('Stats').get('fire_assault') > 0)
    })

def Ice(position):
    formation = Formation(origin=(1,0), formation=[['x', 'x', 'x', 'x', 'x']])
    x, y = position
    return entity.Entity(str(uuid.uuid4()), components={
        'Stats': entity.Stats({'itl': 27}, stat_inc_per_level=LEVEL_PC_STAT_INC),
        'Position': entity.Position(x, y),
        'Render': entity.Render(character='&', colour=tcod.lighter_purple),
        'Item': entity.Item('Spell: Ice', 'Deals ice damage in a 5-tile line'),
        'Usable': skill_factory.Skill(tags=['spell_ice', 'spell', 'offensive'])\
        .with_target_mode(entity.ExcludeItems(entity.TargetFormation(formation, max_range=10)))\
        .damage_targets("{} rains icicles on {}! ({} HP)")\
        .with_sp_cost(2)\
        .with_damage(damage.SpellDamage(1, 'ice'))\
        .change_damage(lambda d, s, t, i : damage.WithSoulDrain(d, 0.1),
                       lambda s, s_e, t_e, i_e : s_e.component('Stats').get('ice_souldrain') > 0)
        .change_damage(lambda d, s, t, i : damage.WithStatusEffect('MIND_BREAK', strength=1, duration=4, damage=d),
                       lambda s, s_e, t_e, i_e : s_e.component('Stats').get('ice_mind_break') > 0)
    })

def Lightning(position):
    formation = Formation(origin=(1,1), formation=[['x', 'x', 'x'],
                                                   ['x', 'x', 'x'],
                                                   ['x', 'x', 'x']])
    x, y = position
    return entity.Entity(str(uuid.uuid4()), components={
        'Stats': entity.Stats({'itl': 27}, stat_inc_per_level=LEVEL_PC_STAT_INC),
        'Position': entity.Position(x, y),
        'Render': entity.Render(character='&', colour=tcod.lighter_purple),
        'Item': entity.Item('Spell: Lightning', 'Deals lightning damage in a 3x3 area'),
        'Usable': skill_factory.Skill(tags=['spell_lightning', 'spell', 'offensive'])\
        .with_target_mode(entity.ExcludeItems(entity.TargetFormation(formation, max_range=10)))\
        .damage_targets("{} drops a bolt of lightning on {}! ({} HP)")\
        .with_sp_cost(2)\
        .with_damage(damage.SpellDamage(1, 'lght'))
        .change_damage(lambda d, s, t, i : damage.WithLifeDrain(d, 0.2),
                       lambda s, s_e, t_e, i_e : s_e.component('Stats').get('lightning_lifedrain') > 0
        )
    })

def LightningBreath(position):
    formation = Formation(origin=(1,3), formation=[['x', 'x', 'x'],
                                                   ['x', 'x', 'x'],
                                                   ['.', 'x', '.'],
                                                   ['.', '.', '.']])
    x, y = position
    return entity.Entity(str(uuid.uuid4()), components={
        'Stats': entity.Stats({'itl': 35}, stat_inc_per_level=LEVEL_PC_STAT_INC),
        'Position': entity.Position(x, y),
        'Render': entity.Render(character='&', colour=tcod.lighter_purple),
        'Item': entity.Item('Spell: Lightning Breath', 'Deals lightning damage in an area in front'),
        'Usable': skill_factory.Skill(tags=['spell_lightning', 'spell', 'offensive'])\
        .with_target_mode(entity.ExcludeItems(entity.TargetFormation(formation, directional=True)))\
        .damage_targets("{} breathes lightning on {}! ({} HP)")\
        .with_sp_cost(3)\
        .with_damage(damage.SpellDamage(1, 'lght'))
        .change_damage(lambda d, s, t, i : damage.WithLifeDrain(d, 0.2),
                       lambda s, s_e, t_e, i_e : s_e.component('Stats').get('lightning_lifedrain') > 0
        )
    })

def StaticShock(position):
    formation = Formation(origin=(1,3), formation=[['x', 'x', 'x'],
                                                   ['x', 'x', 'x'],
                                                   ['.', '.', '.'],
                                                   ['.', '.', '.']])
    x, y = position
    return entity.Entity(str(uuid.uuid4()), components={
        'Stats': entity.Stats({'itl': 15}, stat_inc_per_level=LEVEL_PC_STAT_INC),
        'Position': entity.Position(x, y),
        'Render': entity.Render(character='&', colour=tcod.lighter_purple),
        'Item': entity.Item('Spell: Static Shock', 'Deals lightning damage with a chance to paralyze for 3 turns'),
        'Usable': skill_factory.Skill(tags=['spell_lightning', 'spell', 'offensive', 'status', 'debuff'])\
        .with_target_mode(entity.ExcludeItems(entity.TargetFormation(formation, directional=True)))\
        .damage_targets("{} fires static electricity at {}! ({} HP)")\
        .with_sp_cost(7)\
        .with_damage(damage.SpellDamage(1, 'lght'))
        .change_damage(lambda d, s, t, i : damage.WithStatusEffect('PARALYZE', 1, 4, d))
        .change_damage(lambda d, s, t, i : damage.WithLifeDrain(d, 0.2),
                       lambda s, s_e, t_e, i_e : s_e.component('Stats').get('lightning_lifedrain') > 0)
    })

def Paralyze(position):
    formation = Formation(origin=(0,0), formation=[['x','x'],
                                                   ['x','x']])
    x, y = position
    return entity.Entity(str(uuid.uuid4()), components={
        'Stats': entity.Stats({'itl': 20}, stat_inc_per_level=LEVEL_PC_STAT_INC),
        'Position': entity.Position(x, y),
        'Render': entity.Render(character='&', colour=tcod.purple),
        'Item': entity.Item('Spell: Paralyze', 'Prevents actions for 6 turns'),
        'Usable': skill_factory.Skill(tags=['spell_paralyze', 'spell', 'debuff', 'status'])\
        .with_target_mode(entity.ExcludeItems(entity.TargetFormation(formation, max_range=10)))\
        .damage_targets("{} attempts to paralyze {}!")\
        .with_sp_cost(2)\
        .with_damage(damage.SpellDamage(0))\
        .change_damage(lambda d, s, t, i : damage.WithStatusEffect('PARALYZE', 1, 6, d))
    })

def Poison(position):
    formation = Formation(origin=(0,0), formation=[['x','x','x','x'],
                                                   ['x','x','x','x'],
                                                   ['x','x','x','x'],
                                                   ['x','x','x','x']])
    x, y = position
    return entity.Entity(str(uuid.uuid4()), components={
        'Stats': entity.Stats({'itl': 20}, stat_inc_per_level=LEVEL_PC_STAT_INC),
        'Position': entity.Position(x, y),
        'Render': entity.Render(character='&', colour=tcod.purple),
        'Item': entity.Item('Spell: Poison', 'Deals 5% of max HP as damage per turn, for 8 turns. Can\'t reduce HP below 5%'),
        'Usable': skill_factory.Skill(tags=['spell_poison', 'spell', 'debuff', 'status'])\
        .with_target_mode(entity.ExcludeItems(entity.TargetFormation(formation, max_range=10)))\
        .damage_targets("{} attempts to poison {}!")\
        .with_sp_cost(3)\
        .with_damage(damage.SpellDamage(0))\
        .change_damage(lambda d, s, t, i : damage.WithStatusEffect('POISON', 1, 8, d))
    })

def GuardBreak(position):
    formation = Formation(origin=(0,0), formation=[['x','x','x','x'],
                                                   ['x','x','x','x'],
                                                   ['x','x','x','x'],
                                                   ['x','x','x','x']])
    x, y = position
    return entity.Entity(str(uuid.uuid4()), components={
        'Stats': entity.Stats({'itl': 20}, stat_inc_per_level=LEVEL_PC_STAT_INC),
        'Position': entity.Position(x, y),
        'Render': entity.Render(character='&', colour=tcod.purple),
        'Item': entity.Item('Spell: Guard Break', 'Lowers DFN by 50% for 12 turns'),
        'Usable': skill_factory.Skill(tags=['spell_guard_break', 'spell', 'debuff', 'status'])\
        .with_target_mode(entity.ExcludeItems(entity.TargetFormation(formation, max_range=10)))\
        .damage_targets("{} attempts to guard break {}!")\
        .with_sp_cost(3)\
        .with_damage(damage.SpellDamage(0))\
        .change_damage(lambda d, s, t, i : damage.WithStatusEffect('GUARD_BREAK', 1, 12, d))
    })

def MindBreak(position):
    formation = Formation(origin=(0,0), formation=[['x','x','x','x'],
                                                   ['x','x','x','x'],
                                                   ['x','x','x','x'],
                                                   ['x','x','x','x']])
    x, y = position
    return entity.Entity(str(uuid.uuid4()), components={
        'Stats': entity.Stats({'itl': 20}, stat_inc_per_level=LEVEL_PC_STAT_INC),
        'Position': entity.Position(x, y),
        'Render': entity.Render(character='&', colour=tcod.purple),
        'Item': entity.Item('Spell: Mind Break', 'Lowers RES by 50% for 12 turns'),
        'Usable': skill_factory.Skill(tags=['spell_mind_break', 'spell', 'debuff', 'status'])\
        .with_target_mode(entity.ExcludeItems(entity.TargetFormation(formation, max_range=10)))\
        .damage_targets("{} attempts to mind break {}!")\
        .with_sp_cost(3)\
        .with_damage(damage.SpellDamage(0))\
        .change_damage(lambda d, s, t, i : damage.WithStatusEffect('MIND_BREAK', 1, 12, d))
    })

def Weaken(position):
    formation = Formation(origin=(0,0), formation=[['x','x','x','x'],
                                                   ['x','x','x','x'],
                                                   ['x','x','x','x'],
                                                   ['x','x','x','x']])
    x, y = position
    return entity.Entity(str(uuid.uuid4()), components={
        'Stats': entity.Stats({'itl': 20}, stat_inc_per_level=LEVEL_PC_STAT_INC),
        'Position': entity.Position(x, y),
        'Render': entity.Render(character='&', colour=tcod.purple),
        'Item': entity.Item('Spell: Weaken', 'Lowers ATK by 50% for 12 turns'),
        'Usable': skill_factory.Skill(tags=['spell_weaken', 'spell', 'debuff', 'status'])\
        .with_target_mode(entity.ExcludeItems(entity.TargetFormation(formation, max_range=10)))\
        .damage_targets("{} attempts to weaken {}!")\
        .with_sp_cost(3)\
        .with_damage(damage.SpellDamage(0))\
        .change_damage(lambda d, s, t, i : damage.WithStatusEffect('WEAKEN', 1, 12, d))
    })

def Stoneskin(position):
    formation = Formation(origin=(0,0), formation=[['x']])
    x, y = position
    return entity.Entity(str(uuid.uuid4()), components={
        'Stats': entity.Stats({'itl': 20}, stat_inc_per_level=LEVEL_PC_STAT_INC),
        'Position': entity.Position(x, y),
        'Render': entity.Render(character='&', colour=tcod.purple),
        'Item': entity.Item('Spell: Stoneskin', 'Boosts DFN by 50% for 40 turns'),
        'Usable': skill_factory.Skill(tags=['spell_stoneskin', 'spell', 'buff', 'status'])\
        .with_target_mode(entity.ExcludeItems(entity.TargetFormation(formation, max_range=10)))\
        .damage_targets("{} gives stoneskin to {}!")\
        .with_sp_cost(3)\
        .with_damage(damage.SpellDamage(0))\
        .change_damage(lambda d, s, t, i : damage.WithStatusEffect('STONESKIN', 1, 40, d))
    })

def Invincible(position):
    x, y = position
    return entity.Entity(str(uuid.uuid4()), components={
        'Stats': entity.Stats({'itl': 20}, stat_inc_per_level=LEVEL_PC_STAT_INC),
        'Position': entity.Position(x, y),
        'Render': entity.Render(character='&', colour=tcod.purple),
        'Item': entity.Item('Spell: Invincible', 'Boosts RES by 300% for 4 turns'),
        'Usable': skill_factory.Skill(tags=['spell_invincible', 'spell', 'buff', 'status'])\
        .with_target_mode(entity.TargetUser())\
        .damage_targets("{} becomes invincibile!")\
        .with_sp_cost(11)\
        .with_damage(damage.SpellDamage(0))\
        .change_damage(lambda d, s, t, i : damage.WithStatusEffect('INVINCIBLE', 1, 4, d))
    })

def Unstoppable(position):
    x, y = position
    return entity.Entity(str(uuid.uuid4()), components={
        'Stats': entity.Stats({'itl': 20}, stat_inc_per_level=LEVEL_PC_STAT_INC),
        'Position': entity.Position(x, y),
        'Render': entity.Render(character='&', colour=tcod.purple),
        'Item': entity.Item('Spell: Invincible', 'Boosts DFN by 300% for 4 turns'),
        'Usable': skill_factory.Skill(tags=['spell_unstoppable', 'spell', 'buff', 'status'])\
        .with_target_mode(entity.TargetUser())\
        .damage_targets("{} becomes unstoppable!")\
        .with_sp_cost(11)\
        .with_damage(damage.SpellDamage(0))\
        .change_damage(lambda d, s, t, i : damage.WithStatusEffect('UNSTOPPABLE', 1, 4, d))
    })


def Blink(position):
    formation = Formation(origin=(0,0), formation=[['P']])
    x, y = position
    return entity.Entity(str(uuid.uuid4()), components={
        'Stats': entity.Stats({'itl': 20}, stat_inc_per_level=LEVEL_PC_STAT_INC),
        'Position': entity.Position(x, y),
        'Render': entity.Render(character='&', colour=tcod.purple),
        'Item': entity.Item('Spell: Blink', 'Performs a short-range, targeted teleport'),
        'Usable': skill_factory.Skill(tags=['spell_blink', 'spell', 'movement'])\
        .with_target_mode(entity.ExcludeItems(entity.TargetFormation(formation, max_range=8)))\
        .move_to_targeted_position()\
        .with_sp_cost(15)
    })

def AtkMod(position):
    x, y = position
    return entity.Entity(str(uuid.uuid4()), components={
        'Stats': entity.Stats({'atk': 12}, stat_inc_per_level=LEVEL_PC_STAT_INC),
        'Position': entity.Position(x, y),
        'Render': entity.Render(character='*', colour=tcod.peach),
        'Item': entity.Item('ATK Up', 'Provides a boost in ATK to the attached item'),
        'Mod': entity.Mod(),
    })

def DfnMod(position):
    x, y = position
    return entity.Entity(str(uuid.uuid4()), components={
        'Stats': entity.Stats({'dfn': 12}, stat_inc_per_level=LEVEL_PC_STAT_INC),
        'Position': entity.Position(x, y),
        'Render': entity.Render(character='*', colour=tcod.peach),
        'Item': entity.Item('DFN Up', 'Provides a boost in DFN to the attached item'),
        'Mod': entity.Mod(),
    })

def ItlMod(position):
    x, y = position
    return entity.Entity(str(uuid.uuid4()), components={
        'Stats': entity.Stats({'itl': 12}, stat_inc_per_level=LEVEL_PC_STAT_INC),
        'Position': entity.Position(x, y),
        'Render': entity.Render(character='*', colour=tcod.peach),
        'Item': entity.Item('ITL Up', 'Provides a boost in ITL to the attached item'),
        'Mod': entity.Mod(),
    })

def ResMod(position):
    x, y = position
    return entity.Entity(str(uuid.uuid4()), components={
        'Stats': entity.Stats({'res': 12}, stat_inc_per_level=LEVEL_PC_STAT_INC),
        'Position': entity.Position(x, y),
        'Render': entity.Render(character='*', colour=tcod.peach),
        'Item': entity.Item('RES Up', 'Provides a boost in RES to the attached item'),
        'Mod': entity.Mod(),
    })

def SpdMod(position):
    x, y = position
    return entity.Entity(str(uuid.uuid4()), components={
        'Stats': entity.Stats({'spd': 12}, stat_inc_per_level=LEVEL_PC_STAT_INC),
        'Position': entity.Position(x, y),
        'Render': entity.Render(character='*', colour=tcod.peach),
        'Item': entity.Item('SPD Up', 'Provides a boost in SPD to the attached item'),
        'Mod': entity.Mod(),
    })

def HitMod(position):
    x, y = position
    return entity.Entity(str(uuid.uuid4()), components={
        'Stats': entity.Stats({'hit': 12}, stat_inc_per_level=LEVEL_PC_STAT_INC),
        'Position': entity.Position(x, y),
        'Render': entity.Render(character='*', colour=tcod.peach),
        'Item': entity.Item('HIT Up', 'Provides a boost in HIT to the attached item'),
        'Mod': entity.Mod(),
    })

def MaxHPMod(position):
    x, y = position
    return entity.Entity(str(uuid.uuid4()), components={
        'Stats': entity.Stats({'max_hp': 55}, stat_inc_per_level=LEVEL_PC_STAT_INC),
        'Position': entity.Position(x, y),
        'Render': entity.Render(character='*', colour=tcod.peach),
        'Item': entity.Item('Max HP Up', 'Provides a boost in max HP to the attached item'),
        'Mod': entity.Mod(),
    })

def MeleeLifeDrainMod(position):
    x, y = position
    return entity.Entity(str(uuid.uuid4()), components={
        'Stats': entity.Stats({'lifedrain': 15}, stat_inc_per_level=LEVEL_PC_STAT_INC),
        'Position': entity.Position(x, y),
        'Render': entity.Render(character='*', colour=tcod.red),
        'Item': entity.Item('Melee Lifedrain', 'Grants 15% lifedrain for melee attacks'),
        'Mod': entity.Mod(),
    })

def MeleeDeathblowMod(position):
    x, y = position
    return entity.Entity(str(uuid.uuid4()), components={
        'Stats': entity.Stats({'deathblow': 2}, stat_inc_per_level=LEVEL_PC_STAT_INC),
        'Position': entity.Position(x, y),
        'Render': entity.Render(character='*', colour=tcod.dark_crimson),
        'Item': entity.Item('Melee Deathblow', 'Grants a 2% chance to deal a deathblow on melee attacks'),
        'Mod': entity.Mod(),
    })

def SPRegenMod(position):
    x, y = position
    return entity.Entity(str(uuid.uuid4()), components={
        'Stats': entity.Stats({'sp_regen': 1}, set(['sp_regen']), stat_inc_per_level=LEVEL_PC_STAT_INC),
        'Position': entity.Position(x, y),
        'Render': entity.Render(character='*', colour=tcod.lighter_blue),
        'Item': entity.Item('SP Regen', 'Restores 1 SP every 4 turns (can level)'),
        'Mod': entity.Mod(),
    })

def HPRegenMod(position):
    x, y = position
    return entity.Entity(str(uuid.uuid4()), components={
        'Stats': entity.Stats({'hp_regen': 4}, set(['hp_regen']), stat_inc_per_level=LEVEL_PC_STAT_INC),
        'Position': entity.Position(x, y),
        'Render': entity.Render(character='*', colour=tcod.lighter_red),
        'Item': entity.Item('HP Regen', 'Restores 4 HP every 4 turns (can level)'),
        'Mod': entity.Mod(),
    })

def SpellSoulDrainMod(position):
    x, y = position
    return entity.Entity(str(uuid.uuid4()), components={
        'Stats': entity.Stats({'souldrain': 10}, stat_inc_per_level=LEVEL_PC_STAT_INC),
        'Position': entity.Position(x, y),
        'Render': entity.Render(character='*', colour=tcod.blue),
        'Item': entity.Item('Spell Souldrain', 'Grants 10% spell souldrain'),
        'Mod': entity.Mod(),
    })

def ToxicForceMod(position):
    x, y = position
    return entity.Entity(str(uuid.uuid4()), components={
        'Stats': entity.Stats({'self_poison': 1, 'boost_atk': 1}, stat_inc_per_level=LEVEL_PC_STAT_INC),
        'Position': entity.Position(x, y),
        'Render': entity.Render(character='*', colour=tcod.chartreuse),
        'Item': entity.Item('Toxic Force', 'Boosts ATK (stacks), but self-poisons'),
        'Mod': entity.Mod(),
    })

def ToxicPowerMod(position):
    x, y = position
    return entity.Entity(str(uuid.uuid4()), components={
        'Stats': entity.Stats({'self_poison': 1, 'boost_itl': 1}, stat_inc_per_level=LEVEL_PC_STAT_INC),
        'Position': entity.Position(x, y),
        'Render': entity.Render(character='*', colour=tcod.dark_green),
        'Item': entity.Item('Venom Power', 'Boost ITL (stacks), but self-poisons'),
        'Mod': entity.Mod(),
    })

def PoisonHealMod(position):
    x, y = position
    return entity.Entity(str(uuid.uuid4()), components={
        'Stats': entity.Stats({'poison_heal': 1}, stat_inc_per_level=LEVEL_PC_STAT_INC),
        'Position': entity.Position(x, y),
        'Render': entity.Render(character='*', colour=tcod.green),
        'Item': entity.Item('Poison Heal', 'Poison heals you'),
        'Mod': entity.Mod(),
    })

def SoulConversionMod(position):
    x, y = position
    return entity.Entity(str(uuid.uuid4()), components={
        'Stats': entity.Stats({'sp_usage_heals': 1}, stat_inc_per_level=LEVEL_PC_STAT_INC),
        'Position': entity.Position(x, y),
        'Render': entity.Render(character='*', colour=tcod.purple),
        'Item': entity.Item('Soul Conversion', 'Spending SP restores HP'),
        'Mod': entity.Mod(),
    })

def FireDamageMod(position):
    x, y = position
    return entity.Entity(str(uuid.uuid4()), components={
        'Stats': entity.Stats({'fire_dam': 20}, stat_inc_per_level=LEVEL_PC_STAT_INC),
        'Position': entity.Position(x, y),
        'Render': entity.Render(character='*', colour=tcod.dark_red),
        'Item': entity.Item('Fire Damage Up', 'Increases fire damage dealt by 20% (can level)'),
        'Mod': entity.Mod(),
    })

def IceDamageMod(position):
    x, y = position
    return entity.Entity(str(uuid.uuid4()), components={
        'Stats': entity.Stats({'ice_dam': 20}, stat_inc_per_level=LEVEL_PC_STAT_INC),
        'Position': entity.Position(x, y),
        'Render': entity.Render(character='*', colour=tcod.dark_cyan),
        'Item': entity.Item('Ice Damage Up', 'Increases ice damage dealt by 20% (can level)'),
        'Mod': entity.Mod(),
    })

def LightningDamageMod(position):
    x, y = position
    return entity.Entity(str(uuid.uuid4()), components={
        'Stats': entity.Stats({'lght_dam': 20}, stat_inc_per_level=LEVEL_PC_STAT_INC),
        'Position': entity.Position(x, y),
        'Render': entity.Render(character='*', colour=tcod.dark_yellow),
        'Item': entity.Item('Lightning Damage Up', 'Increases lightning damage dealt by 20% (can level)'),
        'Mod': entity.Mod(),
    })

def PhysicalDamageMod(position):
    x, y = position
    return entity.Entity(str(uuid.uuid4()), components={
        'Stats': entity.Stats({'phys_dam': 20}, stat_inc_per_level=LEVEL_PC_STAT_INC),
        'Position': entity.Position(x, y),
        'Render': entity.Render(character='*', colour=tcod.silver),
        'Item': entity.Item('Physical Damage Up', 'Increases physical damage dealt by 20% (can level)'),
        'Mod': entity.Mod(),
    })

def BloodMagicMod(position):
    x, y = position
    return entity.Entity(str(uuid.uuid4()), components={
        'Stats': entity.Stats({'blood_magic': 1}, stat_inc_per_level=LEVEL_PC_STAT_INC),
        'Position': entity.Position(x, y),
        'Render': entity.Render(character='*', colour=tcod.dark_purple),
        'Item': entity.Item('Blood Magic', 'Use HP instead of SP for costs'),
        'Mod': entity.Mod(),
    })

def AssaultMod(position):
    x, y = position
    return entity.Entity(str(uuid.uuid4()), components={
        'Stats': entity.Stats({'assault': 1}, stat_inc_per_level=LEVEL_PC_STAT_INC),
        'Position': entity.Position(x, y),
        'Render': entity.Render(character='*', colour=tcod.gray),
        'Item': entity.Item('Assault', 'Using melee attack skills grants Assault for 2 turns (deal and take 20% more damage)'),
        'Mod': entity.Mod(),
    })

def BlazeMod(position):
    x, y = position
    return entity.Entity(str(uuid.uuid4()), components={
        'Stats': entity.Stats({'improve_fire_aoe': 1}, stat_inc_per_level=LEVEL_PC_STAT_INC),
        'Position': entity.Position(x, y),
        'Render': entity.Render(character='*', colour=tcod.dark_red),
        'Item': entity.Item('Blaze', 'Fire\'s area of effect is improved'),
        'Mod': entity.Mod(),
    })

def EnergisingColdMod(position):
    x, y = position
    return entity.Entity(str(uuid.uuid4()), components={
        'Stats': entity.Stats({'ice_souldrain': 1}, stat_inc_per_level=LEVEL_PC_STAT_INC),
        'Position': entity.Position(x, y),
        'Render': entity.Render(character='*', colour=tcod.dark_cyan),
        'Item': entity.Item('Energising Cold', 'Ice spells have 10% souldrain'),
        'Mod': entity.Mod(),
    })

def InvigoratingPowerMod(position):
    x, y = position
    return entity.Entity(str(uuid.uuid4()), components={
        'Stats': entity.Stats({'lightning_lifedrain': 1}, stat_inc_per_level=LEVEL_PC_STAT_INC),
        'Position': entity.Position(x, y),
        'Render': entity.Render(character='*', colour=tcod.dark_yellow),
        'Item': entity.Item('Invigorating Power', 'Lightning spells have 10% lifedrain'),
        'Mod': entity.Mod(),
    })

def EmpoweringFlameMod(position):
    x, y = position
    return entity.Entity(str(uuid.uuid4()), components={
        'Stats': entity.Stats({'fire_assault': 1}, stat_inc_per_level=LEVEL_PC_STAT_INC),
        'Position': entity.Position(x, y),
        'Render': entity.Render(character='*', colour=tcod.dark_red),
        'Item': entity.Item('Empowering Flame', 'Fire spells grant Assault for 2 turns'),
        'Mod': entity.Mod(),
    })

def RampageMod(position):
    x, y = position
    return entity.Entity(str(uuid.uuid4()), components={
        'Stats': entity.Stats({'assault_regen_hp': 5}, stat_inc_per_level=LEVEL_PC_STAT_INC),
        'Position': entity.Position(x, y),
        'Render': entity.Render(character='*', colour=tcod.silver),
        'Item': entity.Item('Rampage', 'You regenerate 5% of your max HP per turn when you have assault (stacks)'),
        'Mod': entity.Mod(),
    })

def EnvenomedBladeMod(position):
    x, y = position
    return entity.Entity(str(uuid.uuid4()), components={
        'Stats': entity.Stats({'cleave_poison': 5}, stat_inc_per_level=LEVEL_PC_STAT_INC),
        'Position': entity.Position(x, y),
        'Render': entity.Render(character='*', colour=tcod.light_chartreuse),
        'Item': entity.Item('Envenomed Blade', 'Cleave inflicts poison'),
        'Mod': entity.Mod(),
    })

def FireResistanceMod(position):
    x, y = position
    return entity.Entity(str(uuid.uuid4()), components={
        'Stats': entity.Stats({'fire_res': 20}, stat_inc_per_level=LEVEL_PC_STAT_INC),
        'Position': entity.Position(x, y),
        'Render': entity.Render(character='*', colour=tcod.dark_red),
        'Item': entity.Item('Fire Resistance Up', 'Increases fire resistance by 20% (can level)'),
        'Mod': entity.Mod(),
    })

def IceResistanceMod(position):
    x, y = position
    return entity.Entity(str(uuid.uuid4()), components={
        'Stats': entity.Stats({'ice_res': 20}, stat_inc_per_level=LEVEL_PC_STAT_INC),
        'Position': entity.Position(x, y),
        'Render': entity.Render(character='*', colour=tcod.dark_cyan),
        'Item': entity.Item('Ice Resistance Up', 'Increases ice resistance by 20% (can level)'),
        'Mod': entity.Mod(),
    })

def LightningResistanceMod(position):
    x, y = position
    return entity.Entity(str(uuid.uuid4()), components={
        'Stats': entity.Stats({'lght_res': 20}, stat_inc_per_level=LEVEL_PC_STAT_INC),
        'Position': entity.Position(x, y),
        'Render': entity.Render(character='*', colour=tcod.dark_yellow),
        'Item': entity.Item('Lightning Resistance Up', 'Increases lightning resistance by 20% (can level)'),
        'Mod': entity.Mod(),
    })

def PhysicalResistanceMod(position):
    x, y = position
    return entity.Entity(str(uuid.uuid4()), components={
        'Stats': entity.Stats({'phys_res': 20}, stat_inc_per_level=LEVEL_PC_STAT_INC),
        'Position': entity.Position(x, y),
        'Render': entity.Render(character='*', colour=tcod.silver),
        'Item': entity.Item('Physical Resistance Up', 'Increases physical resistance by 20% (can level)'),
        'Mod': entity.Mod(),
    })

def MindchillMod(position):
    x, y = position
    return entity.Entity(str(uuid.uuid4()), components={
        'Stats': entity.Stats({'ice_mind_break': 1}, stat_inc_per_level=LEVEL_PC_STAT_INC),
        'Position': entity.Position(x, y),
        'Render': entity.Render(character='*', colour=tcod.lighter_purple),
        'Item': entity.Item('Brain freeze', 'Ice spells inflict mind break for 4 turns'),
        'Mod': entity.Mod(),
    })

def StupefyMod(position):
    x, y = position
    return entity.Entity(str(uuid.uuid4()), components={
        'Stats': entity.Stats({'mindbreak_paralyzes': 1}, stat_inc_per_level=LEVEL_PC_STAT_INC),
        'Position': entity.Position(x, y),
        'Render': entity.Render(character='*', colour=tcod.fuchsia),
        'Item': entity.Item('Stupefy', 'Inflicting mind break on enemies paralyzes them as well'),
        'Mod': entity.Mod(),
    })

def StrideMod(position):
    x, y = position
    return entity.Entity(str(uuid.uuid4()), components={
        'Stats': entity.Stats({'improve_dash_length': 1}, stat_inc_per_level=LEVEL_PC_STAT_INC),
        'Position': entity.Position(x, y),
        'Render': entity.Render(character='*', colour=tcod.dark_chartreuse),
        'Item': entity.Item('Stride', 'Dash moves you 3 tiles instead of 2'),
        'Mod': entity.Mod(),
    })

def SuddenDeathMod(position):
    x, y = position
    return entity.Entity(str(uuid.uuid4()), components={
        'Stats': entity.Stats({'deathblow_multiplier': 3, 'max_hp_pc_penalty': 25}, stat_inc_per_level=LEVEL_PC_STAT_INC),
        'Position': entity.Position(x, y),
        'Render': entity.Render(character='*', colour=tcod.dark_chartreuse),
        'Item': entity.Item('Sudden death', 'Your deathblow is tripled, but your max HP is reduced by 25%'),
        'Mod': entity.Mod(),
    })

def WillpowerMod(position):
    x, y = position
    return entity.Entity(str(uuid.uuid4()), components={
        'Stats': entity.Stats({'atk_becomes_itl': 1}),
        'Position': entity.Position(x, y),
        'Render': entity.Render(character='*', colour=tcod.magenta),
        'Item': entity.Item('Willpower', 'Your ATK is set to your ITL'),
        'Mod': entity.Mod(),
    })

def BrutalStrengthMod(position):
    x, y = position
    return entity.Entity(str(uuid.uuid4()), components={
        'Stats': entity.Stats({'itl_becomes_atk': 1}),
        'Position': entity.Position(x, y),
        'Render': entity.Render(character='*', colour=tcod.yellow),
        'Item': entity.Item('Brutal Strength', 'Your ITL is set to your ATK'),
        'Mod': entity.Mod(),
    })
