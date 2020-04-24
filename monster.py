#!/usr/bin/env python

from formation import *
from entity import *
import util
import uuid
import loot
import ai
import skill_factory

LEVEL_PC_STAT_INC = balance.monster_level_stat_inc
TIER_PC_STAT_INC = balance.monster_tier_stat_inc

def Player(position):
    x, y = position
    return Entity('PLAYER', components={
        'Stats': Stats(balance.player_initial_stats),
        'Combat': Combat(),
        'Position': Position(x, y),
        'Render': Render(character="@", colour=tcod.red),
        'PlayerLogic': PlayerLogic(),
        'Inventory': Inventory(),
        'AI': AI(),
        'EquipmentSlots': EquipmentSlots(['Weapon', 'Armour', 'Armour', 'Armour']),
    }, ttype='Player')

def MailmanNPC(position):
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
        'Neutral': Combat(),
        'Position': Position(x, y),
        'Render': Render(character='@', colour=tcod.yellow),
        'Combat': Combat(),
        'NPC': NPC('Jack, mailman'),
        'AI': Mailman()
    }, ttype='MailmanNPC')

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
        'Neutral': Combat(),
        'Position': Position(x, y),
        'Render': Render(character='@', colour=tcod.magenta),
        'Combat': Combat(),
        'NPC': NPC('Lisa, item world clerk'),
        'AI': ItemWorldClerk()
    }, ttype='ItemWorldClerkNPC')

def UptierShopNPC(position):
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
        'Neutral': Combat(),
        'Position': Position(x, y),
        'Render': Render(character='@', colour=tcod.light_gray),
        'Combat': Combat(),
        'NPC': NPC('Alan, weird occultist'),
        'AI': UptierShopkeeper()
    }, ttype='UptierShopNPC')

def ModShopNPC(position):
    import director
    x, y = position
    items = []
    for _ in range(8):
        items += [director.loot_director.loot_from_set(1, director.LootDirector.mods)((0,0))]
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
        'Neutral': Combat(),
        'Position': Position(x, y),
        'Render': Render(character='@', colour=tcod.green),
        'Combat': Combat(),
        'NPC': NPC('Leo, mod salesman'),
        'Inventory': Inventory(items),
        'AI': Shopkeeper()
    }, ttype='ModShopNPC')

def EquipmentShopNPC(position):
    import director
    x, y = position
    items = []
    for _ in range(8):
        items += [director.loot_director.loot_from_set(1, director.LootDirector.equipment).generator(tier=settings.loot_tier)((0,0))]
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
        'Neutral': Combat(),
        'Position': Position(x, y),
        'Render': Render(character='@', colour=tcod.blue),
        'Combat': Combat(),
        'NPC': NPC('Joseph, equipment salesman'),
        'Inventory': Inventory(items),
        'AI': Shopkeeper()
    }, ttype='EquipmentShopNPC')

def SkillShopNPC(position):
    import director
    x, y = position
    items = []
    for _ in range(8):
        items += [director.loot_director
                  .loot_from_set(1, director.LootDirector.attack_skills | director.LootDirector.support_skills)((0,0))]
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
        'Neutral': Combat(),
        'Position': Position(x, y),
        'Render': Render(character='@', colour=tcod.lighter_blue),
        'Combat': Combat(),
        'NPC': NPC('Bridget, skillbook librarian'),
        'Inventory': Inventory(items),
        'AI': Shopkeeper()
    }, ttype='SkillShopNPC')

def GrimmsvilleSkeleton(position):
    import director
    x, y = position
    items = []
    for _ in range(8):
        items += [director.loot_director
                  .loot_from_set(1, director.LootDirector.attack_skills | director.LootDirector.support_skills)((0,0))]
    return Entity(str(uuid.uuid4()), components={
        'Stats': Stats({
            'level': 1,
            'max_hp': 1,
            'cur_hp': 1,
            'atk': 1,
            'dfn': 1,
            'itl': 1,
            'res': 1,
            'spd': 1,
            'hit': 1,
            'exp_granted_bonus_multiplier': -1, #dont kill the skeletons
        }),
        'Neutral': Combat(),
        'Position': Position(x, y),
        'Render': Render(character='s', colour=tcod.gray),
        'Combat': Combat(),
        'NPC': NPC('Skeleton'),
        'Inventory': Inventory(items),
        'AI': GVilleTownsperson()
    }, ttype='GrimmsvilleSkeleton')

def ItemEnhancerNPC(position):
    import director
    x, y = position
    items = []
    for _ in range(8):
        items += [loot.ItemLeveler25((0,0))]
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
        'Neutral': Combat(),
        'Position': Position(x, y),
        'Render': Render(character='@', colour=tcod.peach),
        'Combat': Combat(),
        'NPC': NPC('Diego, item enhancer'),
        'Inventory': Inventory(items),
        'AI': SkullShopkeeper()
    }, ttype='ItemEnhancerNPC')

def MultiplayerItemNPC(position):
    import director
    x, y = position
    items = []
    for _ in range(8):
        items += [director.loot_director
                  .loot_from_set(1, director.LootDirector.multiplayer)((0,0))]
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
        'Neutral': Combat(),
        'Position': Position(x, y),
        'Render': Render(character='@', colour=tcod.lighter_green),
        'Combat': Combat(),
        'NPC': NPC('Kasia, multiplayer item peddler'),
        'Inventory': Inventory(items),
        'AI': Shopkeeper()
    }, ttype='MultiplayerItemNPC')


class Slime:
    base_stats = {
        'max_hp': round(80 * balance.monster_stat_scale['max_hp']),
        'cur_hp': round(80 * balance.monster_stat_scale['max_hp']),
        'max_sp': round(10 * balance.monster_stat_scale['max_sp']),
        'cur_sp': round(10 * balance.monster_stat_scale['max_sp']),
        'atk': round(30 * balance.monster_stat_scale['atk']),
        'dfn': round(10 * balance.monster_stat_scale['dfn']),
        'itl': round(12 * balance.monster_stat_scale['itl']),
        'res': round(10 * balance.monster_stat_scale['res']),
        'spd': round(12 * balance.monster_stat_scale['spd']),
        'hit': 12 * balance.monster_stat_scale['hit']
    }

    names = ['Slime', 'Viscous slime', 'Honey slime', 'Mercury slime', 'Emerald slime']
    colours = [tcod.cyan, tcod.blue, tcod.gold, tcod.silver, tcod.green]

    def Smash():
        formation = Formation(origin=(1,1), formation=[['x','x','x'],
                                                       ['x','.','x'],
                                                       ['x','x','x']])
        return skill_factory.Skill()\
                            .with_target_mode(NoFriendlyFire(ExcludeItems(TargetFormation(formation, directional=True))))\
                            .damage_targets("{} smashes {}! ({} HP)")\
                            .with_damage(damage.MonsterAttackDamage(35, 'phys'))

    def generator(tier=settings.monster_tier, level=1):
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
                .add_skill('Smash', Slime.Smash(), delay=1)\
                .with_state('IDLE', ai.AIState()\
                            .when_player_within_distance(5, lambda e, ai, ev_d : ai.change_state('AGGRO'))\
                            .on_turn_otherwise(lambda e, ai, ev_d : ai.step_randomly(e)))\
                .with_state('AGGRO', ai.AIState()\
                            .when_player_within_distance(1.5, lambda e, ai, ev_d : ai.use_skill(e, 'Smash'))\
                            .on_turn_otherwise(lambda e, ai, ev_d : ai.step_towards_player(e)))\
            }, ttype='Slime_'+str(tier))
        return gen

class Mage:
    base_stats = {
        'max_hp': round(50 * balance.monster_stat_scale['max_hp']),
        'cur_hp': round(50 * balance.monster_stat_scale['max_hp']),
        'max_sp': round(50 * balance.monster_stat_scale['max_sp']),
        'cur_sp': round(50 * balance.monster_stat_scale['max_sp']),
        'atk': round(8 * balance.monster_stat_scale['atk']),
        'dfn': round(12 * balance.monster_stat_scale['dfn']),
        'itl': round(37 * balance.monster_stat_scale['itl']),
        'res': round(18 * balance.monster_stat_scale['res']),
        'spd': round(12 * balance.monster_stat_scale['spd']),
        'hit': 12 * balance.monster_stat_scale['hit']
    }

    names = ['Apprentice', 'Mage', 'Wizard', 'Warlock', 'Master']
    colours = [tcod.blue, tcod.green, tcod.orange, tcod.purple, tcod.violet]

    def Lightning():
        formation = Formation(origin=(1,1), formation=[['.','x','.'],
                                                       ['x','x','x'],
                                                       ['.','x','.']])
        return skill_factory.Skill()\
                            .with_target_mode(NoFriendlyFire(ExcludeItems(TargetFormation(formation, max_range=10))))\
                            .damage_targets("{} drops a bolt of lightning on {}! ({} HP)")\
                            .with_damage(damage.MonsterSpellDamage(45, 'lght'))

    def generator(tier=settings.monster_tier, level=1):
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
                'AI': ai.AI()\
                .add_skill('Lightning', Mage.Lightning(), delay=1)\
                .with_state('IDLE', ai.AIState()\
                            .when_player_within_distance(7, lambda e, ai, ev_d : ai.change_state('AGGRO'))\
                            .on_turn_otherwise(lambda e, ai, ev_d : ai.step_randomly(e)))\
                .with_state('AGGRO', ai.AIState()\
                            .when_player_within_distance(5, lambda e, ai, ev_d : ai.use_skill(e, 'Lightning'))\
                            .on_turn_otherwise(lambda e, ai, ev_d : ai.step_towards_player(e)))\
            }, ttype='Mage_'+str(tier))
        return gen

class Golem:
    base_stats = {
        'max_hp': round(100 * balance.monster_stat_scale['max_hp']),
        'cur_hp': round(100 * balance.monster_stat_scale['max_hp']),
        'max_sp': round(40 * balance.monster_stat_scale['max_sp']),
        'cur_sp': round(40 * balance.monster_stat_scale['max_sp']),
        'atk': round(30 * balance.monster_stat_scale['atk']),
        'dfn': round(12 * balance.monster_stat_scale['dfn']),
        'itl': round(30 * balance.monster_stat_scale['itl']),
        'res': round(9 * balance.monster_stat_scale['res']),
        'spd': round(8 * balance.monster_stat_scale['spd']),
        'hit': 12 * balance.monster_stat_scale['hit']
    }

    names = ['Mud golem', 'Stone golem', 'Iron golem', 'Magma golem', 'Mithril golem']
    colours = [tcod.darker_orange, tcod.dark_yellow, tcod.light_gray, tcod.crimson, tcod.cyan]

    def Stone():
        formation = Formation(origin=(1,1), formation=[['x','x','x'],
                                                       ['x','x','x'],
                                                       ['x','x','x']])
        return skill_factory.Skill()\
                            .with_target_mode(NoFriendlyFire(ExcludeItems(TargetFormation(formation, max_range=5))))\
                            .damage_targets("{} throws a boulder at {}! ({} HP)")\
                            .with_damage(damage.MonsterAttackDamage(25, 'phys'))

    def generator(tier=settings.monster_tier, level=1):
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
                'AI': ai.AI()\
                .add_skill('Stone', Golem.Stone(), delay=1)\
                .with_state('IDLE', ai.AIState()\
                            .when_player_within_distance(7, lambda e, ai, ev_d : ai.change_state('AGGRO'))\
                            .every_n_turns(2, lambda e, ai, ev_d : False)\
                            .on_turn_otherwise(lambda e, ai, ev_d : ai.step_randomly(e)))\
                .with_state('AGGRO', ai.AIState()\
                            .every_n_turns(2, lambda e, ai, ev_d : False)\
                            .when_player_within_distance(5, lambda e, ai, ev_d : ai.use_skill(e, 'Stone'))\
                            .on_turn_otherwise(lambda e, ai, ev_d : ai.step_towards_player(e)))\
            }, ttype='Golem_'+str(tier))
        return gen

class Scorpion:
    base_stats = {
        'max_hp': round(90 * balance.monster_stat_scale['max_hp']),
        'cur_hp': round(90 * balance.monster_stat_scale['max_hp']),
        'max_sp': round(40 * balance.monster_stat_scale['max_sp']),
        'cur_sp': round(40 * balance.monster_stat_scale['max_sp']),
        'atk': round(45 * balance.monster_stat_scale['atk']),
        'dfn': round(11 * balance.monster_stat_scale['dfn']),
        'itl': round(10 * balance.monster_stat_scale['itl']),
        'res': round(8 * balance.monster_stat_scale['res']),
        'spd': round(8 * balance.monster_stat_scale['spd']),
        'hit': 12 * balance.monster_stat_scale['hit']
    }

    names = ['Chittering scorpion', 'Hunter scorpion', 'Reaper scorpion', 'Predator scorpion', 'Death scorpion']
    colours = [tcod.orange, tcod.light_green, tcod.purple, tcod.dark_blue, tcod.crimson]

    def Sting():
        formation = Formation(origin=(1,1), formation=[['x','x','x'],
                                                       ['.','.','.']])
        return skill_factory.Skill()\
                            .with_target_mode(NoFriendlyFire(ExcludeItems(TargetFormation(formation, directional=True))))\
                            .damage_targets("{} pierces {} with its stinger! ({} HP)")\
                            .with_damage(damage.MonsterAttackDamage(45, 'phys'))

    def generator(tier=settings.monster_tier, level=1):
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
                'AI': ai.AI()\
                .add_skill('Sting', Scorpion.Sting(), delay=1)\
                .with_state('IDLE', ai.AIState()\
                            .when_player_within_distance(11, lambda e, ai, ev_d : ai.change_state('AGGRO'))\
                            .on_turn_otherwise(lambda e, ai, ev_d : ai.step_randomly(e)))\
                .with_state('AGGRO', ai.AIState()\
                            .when_player_within_distance(1.9, lambda e, ai, ev_d : ai.use_skill(e, 'Sting'))\
                            .on_turn_otherwise(lambda e, ai, ev_d : ai.step_towards_player(e)))\
            }, ttype='Scorpion_'+str(tier))
        return gen

class Spider:
    base_stats = {
        'max_hp': round(90 * balance.monster_stat_scale['max_hp']),
        'cur_hp': round(90 * balance.monster_stat_scale['max_hp']),
        'max_sp': round(40 * balance.monster_stat_scale['max_sp']),
        'cur_sp': round(40 * balance.monster_stat_scale['max_sp']),
        'atk': round(15 * balance.monster_stat_scale['atk']),
        'dfn': round(13 * balance.monster_stat_scale['dfn']),
        'itl': round(24 * balance.monster_stat_scale['itl']),
        'res': round(8 * balance.monster_stat_scale['res']),
        'spd': round(8 * balance.monster_stat_scale['spd']),
        'hit': 12 * balance.monster_stat_scale['hit']
    }

    names = ['Catchfoot spider', 'Webspitter spider', 'Shadelurk spider', 'Fearspinner spider', 'Deathtrap spider']
    colours = [tcod.green, tcod.red, tcod.purple, tcod.yellow, tcod.crimson]

    def Web():
        formation = Formation(origin=(1,1), formation=[['x','x','x'],
                                                       ['x','x','x'],
                                                       ['x','x','x']])

        return skill_factory.Skill()\
                            .with_target_mode(NoFriendlyFire(ExcludeItems(TargetFormation(formation, max_range=5))))\
                            .damage_targets("{} spins web at {}!")\
                            .with_damage(damage.MonsterSpellDamage(0))\
                            .change_damage(lambda d, s, t, i : damage.WithStatusEffect('PARALYZE', 1, 2, d))

    def generator(tier=settings.monster_tier, level=1):
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
                'AI': ai.AI()\
                .add_skill('Web', Spider.Web(), delay=2)\
                .with_state('IDLE', ai.AIState()\
                            .when_player_within_distance(7, lambda e, ai, ev_d : ai.change_state('AGGRO'))\
                            .on_turn_otherwise(lambda e, ai, ev_d : ai.step_randomly(e)))\
                .with_state('AGGRO', ai.AIState()\
                            .every_n_turns(2, lambda e, ai, ev_d : False)\
                            .when_player_within_distance(3, lambda e, ai, ev_d : ai.step_away_from_player(e))\
                            .when_player_within_distance(6, lambda e, ai, ev_d : ai.use_skill(e, 'Web'))\
                            .on_turn_otherwise(lambda e, ai, ev_d : ai.step_towards_player(e)))\
            }, ttype='Spider_'+str(tier))
        return gen

class Eye:
    base_stats = {
        'max_hp': round(80 * balance.monster_stat_scale['max_hp']),
        'cur_hp': round(80 * balance.monster_stat_scale['max_hp']),
        'max_sp': round(40 * balance.monster_stat_scale['max_sp']),
        'cur_sp': round(40 * balance.monster_stat_scale['max_sp']),
        'atk': round(30 * balance.monster_stat_scale['atk']),
        'dfn': round(10 * balance.monster_stat_scale['dfn']),
        'itl': round(30 * balance.monster_stat_scale['itl']),
        'res': round(18 * balance.monster_stat_scale['res']),
        'spd': round(8 * balance.monster_stat_scale['spd']),
        'hit': 12 * balance.monster_stat_scale['hit']
    }

    names = ['Gaze eye', 'All-seeing eye', 'Chaos eye', 'Pandemonium eye', 'Omniscient eye']
    colours = [tcod.lighter_yellow, tcod.turquoise, tcod.purple, tcod.dark_crimson, tcod.yellow]

    def Gaze():
        formation = Formation(origin=(0,0), formation=[['.'] + ['x'] * 100])
        return skill_factory.Skill()\
                            .with_target_mode(NoFriendlyFire(ExcludeItems(TargetFormation(formation, directional=True))))\
                            .damage_targets("{} scorches {} with a ray of light! ({} HP)")\
                            .with_damage(damage.MonsterSpellDamage(45, 'fire'))

    def generator(tier=settings.monster_tier, level=1):
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
                'AI': ai.AI()\
                .add_skill('Gaze', Eye.Gaze(), delay=1)\
                .with_state('IDLE', ai.AIState()\
                            .on_turn_otherwise(lambda e, ai, ev_d : ai.use_skill(e, 'Gaze')))\
            }, ttype='Eye_'+str(tier))
        return gen

class Wyvern:
    base_stats = {
        'max_hp': round(80 * balance.monster_stat_scale['max_hp']),
        'cur_hp': round(80 * balance.monster_stat_scale['max_hp']),
        'max_sp': round(40 * balance.monster_stat_scale['max_sp']),
        'cur_sp': round(40 * balance.monster_stat_scale['max_sp']),
        'atk': round(30 * balance.monster_stat_scale['atk']),
        'dfn': round(12 * balance.monster_stat_scale['dfn']),
        'itl': round(30 * balance.monster_stat_scale['itl']),
        'res': round(12 * balance.monster_stat_scale['res']),
        'spd': round(8 * balance.monster_stat_scale['spd']),
        'hit': 12 * balance.monster_stat_scale['hit']
    }

    names = ['Scorch wyvern', 'Blaze wyvern', 'Crash wyvern', 'Storm wyvern', 'Eclipse wyvern']
    colours = [tcod.lighter_yellow, tcod.turquoise, tcod.purple, tcod.dark_crimson, tcod.yellow]

    def Ray():
        formation = Formation(origin=(2,2), formation=[['x','x','x','x','x'],
                                                       ['x','x','x','.','x'],
                                                       ['x','x','x','x','x'],
                                                       ['x','.','x','x','x'],
                                                       ['x','x','x','x','x']])
        return skill_factory.Skill()\
                            .with_target_mode(NoFriendlyFire(ExcludeItems(TargetFormation(formation, max_range=7))))\
                            .damage_targets("{} scorches {} with rays from its jaw! ({} HP)")\
                            .with_damage(damage.MonsterSpellDamage(40, 'fire'))

    def generator(tier=settings.monster_tier, level=1):
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
                'AI': ai.AI()\
                .add_skill('Ray', Wyvern.Ray(), delay=1)\
                .with_state('IDLE', ai.AIState()\
                            .when_player_within_distance(9, lambda e, ai, ev_d : ai.change_state('AGGRO'))\
                            .on_turn_otherwise(lambda e, ai, ev_d : ai.step_randomly(e)))\
                .with_state('AGGRO', ai.AIState()\
                            .when_player_within_distance(5, lambda e, ai, ev_d : ai.step_away_from_player(e))\
                            .when_player_within_distance(7, lambda e, ai, ev_d : ai.use_skill(e, 'Ray'))\
                            .on_turn_otherwise(lambda e, ai, ev_d : ai.step_towards_player(e)))\
            }, ttype='Wyvern_'+str(tier))
        return gen

class Beholder:
    base_stats = {
        'max_hp': round(70 * balance.monster_stat_scale['max_hp']),
        'cur_hp': round(70 * balance.monster_stat_scale['max_hp']),
        'max_sp': round(40 * balance.monster_stat_scale['max_sp']),
        'cur_sp': round(40 * balance.monster_stat_scale['max_sp']),
        'atk': round(18 * balance.monster_stat_scale['atk']),
        'dfn': round(14 * balance.monster_stat_scale['dfn']),
        'itl': round(37 * balance.monster_stat_scale['itl']),
        'res': round(8 * balance.monster_stat_scale['res']),
        'spd': round(8 * balance.monster_stat_scale['spd']),
        'hit': 12 * balance.monster_stat_scale['hit']
    }

    names = ['Lesser beholder', 'Beholder', 'Greater beholder', 'Beholder lord', 'Omniscient beholder']
    colours = [tcod.lighter_yellow, tcod.turquoise, tcod.purple, tcod.dark_crimson, tcod.yellow]

    def Ray():
        formation = Formation(origin=(0,2), formation=[['.','.','.','x','x','x','x','x'],
                                                       ['.','.','x','x','x','x','x','.'],
                                                       ['.','x','x','x','x','x','.','.'],
                                                       ['.','.','x','x','x','x','x','.'],
                                                       ['.','.','.','x','x','x','x','x']])
        return skill_factory.Skill()\
                            .with_target_mode(NoFriendlyFire(ExcludeItems(TargetFormation(formation, directional=True))))\
                            .damage_targets("{} scorches {} its eye ray! ({} HP)")\
                            .with_damage(damage.MonsterSpellDamage(45, 'fire'))


    def generator(tier=settings.monster_tier, level=1):
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
                'AI': ai.AI()\
                .add_skill('Ray', Beholder.Ray(), delay=2)\
                .with_state('IDLE', ai.AIState()\
                            .when_player_within_distance(9, lambda e, ai, ev_d : ai.change_state('AGGRO'))\
                            .on_turn_otherwise(lambda e, ai, ev_d : ai.step_randomly(e)))\
                .with_state('AGGRO', ai.AIState()\
                            .when_player_within_distance(4, lambda e, ai, ev_d : ai.step_away_from_player(e))\
                            .when_player_within_distance(5, lambda e, ai, ev_d : ai.use_skill(e, 'Ray'))\
                            .on_turn_otherwise(lambda e, ai, ev_d : ai.step_towards_player(e)))\
            }, ttype='Beholder_'+str(tier))
        return gen

class Giant:
    base_stats = {
        'max_hp': round(170 * balance.monster_stat_scale['max_hp']),
        'cur_hp': round(170 * balance.monster_stat_scale['max_hp']),
        'max_sp': round(40 * balance.monster_stat_scale['max_sp']),
        'cur_sp': round(40 * balance.monster_stat_scale['max_sp']),
        'atk': round(37 * balance.monster_stat_scale['atk']),
        'dfn': round(14 * balance.monster_stat_scale['dfn']),
        'itl': round(18 * balance.monster_stat_scale['itl']),
        'res': round(8 * balance.monster_stat_scale['res']),
        'spd': round(8 * balance.monster_stat_scale['spd']),
        'hit': 12 * balance.monster_stat_scale['hit']
    }

    names = ['Hill giant', 'Moss giant', 'Stone giant', 'Iron giant', 'Fire giant']
    colours = [tcod.lighter_orange, tcod.dark_green, tcod.lighter_gray, tcod.silver, tcod.red]

    def Smash():
        formation = Formation(origin=(1,3), formation=[['x','.','x'],
                                                       ['x','x','x'],
                                                       ['x','x','x'],
                                                       ['.','.','.']])
        return skill_factory.Skill()\
                            .with_target_mode(NoFriendlyFire(ExcludeItems(TargetFormation(formation, directional=True))))\
                            .damage_targets("{} smashes {}! ({} HP)")\
                            .with_damage(damage.MonsterAttackDamage(60, 'phys'))

    def generator(tier=settings.monster_tier, level=1):
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
                'AI': ai.AI()\
                .add_skill('Smash', Giant.Smash(), delay=1)\
                .with_state('IDLE', ai.AIState()\
                            .when_player_within_distance(9, lambda e, ai, ev_d : ai.change_state('AGGRO'))\
                            .on_turn_otherwise(lambda e, ai, ev_d : ai.step_randomly(e)))\
                .with_state('AGGRO', ai.AIState()\
                            .when_player_within_distance(2, lambda e, ai, ev_d : ai.use_skill(e, 'Smash'))\
                            .on_turn_otherwise(lambda e, ai, ev_d : ai.step_towards_player(e)))\
            }, ttype='Giant_'+str(tier))
        return gen

class Gremlin:
    base_stats = {
        'max_hp': round(60 * balance.monster_stat_scale['max_hp']),
        'cur_hp': round(60 * balance.monster_stat_scale['max_hp']),
        'max_sp': round(40 * balance.monster_stat_scale['max_sp']),
        'cur_sp': round(40 * balance.monster_stat_scale['max_sp']),
        'atk': round(9 * balance.monster_stat_scale['atk']),
        'dfn': round(6 * balance.monster_stat_scale['dfn']),
        'itl': round(9 * balance.monster_stat_scale['itl']),
        'res': round(6 * balance.monster_stat_scale['res']),
        'spd': round(6 * balance.monster_stat_scale['spd']),
        'hit': 6 * balance.monster_stat_scale['hit']
    }

    names = ['Snickering gremlin', 'Giggling gremlin', 'Laughing gremlin', 'Shrieking gremlin', 'Howling gremlin']
    colours = [tcod.darker_purple, tcod.darker_green, tcod.darker_yellow, tcod.darker_red, tcod.darker_blue]

    def GuardBreak():
        formation = Formation(origin=(1,1), formation=[['x','.','x'],
                                                       ['.','x','.'],
                                                       ['x','.','x']])

        return skill_factory.Skill()\
                            .with_target_mode(NoFriendlyFire(ExcludeItems(TargetFormation(formation, max_range=7))))\
                            .damage_targets("{} points and laughs {}'s pathetic DFN!")\
                            .with_damage(damage.MonsterSpellDamage(0))\
                            .change_damage(lambda d, s, t, i : damage.WithStatusEffect('GUARD_BREAK', 1, 25, d))

    def MindBreak():
        formation = Formation(origin=(1,1), formation=[['.','x','.'],
                                                       ['x','x','x'],
                                                       ['.','x','.']])

        return skill_factory.Skill()\
                            .with_target_mode(NoFriendlyFire(ExcludeItems(TargetFormation(formation, max_range=7))))\
                            .damage_targets("{} keels over laughing at {}'s pathetic RES!")\
                            .with_damage(damage.MonsterSpellDamage(0))\
                            .change_damage(lambda d, s, t, i : damage.WithStatusEffect('MIND_BREAK', 1, 25, d))

    def generator(tier=settings.monster_tier, level=1):
        actual_stats = util.copy_dict(Gremlin.base_stats)
        actual_stats['level'] = level
        for stat in Stats.primary_stats | Stats.cur_stats - set(['cur_exp']):
            actual_stats[stat] = (Gremlin.base_stats[stat] + Gremlin.base_stats[stat] * (tier - 1) * TIER_PC_STAT_INC)
            actual_stats[stat] += math.floor(LEVEL_PC_STAT_INC * actual_stats[stat]) * (level-1)
        def gen(position):
            x, y = position
            return Entity(str(uuid.uuid4()), components={
                'Stats': Stats(actual_stats),
                'Position': Position(x, y),
                'Render': Render(character='g', colour=Gremlin.colours[tier-1]),
                'Combat': Combat(),
                'NPC': NPC(Gremlin.names[tier-1]),
                'AI': ai.AI()\
                .add_skill('GuardBreak', Gremlin.GuardBreak(), delay=1)\
                .add_skill('MindBreak', Gremlin.MindBreak(), delay=1)\
                .with_state('IDLE', ai.AIState()\
                            .when_player_within_distance(7, lambda e, ai, ev_d : ai.change_state('USE_SPELLS'))\
                            .on_turn_otherwise(lambda e, ai, ev_d : ai.step_randomly(e)))\
                .with_state('USE_SPELLS', ai.AIState()\
                            .when_player_beyond_distance(7, lambda e, ai, ev_d : ai.change_state('GET_CLOSER'))\
                            .on_turn_randomly(0.5, lambda e, ai, ev_d : ai.use_skill(e, 'GuardBreak'))\
                            .on_turn_otherwise(lambda e, ai, ev_d : ai.use_skill(e, 'MindBreak')))\
                .with_state('GET_CLOSER', ai.AIState()\
                            .when_player_within_distance(7, lambda e, ai, ev_d : ai.change_state('USE_SPELLS'))\
                            .on_turn_otherwise(lambda e, ai, ev_d : ai.step_towards_player(e)))\
            }, ttype='Gremlin_'+str(tier))
        return gen

class Inferno:
    base_stats = {
        'max_hp': round(80 * balance.monster_stat_scale['max_hp']),
        'cur_hp': round(80 * balance.monster_stat_scale['max_hp']),
        'max_sp': round(40 * balance.monster_stat_scale['max_sp']),
        'cur_sp': round(40 * balance.monster_stat_scale['max_sp']),
        'atk': round(30 * balance.monster_stat_scale['atk']),
        'dfn': round(10 * balance.monster_stat_scale['dfn']),
        'itl': round(35 * balance.monster_stat_scale['itl']),
        'res': round(10 * balance.monster_stat_scale['res']),
        'spd': round(6 * balance.monster_stat_scale['spd']),
        'hit': round(6 * balance.monster_stat_scale['hit']),
        'fire_res': 100,
    }

    names = ['Flame', 'Blaze', 'Firestorm', 'Inferno', 'Hellfire']
    colours = [tcod.dark_red, tcod.orange, tcod.dark_yellow, tcod.darker_red, tcod.crimson]

    def Explosion():
        formation = Formation(origin=(2,2), formation=util.rectangle(5,5))

        return skill_factory.Skill()\
                            .with_target_mode(NoFriendlyFire(ExcludeItems(TargetFormation(formation, max_range=7))))\
                            .damage_targets("{} causes a fiery explosion on top of {}! ({} HP)")\
                            .with_damage(damage.MonsterSpellDamage(90, 'fire'))\

    def Firestorm():
        return skill_factory.Skill()\
                            .with_target_mode(NoFriendlyFire(ExcludeItems(TargetRandomPositions(7, passable_only=True, within_distance=2))))\
                            .damage_targets("{} singes {} with fire! ({} HP)")\
                            .with_damage(damage.MonsterSpellDamage(60, 'fire'))\

    def generator(tier=settings.monster_tier, level=1):
        actual_stats = util.copy_dict(Inferno.base_stats)
        actual_stats['level'] = level
        for stat in Stats.primary_stats | Stats.cur_stats - set(['cur_exp']):
            actual_stats[stat] = (Inferno.base_stats[stat] + Inferno.base_stats[stat] * (tier - 1) * TIER_PC_STAT_INC)
            actual_stats[stat] += math.floor(LEVEL_PC_STAT_INC * actual_stats[stat]) * (level-1)
        def gen(position):
            x, y = position
            return Entity(str(uuid.uuid4()), components={
                'Stats': Stats(actual_stats),
                'Position': Position(x, y),
                'Render': Render(character='I', colour=Inferno.colours[tier-1]),
                'Combat': Combat(),
                'NPC': NPC(Inferno.names[tier-1]),
                'AI': ai.AI()\
                .add_skill('Firestorm', Inferno.Firestorm(), delay=1, is_passive=True)\
                .add_skill('Explosion', Inferno.Explosion(), delay=1)\
                .with_state('IDLE', ai.AIState()\
                            .on_turn_otherwise(lambda e, ai, ev_d : ai.use_skill(e, 'Firestorm'), False)\
                            .when_player_within_distance(7, lambda e, ai, ev_d : ai.change_state('USE_SPELLS'))\
                            .on_turn_otherwise(lambda e, ai, ev_d : ai.step_randomly(e)))\
                .with_state('USE_SPELLS', ai.AIState()\
                            .on_turn_otherwise(lambda e, ai, ev_d : ai.use_skill(e, 'Firestorm'), False)\
                            .when_player_beyond_distance(6, lambda e, ai, ev_d : ai.step_towards_player(e))\
                            .on_turn_otherwise(lambda e, ai, ev_d : ai.use_skill(e, 'Explosion')))\
            }, ttype='Inferno_'+str(tier))
        return gen

class Bee:
    base_stats = {
        'max_hp': round(20 * balance.monster_stat_scale['max_hp']),
        'cur_hp': round(20 * balance.monster_stat_scale['max_hp']),
        'max_sp': round(40 * balance.monster_stat_scale['max_sp']),
        'cur_sp': round(40 * balance.monster_stat_scale['max_sp']),
        'atk': round(20 * balance.monster_stat_scale['atk']),
        'dfn': round(8 * balance.monster_stat_scale['dfn']),
        'itl': round(20 * balance.monster_stat_scale['itl']),
        'res': round(8 * balance.monster_stat_scale['res']),
        'spd': round(6 * balance.monster_stat_scale['spd']),
        'hit': round(6 * balance.monster_stat_scale['hit']),
    }

    names = ['Bee', 'Wasp', 'Hornet', 'Spiderhawk', 'Apisterax']
    colours = [tcod.light_yellow, tcod.orange, tcod.dark_yellow, tcod.darker_red, tcod.crimson]

    def Sting():
        formation = Formation(origin=(0,0), formation=['.','x','x'])

        return skill_factory.Skill()\
                            .with_target_mode(NoFriendlyFire(ExcludeItems(TargetFormation(formation, directional=True))))\
                            .damage_targets("{} stings {}! ({} HP)")\
                            .with_damage(damage.MonsterSpellDamage(60, 'phys'))\

    def generator(tier=settings.monster_tier, level=1):
        actual_stats = util.copy_dict(Bee.base_stats)
        actual_stats['level'] = level
        for stat in Stats.primary_stats | Stats.cur_stats - set(['cur_exp']):
            actual_stats[stat] = (Bee.base_stats[stat] + Bee.base_stats[stat] * (tier - 1) * TIER_PC_STAT_INC)
            actual_stats[stat] += math.floor(LEVEL_PC_STAT_INC * actual_stats[stat]) * (level-1)
        def gen(position):
            x, y = position
            return Entity(str(uuid.uuid4()), components={
                'Stats': Stats(actual_stats),
                'Position': Position(x, y),
                'Render': Render(character='b', colour=Bee.colours[tier-1]),
                'Combat': Combat(),
                'NPC': NPC(Bee.names[tier-1]),
                'AI': ai.AI()\
                .add_skill('Sting', Bee.Sting(), delay=1)\
                .with_state('IDLE', ai.AIState()\
                            .when_player_within_distance(14, lambda e, ai, ev_d : ai.change_state('USE_SPELLS'))\
                            .on_turn_otherwise(lambda e, ai, ev_d : ai.step_randomly(e)))\
                .with_state('USE_SPELLS', ai.AIState()\
                            .when_player_within_distance(1, lambda e, ai, ev_d : ai.use_skill(e, 'Sting'), False)\
                            .on_turn_otherwise(lambda e, ai, ev_d : ai.step_towards_player(e)))\
            }, ttype='Bee_'+str(tier))
        return gen

class Beehive:
    base_stats = {
        'max_hp': round(150 * balance.monster_stat_scale['max_hp']),
        'cur_hp': round(150 * balance.monster_stat_scale['max_hp']),
        'max_sp': round(40 * balance.monster_stat_scale['max_sp']),
        'cur_sp': round(40 * balance.monster_stat_scale['max_sp']),
        'atk': round(1 * balance.monster_stat_scale['atk']),
        'dfn': round(12 * balance.monster_stat_scale['dfn']),
        'itl': round(1 * balance.monster_stat_scale['itl']),
        'res': round(12 * balance.monster_stat_scale['res']),
        'spd': round(6 * balance.monster_stat_scale['spd']),
        'hit': round(6 * balance.monster_stat_scale['hit']),
    }

    names = ['Beehive', 'Wasp hive', 'Hornet hive', 'Spiderhawk hive', 'Apisterax hive']
    colours = [tcod.light_yellow, tcod.orange, tcod.dark_yellow, tcod.darker_red, tcod.crimson]

    def SummonBees():
        return skill_factory.Skill()\
                            .with_target_mode(NoFriendlyFire(ExcludeItems(TargetRandomPositions(1, passable_only=True, within_distance=2))))\
                            .summon_monsters([Bee])\

    def generator(tier=settings.monster_tier, level=1):
        actual_stats = util.copy_dict(Beehive.base_stats)
        actual_stats['level'] = level
        for stat in Stats.primary_stats | Stats.cur_stats - set(['cur_exp']):
            actual_stats[stat] = (Beehive.base_stats[stat] + Beehive.base_stats[stat] * (tier - 1) * TIER_PC_STAT_INC)
            actual_stats[stat] += math.floor(LEVEL_PC_STAT_INC * actual_stats[stat]) * (level-1)
        def gen(position):
            x, y = position
            return Entity(str(uuid.uuid4()), components={
                'Stats': Stats(actual_stats),
                'Position': Position(x, y),
                'Render': Render(character='B', colour=Beehive.colours[tier-1]),
                'Combat': Combat(),
                'NPC': NPC(Beehive.names[tier-1]),
                'AI': ai.AI()\
                .add_skill('SummonBees', Beehive.SummonBees(), delay=0, is_passive=True)\
                .with_state('IDLE', ai.AIState()\
                            .every_n_turns(10, lambda e, ai, ev_d : ai.use_skill(e, 'SummonBees'), False)\
                            .on_turn_otherwise(lambda e, ai, ev_d : False))\
            }, ttype='Beehive_'+str(tier))
        return gen

class Lavamoeba:
    base_stats = {
        'max_hp': round(50 * balance.monster_stat_scale['max_hp']),
        'cur_hp': round(50 * balance.monster_stat_scale['max_hp']),
        'max_sp': round(40 * balance.monster_stat_scale['max_sp']),
        'cur_sp': round(40 * balance.monster_stat_scale['max_sp']),
        'atk': round(20 * balance.monster_stat_scale['atk']),
        'dfn': round(10 * balance.monster_stat_scale['dfn']),
        'itl': round(25 * balance.monster_stat_scale['itl']),
        'res': round(10 * balance.monster_stat_scale['res']),
        'spd': round(6 * balance.monster_stat_scale['spd']),
        'hit': round(6 * balance.monster_stat_scale['hit']),
        'fire_res': 50,
    }

    names = ['Lavamoeba1', 'Lavamoeba2', 'Lavamoeba3', 'Lavamoeba4', 'Lavamoeba5']
    colours = [tcod.dark_red, tcod.orange, tcod.dark_yellow, tcod.darker_red, tcod.crimson]

    def Scorch():
        formation = Formation(origin=(1,1), formation=util.rectangle(3,3))

        return skill_factory.Skill()\
                            .with_target_mode(NoFriendlyFire(ExcludeItems(TargetFormation(formation, max_range=0))))\
                            .damage_targets("{} hits {} with its fiery body! ({} HP)")\
                            .with_damage(damage.MonsterAttackDamage(45, 'fire'))\

    def Spread():
        return skill_factory.Skill()\
                            .with_target_mode(NoFriendlyFire(ExcludeItems(TargetRandomPositions(1, passable_only=True, within_distance=1))))\
                            .summon_monsters([Lavamoeba])\

    def generator(tier=settings.monster_tier, level=1):
        actual_stats = util.copy_dict(Lavamoeba.base_stats)
        actual_stats['level'] = level
        for stat in Stats.primary_stats | Stats.cur_stats - set(['cur_exp']):
            actual_stats[stat] = (Lavamoeba.base_stats[stat] + Lavamoeba.base_stats[stat] * (tier - 1) * TIER_PC_STAT_INC)
            actual_stats[stat] += math.floor(LEVEL_PC_STAT_INC * actual_stats[stat]) * (level-1)
        def gen(position):
            x, y = position
            return Entity(str(uuid.uuid4()), components={
                'Stats': Stats(actual_stats),
                'Position': Position(x, y),
                'Render': Render(character='s', colour=Lavamoeba.colours[tier-1]),
                'Combat': Combat(),
                'NPC': NPC(Lavamoeba.names[tier-1]),
                'AI': ai.AI()\
                .add_skill('Spread', Lavamoeba.Spread(), delay=0, is_passive=True)\
                .add_skill('Scorch', Lavamoeba.Scorch(), delay=1)\
                .with_state('IDLE', ai.AIState()\
                            .every_n_turns(10, lambda e, ai, ev_d : ai.use_skill(e, 'Spread'), False)\
                            .on_turn_otherwise(lambda e, ai, ev_d : ai.use_skill(e, 'Scorch')))\
            }, ttype='Lavamoeba_'+str(tier))
        return gen

class HostileThunderTotem:
    base_stats = {
        'max_hp': round(10 * balance.monster_stat_scale['max_hp']),
        'cur_hp': round(10 * balance.monster_stat_scale['max_hp']),
        'max_sp': round(10 * balance.monster_stat_scale['max_sp']),
        'cur_sp': round(10 * balance.monster_stat_scale['max_sp']),
        'atk': round(30 * balance.monster_stat_scale['atk']),
        'dfn': round(10 * balance.monster_stat_scale['dfn']),
        'itl': round(30 * balance.monster_stat_scale['itl']),
        'res': round(10 * balance.monster_stat_scale['res']),
        'spd': round(12 * balance.monster_stat_scale['spd']),
        'hit': round(12 * balance.monster_stat_scale['hit']),
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
                            .with_damage(damage.MonsterAttackDamage(60, 'lght'))

    def generator(tier=settings.monster_tier, level=1):
        actual_stats = util.copy_dict(HostileThunderTotem.base_stats)
        actual_stats['level'] = level
        for stat in Stats.primary_stats | Stats.cur_stats - set(['cur_exp']):
            actual_stats[stat] = (HostileThunderTotem.base_stats[stat] + HostileThunderTotem.base_stats[stat] * (tier - 1) * TIER_PC_STAT_INC)
            actual_stats[stat] += math.floor(LEVEL_PC_STAT_INC * actual_stats[stat]) * (level-1)
        def gen(position):
            x, y = position
            return Entity(str(uuid.uuid4()), components={
                'Stats': Stats(actual_stats),
                'Position': Position(x, y),
                'Render': Render(character='t', colour=HostileThunderTotem.colours[tier-1]),
                'Combat': Combat(),
                'NPC': NPC(HostileThunderTotem.names[tier-1]),
                'AI': ai.AI()\
                .add_skill('Shockwave', HostileThunderTotem.Shockwave(), delay=1)\
                .with_state('IDLE', ai.AIState()\
                            .on_turn_otherwise(lambda e, ai, ev_d : ai.find_target(e), False)\
                            .when_target_within_distance(1.5, lambda e, ai, ev_d : ai.use_skill(e, 'Shockwave')))\
            }, ttype='HostileThunderTotem_'+str(tier))
        return gen

class Witchdoctor:
    base_stats = {
        'max_hp': round(50 * balance.monster_stat_scale['max_hp']),
        'cur_hp': round(50 * balance.monster_stat_scale['max_hp']),
        'max_sp': round(40 * balance.monster_stat_scale['max_sp']),
        'cur_sp': round(40 * balance.monster_stat_scale['max_sp']),
        'atk': round(20 * balance.monster_stat_scale['atk']),
        'dfn': round(10 * balance.monster_stat_scale['dfn']),
        'itl': round(25 * balance.monster_stat_scale['itl']),
        'res': round(10 * balance.monster_stat_scale['res']),
        'spd': round(6 * balance.monster_stat_scale['spd']),
        'hit': round(6 * balance.monster_stat_scale['hit']),
        'fire_res': 50,
    }

    names = ['Witchdoctor1', 'Witchdoctor2', 'Witchdoctor3', 'Witchdoctor4', 'Witchdoctor5']
    colours = [tcod.dark_red, tcod.orange, tcod.dark_yellow, tcod.darker_red, tcod.crimson]

    def Hex():
        formation = Formation(origin=(1,1), formation=util.circle(1))

        return skill_factory.Skill()\
                            .with_target_mode(NoFriendlyFire(ExcludeItems(TargetFormation(formation, directional=True))))\
                            .damage_targets("{} is paralyzed and poisoned by {}'s hex!")\
                            .with_damage(damage.MonsterSpellDamage(0))\
                            .change_damage(lambda d, s, t, i : damage.WithStatusEffect('PARALYZE', 1, 2, d))\
                            .change_damage(lambda d, s, t, i : damage.WithStatusEffect('POISON', 1, 2, d))

    def ThunderTotem():
        return skill_factory.Skill()\
                            .with_target_mode(NoFriendlyFire(ExcludeItems(TargetRandomPositions(1, passable_only=True, within_distance=1))))\
                            .summon_monsters([HostileThunderTotem])\

    def generator(tier=settings.monster_tier, level=1):
        actual_stats = util.copy_dict(Witchdoctor.base_stats)
        actual_stats['level'] = level
        for stat in Stats.primary_stats | Stats.cur_stats - set(['cur_exp']):
            actual_stats[stat] = (Witchdoctor.base_stats[stat] + Witchdoctor.base_stats[stat] * (tier - 1) * TIER_PC_STAT_INC)
            actual_stats[stat] += math.floor(LEVEL_PC_STAT_INC * actual_stats[stat]) * (level-1)
        def gen(position):
            x, y = position
            return Entity(str(uuid.uuid4()), components={
                'Stats': Stats(actual_stats),
                'Position': Position(x, y),
                'Render': Render(character='w', colour=Witchdoctor.colours[tier-1]),
                'Combat': Combat(),
                'NPC': NPC(Witchdoctor.names[tier-1]),
                'AI': ai.AI()\
                .add_skill('Hex', Witchdoctor.Hex(), delay=1, is_passive=True)\
                .add_skill('ThunderTotem', Witchdoctor.ThunderTotem(), delay=0)\
                .with_state('IDLE', ai.AIState()\
                            .when_player_within_distance(7, lambda e, ai, ev_d : ai.change_state('AGGRO'))\
                            .on_turn_otherwise(lambda e, ai, ev_d : ai.step_randomly(e)))\
                .with_state('AGGRO', ai.AIState()\
                            .every_n_turns(1, lambda e, ai, ev_d : ai.use_skill(e, 'Hex'), False)\
                            .when_player_beyond_distance(3, lambda e, ai, ev_d : ai.step_towards_player(e))\
                            .every_n_turns(2, lambda e, ai, ev_d : ai.use_skill(e, 'ThunderTotem'))\
                            .on_turn_otherwise(lambda e, ai, ev_d : False))\
            }, ttype='Witchdoctor_'+str(tier))
        return gen

# Bosses

class BossTheSneak:
    base_stats = {
        'max_hp': round(200 * balance.monster_stat_scale['max_hp']),
        'cur_hp': round(200 * balance.monster_stat_scale['max_hp']),
        'max_sp': round(10 * balance.monster_stat_scale['max_sp']),
        'cur_sp': round(10 * balance.monster_stat_scale['max_sp']),
        'atk': round(30 * balance.monster_stat_scale['atk']),
        'dfn': round(15 * balance.monster_stat_scale['dfn']),
        'itl': round(45 * balance.monster_stat_scale['itl']),
        'res': round(15 * balance.monster_stat_scale['res']),
        'spd': round(12 * balance.monster_stat_scale['spd']),
        'hit': 12 * balance.monster_stat_scale['hit']
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
                            .with_damage(damage.MonsterSpellDamage(65, 'lght'))

    def BigFire():
        formation = Formation(origin=(2,2), formation=[['x','x','x','x','x'],
                                                       ['x','x','x','x','x'],
                                                       ['x','x','x','x','x'],
                                                       ['x','x','x','x','x'],
                                                       ['x','x','x','x','x']])
        return skill_factory.Skill()\
                            .with_target_mode(NoFriendlyFire(ExcludeItems(TargetFormation(formation))))\
                            .damage_targets("{} emits a blast of fire at {}! ({} HP)")\
                            .with_damage(damage.MonsterSpellDamage(70, 'fire'))

    def Escape():
        return skill_factory.Skill()\
                            .with_target_mode(TargetUser())\
                            .teleport_targets_randomly()\
                            .print_message("Jerome laughs as he disappears into thin air!")

    def generator(tier=settings.monster_tier, level=1):
        print("The sneak tier:", tier)
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
            }, ttype='BossTheSneak_'+str(tier))
        return gen

class BossUltimateBeholder:
    base_stats = {
        'max_hp': round(200 * balance.monster_stat_scale['max_hp']),
        'cur_hp': round(200 * balance.monster_stat_scale['max_hp']),
        'max_sp': round(10 * balance.monster_stat_scale['max_sp']),
        'cur_sp': round(10 * balance.monster_stat_scale['max_sp']),
        'atk': round(30 * balance.monster_stat_scale['atk']),
        'dfn': round(15 * balance.monster_stat_scale['dfn']),
        'itl': round(50 * balance.monster_stat_scale['itl']),
        'res': round(15 * balance.monster_stat_scale['res']),
        'spd': round(12 * balance.monster_stat_scale['spd']),
        'hit': 12 * balance.monster_stat_scale['hit']
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
                            .with_damage(damage.MonsterSpellDamage(70, 'fire'))

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

    def generator(tier=settings.monster_tier, level=1):
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
                            .on_turn_randomly(0.1, lambda e, ai, ev_d : ai.use_skill(e, 'Escape'))\
                            .on_turn_randomly(0.2, lambda e, ai, ev_d : ai.use_skill(e, 'TeleportAdds'))\
                            .when_player_within_distance(25, lambda e, ai, ev_d : ai.use_skill(e, 'Laser'))\
                            .on_turn_otherwise(lambda e, ai, ev_d : ai.step_towards_player(e)))\
            }, ttype='BossUltimateBeholder_'+str(tier))
        return gen

class BossTheTower:
    base_stats = {
        'max_hp': round(220 * balance.monster_stat_scale['max_hp']),
        'cur_hp': round(220 * balance.monster_stat_scale['max_hp']),
        'max_sp': round(10 * balance.monster_stat_scale['max_sp']),
        'cur_sp': round(10 * balance.monster_stat_scale['max_sp']),
        'atk': round(30 * balance.monster_stat_scale['atk']),
        'dfn': round(17 * balance.monster_stat_scale['dfn']),
        'itl': round(50 * balance.monster_stat_scale['itl']),
        'res': round(17 * balance.monster_stat_scale['res']),
        'spd': round(12 * balance.monster_stat_scale['spd']),
        'hit': round(12 * balance.monster_stat_scale['hit']),
    }

    names = ['XVI - The Tower'] * 5
    colours = [tcod.green, tcod.blue, tcod.red, tcod.pink, tcod.cyan]

    def Laser():
        formation = Formation(origin=(2,0), formation=[['x','x','.','x','x'],
                                                       ['x','x','x','x','x'],
                                                       ['x','x','x','x','x'],
                                                       ['x','x','x','x','x']] + [['x','x','x','x','x']] * 30)
        return skill_factory.Skill()\
                            .with_target_mode(NoFriendlyFire(ExcludeItems(TargetFormation(formation, directional=True))))\
                            .damage_targets("{}'s blazing ray scorches {}! ({} HP)")\
                            .with_damage(damage.MonsterSpellDamage(85, 'fire'))

    def HorLaser():
        formation = Formation(origin=(50,1), formation=[['x'] * 100,
                                                       ['x'] * 100,
                                                       ['x'] * 100])
        return skill_factory.Skill()\
                            .with_target_mode(NoFriendlyFire(ExcludeItems(TargetFormation(formation, positioned_randomly=True))))\
                            .damage_targets("{}'s blazing ray scorches {}! ({} HP)")\
                            .with_damage(damage.MonsterSpellDamage(85, 'fire'))

    def TeleportPlayer():
        return skill_factory.Skill()\
                            .with_target_mode(WithComponents(['PlayerLogic'], TargetEveryone()))\
                            .teleport_targets_randomly()\
                            .print_message("You are lifted into the air and thrown by psychic power!")

    def Smite1():
        formation = Formation(origin=(2,2), formation=[['.','.','x','.','.'],
                                                       ['.','x','x','x','.'],
                                                       ['x','x','x','x','x'],
                                                       ['.','x','x','x','.'],
                                                       ['.','.','x','.','.']])
        return skill_factory.Skill()\
                            .with_target_mode(NoFriendlyFire(ExcludeItems(TargetFormation(formation, positioned_randomly=True))))\
                            .damage_targets("{} smites {}! ({} HP)")\
                            .with_damage(damage.MonsterSpellDamage(85, 'fire'))

    def Smite2():
        formation = Formation(origin=(2,3), formation=[['x','x','x','.','.'],
                                                       ['x','x','x','.','.'],
                                                       ['x','x','x','.','.'],
                                                       ['.','.','.','.','.'],
                                                       ['.','.','x','x','x'],
                                                       ['.','.','x','x','x'],
                                                       ['.','.','x','x','x']])
        return skill_factory.Skill()\
                            .with_target_mode(NoFriendlyFire(ExcludeItems(TargetFormation(formation, positioned_randomly=True))))\
                            .damage_targets("{} smites {}! ({} HP)")\
                            .with_damage(damage.MonsterSpellDamage(85, 'fire'))

    def Smite3():
        formation = Formation(origin=(2,3), formation=[['.','x','x','x','.'],
                                                       ['x','x','x','x','x'],
                                                       ['x','x','x','x','x'],
                                                       ['x','x','x','x','x'],
                                                       ['.','x','x','x','.']])
        return skill_factory.Skill()\
                            .with_target_mode(NoFriendlyFire(ExcludeItems(TargetFormation(formation))))\
                            .damage_targets("{} smites {}! ({} HP)")\
                            .with_damage(damage.MonsterSpellDamage(90, 'fire'))

    def Clock():
        return skill_factory.Skill()\
                            .print_message("An ominous bell rings...", tcod.dark_crimson)

    def StartCountdown():
        return skill_factory.Skill()\
                            .print_message(" -- YOU HAVE 120 TURNS UNTIL MIDNIGHT -- ", tcod.dark_crimson)

    def generator(tier=settings.monster_tier, level=1):
        actual_stats = util.copy_dict(BossTheTower.base_stats)
        actual_stats['level'] = level
        for stat in Stats.primary_stats | Stats.cur_stats - set(['cur_exp']):
            actual_stats[stat] = (BossTheTower.base_stats[stat] + BossTheTower.base_stats[stat] * (tier - 1) * TIER_PC_STAT_INC)
            actual_stats[stat] += math.floor(LEVEL_PC_STAT_INC * actual_stats[stat]) * (level-1)
        def gen(position):
            x, y = position
            return Entity(str(uuid.uuid4()), components={
                'Stats': Stats(actual_stats),
                'Position': Position(x, y),
                'Render': Render(character='T', colour=BossTheTower.colours[tier-1]),
                'Combat': Combat(),
                'NPC': NPC(BossTheTower.names[tier-1]),
                'AI': ai.AI(initial_state='COUNTDOWN_PHASE')\
                .add_skill('StartCountdown', BossTheTower.StartCountdown(), 0)\
                .add_skill('Clock', BossTheTower.Clock(), 0)\
                .add_skill('Laser', BossTheTower.Laser(), 2)\
                .add_skill('HorLaser', BossTheTower.HorLaser(), 1)\
                .add_skill('TeleportPlayer', BossTheTower.TeleportPlayer(), 3)\
                .add_skill('Smite1', BossTheTower.Smite1(), 1)\
                .add_skill('Smite2', BossTheTower.Smite2(), 1)\
                .add_skill('Smite3', BossTheTower.Smite3(), 1)\
                .with_state('COUNTDOWN_PHASE', ai.AIState()\
                            .after_n_turns(120, lambda e, ai, ev_d : ai.change_state('MIDNIGHT_PHASE'))\
                            .after_n_turns(1, lambda e, ai, ev_d : ai.use_skill(e, 'StartCountdown'), should_stop=False)\
                            .every_n_turns(10, lambda e, ai, ev_d : ai.use_skill(e, 'Clock'), should_stop=False)\
                            .when_player_within_distance(4, lambda e, ai, ev_d : ai.use_skill(e, 'TeleportPlayer'))\
                            .every_n_turns(5, lambda e, ai, ev_d : ai.use_skill(e, 'HorLaser'))\
                            .every_n_turns(4, lambda e, ai, ev_d : ai.use_skill(e, 'Smite3'))\
                            .every_n_turns(3, lambda e, ai, ev_d : ai.use_skill(e, 'Smite2'))\
                            .every_n_turns(2, lambda e, ai, ev_d : ai.use_skill(e, 'Smite1'))\
                            .on_turn_otherwise(lambda e, ai, ev_d : ai.use_skill(e, 'HorLaser')))\
                .with_state('MIDNIGHT_PHASE', ai.AIState()\
                            .after_n_turns(1, lambda e, ai, ev_d : ai.use_skill('Deadline'))\
                            .when_player_within_distance(4, lambda e, ai, ev_d : ai.use_skill(e, 'TeleportPlayer'))\
                            .on_turn_otherwise(lambda e, ai, ev_d : ai.use_skill(e, 'Smite3')))\
            }, ttype='BossTheTower_'+str(tier))
        return gen

class BossTheTowerMinion:
    base_stats = {
        'max_hp': round(60 * balance.monster_stat_scale['max_hp']),
        'cur_hp': round(60 * balance.monster_stat_scale['max_hp']),
        'max_sp': round(10 * balance.monster_stat_scale['max_sp']),
        'cur_sp': round(10 * balance.monster_stat_scale['max_sp']),
        'atk': round(30 * balance.monster_stat_scale['atk']),
        'dfn': round(20 * balance.monster_stat_scale['dfn']),
        'itl': round(45 * balance.monster_stat_scale['itl']),
        'res': round(20 * balance.monster_stat_scale['res']),
        'spd': round(12 * balance.monster_stat_scale['spd']),
        'hit': round(12 * balance.monster_stat_scale['hit']),
    }

    names = ['Grim Watcher'] * 5
    colours = [tcod.darker_green, tcod.darker_blue, tcod.darker_red, tcod.darker_pink, tcod.darker_cyan]

    def HorLaser():
        formation = Formation(origin=(2,0), formation=[['x'] * 500,
                                                       ['x'] * 500,
                                                       ['x'] * 500])
        return skill_factory.Skill()\
                            .with_target_mode(NoFriendlyFire(ExcludeItems(TargetFormation(formation, positioned_randomly=True))))\
                            .damage_targets("{}'s blazing ray scorches {}! ({} HP)")\
                            .with_damage(damage.MonsterSpellDamage(85, 'fire'))

    def Smite1():
        formation = Formation(origin=(2,2), formation=[['.','.','x','.','.'],
                                                       ['.','x','x','x','.'],
                                                       ['x','x','x','x','x'],
                                                       ['.','x','x','x','.'],
                                                       ['.','.','x','.','.']])
        return skill_factory.Skill()\
                            .with_target_mode(NoFriendlyFire(ExcludeItems(TargetFormation(formation, positioned_randomly=True))))\
                            .damage_targets("{} smites {}! ({} HP)")\
                            .with_damage(damage.MonsterSpellDamage(85, 'fire'))

    def Smite2():
        formation = Formation(origin=(2,3), formation=[['x','x','x','.','.'],
                                                       ['x','x','x','.','.'],
                                                       ['x','x','x','.','.'],
                                                       ['.','.','.','.','.'],
                                                       ['.','.','x','x','x'],
                                                       ['.','.','x','x','x'],
                                                       ['.','.','x','x','x']])
        return skill_factory.Skill()\
                            .with_target_mode(NoFriendlyFire(ExcludeItems(TargetFormation(formation, positioned_randomly=True))))\
                            .damage_targets("{} smites {}! ({} HP)")\
                            .with_damage(damage.MonsterSpellDamage(90, 'fire'))

    def generator(tier=settings.monster_tier, level=1):
        actual_stats = util.copy_dict(BossTheTowerMinion.base_stats)
        actual_stats['level'] = level
        for stat in Stats.primary_stats | Stats.cur_stats - set(['cur_exp']):
            actual_stats[stat] = (BossTheTowerMinion.base_stats[stat] + BossTheTowerMinion.base_stats[stat] * (tier - 1) * TIER_PC_STAT_INC)
            actual_stats[stat] += math.floor(LEVEL_PC_STAT_INC * actual_stats[stat]) * (level-1)
        def gen(position):
            x, y = position
            return Entity(str(uuid.uuid4()), components={
                'Stats': Stats(actual_stats),
                'Position': Position(x, y),
                'Render': Render(character='t', colour=BossTheTowerMinion.colours[tier-1]),
                'Combat': Combat(),
                'NPC': NPC(BossTheTowerMinion.names[tier-1]),
                'AI': ai.AI(initial_state='COUNTDOWN_PHASE')\
                .add_skill('HorLaser', BossTheTowerMinion.HorLaser(), 1)\
                .add_skill('Smite1', BossTheTowerMinion.Smite1(), 1)\
                .add_skill('Smite2', BossTheTowerMinion.Smite2(), 1)\
                .with_state('COUNTDOWN_PHASE', ai.AIState()\
                            .on_turn_randomly(0.66, lambda e, ai, ev_d : None)\
                            .on_turn_randomly(0.5, lambda e, ai, ev_d : ai.use_skill(e, 'Smite2'))\
                            .on_turn_randomly(0.5, lambda e, ai, ev_d : ai.use_skill(e, 'Smite1'))\
                            .on_turn_randomly(0.5, lambda e, ai, ev_d : ai.use_skill(e, 'HorLaser'))\
                            .on_turn_otherwise(lambda e, ai, ev_d : None))\
            }, ttype='BossTheTowerMinion_'+str(tier))
        return gen

