#!/usr/bin/env python

import tcod
import tcod.event
import random
import math
import json
from entitylistview import EntityListView

class Map:
    def __init__(self, map_group=None, turn_limit=None, can_escape=True,
                 floor_colour=tcod.gray, wall_colour=tcod.white,
                 max_view_distance=None):
        self._floor_colour = floor_colour
        self._wall_colour = wall_colour
        self._turn_limit = turn_limit
        self._map_group = map_group
        self._can_save = False
        self._max_view_distance = max_view_distance
        self._can_escape = can_escape
        self._entities = {}
        self._terrain = []
        self._entities_updates = {
            'adds': [],
            'removes': []
        }
        # dict<position -> ident -> delay[]>
        self._threatened_positions = {}

    def max_view_distance(self):
        return self._max_view_distance

    def can_escape(self):
        return self._can_escape

    def can_save(self):
        return self._can_save

    def save(self):
        def save_entities():
            ents = {}
            for (k, v) in self._entities.items():
                ents[k] = v.save()
            return ents
       
        obj = {
            'TYPE': 'MAP',
            'turn_limit': self._turn_limit if self._turn_limit is not None else 'None',
            'entities': save_entities(),
            'terrain': self._terrain,
            'can_save': self._can_save,
            'can_escape': self._can_escape,
            'max_view_distance': self._max_view_distance,
        }
        return obj

    def random_passable_position_for(self, entity):
        w, h = self.dimensions()
        x, y = random.randint(0, w-1), random.randint(0,h-1)
        while not self.is_passable_for(entity, (x, y)):
            x, y = random.randint(0, w-1), random.randint(0,h-1)
        return (x, y)

    def player_start_position(self, player):
        return self.random_passable_position_for(player)

    def add_threatened_positions(self, positions, delay, threatened_by_ident):
        for p in positions:
            if p not in self._threatened_positions:
                self._threatened_positions[p] = {}
            if threatened_by_ident not in self._threatened_positions[p]:
                self._threatened_positions[p][threatened_by_ident] = []
            self._threatened_positions[p][threatened_by_ident].append(delay)

    def remove_threatened_positions(self, threatened_by_ident):
        for d in self._threatened_positions.values():
            if threatened_by_ident in d:
                d[threatened_by_ident] = []

    def _countdown_threatened_positions(self):
        for d in self._threatened_positions.values():
            for ident in d:
                e = self.entity(ident)
                if e is None or e.component('Stats').has_status('PARALYZE'):
                    continue
                new_list = []
                for delay in d[ident]:
                    if delay - 1 <= 0:
                        continue
                    else:
                        new_list.append(delay - 1)
                d[ident] = new_list

    def _position_threatened(self, position):
        return position in self._threatened_positions and \
            len([y for x in self._threatened_positions[position].values() for y in x]) > 0

    def is_descendable(self, pos):
        x, y = pos
        ents_at_pos = self.entities().at_position(pos).with_all_components('Descendable')
        return self._terrain[y][x] == '>' or \
            (ents_at_pos.size() > 0 and ents_at_pos.where(lambda e : e.component('Descendable').can_descend()))

    def render(self, console, origin=(0,0), override_colour=None):
        import util
        x, y = origin
        for row in self._terrain:
            for tile in row:
                dx = x - origin[0]
                dy = y - origin[1]
                player = self.entity('PLAYER')
                if self.max_view_distance() is None or \
                   player is None or \
                   util.distance((dx, dy), player.position().get()) <= self.max_view_distance():
                    fg_changed = False
                    old_fg = console.default_fg
                    if tile == '.':
                        console.default_fg = override_colour or self._floor_colour
                        fg_changed = True
                    elif tile == '#':
                        console.default_fg = override_colour or self._wall_colour
                        fg_changed = True
                    console.print_(x=x, y=y, string=tile)
                    if self._position_threatened((x - origin[0], y - origin[1])):
                        min_delay = min([y for x in self._threatened_positions[(x-origin[0], y-origin[1])].values() for y in x])
                        console.print_(x=x, y=y, string=str(min_delay))
                        console.bg[x][y] = tcod.darkest_yellow
                    if fg_changed:
                        console.default_fg = old_fg
                x += 1
            y += 1
            x = origin[0]

    def passability_map_for(self, entity):
        w = len(self._terrain[0])
        h = len(self._terrain)
        passable_tiles = ['.', '<', '>']
        return [[(self._terrain[y][x] in passable_tiles and self._is_entity_passable_at((x, y))) for x in range(w)] \
                for y in range(h)]

    def _is_entity_passable_at(self, pos):
        ents = self.entities().with_all_components(['Position', 'NPC']).where(lambda ent: ent.component('Position').get() == pos)
        return ents.size() == 0

    def is_passable_for(self, entity, pos):
        x, y = pos
        passable_tiles = ['.', '<', '>']
        return x >= 0 and x < len(self._terrain) and \
            y >= 0 and y < len(self._terrain[0]) and \
            self._terrain[y][x] in passable_tiles and \
            self._is_entity_passable_at((x, y))

    def dimensions(self):
        return (len(self._terrain[0]) if len(self._terrain) > 0 else 0, len(self._terrain))

    def commit(self):
        for entity in self._entities_updates['adds']:
            self._entities[entity.ident()] = entity
        self._entities_updates['adds'] = []
        for ident in self._entities_updates['removes']:
            self._entities.pop(ident, None)
        self._entities_updates['removes'] = []

    def add_entity(self, entity):
        self._entities_updates['adds'].append(entity)

    def remove_entity(self, ident):
        self.entity(ident).disable()
        self._entities_updates['removes'].append(ident)

    def entity(self, ident):
        return self._entities.get(ident)

    def entities(self):
        return EntityListView(self._entities.values())\
            .where(lambda ent: ent.ident() not in self._entities_updates['removes'])

    def trigger_pandemonium(self):
        import settings, director
        difficulty = director.map_director.difficulty() * 30
        for _ in range(random.randint(30, 50)):
            monster = director.monster_director.monster(difficulty, difficulty)((0,0))
            pos = self.random_passable_position_for(monster)
            monster.component('Position').set(pos[0], pos[1])
            settings.current_map.add_entity(monster)

    def _decrement_turn_limit(self):
        import settings
        if self._turn_limit is None or self._turn_limit <= 0:
            return
        self._turn_limit -= 1
        if self._turn_limit % 25 == 0 and self._turn_limit <= 100 or self._turn_limit < 10:
            settings.message_panel.info("There are {} turns remaining".format(self._turn_limit), tcod.darker_crimson)
        if self._turn_limit == 0:
            settings.message_panel.info("A sense of dread overcomes you...", tcod.darker_crimson)
            settings.message_panel.info("It's pandemonium!", tcod.darker_crimson)
            self.trigger_pandemonium()

    def end_turn(self):
        self._countdown_threatened_positions()
        self._decrement_turn_limit()
        for e in self._entities.values():
            if e.handle_event(("NPC_TURN", None), self):
                return

class Cave(Map):
    def __init__(self, width, height, map_group=None, turn_limit=None, can_escape=True, max_view_distance=None):
        super().__init__(map_group, turn_limit, can_escape=can_escape, \
                         wall_colour=tcod.darker_orange, max_view_distance=max_view_distance)
        self._terrain = [['.' if random.randint(0, 2) == 0 else '#' for x in range(width)] for y in range(height)]
        s_x, s_y = random.randint(0, width-1), random.randint(0, height-1)
        while self._terrain[s_y][s_x] == '#':
            s_x, s_y = random.randint(0, width-1), random.randint(0, height-1)
        self._terrain[s_y][s_x] = '>'
        for _ in range(4):
            for x in range(width):
                for y in range(height):
                    if self._terrain[y][x] == '>':
                        continue
                    living = 0
                    for xx in range(-1, 2):
                        for yy in range(-1, 2):
                            if xx == 0 and yy == 0:
                                continue
                            living += 1 if x + xx >= 0 and \
                                           y + yy >= 0 and \
                                           x + xx < width and \
                                           y + yy < height and \
                                           (self._terrain[y+yy][x+xx][0] == '#') else 0
                    if living > 6:
                        self._terrain[y][x] = '._'
                    elif living < 5:
                        self._terrain[y][x] = '#_'
            for x in range(width):
                for y in range(height):
                    self._terrain[y][x] = '#' if self._terrain[y][x] == '._' else \
                                          '.' if self._terrain[y][x] == '#_' else self._terrain[y][x]

class Rooms(Map):
    def __init__(self, width, height, map_group=None, turn_limit=None, can_escape=True, max_view_distance=None):
        super().__init__(map_group, turn_limit, can_escape=can_escape, max_view_distance=max_view_distance)
        self._terrain = [['#' for x in range(width)] for y in range(height)]
        max_w = 8
        max_h = 8
        rooms = [(random.randint(1,width-max_w), random.randint(1,height-max_h), random.randint(3,max_w), random.randint(3,max_h)) for _ in range(random.randint(3,6))]
        prev_room = None
        for (x, y, w, h) in rooms:
            for xx in range(x, x+w):
                for yy in range(y, y+h):
                    self._terrain[yy][xx] = '.'
            if prev_room is not None:
                (px, py, pw, ph) = prev_room
                xx, yy = (random.randint(x, x+w-1), random.randint(y, y+h-1))
                ax, ay = (random.randint(px, px+pw-1), random.randint(py, py+ph-1))
                if random.randint(0,1) == 1:
                    while xx != ax:
                        self._terrain[yy][xx] = '.'
                        xx += 1 if ax > xx else -1
                    while yy != ay:
                        self._terrain[yy][xx] = '.'
                        yy += 1 if ay > yy else -1
                else:
                    while yy != ay:
                        self._terrain[yy][xx] = '.'
                        yy += 1 if ay > yy else -1
                    while xx != ax:
                        self._terrain[yy][xx] = '.'
                        xx += 1 if ax > xx else -1
            prev_room = (x, y, w, h)

        (s_x, s_y, s_w, s_h) = rooms[random.randint(0, len(rooms)-1)]
        self._terrain[random.randint(s_y, s_y+s_h)][random.randint(s_x, s_x+s_w)] = '>'

class Grid(Map):
    def _get_door_pos(self, direction, xx, yy, room_size):
        floor = math.floor
        if direction == 'N':
            door_x, door_y = floor((xx + 0.5) * room_size), yy * room_size
        elif direction == 'E':
            door_x, door_y = (xx + 1) * room_size, floor((yy + 0.5) * room_size)
        elif direction == 'S':
            door_x, door_y = floor((xx + 0.5) * room_size), (yy + 1) * room_size
        elif direction == 'W':
            door_x, door_y = xx * room_size, floor((yy + 0.5) * room_size)
        return (door_x, door_y)

    def __init__(self, width, height, map_group=None, turn_limit=None, can_escape=True, max_view_distance=None):
        super().__init__(map_group, turn_limit, can_escape=can_escape, max_view_distance=max_view_distance)
        floor = math.floor
        room_size = 6
        rooms_w = width // room_size
        rooms_h = height // room_size
        rooms_grid = [[random.choice(['N', 'E', 'S', 'W'] * 3 + ['#', '#', '#', 'C']) for x in range(rooms_w)] for y in range(rooms_h)]
        self._terrain = [['#' if (x % room_size) * (y % room_size) == 0 or \
                          rooms_grid[y//room_size][x//room_size] == '#' \
                          else '.' for x in range(width)] for y in range(height)]
        start_room = (random.randint(0, rooms_w - 1), random.randint(0, rooms_h - 1))
        seen = set([start_room])
        q = [start_room]
        while len(q) > 0:
            x, y = q.pop()
            for dx in range(-1,2):
                for dy in range(-1,2):
                    if dy * dx != 0 or (dx == 0 and dy == 0):
                        continue
                    in_bounds = x + dx >= 0 and y + dy >= 0 and x + dx < rooms_w and y + dy < rooms_h
                    if in_bounds and (x+dx, y+dy) not in seen and rooms_grid[y+dy][x+dx] not in ['#', 'C']:
                        seen = seen | set([(x+dx, y+dy)])
                        rooms_grid[y+dy][x+dx] = 'W' if dx == 1 else 'E' if dx == -1 else 'N' if dy == 1 else 'S'
                        if random.randint(0,1) == 1:
                            q.append((x+dx, y+dy))
                        else:
                            q = [(x+dx, y+dy)] + q
        for xx in range(rooms_w):
            for yy in range(rooms_h):
                if rooms_grid[yy][xx] in ['N', 'E', 'S', 'W']:
                    door_x, door_y = self._get_door_pos(rooms_grid[yy][xx], xx, yy, room_size)
                elif rooms_grid[yy][xx] == 'C': # checkerboard pattern
                    flag = False
                    for x in range(0, room_size):
                        for y in range(0, room_size):
                            self._terrain[yy*room_size + y][xx*room_size + x] = '.' if flag else '#'
                            flag = not flag
                        flag = not flag
                    door_x, door_y = self._get_door_pos(random.choice(['N', 'E', 'S', 'W']), xx, yy, room_size)
                else:
                    continue
                if door_x < width and door_y < height:
                    self._terrain[door_y][door_x] = '.'
        stairs_x, stairs_y = random.randint(0, width-1), random.randint(0, height-1)
        while self._terrain[stairs_y][stairs_x] == '#':
            stairs_x, stairs_y = random.randint(0, width-1), random.randint(0, height-1)
        self._terrain[stairs_y][stairs_x] = '>'

class TwoRooms(Map):
    def player_start_position(self, player):
        x, y = self._width // 2 - self._room_size // 2 - self._corridor_len // 2, self._height // 2 - self._room_size // 2 - 1
        return (x, y)

    def __init__(self, width, height, room_size=5, corridor_len=9, map_group=None, turn_limit=None, can_escape=True, max_view_distance=None):
        super().__init__(map_group, turn_limit, can_escape=can_escape, max_view_distance=max_view_distance)
        self._width = width
        self._height = height
        self._room_size = room_size
        self._corridor_len = corridor_len
        self._terrain = [['#' for x in range(width)] for y in range(height)]
        # Left room
        x, y = width // 2 - room_size - corridor_len // 2, height // 2 - room_size // 2 - 1
        for xx in range(room_size):
            for yy in range(room_size):
                self._terrain[y+yy][x+xx] = '.'
        # Right room
        x += room_size + corridor_len
        for xx in range(room_size):
            for yy in range(room_size):
                self._terrain[y+yy][x+xx] = '.'
        x, y = width // 2 - corridor_len // 2, height // 2 - 1
        for xx in range(corridor_len):
            self._terrain[y][x+xx] = '.'
        x, y = width // 2 + corridor_len // 2 + room_size // 2, height // 2 - 1
        self._terrain[y][x] = '>'

class Corridors(Map):
    def __init__(self, width, height, room_size=5, map_group=None, turn_limit=None, can_escape=True, max_view_distance=None):
        super().__init__(map_group, turn_limit, can_escape=can_escape, max_view_distance=max_view_distance)
        self._width = width
        self._height = height
        self._room_size = room_size
        self._terrain = [['#' for x in range(width)] for y in range(height)]
        # Room
        # rx, ry = width // 2 - room_size // 2, height // 2 - room_size // 2
        rx, ry = random.randint(1, width-2 - room_size), random.randint(1, height-2 - room_size)
        for xx in range(room_size):
            for yy in range(room_size):
                self._terrain[ry+yy][rx+xx] = '.'
        # Corridors
        corr = [ry] + [random.randint(1, width-2) for _ in range(random.randint(3, 5))]
        c = corr[0]
        for x in range(width):
            self._terrain[c][x] = '.'
        c = corr[1]
        for y in range(width):
            self._terrain[y][c] = '.'
        for c in corr[2:]:
            if random.randint(0,1) == 0:
                for x in range(width):
                    self._terrain[c][x] = '.'
            else:
                for y in range(width):
                    self._terrain[y][c] = '.'
        # Stairs
        self._terrain[ry + room_size//2][rx + room_size//2] = '>'

class Town(Map):
    def _building(self, x, y, w, h):
        for xx in range(x, x+w):
            for yy in range(y, y+h):
                self._terrain[yy][xx] = '#'

    def __init__(self, width, height, residents, map_group=None, turn_limit=None, can_escape=True, max_view_distance=None):
        super().__init__(map_group, turn_limit, can_escape=can_escape, max_view_distance=max_view_distance)
        self._can_save = True
        self._terrain = [['.' for x in range(width)] for y in range(height)]
        x, y = width // 2, height // 2
        self._terrain[y][x] = '>'

        buildings = [
            (1, 1, 10, 4),
            (width-12, 1, 8, 4),
            (1, 6, 4, 10),
            (width-5, 1, 4, 8),
            (width-10, 6, 4, 8),
            (1, height-7, 7, 6),
        ]
        for x, y, w, h in buildings:
            self._building(x, y, w, h)

        for generator in residents:
            ent = generator((random.randint(3, width-3),random.randint(3, height-3)))
            x, y = self.random_passable_position_for(ent)
            ent.component('Position').set(x, y)
            self.add_entity(ent)

class TheTowerArena(Map):
    def _room(self, x, y, w, h):
        for xx in range(x, x+w):
            for yy in range(y, y+h):
                self._terrain[yy][xx] = '.'

    def __init__(self, width, height, map_group=None, turn_limit=None, can_escape=True, max_view_distance=None):
        super().__init__(map_group, turn_limit, can_escape=can_escape, max_view_distance=max_view_distance)
        self._width = width
        self._height = height
        self._terrain = [['#' for x in range(width)] for y in range(height)]
        self._room(1, height // 3 - 1, width - 2, 2 * height // 3)
        self._room(width // 2, 1, 1, height - 2)
        self._terrain[5][width // 2] = '>'

class BeholderArena(Map):
    def __init__(self, width, height, room_size=5, map_group=None, turn_limit=None, can_escape=True, max_view_distance=None):
        super().__init__(map_group, turn_limit, can_escape=can_escape, max_view_distance=max_view_distance)
        self._width = width
        self._height = height
        self._room_size = room_size
        self._terrain = [['#' for x in range(width)] for y in range(height)]
        # Room
        # rx, ry = width // 2 - room_size // 2, height // 2 - room_size // 2
        rx, ry = random.randint(1, width-2 - room_size), random.randint(1, height-2 - room_size)
        for xx in range(room_size):
            for yy in range(room_size):
                self._terrain[ry+yy][rx+xx] = '.'
        # Corridors
        corr = [ry] + [random.randint(1, width-2) for _ in range(random.randint(3, 5))]
        c = corr[0]
        for x in range(width):
            self._terrain[c][x] = '.'
        c = corr[1]
        for y in range(width):
            self._terrain[y][c] = '.'
        for c in corr[2:]:
            if random.randint(0,1) == 0:
                for x in range(width):
                    self._terrain[c][x] = '.'
            else:
                for y in range(width):
                    self._terrain[y][c] = '.'
        # Stairs
        self._terrain[ry + room_size//2][rx + room_size//2] = '>'

class TheSneakArena(Map):
    def __init__(self, width, height, map_group=None, turn_limit=None, can_escape=True, max_view_distance=None):
        super().__init__(map_group, turn_limit, can_escape=can_escape, max_view_distance=max_view_distance)
        floor = math.floor
        room_size = 6
        rooms_w = width // room_size
        rooms_h = height // room_size
        rooms_grid = [[random.choice(['N', 'E', 'S', 'W']) for x in range(rooms_w)] for y in range(rooms_h)]
        self._terrain = [['#' if (x % room_size) * (y % room_size) == 0 else '.' for x in range(width)] for y in range(height)]
        start_room = (random.randint(0, rooms_w - 1), random.randint(0, rooms_h - 1))
        seen = set([start_room])
        q = [start_room]
        while len(q) > 0:
            x, y = q.pop()
            for dx in range(-1,2):
                for dy in range(-1,2):
                    if dy * dx != 0 or (dx == 0 and dy == 0):
                        continue
                    if x + dx >= 0 and y + dy >= 0 and x + dx < rooms_w and y + dy < rooms_h and (x+dx, y+dy) not in seen:
                        seen = seen | set([(x+dx, y+dy)])
                        rooms_grid[y+dy][x+dx] = 'W' if dx == 1 else 'E' if dx == -1 else 'N' if dy == 1 else 'S'
                        if random.randint(0,1) == 1:
                            q.append((x+dx, y+dy))
                        else:
                            q = [(x+dx, y+dy)] + q
        for xx in range(rooms_w):
            for yy in range(rooms_h):
                if rooms_grid[yy][xx] == 'N':
                    door_x, door_y = floor((xx + 0.5) * room_size), yy * room_size
                elif rooms_grid[yy][xx] == 'E':
                    door_x, door_y = (xx + 1) * room_size, floor((yy + 0.5) * room_size)
                elif rooms_grid[yy][xx] == 'S':
                    door_x, door_y = floor((xx + 0.5) * room_size), (yy + 1) * room_size
                elif rooms_grid[yy][xx] == 'W':
                    door_x, door_y = xx * room_size, floor((yy + 0.5) * room_size)
                if door_x < width and door_y < height:
                    self._terrain[door_y][door_x] = '.'
        stairs_x, stairs_y = random.randint(0, width-1), random.randint(0, height-1)
        while self._terrain[stairs_y][stairs_x] == '#':
            stairs_x, stairs_y = random.randint(0, width-1), random.randint(0, height-1)
        self._terrain[stairs_y][stairs_x] = '>'

class Rivers(Map):
    def _fill(self, w, h, tile):
        self._terrain = [[tile for x in range(w)] for y in range(h)]

    def _in_bounds(self, p, w, h):
        x, y = p
        return x >= 0 and y >= 0 and x < w and y < h

    def _place_stairs(self, width, height):
        stairs_x, stairs_y = random.randint(0, width-1), random.randint(0, height-1)
        while self._terrain[stairs_y][stairs_x] == '#':
            stairs_x, stairs_y = random.randint(0, width-1), random.randint(0, height-1)
        self._terrain[stairs_y][stairs_x] = '>'

    def _apply_brush(self, brush, position, w, h):
        import util
        x, y = util.vec_round(position)
        for xx in range(len(brush[0])):
            for yy in range(len(brush)):
                if not self._in_bounds((x+xx, y+yy), w, h):
                    continue
                self._terrain[y+yy][x+xx] = brush[yy][xx]

    def __init__(self, width, height, n_rivers=3, thickness=2, inverted=False, map_group=None, turn_limit=None, can_escape=True, max_view_distance=None):
        import util
        super().__init__(map_group, turn_limit, can_escape=can_escape, max_view_distance=max_view_distance)
        brush = [
            ['#' if inverted else '.'] * thickness
        ] * thickness
        self._fill(width, height, '.' if inverted else '#')
        for _i in range(n_rivers):
            roll = random.randint(0,3)
            if roll == 0:
                point = (0, random.randint(0, height-1))
            elif roll == 1:
                point = (width-1, random.randint(0, height-1))
            elif roll == 2:
                point = (random.randint(0, width-1), 0)
            elif roll == 3:
                point = (random.randint(0, width-1), height-1)
            center = (width/2, height/2)
            delta = util.normalize(util.difference(point, center))
            orig_delta = delta
            print(delta)
            turn_l = util.rot_ccw_90(orig_delta)
            turn_r = util.rot_cw_90(orig_delta)
            iterations = 0
            while self._in_bounds(point, width, height):
                self._apply_brush(brush, point, width, height)
                if iterations > width / 3:
                    pert = util.normalize(
                        util.add(delta, util.scalar_mult(random.choice([turn_l, turn_r]), 0.7 + 0.3*random.random())))
                    delta = util.normalize(util.add(delta, pert))
                point = util.add(point, delta)
                iterations += 1
        self._place_stairs(width, height)

class Ring(Map):
    def _fill(self, w, h, tile):
        self._terrain = [[tile for x in range(w)] for y in range(h)]

    def _in_bounds(self, p, w, h):
        x, y = p
        return x >= 0 and y >= 0 and x < w and y < h

    def _apply_brush(self, brush, position, w, h):
        import util
        x, y = util.vec_round(position)
        for xx in range(len(brush[0])):
            for yy in range(len(brush)):
                if not self._in_bounds((x+xx, y+yy), w, h):
                    continue
                self._terrain[y+yy][x+xx] = brush[yy][xx]

    def _place_stairs(self, width, height):
        stairs_x, stairs_y = random.randint(0, width-1), random.randint(0, height-1)
        while self._terrain[stairs_y][stairs_x] == '#':
            stairs_x, stairs_y = random.randint(0, width-1), random.randint(0, height-1)
        self._terrain[stairs_y][stairs_x] = '>'

    def _draw_ring(self, width, height, ring_thickness, ring_offset):
        brush = [
            ['#' if self._inverted else '.'] * ring_thickness
        ] * ring_thickness
        # Top & bottom
        for x in range(ring_offset, width - ring_thickness):
            self._apply_brush(brush, (x, ring_offset), width, height)
            self._apply_brush(brush, (x, height - ring_thickness - 1), width, height)
        # Left & right
        for y in range(ring_offset, height - ring_thickness - 1):
            self._apply_brush(brush, (ring_offset, y), width, height)
            self._apply_brush(brush, (width - ring_thickness - 1, y), width, height)

    def _draw_room(self, width, height, room_size):
        x_min = math.floor(width/2) - math.floor(room_size/2)
        x_max = math.floor(width/2) + math.floor(room_size/2)
        y_min = math.floor(height/2) - math.floor(room_size/2)
        y_max = math.floor(height/2) + math.floor(room_size/2)
        for x in range(x_min, x_max):
            for y in range(y_min, y_max):
                self._terrain[y][x] = '#' if self._inverted else '.'

    def _draw_corridor(self, width, height, room_size, ring_offset, ring_thickness):
        x = math.floor(width/2)
        y_max = math.floor(height/2) - math.floor(room_size/2)
        flag = False
        for y in range(ring_offset+ring_thickness, y_max):
            if flag:
                self._terrain[y][x-1] = '#' if self._inverted else '.'
                self._terrain[y][x] = '.' if self._inverted else '#'
            else:
                self._terrain[y][x-1] = '.' if self._inverted else '#'
                self._terrain[y][x] = '#' if self._inverted else '.'
            flag = not flag

    def __init__(self, width, height, room_size=8, ring_thickness=3, ring_offset=1, inverted=False, map_group=None, turn_limit=None, can_escape=True, max_view_distance=None):
        import util
        self._inverted = inverted
        super().__init__(map_group, turn_limit, can_escape=can_escape, max_view_distance=max_view_distance)
        self._fill(width, height, '.' if self._inverted else '#')
        self._draw_ring(width, height, ring_thickness, ring_offset)
        self._draw_room(width, height, room_size)
        self._draw_corridor(width, height, room_size, ring_offset, ring_thickness)
        self._place_stairs(width, height)

class Checkerboard(Map):
    def _place_stairs(self, width, height):
        stairs_x, stairs_y = random.randint(0, width-1), random.randint(0, height-1)
        while self._terrain[stairs_y][stairs_x] == '#':
            stairs_x, stairs_y = random.randint(0, width-1), random.randint(0, height-1)
        self._terrain[stairs_y][stairs_x] = '>'

    def __init__(self, width, height, map_group=None, turn_limit=None, can_escape=True, max_view_distance=None):
        import util
        super().__init__(map_group, turn_limit, can_escape=can_escape, max_view_distance=max_view_distance)
        self._terrain = [['.' if (x + y) % 2 == 0 else '#' for x in range(width)] for y in range(height)]
        for x in range(0, width):
            self._terrain[0][x] = '#'
            self._terrain[height-1][x] = '#'
        for y in range(0, width):
            self._terrain[y][0] = '#'
            self._terrain[y][width-1] = '#'
        self._place_stairs(width, height)

class Posts(Map):
    def _place_stairs(self, width, height):
        stairs_x, stairs_y = random.randint(0, width-1), random.randint(0, height-1)
        while self._terrain[stairs_y][stairs_x] == '#':
            stairs_x, stairs_y = random.randint(0, width-1), random.randint(0, height-1)
        self._terrain[stairs_y][stairs_x] = '>'

    def __init__(self, width, height, map_group=None, inverted=False, turn_limit=None, can_escape=True, max_view_distance=None):
        import util
        super().__init__(map_group, turn_limit, can_escape=can_escape, max_view_distance=max_view_distance)
        a = '.' if not inverted else '#'
        b = '#' if not inverted else '.'
        self._terrain = [[a if y % 2 == 0 else b if x % 2 == 0 else a for x in range(width)] for y in range(height)]
        for x in range(0, width):
            self._terrain[0][x] = b
            self._terrain[height-1][x] = b
        for y in range(0, width):
            self._terrain[y][0] = b
            self._terrain[y][width-1] = b
        self._place_stairs(width, height)

class Grimmsville(Map):
    def _building(self, x, y, w, h):
        for xx in range(x, x+w):
            for yy in range(y, y+h):
                self._terrain[yy][xx] = '#'

    def __init__(self, width, height, residents, map_group=None, turn_limit=None, can_escape=True, max_view_distance=None):
        super().__init__(map_group, turn_limit, can_escape=can_escape, \
                         max_view_distance=max_view_distance, wall_colour=tcod.dark_red, floor_colour=tcod.darkest_orange)
        self._can_save = True
        self._terrain = [['.' for x in range(width)] for y in range(height)]
        x, y = width // 2, height // 2
        self._terrain[y][x] = '>'

        buildings = [
            (1, 1, 10, 4),
            (width-12, height-5, 8, 4),
            (width-5, height-9, 4, 8),
            (1, 6, 4, 10),
            (width-10, 6, 4, 8),
            (1, height-7, 7, 6),
        ]
        for x, y, w, h in buildings:
            self._building(x, y, w, h)

        for generator in residents:
            ent = generator((random.randint(3, width-3),random.randint(3, height-3)))
            x, y = self.random_passable_position_for(ent)
            ent.component('Position').set(x, y)
            self.add_entity(ent)

class Labyrinth(Map):
    def _place_stairs(self, width, height):
        stairs_x, stairs_y = 15, 15
        self._terrain[stairs_y][stairs_x] = '>'

    def __init__(self, width, height, map_group=None, inverted=False, turn_limit=None, \
                 can_escape=True, max_view_distance=None):
        import util
        super().__init__(map_group, turn_limit, can_escape=can_escape, max_view_distance=max_view_distance)
        a = '.' if not inverted else '#'
        b = '#' if not inverted else '.'
        self._terrain = [[a for x in range(width)] for y in range(height)]
        for x in range(0, width):
            self._terrain[0][x] = b
            self._terrain[height-1][x] = b
        for y in range(0, width):
            self._terrain[y][0] = b
            self._terrain[y][width-1] = b

        w = width
        h = height
        x, y = 0, 0
        while w > 2 and h > 2:
            print(x, y)
            for _ in range(w):
                self._terrain[y][x] = b
                x += 1
            x -= 1
            for _ in range(h):
                self._terrain[y][x] = b
                y += 1
            y -= 1
            for _ in range(w-2):
                self._terrain[y][x] = b
                x -= 1
            x += 1
            for _ in range(h-2):
                self._terrain[y][x] = b
                y -= 1
            y += 1
            w -= 4
            h -= 4
       
        self._place_stairs(width, height)
