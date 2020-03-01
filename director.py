#!/usr/bin/env python
import loot
import monster
import settings
from map import *

class MapDirector:
    def __init__(self):
        self._current_floor = 0

    def _area_for_floor(self, floor):
       if floor == 0:
           return 'TOWN'
       if floor % 5 == 0:
           return 'TWO_ROOMS'
       elif floor > 0 and floor < 10:
           return 'CAVE'
       elif floor >= 10 and floor < 20:
           return 'ROOMS'
       else:
           return 'GRID'

    def map(self, area, level):
        roll = random.randint(0,2)
        mapp = Cave(10, 10)
        w, h = 10, 10
        if area == 'ROOMS':
            mapp = Rooms(30,30)
            w,h=30,30
        elif area == 'GRID':
            mapp = Grid(30,30)
            w,h=30,30
        elif area == 'CAVE':
            mapp = Cave(30, 30)
            w,h=30,30
        elif area == 'TWO_ROOMS':
            mapp = TwoRooms(30, 30, room_size=9)
            w,h=30,30
        n_items = random.randint(2, 7)
        for _ in range(n_items):
            item = loot_director.ground_loot(area, level)
            x, y = random.randint(0, w-1), random.randint(0,h-1)
            while not mapp.is_passable_for(item((0,0)), (x, y)):
                x, y = random.randint(0, w-1), random.randint(0,h-1)
            mapp.add_entity(item((x, y)))

        n_monst = random.randint(2, 10)
        for _ in range(n_monst):
            monst = monster_director.monster(area, level)
            x, y = random.randint(0, w-1), random.randint(0,h-1)
            while not mapp.is_passable_for(monst((0,0)), (x, y)):
                x, y = random.randint(0, w-1), random.randint(0,h-1)
            mapp.add_entity(monst((x, y)))
        return mapp

    def difficulty(self):
        return 3 + self._current_floor * 5

    def move_to_floor(self, floor):
        self._current_floor = floor
        settings.message_panel.info("You descend to floor " + str(self._current_floor))
        player = settings.current_map.entity('PLAYER')
        area = self._area_for_floor(self._current_floor)
        settings.set_current_map(self.map(area, self.difficulty()))
        x, y = settings.current_map.player_start_position(player)
        player.component('Position').set(x, y)

    def descend(self):
        self._current_floor += 1
        settings.message_panel.info("You descend to floor " + str(self._current_floor))
        player = settings.current_map.entity('PLAYER')
        area = self._area_for_floor(self._current_floor)
        settings.set_current_map(self.map(area, self.difficulty()))
        x, y = settings.current_map.player_start_position(player)
        player.component('Position').set(x, y)

map_director = MapDirector()

class MonsterDirector:
    monsters = [
        monster.Slime,
        # monster.Slime,
        # monster.Slime,
        # monster.Slime,
        # monster.Slime,
        monster.Mage,
        # monster.Mage,
        # monster.Mage,
        # monster.Mage,
        # monster.Mage,
        monster.Golem,
        # monster.Golem,
        # monster.Golem,
        # monster.Golem,
        # monster.Golem,
    ]
    def __init__(self):
        pass

    def monster(self, area, level):
        return random.choice(MonsterDirector.monsters).generator(tier=1, level=level)

monster_director = MonsterDirector()

class LootDirector:
    items = [
        loot.Healing,
        # loot.Healing,
        # loot.Healing,
        # loot.Healing,
        # loot.Healing,
        # loot.Healing,
        # loot.Healing,
        loot.Refreshing,
        # loot.Refreshing,
        # loot.Refreshing,
        # loot.Refreshing,
        loot.Sword,
        # loot.Sword,
        # loot.Sword,
        # loot.Sword,
        # loot.Sword,
        # loot.Sword,
        # loot.Sword,
        loot.Staff,
        # loot.Staff,
        # loot.Staff,
        # loot.Staff,
        # loot.Staff,
        # loot.Staff,
        # loot.Staff,
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

    def __init__(self):
        pass

    def monster_loot(self, area, level):
        return random.choice(LootDirector.items)

    def ground_loot(self, area, level):
        roll = random.randint(0,500)
        if roll < 150:
            return loot.Healing.generator(tier=1)
        elif roll < 300:
            return loot.Refreshing.generator(tier=1)
        elif roll < 400:
            return random.choice(LootDirector.weapons).generator(tier=1)
        elif roll < 450:
            return random.choice(LootDirector.attack_skills)
        else:
            return random.choice(LootDirector.support_skills)
        return random.choice(LootDirector.items)

loot_director = LootDirector()
