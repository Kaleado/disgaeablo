#!/usr/bin/env python

import entity, map, panel, loot
from typing import Callable
import tcod, random

class Curse(entity.Usable):
    def __init__(self):
        super().__init__(targeting_mode=entity.TargetNobody())

    def generate_map(self, entity: entity.Entity, user_entity: entity.Entity, mapp: map.Map, menu: panel.Menu):
        pass

    def use(self, entity: entity.Entity, user_entity: entity.Entity, mapp: map.Map, menu: panel.Menu):
        import director
        recipient = panel.text_prompt("Enter net name of recipient:")
        message = panel.text_prompt("Enter message to attach to curse:")
        curse_map = self.generate_map(entity, user_entity, mapp, menu)
        print(curse_map)
        director.net_director.queue_events([('NET_RECEIVED_CURSE', {
            'sender': director.net_director.net_name(),
            'receiver': recipient,
            'message': message,
            'curse_map': curse_map.save()
        })])
        director.net_director.send_events()
        return False

def CurseBees(position: entity.Position):
    class _CurseBees(Curse):
        def generate_map(self, entity: entity.Entity, user_entity: entity.Entity, mapp: map.Map, menu: panel.Menu):
            difficulty = user_entity.stat('level')
            curse_map = map.TwoRooms(30, 30, can_escape=False)
            for _ in range(25):
                beehive = monster.Beehive.generator(level=difficulty)((0,0))
                x, y = curse_map.random_passable_position_for(beehive)
                beehive.component('Position').set(x, y)
                curse_map.add_entity(beehive)
            curse_map.commit()
            print("entities", curse_map._can_escape)
            return curse_map

    import monster, uuid
    x, y = position
    return entity.Entity(str(uuid.uuid4()), components={
        'Stats': entity.Stats({}, stat_inc_per_level=loot.LEVEL_PC_STAT_INC),
        'Position': entity.Position(x, y),
        'Render': entity.Render(character='?', colour=tcod.yellow),
        'Usable': entity.ConsumeAfter(_CurseBees()),
        'Item': entity.Item("Curse of bees", 'Network item; Force a player to encounter a floor full of bees'),
    }, ttype='CurseBees')
