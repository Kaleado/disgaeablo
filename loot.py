#!/usr/bin/env python

from formation import *
import util
import entity
import uuid
import tcod
import math

##################################################### CONSUMABLES

class Healing:
    base_stats = {
        'max_hp': 50,
        'cur_hp': 50,
    }
    names = ['Rosemary', 'Sage', 'Daffodil', 'Nettle', 'Chamomile', 'Ginseng', 'Valerian']
    colours = [tcod.cyan, tcod.blue, tcod.gold, tcod.silver, tcod.green, tcod.magenta, tcod.red]

    def generator(tier=1, level=1):
        actual_stats = util.copy_dict(Healing.base_stats)
        for stat in Healing.base_stats:
            actual_stats[stat] = (Healing.base_stats[stat] + Healing.base_stats[stat] * (tier - 1) * 100)
            actual_stats[stat] += math.floor(0.07 * actual_stats[stat]) * (level-1)
        def gen(position):
            x, y = position
            return entity.Entity(str(uuid.uuid4()), components={
                'Stats': entity.Stats(actual_stats),
                'Position': entity.Position(x, y),
                'Render': entity.Render(character='"', colour=Healing.colours[tier-1]),
                'Item': entity.Item(Healing.names[tier-1]),
                'Usable': entity.ConsumeAfter(entity.Heal(entity.TargetUser()))
            })
        return gen

class Refreshing:
    base_stats = {
        'max_sp': 50,
        'cur_sp': 50,
    }
    names = ['Spring water', 'Apple juice', 'Nectar', 'Morning dew']
    colours = [tcod.cyan, tcod.blue, tcod.gold, tcod.silver, tcod.green]

    def generator(tier=1, level=1):
        actual_stats = util.copy_dict(Refreshing.base_stats)
        for stat in Refreshing.base_stats:
            actual_stats[stat] = (Refreshing.base_stats[stat] + Refreshing.base_stats[stat] * (tier - 1) * 100)
            actual_stats[stat] += math.floor(0.07 * actual_stats[stat]) * (level-1)
        def gen(position):
            x, y = position
            return entity.Entity(str(uuid.uuid4()), components={
                'Stats': entity.Stats(actual_stats),
                'Position': entity.Position(x, y),
                'Render': entity.Render(character='!', colour=Refreshing.colours[tier-1]),
                'Item': entity.Item(Refreshing.names[tier-1]),
                'Usable': entity.ConsumeAfter(entity.Refresh(entity.TargetUser()))
            })
        return gen

##################################################### WEAPONS

class Sword:
    base_stats = {
        'atk': 15,
    }
    names = ['Rusted sword', 'Shortsword', 'Broadsword', 'Estoc', 'Claymore', 'Flamberge', 'Zanbato']
    colours = [tcod.cyan, tcod.blue, tcod.gold, tcod.silver, tcod.green, tcod.magenta, tcod.red]

    def generator(tier=1, level=1):
        actual_stats = util.copy_dict(Sword.base_stats)
        for stat in Sword.base_stats:
            actual_stats[stat] = (Sword.base_stats[stat] + Sword.base_stats[stat] * (tier - 1) * 100)
            actual_stats[stat] += math.floor(0.07 * actual_stats[stat]) * (level-1)
        def gen(position):
            x, y = position
            return entity.Entity(str(uuid.uuid4()), components={
                'Stats': entity.Stats(actual_stats),
                'Position': entity.Position(x, y),
                'Equipment': entity.Equipment(),
                'Render': entity.Render(character='/', colour=Sword.colours[tier-1]),
                'Item': entity.Item(Sword.names[tier-1]),
            })
        return gen

class Staff:
    base_stats = {
        'itl': 15,
    }
    names = ['Bent staff', 'Apprentice staff', 'Novice rod', 'Battlestaff', 'Angel\'s cane', 'Greatstaff', 'Yggdrasil branch']
    colours = [tcod.cyan, tcod.blue, tcod.gold, tcod.silver, tcod.green, tcod.magenta, tcod.red]

    def generator(tier=1, level=1):
        actual_stats = util.copy_dict(Staff.base_stats)
        for stat in Staff.base_stats:
            actual_stats[stat] = (Staff.base_stats[stat] + Staff.base_stats[stat] * (tier - 1) * 100)
            actual_stats[stat] += math.floor(0.07 * actual_stats[stat]) * (level-1)
        def gen(position):
            x, y = position
            return entity.Entity(str(uuid.uuid4()), components={
                'Stats': entity.Stats(actual_stats),
                'Position': entity.Position(x, y),
                'Equipment': entity.Equipment(),
                'Render': entity.Render(character='|', colour=Staff.colours[tier-1]),
                'Item': entity.Item(Staff.names[tier-1]),
            })
        return gen

##################################################### SKLLS

def Cleave(position):
    formation = Formation(origin=(1,2), formation=[['x','x','x'],
                                                   ['x','x','x'],
                                                   ['.','.',',']])
    x, y = position
    return entity.Entity(str(uuid.uuid4()), components={
        'Stats': entity.Stats({'atk': 30}),
        'Position': entity.Position(x, y),
        'Render': entity.Render(character='&', colour=tcod.green),
        'Item': entity.Item('Skill: Cleave'),
        'Usable': entity.Cost(sp=3, usable=entity.SkillMelee(formation)),
    })

def Pierce(position):
    formation = Formation(origin=(0,4), formation=[['x'],
                                                   ['x'],
                                                   ['x'],
                                                   ['x'],
                                                   ['.']])
    x, y = position
    return entity.Entity(str(uuid.uuid4()), components={
        'Stats': entity.Stats({'atk': 25}),
        'Position': entity.Position(x, y),
        'Render': entity.Render(character='&', colour=tcod.green),
        'Item': entity.Item('Skill: Pierce'),
        'Usable': entity.Cost(sp=3, usable=entity.SkillMelee(formation)),
    })

def Dash(position):
    formation = Formation(origin=(0,2), formation=[['P'],
                                                   ['.'],
                                                   ['.']])
    x, y = position
    return entity.Entity(str(uuid.uuid4()), components={
        'Stats': entity.Stats(),
        'Position': entity.Position(x, y),
        'Render': entity.Render(character='&', colour=tcod.green),
        'Item': entity.Item('Skill: Dash'),
        'Usable': entity.Cost(sp=10, usable=entity.SkillMelee(formation)),
    })

def RollingStab(position):
    formation = Formation(origin=(0,2), formation=[['P'],
                                                   ['.'],
                                                   ['x'],
                                                   ['.']])
    x, y = position
    return entity.Entity(str(uuid.uuid4()), components={
        'Stats': entity.Stats({'atk': 20}),
        'Position': entity.Position(x, y),
        'Render': entity.Render(character='&', colour=tcod.green),
        'Item': entity.Item('Skill: Rolling stab'),
        'Usable': entity.Cost(sp=10, usable=entity.SkillMelee(formation)),
    })

def Fire(position):
    formation = Formation(origin=(0,0), formation=[['x']])
    x, y = position
    return entity.Entity(str(uuid.uuid4()), components={
        'Stats': entity.Stats({'itl': 30}),
        'Position': entity.Position(x, y),
        'Render': entity.Render(character='&', colour=tcod.green),
        'Item': entity.Item('Spell: Fire'),
        'Usable': entity.Cost(sp=5, usable=entity.SkillSpell(formation)),
    })

def Ice(position):
    formation = Formation(origin=(1,0), formation=[['x', 'x', 'x', 'x', 'x']])
    x, y = position
    return entity.Entity(str(uuid.uuid4()), components={
        'Stats': entity.Stats({'itl': 20}),
        'Position': entity.Position(x, y),
        'Render': entity.Render(character='&', colour=tcod.green),
        'Item': entity.Item('Spell: Ice'),
        'Usable': entity.Cost(sp=3, usable=entity.SkillSpell(formation)),
    })

def Lightning(position):
    formation = Formation(origin=(1,1), formation=[['x', 'x', 'x'],
                                                   ['x', 'x', 'x'],
                                                   ['x', 'x', 'x']])
    x, y = position
    return entity.Entity(str(uuid.uuid4()), components={
        'Stats': entity.Stats({'itl': 25}),
        'Position': entity.Position(x, y),
        'Render': entity.Render(character='&', colour=tcod.green),
        'Item': entity.Item('Spell: Lightning'),
        'Usable': entity.Cost(sp=3, usable=entity.SkillSpell(formation)),
    })

def Paralyze(position):
    formation = Formation(origin=(0,0), formation=[['x','x'],
                                                   ['x','x']])
    x, y = position
    return entity.Entity(str(uuid.uuid4()), components={
        'Stats': entity.Stats({'itl': 20}),
        'Position': entity.Position(x, y),
        'Render': entity.Render(character='&', colour=tcod.green),
        'Item': entity.Item('Spell: Paralyze'),
        'Usable': entity.Cost(sp=3, usable=entity.SkillStatusSpell(formation, 'PARALYZE', 6)),
    })

def Poison(position):
    formation = Formation(origin=(0,0), formation=[['x','x','x','x'],
                                                   ['x','x','x','x'],
                                                   ['x','x','x','x'],
                                                   ['x','x','x','x']])
    x, y = position
    return entity.Entity(str(uuid.uuid4()), components={
        'Stats': entity.Stats({'itl': 20}),
        'Position': entity.Position(x, y),
        'Render': entity.Render(character='&', colour=tcod.green),
        'Item': entity.Item('Spell: Poison'),
        'Usable': entity.Cost(sp=3, usable=entity.SkillStatusSpell(formation, 'POISON', 8)),
    })

def GuardBreak(position):
    formation = Formation(origin=(0,0), formation=[['x','x','x','x'],
                                                   ['x','x','x','x'],
                                                   ['x','x','x','x'],
                                                   ['x','x','x','x']])
    x, y = position
    return entity.Entity(str(uuid.uuid4()), components={
        'Stats': entity.Stats({'itl': 20}),
        'Position': entity.Position(x, y),
        'Render': entity.Render(character='&', colour=tcod.green),
        'Item': entity.Item('Spell: Guard Break'),
        'Usable': entity.Cost(sp=3, usable=entity.SkillStatusSpell(formation, 'GUARD_BREAK', 12)),
    })

def MindBreak(position):
    formation = Formation(origin=(0,0), formation=[['x','x','x','x'],
                                                   ['x','x','x','x'],
                                                   ['x','x','x','x'],
                                                   ['x','x','x','x']])
    x, y = position
    return entity.Entity(str(uuid.uuid4()), components={
        'Stats': entity.Stats({'itl': 20}),
        'Position': entity.Position(x, y),
        'Render': entity.Render(character='&', colour=tcod.green),
        'Item': entity.Item('Spell: Mind Break'),
        'Usable': entity.Cost(sp=3, usable=entity.SkillStatusSpell(formation, 'MIND_BREAK', 12)),
    })

def Weaken(position):
    formation = Formation(origin=(0,0), formation=[['x','x','x','x'],
                                                   ['x','x','x','x'],
                                                   ['x','x','x','x'],
                                                   ['x','x','x','x']])
    x, y = position
    return entity.Entity(str(uuid.uuid4()), components={
        'Stats': entity.Stats({'itl': 20}),
        'Position': entity.Position(x, y),
        'Render': entity.Render(character='&', colour=tcod.green),
        'Item': entity.Item('Spell: Weaken'),
        'Usable': entity.Cost(sp=3, usable=entity.SkillStatusSpell(formation, 'WEAKEN', 12)),
    })

def Stoneskin(position):
    formation = Formation(origin=(0,0), formation=[['x']])
    x, y = position
    return entity.Entity(str(uuid.uuid4()), components={
        'Stats': entity.Stats({'itl': 20}),
        'Position': entity.Position(x, y),
        'Render': entity.Render(character='&', colour=tcod.green),
        'Item': entity.Item('Spell: Stoneskin'),
        'Usable': entity.Cost(sp=3, usable=entity.SkillStatusSpell(formation, 'STONESKIN', 10)),
    })

def Blink(position):
    x, y = position
    return entity.Entity(str(uuid.uuid4()), components={
        'Stats': entity.Stats({'itl': 20}),
        'Position': entity.Position(x, y),
        'Render': entity.Render(character='&', colour=tcod.green),
        'Item': entity.Item('Spell: Blink'),
        'Usable': entity.Cost(sp=15, usable=entity.TeleportToPosition(4)),
    })
