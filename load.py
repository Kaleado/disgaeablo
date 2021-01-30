#!/usr/bin/env python
import loot
import monster
import map
import json
import director
import settings

def load_component(obj):
    import entity
    if (obj['SUBTYPE'] == 'STATS'):
        comp = entity.Stats(obj['base_stats'])
        comp._stats = obj['stats']
        comp._stat_inc_per_level = obj['stat_inc_per_level']
        comp._base_stats = obj['base_stats']
        comp._stats_gained_on_level = obj['stats_gained_on_level']
        comp._modifiers = obj['modifiers']
        comp._status_effects = obj['status_effects']
    elif (obj['SUBTYPE'] == 'INVENTORY'):
        items = [load_entity(i) for i in obj['items']]
        comp = entity.Inventory(items)
    elif (obj['SUBTYPE'] == 'POSITION'):
        comp = entity.Position(int(obj['x']), int(obj['y']))
    elif (obj['SUBTYPE'] == 'EQUIPMENT'):
        comp = entity.Equipment([load_entity(i) for i in obj['mod_slots']])
    elif (obj['SUBTYPE'] == 'EQUIPMENTSLOTS'):
        comp = entity.EquipmentSlots([])
        for k, v in obj['slots'].items():
            items = [load_entity(i) for i in v]
            comp._slots[k] = items
    else:
        print("Unrecognized SUBTYPE: " + str(obj['SUBTYPE']))
        raise
    return comp

def load_entity(obj):
    import entity

    if obj == 'None':
        return None
    generator_type = obj['generator_type']
    try:
        underscore = generator_type.index('_')
        is_tiered = True
    except ValueError:
        is_tiered = False
    classname = generator_type if not is_tiered else generator_type[:underscore]
    tier = None if not is_tiered else int(generator_type[underscore+1:])
    if hasattr(loot, classname):
        module = loot
    elif hasattr(monster, classname):
        module = monster
    else:
        print("Invalid classname: " + classname)
        raise
    gen = getattr(module, classname)
    if is_tiered:
        gen = gen.generator(tier=tier)
    template = gen((0,0))
    template._ident = obj['ident']
    for (k, v) in obj['components'].items():
        comp = load_component(v)
        template._components[k] = comp
    return template

def load_map(obj):
    mapp = map.Map()
    mapp._turn_limit = None if obj['turn_limit'] == 'None' else obj['turn_limit']
    mapp._terrain = obj['terrain']
    mapp._can_save = obj['can_save']
    mapp._can_escape = obj['can_escape']
    mapp._max_view_distance = obj['max_view_distance']
    mapp._entities = {}
    for (k, v) in obj['entities'].items():
        mapp._entities[k] = load_entity(v)
    return mapp

def load_save_file(filename):
    try:
        obj = json.load(open(filename))
        settings.main_dungeon_lowest_floor = obj['main_dungeon_lowest_floor']
        settings.loot_tier = obj['loot_tier']
        settings.monster_tier = obj['monster_tier']
        return load_map(obj['current_map'])
    except:
        return None
