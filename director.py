#!/usr/bin/env python
import loot
import monster
import settings
from map import *

class MapDirector:
    def __init__(self):
        self._current_floor = 0
        self._item_world = None # item_world = none indicates we are in the main dungeon

    def set_item_world(self, item):
        self._item_world = item

    def _item_world_map(self, level):
        mapp = Grid(30,30)
        w,h=30,30
        return mapp, w, h

    def _main_dungeon_map(self, level):
        mapp = Grid(30,30)
        w,h=30,30
        if self._current_floor == 0:
            mapp = Town(30, 30, [monster.ItemWorldClerkNPC])
            w,h=30,30
        elif self._current_floor % 5 == 0:
            mapp = TwoRooms(30, 30, room_size=9)
            w,h=30,30
        elif self._current_floor in range(0, 10):
            mapp = Cave(30, 30)
            w,h=30,30
        elif self._current_floor % 10 == 1:
            mapp = Corridors(30, 30, room_size=5)
            w,h=30,30
        elif self._current_floor in range(10, 20):
            mapp = Rooms(30,30)
            w,h=30,30
        return mapp, w, h

    def map(self, level):
        if self._item_world is not None:
            mapp, w, h = self._item_world_map(level)
        else:
            mapp, w, h = self._main_dungeon_map(level)

        if self._current_floor == 0 and self._item_world is None:
            return mapp
       
        n_items = random.randint(2, 7)
        for _ in range(n_items):
            item = loot_director.ground_loot(level)
            x, y = random.randint(0, w-1), random.randint(0,h-1)
            while not mapp.is_passable_for(item((0,0)), (x, y)):
                x, y = random.randint(0, w-1), random.randint(0,h-1)
            mapp.add_entity(item((x, y)))

        n_monst = random.randint(2, 10)
        for _ in range(n_monst):
            monst = monster_director.monster(level)
            x, y = random.randint(0, w-1), random.randint(0,h-1)
            while not mapp.is_passable_for(monst((0,0)), (x, y)):
                x, y = random.randint(0, w-1), random.randint(0,h-1)
            mapp.add_entity(monst((x, y)))
        return mapp

    def difficulty(self):
        if self._item_world == None:
            return 3 + self._current_floor * 5
        else:
            import entity
            stats = self._item_world.component('Stats')
            primaries = entity.Stats.primary_stats - set(['max_hp', 'max_sp'])
            tot = sum([stats.get_base(stat) for stat in primaries])
            return 3 + self._current_floor + math.floor(tot / 5)

    def _change_floor(self):
        if self._item_world is None:
            settings.main_dungeon_lowest_floor = max(settings.main_dungeon_lowest_floor, self._current_floor)
        player = settings.current_map.entity('PLAYER')
        settings.set_current_map(self.map(self.difficulty()))
        x, y = settings.current_map.player_start_position(player)
        player.component('Position').set(x, y)

    def return_to_town(self):
        # Replenish HP and SP
        player = settings.current_map.entity('PLAYER')
        max_hp = player.component('Stats').get_value('max_hp')
        max_sp = player.component('Stats').get_value('max_sp')
        player.component('Stats').set_base('cur_hp', max_hp)
        player.component('Stats').set_base('cur_sp', max_sp)
        # Return to town
        settings.set_item_world(None)
        self.move_to_floor(0)

    def move_to_floor(self, floor):
        settings.message_panel.info("You move to floor {}".format(floor))
        self._current_floor = floor
        self._change_floor()

    def descend(self):
        # If entering the main dungeon, return to the lowest floor in the dungeon
        if self._current_floor == 0:
            if self._item_world is None:
                self.move_to_floor(settings.main_dungeon_lowest_floor)
            else:
                item = self._item_world
                self.move_to_floor(item.component('Item').item_world_floor(item))
            return

        settings.message_panel.info("You descend to floor {}".format(self._current_floor+1))
        if self._item_world is not None:
            self._item_world.component('Stats').increase_level(1)
        self._current_floor += 1
        self._change_floor()

map_director = MapDirector()

class MonsterDirector:
    monsters = [
        monster.Slime,
        monster.Mage,
        monster.Golem,
        monster.Scorpion,
        monster.Spider,
        monster.Eye,
        # monster.Golem,
        # monster.Golem,
        # monster.Golem,
        # monster.Golem,
    ]
    def __init__(self):
        self._item_world = None

    def set_item_world(self, item):
        self._item_world = item

    def monster(self, level):
        tier = 1
        if random.randint(0, 100) < 3:
            tier += 1
            level = math.floor(level * 0.1)
        return random.choice(MonsterDirector.monsters).generator(tier=tier, level=level)

monster_director = MonsterDirector()

class LootDirector:
    items = [
        loot.Healing,
        loot.Refreshing,
        loot.Sword,
        loot.Staff,
        loot.Cleave,
        loot.Pierce,
        loot.Fire,
        loot.Ice,
        loot.Lightning,
        loot.Paralyze,
        loot.Poison,
        loot.GuardBreak,
        loot.MindBreak,
        loot.Weaken,
        loot.Stoneskin,
        loot.Blink,
    ]

    weapons = [
        loot.Staff,
        loot.Sword,
    ]

    attack_skills = [
        loot.Cleave,
        loot.Pierce,
        loot.Fire,
        loot.Ice,
        loot.Lightning,
        loot.RollingStab,
        loot.AerialDrop,
        loot.WhipSlash,
        loot.Bypass,
    ]

    support_skills = [
        loot.Paralyze,
        loot.Poison,
        loot.GuardBreak,
        loot.MindBreak,
        loot.Weaken,
        loot.Stoneskin,
        loot.Blink,
        loot.Dash,
    ]

    mods = [
        loot.AtkMod,
        loot.DfnMod,
        loot.ItlMod,
        loot.ResMod,
        loot.SpdMod,
        loot.HitMod,
        loot.MeleeLifeDrainMod,
        loot.MeleeDeathblowMod,
        loot.SPRegenMod,
        loot.HPRegenMod,
        loot.SpellSoulDrainMod,
        loot.ToxicForceMod,
        loot.PoisonHealMod,
        loot.SoulConversionMod,
        loot.LightningDamageMod,
        loot.FireDamageMod,
        loot.IceDamageMod,
        loot.PhysicalDamageMod,
    ]

    def __init__(self):
        self._item_world = None

    def set_item_world(self, item):
        self._item_world = item

    def monster_loot(self, level):
        return random.choice(LootDirector.items)

    def ground_loot(self, level):
        roll = random.randint(0,500)
        if roll < 100:
            return loot.Healing.generator(tier=1)
        elif roll < 150:
            return loot.Refreshing.generator(tier=1)
        elif roll < 200:
            return loot.TownPortal
        elif roll < 300:
            return random.choice(LootDirector.mods)
        elif roll < 400:
            return random.choice(LootDirector.weapons).generator(tier=1)
        elif roll < 450:
            return random.choice(LootDirector.attack_skills)
        else:
            return random.choice(LootDirector.support_skills)
        return random.choice(LootDirector.items)

loot_director = LootDirector()
