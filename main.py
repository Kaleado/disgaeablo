#!/usr/bin/env python

# Make sure 'arial10x10.png' is in the same directory as this script.
import tcod
import tcod.event
import random
import loot
import monster
import settings
from map import *
from panel import *
from entity import *
from director import *

settings.set_current_map(map_director.map(1))

settings.current_map._entities = {
    'PLAYER': Entity('PLAYER', components={
        'Stats': Stats({
            'max_hp': 200,
            'cur_hp': 200,
            'max_sp': 25,
            'cur_sp': 25,
            'atk': 15,
            'dfn': 15,
            'itl': 15,
            'res': 15,
            'spd': 15,
            'hit': 15,
            'max_exp': 50
        }),
        'Combat': Combat(),
        'Position': Position(15, 15),
        'Render': Render(character="@", colour=tcod.red),
        'PlayerLogic': PlayerLogic(),
        'Inventory': Inventory(),
        'EquipmentSlots': EquipmentSlots(['Weapon', 'Armour', 'Armour', 'Armour']),
    })
}
settings.current_map.entity('PLAYER').component('Inventory').add(loot.TownPortal((0,0)))
settings.current_map.entity('PLAYER').component('Inventory').add(loot.TownPortal((0,0)))
settings.current_map.entity('PLAYER').component('Inventory').add(loot.TownPortal((0,0)))
settings.current_map.entity('PLAYER').component('Inventory').add(loot.Fire((0,0)))
settings.current_map.entity('PLAYER').component('Inventory').add(loot.Sword.generator()((0,0)))
settings.current_map.entity('PLAYER').component('Inventory').add(loot.BlazeMod((0,0)))
settings.current_map.add_entity(monster.BossTheSneak.generator()((3,3)))

settings.root_menu.run(settings.root_console)
