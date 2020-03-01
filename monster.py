#!/usr/bin/env python

from formation import *
from entity import *
import util
import uuid
import loot

class Slime:
    base_stats = {
        'max_hp': 120,
        'cur_hp': 120,
        'max_sp': 10,
        'cur_sp': 10,
        'atk': 20,
        'dfn': 12,
        'itl': 12,
        'res': 12,
        'spd': 12,
        'hit': 12
    }

    names = ['Slime', 'Viscous slime', 'Honey slime', 'Mercury slime', 'Emerald slime']
    colours = [tcod.cyan, tcod.blue, tcod.gold, tcod.silver, tcod.green]

    def MonWave():
        return SkillMelee(formation=Formation(origin=(1,1), formation=[['x','x','x'],['x','.','x'],['x','x','x']]))

    def generator(tier=1, level=1):
        actual_stats = util.copy_dict(Slime.base_stats)
        for stat in Stats.primary_stats | Stats.cur_stats - set(['cur_exp']):
            actual_stats[stat] = (Slime.base_stats[stat] + Slime.base_stats[stat] * (tier - 1) * 100)
            actual_stats[stat] += math.floor(0.07 * actual_stats[stat]) * (level-1)
        def gen(position):
            x, y = position
            return Entity(str(uuid.uuid4()), components={
                'Stats': Stats(actual_stats),
                'Position': Position(x, y),
                'Render': Render(character='s', colour=Slime.colours[tier-1]),
                'Combat': Combat(),
                'NPC': NPC(Slime.names[tier-1]),
                'AI': Hostile(primary_skill=Slime.MonWave(), primary_skill_range=1.5)
            })
        return gen

class Mage:
    base_stats = {
        'max_hp': 80,
        'cur_hp': 80,
        'max_sp': 50,
        'cur_sp': 50,
        'atk': 8,
        'dfn': 12,
        'itl': 18,
        'res': 20,
        'spd': 12,
        'hit': 12
    }

    names = ['Apprentice', 'Mage', 'Wizard', 'Warlock', 'Master']
    colours = [tcod.blue, tcod.green, tcod.orange, tcod.purple, tcod.violet]

    def Lightning():
        return SkillSpell(formation=Formation(origin=(1,1), formation=[['.','x','.'],['x','x','x'],['.','x','.']]))

    def generator(tier=1, level=1):
        actual_stats = util.copy_dict(Mage.base_stats)
        for stat in Stats.primary_stats | Stats.cur_stats - set(['cur_exp']):
            actual_stats[stat] = (Mage.base_stats[stat] + Mage.base_stats[stat] * (tier - 1) * 100)
            actual_stats[stat] += math.floor(0.07 * actual_stats[stat]) * (level-1)
        def gen(position):
            x, y = position
            return Entity(str(uuid.uuid4()), components={
                'Stats': Stats(actual_stats),
                'Position': Position(x, y),
                'Render': Render(character='m', colour=Mage.colours[tier-1]),
                'Combat': Combat(),
                'NPC': NPC(Mage.names[tier-1]),
                'AI': Hostile(aggro_range=7, primary_skill=Mage.Lightning(), primary_skill_range=5)
            })
        return gen

class Golem:
    base_stats = {
        'max_hp': 180,
        'cur_hp': 180,
        'max_sp': 40,
        'cur_sp': 40,
        'atk': 20,
        'dfn': 12,
        'itl': 18,
        'res': 10,
        'spd': 8,
        'hit': 12
    }

    names = ['Mud golem', 'Stone golem', 'Iron golem', 'Magma golem', 'Mithril golem']
    colours = [tcod.orange, tcod.yellow, tcod.light_gray, tcod.crimson, tcod.cyan]

    def Stone():
        return SkillSpell(formation=Formation(origin=(1,1), formation=[['x','x','x'],['x','x','x'],['x','x','x']]))

    def generator(tier=1, level=1):
        actual_stats = util.copy_dict(Golem.base_stats)
        for stat in Stats.primary_stats | Stats.cur_stats - set(['cur_exp']):
            actual_stats[stat] = (Golem.base_stats[stat] + Golem.base_stats[stat] * (tier - 1) * 100)
            actual_stats[stat] += math.floor(0.07 * actual_stats[stat]) * (level-1)
        def gen(position):
            x, y = position
            return Entity(str(uuid.uuid4()), components={
                'Stats': Stats(actual_stats),
                'Position': Position(x, y),
                'Render': Render(character='G', colour=Golem.colours[tier-1]),
                'Combat': Combat(),
                'NPC': NPC(Golem.names[tier-1]),
                'AI': Slow(ai=Hostile(aggro_range=7, primary_skill=Golem.Stone(), primary_skill_range=5))
            })
        return gen
