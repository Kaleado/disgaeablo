#!/usr/bin/env python

# Make sure 'arial10x10.png' is in the same directory as this script.
import tcod
import tcod.event
import random
import loot
import monster
import settings
import ai
from map import *
from panel import *
from entity import *
from director import *

settings.set_current_map(map_director.map(1))

settings.current_map._entities = {
    'PLAYER': monster.Player((15, 15))
}

# settings.current_map.add_entity(monster.Beehive.generator()((10,10)))

settings.current_map.entity('PLAYER').component('Inventory').add(loot.TownPortal((0,0)))
settings.current_map.entity('PLAYER').component('Inventory').add(loot.TownPortal((0,0)))
settings.current_map.entity('PLAYER').component('Inventory').add(loot.TownPortal((0,0)))
settings.current_map.entity('PLAYER').component('Inventory').add(loot.TownPortal((0,0)))
settings.current_map.entity('PLAYER').component('Inventory').add(loot.WillpowerMod((0,0)))

settings.root_menu.run(settings.root_console)
