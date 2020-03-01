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

settings.set_current_map(map_director.map('CAVE', 1))

settings.current_map._entities = {
    'PLAYER': Entity('PLAYER', components={
        'Stats': Stats({
            'max_hp': 200,
            'cur_hp': 200,
            'max_sp': 45,
            'cur_sp': 45,
            'atk': 15,
            'dfn': 15,
            'itl': 15,
            'res': 15,
            'spd': 15,
            'hit': 15,
            'max_exp': 50
        }),
        'Combat': Combat(),
        'Position': Position(5, 5),
        'Render': Render(character='@', colour=tcod.red),
        'PlayerLogic': PlayerLogic(),
        'Inventory': Inventory(),
        'EquipmentSlots': EquipmentSlots(['Weapon', 'Armour', 'Armour', 'Armour']),
    })
}

settings.current_map.add_entity(loot.AerialDrop((6,5)))
settings.current_map.add_entity(loot.RollingStab((7,5)))
settings.current_map.add_entity(loot.AtkMod((8,5)))
settings.current_map.add_entity(loot.Sword.generator(tier=1)((9,5)))
settings.current_map.add_entity(loot.MeleeLifeDrainMod((10,5)))
settings.current_map.add_entity(loot.MeleeDeathblowMod((11,5)))

settings.root_menu.run(settings.root_console)
