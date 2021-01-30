#!/usr/bin/env python

import tcod
import tcod.event
import random
from panel import *
from map import *
from console import *
import loot

main_dungeon_lowest_floor = 1
loot_tier = 1
monster_tier = 1
pending_items_received = []
pending_curses_received = []

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

def get_stat(stat):
    return lambda: current_map.entity('PLAYER').component('Stats').get(stat)

panels = {
    'MapPanel': ((15,3), MapPanel(current_map)),
    'StatsPanel': ((1,3), StatsPanel(current_map, 'PLAYER')),
    'InventoryPanel': ((46,3), InventoryPanel('PLAYER', current_map, root_console)),
    'EntityStatsPanel': ((1,15), EntityStatsPanel()),
    'EquipmentSlotPanel': ((46,29), EquipmentSlotPanel('PLAYER', current_map)),
    'MessagePanel': ((1,35), message_panel),
    'ModSlotPanel': ((66,29), ModSlotPanel(None)),
    'HelpPanel': ((1,51), TextPanel("Help", wrap_chars=70)),
    'BuffsPanel': ((1,55), BuffsPanel('PLAYER')),
    'LocationPanel': ((1,0), LocationPanel()),
    'HungerMeterPanel': ((1, 57), Meter('Hunger', get_stat('cur_hunger'), get_stat('max_hunger'), 50, colour=tcod.orange)),
    'ExperienceMeterPanel': ((1, 58), Meter('Experience', get_stat('cur_exp'), get_stat('max_exp'), 50, colour=tcod.yellow))
}

focus_list = ['MapPanel', 'InventoryPanel', 'EquipmentSlotPanel', 'MessagePanel', 'StatsPanel', 'ModSlotPanel', 'HelpPanel', 'EntityStatsPanel']
focus_index = 0
panels['MapPanel'][1].focus()

root_menu = Menu(panels, focus_list)
