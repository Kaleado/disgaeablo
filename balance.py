#!/usr/bin/env python3

stat_cap = {
    'fire_res': 70,
    'ice_res': 70,
    'lght_res': 70,
    'phys_res': 70,
    'deathblow': 33,
    'lifedrain': 80,
}

monster_stat_scale = {
        'max_hp': 0.3,
        'cur_hp': 1.0,
        'max_sp': 1.0,
        'cur_sp': 1.0,
        'atk': 0.8,
        'dfn': 0.3,
        'itl': 0.8,
        'res': 0.3,
        'spd': 1.0,
        'hit': 1.0,
}

monster_level_stat_inc = 2.0

monster_tier_stat_inc = 30

player_initial_stats = {
    'level': 1,
    'max_hp': 200,
    'cur_hp': 200,
    'max_sp': 25,
    'cur_sp': 25,
    'atk': 200,
    'dfn': 70,
    'itl': 200,
    'res': 70,
    'spd': 15,
    'hit': 15,
    'max_exp': 350
}

exp_yield_scale = 1.0

stat_inc_per_level = 0.1
