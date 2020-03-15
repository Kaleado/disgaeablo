#!/usr/bin/env python

from formation import *
from entity import *
import util
import uuid
import loot
import ai
import skill_factory

LEVEL_PC_STAT_INC = 0.2
TIER_PC_STAT_INC = 10

def ItemWorldClerkNPC(position):
    x, y = position
    return Entity(str(uuid.uuid4()), components={
        'Stats': Stats({
            'level': 999999,
            'max_hp': 9 * 10 ** 5,
            'cur_hp': 9 * 10 ** 5,
            'atk': 9 * 10 ** 9,
            'dfn': 9 * 10 ** 9,
            'itl': 9 * 10 ** 9,
            'res': 9 * 10 ** 9,
            'spd': 9 * 10 ** 9,
            'hit': 9 * 10 ** 9,
        }),

        'Position': Position(x, y),
        'Render': Render(character='@', colour=tcod.magenta),
        'Combat': Combat(),
        'NPC': NPC('Item world clerk'),
        'AI': ItemWorldClerk()
    })

class Slime:
    base_stats = {
        'max_hp': 100,
        'cur_hp': 100,
        'max_sp': 10,
        'cur_sp': 10,
        'atk': 20,
        'dfn': 10,
        'itl': 12,
        'res': 10,
        'spd': 12,
        'hit': 12
    }

    names = ['Slime', 'Viscous slime', 'Honey slime', 'Mercury slime', 'Emerald slime']
    colours = [tcod.cyan, tcod.blue, tcod.gold, tcod.silver, tcod.green]

    def MonWave():
        return SkillMelee(formation=Formation(origin=(1,1), formation=[['x','x','x'],['x','.','x'],['x','x','x']]))

    def generator(tier=1, level=1):
        actual_stats = util.copy_dict(Slime.base_stats)
        actual_stats['level'] = level
        for stat in Stats.primary_stats | Stats.cur_stats - set(['cur_exp']):
            actual_stats[stat] = (Slime.base_stats[stat] + Slime.base_stats[stat] * (tier - 1) * TIER_PC_STAT_INC)
            actual_stats[stat] += math.floor(LEVEL_PC_STAT_INC * actual_stats[stat]) * (level-1)
        def gen(position):
            x, y = position
            return Entity(str(uuid.uuid4()), components={
                'Stats': Stats(actual_stats),
                'Position': Position(x, y),
                'Render': Render(character='s', colour=Slime.colours[tier-1]),
                'Combat': Combat(),
                'NPC': NPC(Slime.names[tier-1]),
                'AI': ai.AI()\
                .add_skill('MonWave', Slime.MonWave(), delay=1)\
                .with_state('IDLE', ai.AIState()\
                            .when_player_within_distance(5, lambda e, ai, ev_d : ai.change_state('AGGRO'))\
                            .on_turn_otherwise(lambda e, ai, ev_d : ai.step_randomly(e)))\
                .with_state('AGGRO', ai.AIState()\
                            .when_player_within_distance(1.5, lambda e, ai, ev_d : ai.use_skill(e, 'MonWave'))\
                            .on_turn_otherwise(lambda e, ai, ev_d : ai.step_towards_player(e)))\
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
        actual_stats['level'] = level
        for stat in Stats.primary_stats | Stats.cur_stats - set(['cur_exp']):
            actual_stats[stat] = (Mage.base_stats[stat] + Mage.base_stats[stat] * (tier - 1) * TIER_PC_STAT_INC)
            actual_stats[stat] += math.floor(LEVEL_PC_STAT_INC * actual_stats[stat]) * (level-1)
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
        'atk': 15,
        'dfn': 12,
        'itl': 15,
        'res': 9,
        'spd': 8,
        'hit': 12
    }

    names = ['Mud golem', 'Stone golem', 'Iron golem', 'Magma golem', 'Mithril golem']
    colours = [tcod.orange, tcod.yellow, tcod.light_gray, tcod.crimson, tcod.cyan]

    def Stone():
        return SkillRanged(formation=Formation(origin=(1,1), formation=[['x','x','x'],['x','x','x'],['x','x','x']]), max_range=10)

    def generator(tier=1, level=1):
        actual_stats = util.copy_dict(Golem.base_stats)
        actual_stats['level'] = level
        for stat in Stats.primary_stats | Stats.cur_stats - set(['cur_exp']):
            actual_stats[stat] = (Golem.base_stats[stat] + Golem.base_stats[stat] * (tier - 1) * TIER_PC_STAT_INC)
            actual_stats[stat] += math.floor(LEVEL_PC_STAT_INC * actual_stats[stat]) * (level-1)
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

class Scorpion:
    base_stats = {
        'max_hp': 150,
        'cur_hp': 150,
        'max_sp': 40,
        'cur_sp': 40,
        'atk': 30,
        'dfn': 12,
        'itl': 10,
        'res': 8,
        'spd': 8,
        'hit': 12
    }

    names = ['Chittering scorpion', 'Hunter scorpion', 'Reaper scorpion', 'Predator scorpion', 'Death scorpion']
    colours = [tcod.orange, tcod.light_green, tcod.purple, tcod.dark_blue, tcod.crimson]

    def Sting():
        return SkillMelee(formation=Formation(origin=(1,1), formation=[['x','x','x'],
                                                                       ['.','.','.']]))

    def generator(tier=1, level=1):
        actual_stats = util.copy_dict(Scorpion.base_stats)
        actual_stats['level'] = level
        for stat in Stats.primary_stats | Stats.cur_stats - set(['cur_exp']):
            actual_stats[stat] = (Scorpion.base_stats[stat] + Scorpion.base_stats[stat] * (tier - 1) * TIER_PC_STAT_INC)
            actual_stats[stat] += math.floor(LEVEL_PC_STAT_INC * actual_stats[stat]) * (level-1)
        def gen(position):
            x, y = position
            return Entity(str(uuid.uuid4()), components={
                'Stats': Stats(actual_stats),
                'Position': Position(x, y),
                'Render': Render(character='S', colour=Scorpion.colours[tier-1]),
                'Combat': Combat(),
                'NPC': NPC(Scorpion.names[tier-1]),
                'AI': Hostile(aggro_range=7, primary_skill=Scorpion.Sting(), primary_skill_range=1.9)
            })
        return gen

class Spider:
    base_stats = {
        'max_hp': 120,
        'cur_hp': 120,
        'max_sp': 40,
        'cur_sp': 40,
        'atk': 10,
        'dfn': 16,
        'itl': 16,
        'res': 8,
        'spd': 8,
        'hit': 12
    }

    names = ['Catchfoot spider', 'Webspitter spider', 'Shadelurk spider', 'Fearspinner spider', 'Deathtrap spider']
    colours = [tcod.green, tcod.red, tcod.purple, tcod.yellow, tcod.crimson]

    def Web():
        return SkillStatusSpell(status_effect='PARALYZE', status_duration=2,
                                formation=Formation(origin=(1,1), formation=[['x','x','x'],
                                                                             ['x','x','x'],
                                                                             ['x','x','x']]))

    def generator(tier=1, level=1):
        actual_stats = util.copy_dict(Spider.base_stats)
        actual_stats['level'] = level
        for stat in Stats.primary_stats | Stats.cur_stats - set(['cur_exp']):
            actual_stats[stat] = (Spider.base_stats[stat] + Spider.base_stats[stat] * (tier - 1) * TIER_PC_STAT_INC)
            actual_stats[stat] += math.floor(LEVEL_PC_STAT_INC * actual_stats[stat]) * (level-1)
        def gen(position):
            x, y = position
            return Entity(str(uuid.uuid4()), components={
                'Stats': Stats(actual_stats),
                'Position': Position(x, y),
                'Render': Render(character='P', colour=Spider.colours[tier-1]),
                'Combat': Combat(),
                'NPC': NPC(Spider.names[tier-1]),
                'AI': Slow(ai=Hostile(aggro_range=7, primary_skill=Spider.Web(), primary_skill_range=5, keep_at_range=3, primary_skill_delay=2))
            })
        return gen

class Eye:
    base_stats = {
        'max_hp': 80,
        'cur_hp': 80,
        'max_sp': 40,
        'cur_sp': 40,
        'atk': 20,
        'dfn': 10,
        'itl': 16,
        'res': 18,
        'spd': 8,
        'hit': 12
    }

    names = ['Gaze eye', 'All-seeing eye', 'Chaos eye', 'Pandemonium eye', 'Omniscient eye']
    colours = [tcod.lighter_yellow, tcod.turquoise, tcod.purple, tcod.dark_crimson, tcod.yellow]

    def Gaze():
        return SkillMelee(formation=Formation(origin=(0,0), formation=[['.'] + ['x'] * 100]))

    def generator(tier=1, level=1):
        actual_stats = util.copy_dict(Eye.base_stats)
        actual_stats['level'] = level
        for stat in Stats.primary_stats | Stats.cur_stats - set(['cur_exp']):
            actual_stats[stat] = (Eye.base_stats[stat] + Eye.base_stats[stat] * (tier - 1) * TIER_PC_STAT_INC)
            actual_stats[stat] += math.floor(LEVEL_PC_STAT_INC * actual_stats[stat]) * (level-1)
        def gen(position):
            x, y = position
            return Entity(str(uuid.uuid4()), components={
                'Stats': Stats(actual_stats),
                'Position': Position(x, y),
                'Render': Render(character='e', colour=Eye.colours[tier-1]),
                'Combat': Combat(),
                'NPC': NPC(Eye.names[tier-1]),
                'AI': Hostile(aggro_range=1000, primary_skill=Eye.Gaze(), immobile=True)
            })
        return gen

class Wyvern:
    base_stats = {
        'max_hp': 80,
        'cur_hp': 80,
        'max_sp': 40,
        'cur_sp': 40,
        'atk': 20,
        'dfn': 12,
        'itl': 16,
        'res': 12,
        'spd': 8,
        'hit': 12
    }

    names = ['Scorch wyvern', 'Blaze wyvern', 'Crash wyvern', 'Storm wyvern', 'Eclipse wyvern']
    colours = [tcod.lighter_yellow, tcod.turquoise, tcod.purple, tcod.dark_crimson, tcod.yellow]

    def Ray():
        return SkillSpell(formation=Formation(origin=(2,2), formation=[
            ['x','x','x','x','x'],
            ['x','x','x','.','x'],
            ['x','x','x','x','x'],
            ['x','.','x','x','x'],
            ['x','x','x','x','x'],
        ]))

    def generator(tier=1, level=1):
        actual_stats = util.copy_dict(Wyvern.base_stats)
        actual_stats['level'] = level
        for stat in Stats.primary_stats | Stats.cur_stats - set(['cur_exp']):
            actual_stats[stat] = (Wyvern.base_stats[stat] + Wyvern.base_stats[stat] * (tier - 1) * TIER_PC_STAT_INC)
            actual_stats[stat] += math.floor(LEVEL_PC_STAT_INC * actual_stats[stat]) * (level-1)
        def gen(position):
            x, y = position
            return Entity(str(uuid.uuid4()), components={
                'Stats': Stats(actual_stats),
                'Position': Position(x, y),
                'Render': Render(character='W', colour=Wyvern.colours[tier-1]),
                'Combat': Combat(),
                'NPC': NPC(Wyvern.names[tier-1]),
                'AI': Hostile(aggro_range=12, primary_skill=Wyvern.Ray(), keep_at_range=3)
            })
        return gen

class Beholder:
    base_stats = {
        'max_hp': 70,
        'cur_hp': 70,
        'max_sp': 40,
        'cur_sp': 40,
        'atk': 20,
        'dfn': 14,
        'itl': 12,
        'res': 8,
        'spd': 8,
        'hit': 12
    }

    names = ['Lesser beholder', 'Beholder', 'Greater beholder', 'Beholder lord', 'Omniscient beholder']
    colours = [tcod.lighter_yellow, tcod.turquoise, tcod.purple, tcod.dark_crimson, tcod.yellow]

    def Ray():
        return SkillMelee(formation=Formation(origin=(0,2), formation=[
            ['.','.','.','x','x','x','x'],
            ['.','.','x','x','x','x','x'],
            ['.','x','x','x','x','x','x'],
            ['.','.','x','x','x','x','x'],
            ['.','.','.','x','x','x','x'],
        ]))

    def generator(tier=1, level=1):
        actual_stats = util.copy_dict(Beholder.base_stats)
        actual_stats['level'] = level
        for stat in Stats.primary_stats | Stats.cur_stats - set(['cur_exp']):
            actual_stats[stat] = (Beholder.base_stats[stat] + Beholder.base_stats[stat] * (tier - 1) * TIER_PC_STAT_INC)
            actual_stats[stat] += math.floor(LEVEL_PC_STAT_INC * actual_stats[stat]) * (level-1)
        def gen(position):
            x, y = position
            return Entity(str(uuid.uuid4()), components={
                'Stats': Stats(actual_stats),
                'Position': Position(x, y),
                'Render': Render(character='E', colour=Beholder.colours[tier-1]),
                'Combat': Combat(),
                'NPC': NPC(Beholder.names[tier-1]),
                'AI': Hostile(aggro_range=10, primary_skill=Beholder.Ray(), primary_skill_range=5, keep_at_range=3)
            })
        return gen

class Giant:
    base_stats = {
        'max_hp': 170,
        'cur_hp': 170,
        'max_sp': 40,
        'cur_sp': 40,
        'atk': 20,
        'dfn': 14,
        'itl': 12,
        'res': 8,
        'spd': 8,
        'hit': 12
    }

    names = ['Hill giant', 'Moss giant', 'Stone giant', 'Iron giant', 'Fire giant']
    colours = [tcod.lighter_orange, tcod.dark_green, tcod.lighter_gray, tcod.silver, tcod.red]

    def Smash():
        return SkillMelee(formation=Formation(origin=(1,3), formation=[
            ['x','x','x'],
            ['x','x','x'],
            ['x','x','x'],
            ['.','.','.']
        ]))

    def generator(tier=1, level=1):
        actual_stats = util.copy_dict(Giant.base_stats)
        actual_stats['level'] = level
        for stat in Stats.primary_stats | Stats.cur_stats - set(['cur_exp']):
            actual_stats[stat] = (Giant.base_stats[stat] + Giant.base_stats[stat] * (tier - 1) * TIER_PC_STAT_INC)
            actual_stats[stat] += math.floor(LEVEL_PC_STAT_INC * actual_stats[stat]) * (level-1)
        def gen(position):
            x, y = position
            return Entity(str(uuid.uuid4()), components={
                'Stats': Stats(actual_stats),
                'Position': Position(x, y),
                'Render': Render(character='G', colour=Giant.colours[tier-1]),
                'Combat': Combat(),
                'NPC': NPC(Giant.names[tier-1]),
                'AI': Hostile(aggro_range=10, primary_skill=Giant.Smash(), primary_skill_range=2)
            })
        return gen

# Bosses

class BossTheSneak:
    base_stats = {
        'max_hp': 300,
        'cur_hp': 300,
        'max_sp': 10,
        'cur_sp': 10,
        'atk': 20,
        'dfn': 17,
        'itl': 50,
        'res': 27,
        'spd': 12,
        'hit': 12
    }

    names = ['Jerome, the sneak'] * 5
    colours = [tcod.cyan, tcod.blue, tcod.gold, tcod.silver, tcod.green]

    def Lightning():
        formation = Formation(origin=(1,1), formation=[['.','x','.'],
                                                       ['x','x','x'],
                                                       ['.','x','.']])
        return skill_factory.Skill()\
                            .with_target_mode(NoFriendlyFire(ExcludeItems(TargetFormation(formation))))\
                            .damage_targets("{} drops a bolt of lightning on {}! ({} HP)")\
                            .with_damage(damage.SpellDamage(1, 'lght'))

    def BigFire():
        formation = Formation(origin=(2,2), formation=[['x','x','x','x','x'],
                                                       ['x','x','x','x','x'],
                                                       ['x','x','x','x','x'],
                                                       ['x','x','x','x','x'],
                                                       ['x','x','x','x','x']])
        return skill_factory.Skill()\
                            .with_target_mode(NoFriendlyFire(ExcludeItems(TargetFormation(formation))))\
                            .damage_targets("{} emits a blast of fire at {}! ({} HP)")\
                            .with_damage(damage.SpellDamage(1, 'fire'))

    def Escape():
        return skill_factory.Skill()\
                            .with_target_mode(TargetUser())\
                            .teleport_targets_randomly()\
                            .print_message("Jerome laughs as he disappears into thin air!")

    def generator(tier=1, level=1):
        actual_stats = util.copy_dict(BossTheSneak.base_stats)
        actual_stats['level'] = level
        for stat in Stats.primary_stats | Stats.cur_stats - set(['cur_exp']):
            actual_stats[stat] = (BossTheSneak.base_stats[stat] + BossTheSneak.base_stats[stat] * (tier - 1) * TIER_PC_STAT_INC)
            actual_stats[stat] += math.floor(LEVEL_PC_STAT_INC * actual_stats[stat]) * (level-1)
        def gen(position):
            x, y = position
            return Entity(str(uuid.uuid4()), components={
                'Stats': Stats(actual_stats),
                'Position': Position(x, y),
                'Render': Render(character='h', colour=BossTheSneak.colours[tier-1]),
                'Combat': Combat(),
                'NPC': NPC(BossTheSneak.names[tier-1]),
                'AI': ai.AI()\
                .add_skill('Escape', BossTheSneak.Escape(), 2)\
                .add_skill('BigFire', BossTheSneak.BigFire(), 2)\
                .add_skill('Lightning', BossTheSneak.Lightning(), 1)\
                .with_state('IDLE', ai.AIState()\
                            .when_player_within_distance(25, lambda e, ai, ev_d : ai.change_state('RANGED_PHASE'))\
                            .on_turn_otherwise(lambda e, ai, ev_d : ai.step_randomly(e)))\
                .with_state('RANGED_PHASE', ai.AIState()\
                            .when_under_proportion_hp(0.5, lambda e, ai, ev_d : ai.change_state('MELEE_PHASE'))\
                            .when_player_within_distance(1.5, lambda e, ai, ev_d : ai.use_skill(e, 'Escape'))\
                            .when_player_within_distance(7, lambda e, ai, ev_d : ai.use_skill(e, 'BigFire'))\
                            .when_player_within_distance(25, lambda e, ai, ev_d : ai.use_skill(e, 'Lightning'))\
                            .on_turn_otherwise(lambda e, ai, ev_d : ai.step_towards_player(e)))\
                .with_state('MELEE_PHASE', ai.AIState()\
                            .when_player_beyond_distance(2, lambda e, ai, ev_d : ai.use_skill(e, 'BigFire'))\
                            .on_turn_randomly(0.1, lambda e, ai, ev_d : ai.use_skill(e, 'Escape'))\
                            .on_turn_otherwise(lambda e, ai, ev_d : ai.step_away_from_player(e)))\
            })
        return gen

class BossUltimateBeholder:
    base_stats = {
        'max_hp': 300,
        'cur_hp': 300,
        'max_sp': 10,
        'cur_sp': 10,
        'atk': 20,
        'dfn': 12,
        'itl': 50,
        'res': 27,
        'spd': 12,
        'hit': 12
    }

    names = ['Azxtryzxtaz, King of beholders'] * 5
    colours = [tcod.red, tcod.orange, tcod.green, tcod.chartreuse, tcod.peach]

    def Laser():
        formation = Formation(origin=(2,0), formation=[['.','.','.','.','.'],
                                                       ['.','.','x','.','.'],
                                                       ['.','x','x','x','.'],
                                                       ['x','x','x','x','x']] + [['x','x','x','x','x']] * 30)
        return skill_factory.Skill()\
                            .with_target_mode(NoFriendlyFire(ExcludeItems(TargetFormation(formation, directional=True))))\
                            .damage_targets("{}'s blazing eye ray scorches {}! ({} HP)")\
                            .with_damage(damage.SpellDamage(2, 'fire'))

    def TeleportAdds():
        return skill_factory.Skill()\
                            .with_target_mode(WithComponents(['UltimateBeholderAdd'], TargetEveryone()))\
                            .teleport_targets_randomly()\
                            .print_message("Azxtryzxtaz emits a sharp screeching noise!")

    def Escape():
        return skill_factory.Skill()\
                            .with_target_mode(TargetUser())\
                            .teleport_targets_randomly()\
                            .print_message("Azxtryzxtaz laughs as he disappears into thin air!")

    def generator(tier=1, level=1):
        actual_stats = util.copy_dict(BossUltimateBeholder.base_stats)
        actual_stats['level'] = level
        for stat in Stats.primary_stats | Stats.cur_stats - set(['cur_exp']):
            actual_stats[stat] = (BossUltimateBeholder.base_stats[stat] + BossUltimateBeholder.base_stats[stat] * (tier - 1) * TIER_PC_STAT_INC)
            actual_stats[stat] += math.floor(LEVEL_PC_STAT_INC * actual_stats[stat]) * (level-1)
        def gen(position):
            x, y = position
            return Entity(str(uuid.uuid4()), components={
                'Stats': Stats(actual_stats),
                'Position': Position(x, y),
                'Render': Render(character='E', colour=BossUltimateBeholder.colours[tier-1]),
                'Combat': Combat(),
                'NPC': NPC(BossUltimateBeholder.names[tier-1]),
                'AI': ai.AI()\
                .add_skill('Laser', BossUltimateBeholder.Laser(), 2)\
                .add_skill('Escape', BossUltimateBeholder.Escape(), 3)\
                .add_skill('TeleportAdds', BossUltimateBeholder.TeleportAdds(), 0)\
                .with_state('IDLE', ai.AIState()\
                            .when_player_within_distance(25, lambda e, ai, ev_d : ai.change_state('RANGED_PHASE'))\
                            .on_turn_otherwise(lambda e, ai, ev_d : ai.step_randomly(e)))\
                .with_state('RANGED_PHASE', ai.AIState()\
                            .when_player_within_distance(2, lambda e, ai, ev_d : ai.use_skill(e, 'Escape'))\
                            .on_turn_randomly(0.2, lambda e, ai, ev_d : ai.use_skill(e, 'TeleportAdds'))\
                            .when_player_within_distance(25, lambda e, ai, ev_d : ai.use_skill(e, 'Laser'))\
                            .on_turn_otherwise(lambda e, ai, ev_d : ai.step_towards_player(e)))\
            })
        return gen
