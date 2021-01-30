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
# settings.current_map.entity('PLAYER').component('Inventory').add(loot.GrimmsvillePortal((0,0)))
# settings.current_map.entity('PLAYER').component('Inventory').add(loot.AtkMod((0,0)))
# settings.current_map.entity('PLAYER').component('Inventory').add(loot.ItemLeveler10((0,0)))
# settings.current_map.entity('PLAYER').component('Inventory').add(loot.ItemLeveler25((0,0)))
# settings.current_map.entity('PLAYER').component('Inventory').add(loot.CurseBees((0,0)))

def load_last_save():
    """
    Use the config.json to load the last save, if it exists.
    """

    settings.root_console.clear()
    settings.root_console.print_(x=30, y=30, string="Now loading...")
    tcod.console_flush()  # Show the console.

    import load
    with open('config.json', mode='r') as f:
        config = json.load(f)

        last_save = config["last_save"]
        if last_save is not None:
            m = load.load_save_file(last_save)
            if m is not None:
                settings.current_map = None
                settings.set_current_map(m)

try:
    load_last_save()
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
