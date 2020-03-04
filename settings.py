#!/usr/bin/env python

import tcod
import tcod.event
import random
from panel import *
from map import *
from console import *
import loot

main_dungeon_lowest_floor = 1

message_panel = MessagePanel(14)

current_map = None

def set_item_world(item):
    import director
    director.map_director.set_item_world(item)
    director.monster_director.set_item_world(item)
    director.loot_director.set_item_world(item)

def set_current_map(mapp):
    global current_map, root_menu
    if current_map is not None:
        player = current_map.entity('PLAYER')
        mapp.add_entity(player)
    current_map = mapp
    root_menu.panel('MapPanel')[1].set_map(mapp)
    root_menu.panel('StatsPanel')[1].set_map(mapp)
    root_menu.panel('InventoryPanel')[1].set_map(mapp)
    root_menu.panel('EquipmentSlotPanel')[1].set_map(mapp)

panels = {
    'MapPanel': ((15,2), MapPanel(current_map)),
    'StatsPanel': ((1,2), StatsPanel(current_map, 'PLAYER')),
    'InventoryPanel': ((46,2), InventoryPanel('PLAYER', current_map, root_console)),
    'EntityStatsPanel': ((66,2), EntityStatsPanel()),
    'EquipmentSlotPanel': ((46,28), EquipmentSlotPanel('PLAYER', current_map)),
    'MessagePanel': ((1,34), message_panel),
    'ModSlotPanel': ((66,28), ModSlotPanel(None))
}

focus_list = ['MapPanel', 'StatsPanel', 'InventoryPanel', 'EquipmentSlotPanel', 'MessagePanel']
focus_index = 0
panels['MapPanel'][1].focus()

root_menu = Menu(panels, focus_list)
