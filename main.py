#!/usr/bin/env python

# Make sure 'arial10x10.png' is in the same directory as this script.
import tcod
import tcod.event
import random
import loot
import monster
import settings
import ai
import ally
from map import *
from panel import *
from entity import *
from director import *

settings.set_current_map(map_director.map(1))

settings.current_map._entities = {
    'PLAYER': monster.Player((15, 15))
}

# settings.current_map.add_entity(monster.Witchdoctor.generator()((10,10)))
# settings.current_map.add_entity(monster.Beehive.generator()((10,10)))
# settings.current_map.add_entity(ally.Allyslime.generator()((10,10)))

settings.current_map.entity('PLAYER').component('Inventory').add(loot.TownPortal((0,0)))
settings.current_map.entity('PLAYER').component('Inventory').add(loot.TownPortal((0,0)))
settings.current_map.entity('PLAYER').component('Inventory').add(loot.TownPortal((0,0)))
settings.current_map.entity('PLAYER').component('Inventory').add(loot.TownPortal((0,0)))
settings.current_map.entity('PLAYER').component('Inventory').add(loot.GrimmsvillePortal((0,0)))
settings.current_map.entity('PLAYER').component('Inventory').add(loot.AtkMod((0,0)))
settings.current_map.entity('PLAYER').component('Inventory').add(loot.ItemLeveler10((0,0)))
settings.current_map.entity('PLAYER').component('Inventory').add(loot.ItemLeveler25((0,0)))
settings.current_map.entity('PLAYER').component('Inventory').add(loot.CurseBees((0,0)))

try:
    settings.root_menu.run(settings.root_console)
except GameplayException:
    pass
except:
    print("Exception occurred, saving game file to save_error.json")
    save = {
        'current_map': settings.current_map.save(),
        'main_dungeon_lowest_floor': settings.main_dungeon_lowest_floor,
        'loot_tier': settings.loot_tier,
        'monster_tier': settings.monster_tier,
    }
    strg = json.dump(save, open('save_error.json', mode='w'))
    raise
