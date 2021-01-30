#!/usr/bin/env python

from formation import *
from entity import *
import util
import uuid
import loot
import ai
import skill_factory
import monster

class Allyslime:
    base_stats = {
        'max_hp': 80,
        'cur_hp': 80,
        'max_sp': 10,
        'cur_sp': 10,
        'atk': 30,
        'dfn': 10,
        'itl': 12,
        'res': 10,
        'spd': 12,
        'hit': 12,
        'exp_granted_bonus_multiplier': -1.0
    }

    names = ['Allyslime', 'Viscous allyslime', 'Honey allyslime', 'Mercury allyslime', 'Emerald allyslime']
    colours = [tcod.lighter_cyan, tcod.lighter_blue, tcod.lighter_yellow, tcod.lighter_grey, tcod.lighter_green]

    def MonWave():
        formation = Formation(origin=(1,1), formation=[['x','x','x'],
                                                       ['x','.','x'],
                                                       ['x','x','x']])
        return skill_factory.Skill()\
                            .with_target_mode(ExcludeItems(TargetFormation(formation, directional=True)))\
                            .damage_targets("{} smashes {}! ({} HP)")\
                            .with_damage(damage.MonsterAttackDamage(35, 'phys'))

    def generator(tier=settings.monster_tier, level=1):
        actual_stats = util.copy_dict(Allyslime.base_stats)
        actual_stats['level'] = level
        for stat in Stats.primary_stats | Stats.cur_stats - set(['cur_exp']):
            actual_stats[stat] = (Allyslime.base_stats[stat] + Allyslime.base_stats[stat] * (tier - 1) * monster.TIER_PC_STAT_INC)
            actual_stats[stat] += math.floor(monster.LEVEL_PC_STAT_INC * actual_stats[stat]) * (level-1)
        def gen(position):
            x, y = position
            return Entity(str(uuid.uuid4()), components={
                'Stats': Stats(actual_stats),
                'Position': Position(x, y),
                'Render': Render(character='s', colour=Allyslime.colours[tier-1]),
                'Combat': Combat(),
                'Ally': Combat(),
                'NPC': NPC(Allyslime.names[tier-1]),
                'AI': ai.AI()\
                .add_skill('MonWave', Allyslime.MonWave(), delay=1)\
                .with_state('IDLE', ai.AIState()\
                            .when_target_within_distance(1.5, lambda e, ai, ev_d : ai.use_skill(e, 'MonWave'))\
                            .when_target_within_distance(5, lambda e, ai, ev_d : ai.step_towards_target(e))\
                            .on_turn_otherwise(lambda e, ai, ev_d : ai.find_target(e), False)\
                            .on_turn_otherwise(lambda e, ai, ev_d : ai.step_towards_player(e)))\
            }, ttype='Allyslime_'+str(tier))
        return gen

class ThunderTotem:
    base_stats = {
        'max_hp': 10,
        'cur_hp': 10,
        'max_sp': 10,
        'cur_sp': 10,
        'atk': 30,
        'dfn': 10,
        'itl': 30,
        'res': 10,
        'spd': 12,
        'hit': 12,
        'exp_granted_bonus_multiplier': -1.0
    }

    names = ['Thunder totem', 'Thunder totem', 'Thunder totem', 'Thunder totem', 'Thunder totem']
    colours = [tcod.yellow, tcod.yellow, tcod.yellow, tcod.yellow, tcod.yellow]

    def Shockwave():
        formation = Formation(origin=(1,1), formation=[['x','x','x'],
                                                       ['x','.','x'],
                                                       ['x','x','x']])
        return skill_factory.Skill()\
                            .with_target_mode(ExcludeItems(TargetFormation(formation, directional=True)))\
                            .damage_targets("{} hits {} with a shockwave! ({} HP)")\
                            .with_damage(damage.MonsterAttackDamage(35, 'lght'))

    def generator(tier=settings.monster_tier, level=1):
        actual_stats = util.copy_dict(ThunderTotem.base_stats)
        actual_stats['level'] = level
        for stat in Stats.primary_stats | Stats.cur_stats - set(['cur_exp']):
            actual_stats[stat] = (ThunderTotem.base_stats[stat] + ThunderTotem.base_stats[stat] * (tier - 1) * monster.TIER_PC_STAT_INC)
            actual_stats[stat] += math.floor(monster.LEVEL_PC_STAT_INC * actual_stats[stat]) * (level-1)
        def gen(position):
            x, y = position
            return Entity(str(uuid.uuid4()), components={
                'Stats': Stats(actual_stats).with_status('.TEMPORARY', strength=1, duration=10),
                'Position': Position(x, y),
                'Render': Render(character='t', colour=ThunderTotem.colours[tier-1]),
                'Combat': Combat(),
                'Ally': Combat(),
                'NPC': NPC(ThunderTotem.names[tier-1]),
                'AI': ai.AI()\
                .add_skill('Shockwave', ThunderTotem.Shockwave(), delay=1)\
                .with_state('IDLE', ai.AIState()\
                            .on_turn_otherwise(lambda e, ai, ev_d : ai.find_target(e), False)\
                            .when_target_within_distance(1.5, lambda e, ai, ev_d : ai.use_skill(e, 'Shockwave')))\
            }, ttype='ThunderTotem_'+str(tier))
        return gen
