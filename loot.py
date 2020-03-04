#!/usr/bin/env python

from formation import *
import util
import entity
import uuid
import tcod
import math
import random

##################################################### CONSUMABLES
def TownPortal(position):
    x, y = position
    return entity.Entity(str(uuid.uuid4()), components={
        'Stats': entity.Stats({}),
        'Position': entity.Position(x, y),
        'Render': entity.Render(character='+', colour=tcod.lighter_blue),
        'Item': entity.Item("Town portal"),
        'Usable': entity.ConsumeAfter(entity.ReturnToTown())
    })

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
        'max_sp': 25,
        'cur_sp': 25,
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
                'Equipment': entity.Equipment(mod_slots=[None] * random.randint(0,4)),
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
                'Equipment': entity.Equipment(mod_slots=[None] * random.randint(0,4)),
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
        'Stats': entity.Stats({'atk': 35}),
        'Position': entity.Position(x, y),
        'Render': entity.Render(character='&', colour=tcod.light_green),
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
        'Stats': entity.Stats({'atk': 35}),
        'Position': entity.Position(x, y),
        'Render': entity.Render(character='&', colour=tcod.light_green),
        'Item': entity.Item('Skill: Pierce'),
        'Usable': entity.Cost(sp=3, usable=entity.SkillMelee(formation)),
    })

def Bypass(position):
    formation = Formation(origin=(0,3), formation=[['x','.'],
                                                   ['x','.'],
                                                   ['x','P'],
                                                   ['.','.']])
    x, y = position
    return entity.Entity(str(uuid.uuid4()), components={
        'Stats': entity.Stats({'atk': 25}),
        'Position': entity.Position(x, y),
        'Render': entity.Render(character='&', colour=tcod.light_green),
        'Item': entity.Item('Skill: Bypass'),
        'Usable': entity.Cost(sp=3, usable=entity.SkillMelee(formation)),
    })

def WhipSlash(position):
    formation = Formation(origin=(0,1), formation=[['x','x','x'],
                                                   ['x','.','P']])
    x, y = position
    return entity.Entity(str(uuid.uuid4()), components={
        'Stats': entity.Stats({'atk': 25}),
        'Position': entity.Position(x, y),
        'Render': entity.Render(character='&', colour=tcod.light_green),
        'Item': entity.Item('Skill: Whip slash'),
        'Usable': entity.Cost(sp=3, usable=entity.SkillMelee(formation)),
    })

def Dash(position):
    formation = Formation(origin=(0,2), formation=[['P'],
                                                   ['.'],
                                                   ['.']])
    x, y = position
    return entity.Entity(str(uuid.uuid4()), components={
        'Stats': entity.Stats({}),
        'Position': entity.Position(x, y),
        'Render': entity.Render(character='&', colour=tcod.green),
        'Item': entity.Item('Skill: Dash'),
        'Usable': entity.Cost(sp=2, usable=entity.SkillMelee(formation)),
    })

def RollingStab(position):
    formation = Formation(origin=(0,3), formation=[['P'],
                                                   ['x'],
                                                   ['x'],
                                                   ['.']])
    x, y = position
    return entity.Entity(str(uuid.uuid4()), components={
        'Stats': entity.Stats({'atk': 20}),
        'Position': entity.Position(x, y),
        'Render': entity.Render(character='&', colour=tcod.light_green),
        'Item': entity.Item('Skill: Rolling stab'),
        'Usable': entity.Cost(sp=7, usable=entity.SkillMelee(formation)),
    })

def AerialDrop(position):
    formation = Formation(origin=(1,1), formation=[['x','x','x'],
                                                   ['x','P','x'],
                                                   ['x','x','x']])
    x, y = position
    return entity.Entity(str(uuid.uuid4()), components={
        'Stats': entity.Stats({'atk': 20}),
        'Position': entity.Position(x, y),
        'Render': entity.Render(character='&', colour=tcod.light_green),
        'Item': entity.Item('Skill: Aerial drop'),
        'Usable': entity.Cost(sp=15, usable=entity.SkillRanged(formation, max_range=5)),
    })

def Fire(position):
    formation = Formation(origin=(0,0), formation=[['x']])
    x, y = position
    return entity.Entity(str(uuid.uuid4()), components={
        'Stats': entity.Stats({'itl': 35}),
        'Position': entity.Position(x, y),
        'Render': entity.Render(character='&', colour=tcod.light_purple),
        'Item': entity.Item('Spell: Fire'),
        'Usable': entity.Cost(sp=2, usable=entity.SkillSpell(formation, element='fire')),
    })

def Ice(position):
    formation = Formation(origin=(1,0), formation=[['x', 'x', 'x', 'x', 'x']])
    x, y = position
    return entity.Entity(str(uuid.uuid4()), components={
        'Stats': entity.Stats({'itl': 27}),
        'Position': entity.Position(x, y),
        'Render': entity.Render(character='&', colour=tcod.light_purple),
        'Item': entity.Item('Spell: Ice'),
        'Usable': entity.Cost(sp=2, usable=entity.SkillSpell(formation, element='ice')),
    })

def Lightning(position):
    formation = Formation(origin=(1,1), formation=[['x', 'x', 'x'],
                                                   ['x', 'x', 'x'],
                                                   ['x', 'x', 'x']])
    x, y = position
    return entity.Entity(str(uuid.uuid4()), components={
        'Stats': entity.Stats({'itl': 27}),
        'Position': entity.Position(x, y),
        'Render': entity.Render(character='&', colour=tcod.light_purple),
        'Item': entity.Item('Spell: Lightning'),
        'Usable': entity.Cost(sp=2, usable=entity.SkillSpell(formation, element='lght')),
    })

def Paralyze(position):
    formation = Formation(origin=(0,0), formation=[['x','x'],
                                                   ['x','x']])
    x, y = position
    return entity.Entity(str(uuid.uuid4()), components={
        'Stats': entity.Stats({'itl': 20}),
        'Position': entity.Position(x, y),
        'Render': entity.Render(character='&', colour=tcod.purple),
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
        'Render': entity.Render(character='&', colour=tcod.purple),
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
        'Render': entity.Render(character='&', colour=tcod.purple),
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
        'Render': entity.Render(character='&', colour=tcod.purple),
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
        'Render': entity.Render(character='&', colour=tcod.purple),
        'Item': entity.Item('Spell: Weaken'),
        'Usable': entity.Cost(sp=3, usable=entity.SkillStatusSpell(formation, 'WEAKEN', 12)),
    })

def Stoneskin(position):
    formation = Formation(origin=(0,0), formation=[['x']])
    x, y = position
    return entity.Entity(str(uuid.uuid4()), components={
        'Stats': entity.Stats({'itl': 20}),
        'Position': entity.Position(x, y),
        'Render': entity.Render(character='&', colour=tcod.purple),
        'Item': entity.Item('Spell: Stoneskin'),
        'Usable': entity.Cost(sp=3, usable=entity.SkillStatusSpell(formation, 'STONESKIN', 10)),
    })

def Blink(position):
    x, y = position
    return entity.Entity(str(uuid.uuid4()), components={
        'Stats': entity.Stats({'itl': 20}),
        'Position': entity.Position(x, y),
        'Render': entity.Render(character='&', colour=tcod.purple),
        'Item': entity.Item('Spell: Blink'),
        'Usable': entity.Cost(sp=15, usable=entity.TeleportToPosition(4)),
    })

def AtkMod(position):
    x, y = position
    return entity.Entity(str(uuid.uuid4()), components={
        'Stats': entity.Stats({'atk': 7}),
        'Position': entity.Position(x, y),
        'Render': entity.Render(character='*', colour=tcod.peach),
        'Item': entity.Item('ATK Up'),
        'Mod': entity.Mod(),
    })

def DfnMod(position):
    x, y = position
    return entity.Entity(str(uuid.uuid4()), components={
        'Stats': entity.Stats({'dfn': 7}),
        'Position': entity.Position(x, y),
        'Render': entity.Render(character='*', colour=tcod.peach),
        'Item': entity.Item('DFN Up'),
        'Mod': entity.Mod(),
    })

def ItlMod(position):
    x, y = position
    return entity.Entity(str(uuid.uuid4()), components={
        'Stats': entity.Stats({'itl': 7}),
        'Position': entity.Position(x, y),
        'Render': entity.Render(character='*', colour=tcod.peach),
        'Item': entity.Item('ITL Up'),
        'Mod': entity.Mod(),
    })

def ResMod(position):
    x, y = position
    return entity.Entity(str(uuid.uuid4()), components={
        'Stats': entity.Stats({'res': 7}),
        'Position': entity.Position(x, y),
        'Render': entity.Render(character='*', colour=tcod.peach),
        'Item': entity.Item('RES Up'),
        'Mod': entity.Mod(),
    })

def SpdMod(position):
    x, y = position
    return entity.Entity(str(uuid.uuid4()), components={
        'Stats': entity.Stats({'spd': 7}),
        'Position': entity.Position(x, y),
        'Render': entity.Render(character='*', colour=tcod.peach),
        'Item': entity.Item('SPD Up'),
        'Mod': entity.Mod(),
    })

def HitMod(position):
    x, y = position
    return entity.Entity(str(uuid.uuid4()), components={
        'Stats': entity.Stats({'hit': 7}),
        'Position': entity.Position(x, y),
        'Render': entity.Render(character='*', colour=tcod.peach),
        'Item': entity.Item('HIT Up'),
        'Mod': entity.Mod(),
    })

def MeleeLifeDrainMod(position):
    x, y = position
    return entity.Entity(str(uuid.uuid4()), components={
        'Stats': entity.Stats({'lifedrain': 2}),
        'Position': entity.Position(x, y),
        'Render': entity.Render(character='*', colour=tcod.red),
        'Item': entity.Item('Melee Lifedrain'),
        'Mod': entity.Mod(),
    })

def MeleeDeathblowMod(position):
    x, y = position
    return entity.Entity(str(uuid.uuid4()), components={
        'Stats': entity.Stats({'deathblow': 2}),
        'Position': entity.Position(x, y),
        'Render': entity.Render(character='*', colour=tcod.dark_crimson),
        'Item': entity.Item('Melee Deathblow'),
        'Mod': entity.Mod(),
    })

def SPRegenMod(position):
    x, y = position
    return entity.Entity(str(uuid.uuid4()), components={
        'Stats': entity.Stats({'sp_regen': 1}),
        'Position': entity.Position(x, y),
        'Render': entity.Render(character='*', colour=tcod.lighter_blue),
        'Item': entity.Item('SP Regen'),
        'Mod': entity.Mod(),
    })

def HPRegenMod(position):
    x, y = position
    return entity.Entity(str(uuid.uuid4()), components={
        'Stats': entity.Stats({'hp_regen': 1}),
        'Position': entity.Position(x, y),
        'Render': entity.Render(character='*', colour=tcod.lighter_red),
        'Item': entity.Item('HP Regen'),
        'Mod': entity.Mod(),
    })

def SpellSoulDrainMod(position):
    x, y = position
    return entity.Entity(str(uuid.uuid4()), components={
        'Stats': entity.Stats({'souldrain': 2}),
        'Position': entity.Position(x, y),
        'Render': entity.Render(character='*', colour=tcod.blue),
        'Item': entity.Item('Spell Souldrain'),
        'Mod': entity.Mod(),
    })

def ToxicForceMod(position):
    x, y = position
    return entity.Entity(str(uuid.uuid4()), components={
        'Stats': entity.Stats({'self_poison': 1, 'double_atk': 1}),
        'Position': entity.Position(x, y),
        'Render': entity.Render(character='*', colour=tcod.chartreuse),
        'Item': entity.Item('Toxic Force'),
        'Mod': entity.Mod(),
    })

def ToxicPowerMod(position):
    x, y = position
    return entity.Entity(str(uuid.uuid4()), components={
        'Stats': entity.Stats({'self_poison': 1, 'double_itl': 1}),
        'Position': entity.Position(x, y),
        'Render': entity.Render(character='*', colour=tcod.dark_green),
        'Item': entity.Item('Toxic Power'),
        'Mod': entity.Mod(),
    })

def PoisonHealMod(position):
    x, y = position
    return entity.Entity(str(uuid.uuid4()), components={
        'Stats': entity.Stats({'poison_heal': 1}),
        'Position': entity.Position(x, y),
        'Render': entity.Render(character='*', colour=tcod.green),
        'Item': entity.Item('Poison Heal'),
        'Mod': entity.Mod(),
    })

def SoulConversionMod(position):
    x, y = position
    return entity.Entity(str(uuid.uuid4()), components={
        'Stats': entity.Stats({'sp_usage_heals': 1}),
        'Position': entity.Position(x, y),
        'Render': entity.Render(character='*', colour=tcod.purple),
        'Item': entity.Item('Soul Conversion'),
        'Mod': entity.Mod(),
    })

def FireDamageMod(position):
    x, y = position
    return entity.Entity(str(uuid.uuid4()), components={
        'Stats': entity.Stats({'fire_dam': 10}),
        'Position': entity.Position(x, y),
        'Render': entity.Render(character='*', colour=tcod.dark_red),
        'Item': entity.Item('Fire Damage Up'),
        'Mod': entity.Mod(),
    })

def IceDamageMod(position):
    x, y = position
    return entity.Entity(str(uuid.uuid4()), components={
        'Stats': entity.Stats({'ice_dam': 10}),
        'Position': entity.Position(x, y),
        'Render': entity.Render(character='*', colour=tcod.dark_cyan),
        'Item': entity.Item('Ice Damage Up'),
        'Mod': entity.Mod(),
    })

def LightningDamageMod(position):
    x, y = position
    return entity.Entity(str(uuid.uuid4()), components={
        'Stats': entity.Stats({'lght_dam': 10}),
        'Position': entity.Position(x, y),
        'Render': entity.Render(character='*', colour=tcod.dark_yellow),
        'Item': entity.Item('Lightning Damage Up'),
        'Mod': entity.Mod(),
    })

def PhysicalDamageMod(position):
    x, y = position
    return entity.Entity(str(uuid.uuid4()), components={
        'Stats': entity.Stats({'phys_dam': 10}),
        'Position': entity.Position(x, y),
        'Render': entity.Render(character='*', colour=tcod.silver),
        'Item': entity.Item('Physical Damage Up'),
        'Mod': entity.Mod(),
    })
