#!/usr/bin/env python

import tcod
import tcod.event
import random
import settings
from util import *

class Menu:
    def __init__(self, panels, focus_list):
        self._panels = panels
        self._focus_list = focus_list
        self._focus_index = 0
        self._has_resolved = False
        self._resolution_value = None
        self._repositioning_panels = False

        self._panels[self._focus_list[self._focus_index]][1].focus()

    def _focused_panel(self):
        return self._panels[self._focus_list[self._focus_index]][1]

    def focus(self, panel_ident):
        self._focused_panel().unfocus()
        index = 0
        for ident in self._focus_list:
            if ident == panel_ident:
                self.focus_index = index
            index += 1
        self._panels[panel_ident][1].focus()

    def panel(self, panel):
        return self._panels.get(panel)

    def set_panel(self, panel, new_panel):
        self._panels[panel] = new_panel

    def resolve(self, value=None):
        self._resolution_value = value
        self._has_resolved = True

    def unresolve(self):
        self._resolution_value = None
        self._has_resolved = False

    def run(self, console):
        import director, entity
        render_tick = 0
        while not self._has_resolved:
            console.clear()
            for origin, panel in self._panels.values():
                panel.render(console, origin)
            if self._repositioning_panels:
                console.print_(x=0, y=0, string="Repositioning panels -- press ~ when finished")
            tcod.console_flush()  # Show the console.
            for event in tcod.event.wait(timeout=0.2):
                if event.type == "KEYDOWN" and event.sym == tcod.event.K_BACKQUOTE:
                    self._repositioning_panels = not self._repositioning_panels
                if event.type == "KEYDOWN" and event.sym == tcod.event.K_TAB:
                    delta = -1 if event.mod & tcod.event.KMOD_LSHIFT else 1
                    key = self._focus_list[self._focus_index]
                    self._panels[key][1].unfocus()
                    self._focus_index = (self._focus_index + delta) % len(self._focus_list)
                    key = self._focus_list[self._focus_index]
                    self._panels[key][1].focus()
                if event.type == "QUIT":
                    raise entity.GameplayException("User quit")
                if not self._repositioning_panels:
                    for _, panel in self._panels.values():
                        panel.handle_event(("TCOD", event), self)
                else:
                    if event.type == "KEYDOWN":
                        step = 5 if event.mod & tcod.event.KMOD_LSHIFT else 1
                        pos, pan = self._panels[self._focus_list[self._focus_index]]
                        if event.sym in [tcod.event.K_i, tcod.event.K_KP_8]:
                            pos = (pos[0], pos[1]-step)
                        if event.sym in [tcod.event.K_j, tcod.event.K_KP_4]:
                            pos = (pos[0]-step, pos[1])
                        if event.sym in [tcod.event.K_k, tcod.event.K_KP_2]:
                            pos = (pos[0], pos[1]+step)
                        if event.sym in [tcod.event.K_l, tcod.event.K_KP_6]:
                            pos = (pos[0]+step, pos[1])
                    self._panels[self._focus_list[self._focus_index]] = (pos, pan)
            render_tick = (render_tick + 1) % 100
            settings.current_map.commit()
            if render_tick % 3 == 0:
                director.net_director.propagate_events()
        return self._resolution_value

class Panel:
    def __init__(self):
        self._has_focus = False

    def render(self, console, origin):
        old_fg = console.default_fg
        if self._has_focus:
            console.default_fg = tcod.yellow
        else:
            console.default_fg = tcod.white
        self._render(console, origin)
        console.default_fg = old_fg

    def handle_event(self, event, menu):
        return False

    def focus(self):
        self._has_focus = True

    def unfocus(self):
        self._has_focus = False

class MapPanel(Panel):
    def __init__(self, mapp):
        super().__init__()
        self._map = mapp
        self._look_mode = False
        self._cursor_pos = (0, 0)

    def set_map(self, mapp):
        self._map = mapp

    def render(self, console, origin):
        old_fg = console.default_fg
        if not self._has_focus:
            console.default_fg = tcod.gray
        else:
            console.default_fg = tcod.white
        if self._look_mode:
            self._render_look_mode(console, origin)
        else:
            self._render(console, origin)
        console.default_fg = old_fg

    def _render(self, console, origin):
        x, y = origin
        def render_entity(ent):
            xx, yy = ent.component('Position').get()
            ent_origin = (xx + x, yy + y)
            ent.component('Render').render(ent, console, ent_origin)
        self._map.render(console, origin, None if self._has_focus else tcod.gray)
        self._map.entities().with_all_components(['Render', 'Item', 'Position'])\
                            .transform(render_entity)
        self._map.entities().without_components(['Item']).with_all_components(['Render', 'Position'])\
                            .transform(render_entity)

    def _render_look_mode(self, console, origin):
        x, y = origin
        def render_entity(ent):
            xx, yy = ent.component('Position').get()
            ent_origin = (xx + x, yy + y)
            ent.component('Render').render(ent, console, ent_origin)
        self._map.render(console, origin)
        self._map.entities().with_all_components(['Render', 'Item', 'Position'])\
                            .transform(render_entity)
        self._map.entities().without_components(['Item']).with_all_components(['Render', 'Position'])\
                            .transform(render_entity)
        xx, yy = self._cursor_pos
        console.bg[x+xx][y+yy] = tcod.red

    def _handle_event_look_mode(self, event, menu):
        event_type, event_data = event
        if event_type == 'TCOD' and event_data.type == 'KEYDOWN':
            new_pos = None
            lshift_held = event_data.mod & tcod.event.KMOD_LSHIFT == 1
            step = 5 if lshift_held else 1
            if event_data.sym == tcod.event.K_ESCAPE:
                self._look_mode = False
                return True
            elif event_data.sym in [tcod.event.K_i, tcod.event.K_KP_8]:
                new_pos = (self._cursor_pos[0], self._cursor_pos[1]-step)
            elif event_data.sym in [tcod.event.K_j, tcod.event.K_KP_4]:
                new_pos = (self._cursor_pos[0]-step, self._cursor_pos[1])
            elif event_data.sym in [tcod.event.K_k, tcod.event.K_KP_2]:
                new_pos = (self._cursor_pos[0], self._cursor_pos[1]+step)
            elif event_data.sym in [tcod.event.K_l, tcod.event.K_KP_6]:
                new_pos = (self._cursor_pos[0]+step, self._cursor_pos[1])
            elif event_data.sym in [tcod.event.K_KP_7]:
                new_pos = (self._cursor_pos[0]-step, self._cursor_pos[1]-step)
            elif event_data.sym in [tcod.event.K_KP_9]:
                new_pos = (self._cursor_pos[0]+step, self._cursor_pos[1]-step)
            elif event_data.sym in [tcod.event.K_KP_1]:
                new_pos = (self._cursor_pos[0]-step, self._cursor_pos[1]+step)
            elif event_data.sym in [tcod.event.K_KP_3]:
                new_pos = (self._cursor_pos[0]+step, self._cursor_pos[1]+step)

            w, h = self._map.dimensions()
            if new_pos is not None and new_pos[0] >= 0 and new_pos[1] >= 0 and new_pos[0] < w and new_pos[1] < h:
                self._cursor_pos = new_pos
                under_cursor = settings.current_map.entities().at_position(self._cursor_pos).as_list()
                if len(under_cursor) > 0:
                    menu.panel('EntityStatsPanel')[1].set_entity(under_cursor[0])
                else:
                    menu.panel('EntityStatsPanel')[1].set_entity(None)
            return True

    def handle_event(self, event, menu):
        if not self._has_focus:
            return False
        event_type, event_data = event
        if not self._look_mode:
            if event_type == 'TCOD' and event_data.type == 'KEYDOWN':
                if event_data.sym == tcod.event.K_x:
                    self._cursor_pos = self._map.entity('PLAYER').component('Position').get()
                    self._look_mode = True
                    return True
        elif self._handle_event_look_mode(event, menu):
            return True
        return self._map.entities().for_each_until(lambda ent: ent.handle_event(event, self._map))

class TextPanel(Panel):
    def __init__(self, heading, text="", colour=tcod.white):
        super().__init__()
        self._heading = heading
        self._text = text
        self._colour = colour

    def set_text(self, text, colour=None):
        self._text = text
        if colour is not None:
            self._colour = colour

    def _render(self, console, origin):
        x, y = origin
        console.print_(x=x, y=y, string=self._heading)
        old_fg = console.default_fg
        console.default_fg = self._colour
        x, y = origin
        console.print_(x=x, y=y+1, string=self._text)
        console.default_fg = old_fg

class PlaceFormationOnMapPanel(MapPanel):
    _last_position = None
    _cursor_rotation = 0
   
    def __init__(self, mapp, formation, cursor_position, directional=False, max_range=None, user_position=None):
        import util
        super().__init__(mapp)
        self._formation = formation
        self._cursor_position = cursor_position if directional or user_position is None or \
            PlaceFormationOnMapPanel._last_position is None or \
            (max_range is not None and \
             util.distance(PlaceFormationOnMapPanel._last_position, user_position) > max_range) \
             else PlaceFormationOnMapPanel._last_position
        self._directional = directional
        self._max_range = max_range
        self._user_position = user_position

    def _render(self, console, origin):
        super()._render(console, origin)
        x, y = origin
        in_formation = self._formation.positions_in_formation(self._cursor_position, PlaceFormationOnMapPanel._cursor_rotation, group='x')
        for (xx, yy) in in_formation:
            console.bg[x+xx][y+yy] = tcod.darkest_red
        in_user_movement = self._formation.positions_in_formation(self._cursor_position, PlaceFormationOnMapPanel._cursor_rotation, group='P')
        for (xx, yy) in in_user_movement:
            console.bg[x+xx][y+yy] = tcod.darkest_green

    def _done(self, menu):
        menu.resolve((self._cursor_position, PlaceFormationOnMapPanel._cursor_rotation))

    def _handle_event_directional(self, event, menu):
        if not self._has_focus:
            return False
        event_type, event_data = event
        cx, cy = self._cursor_position
        if event_type == "TCOD" and event_data.type == "KEYDOWN":
            lshift_held = (event_data.mod & tcod.event.KMOD_LSHIFT == 1)
            if event_data.sym in [tcod.event.K_KP_8, tcod.event.K_i]:
                PlaceFormationOnMapPanel._cursor_rotation = 0
                if not lshift_held:
                    self._done(menu)
                return True
            if event_data.sym in [tcod.event.K_KP_2, tcod.event.K_k]:
                PlaceFormationOnMapPanel._cursor_rotation = 2
                if not lshift_held:
                    self._done(menu)
                return True
            if event_data.sym in [tcod.event.K_KP_6, tcod.event.K_l]:
                PlaceFormationOnMapPanel._cursor_rotation = 1
                if not lshift_held:
                    self._done(menu)
                return True
            if event_data.sym in [tcod.event.K_KP_4, tcod.event.K_j]:
                PlaceFormationOnMapPanel._cursor_rotation = 3
                if not lshift_held:
                    self._done(menu)
                return True
            if event_data.sym == tcod.event.K_r:
                PlaceFormationOnMapPanel._cursor_rotation = (PlaceFormationOnMapPanel._cursor_rotation - (1 if lshift_held else -1)) % 4
                return True
            if event_data.sym == tcod.event.K_e:
                self._done(menu)
                return True
            if event_data.sym == tcod.event.K_ESCAPE:
                self._cursor_position = None
                self._cursor_rotation = None
                self._done(menu)
                return True
        return False

    def handle_event(self, event, menu):
        if self._directional:
            return self._handle_event_directional(event, menu)
        else:
            return self._handle_event_nondirectional(event, menu)

    def _handle_event_nondirectional(self, event, menu):
        if not self._has_focus:
            return False
        event_type, event_data = event
        cx, cy = self._cursor_position
        w, h = self._map.dimensions()
        if event_type == "TCOD" and event_data.type == "KEYDOWN":
            lshift_held = (event_data.mod & tcod.event.KMOD_LSHIFT == 1)
            step = 5 if lshift_held else 1
            new_cursor_position = self._cursor_position
            if event_data.sym in [tcod.event.K_KP_8, tcod.event.K_i]:
                new_cursor_position = cx, max(cy - step, 0)
            elif event_data.sym in [tcod.event.K_KP_2, tcod.event.K_k]:
                new_cursor_position = cx, min(cy + step, h - step)
            elif event_data.sym in [tcod.event.K_KP_6, tcod.event.K_l]:
                new_cursor_position = min(cx + step, w - step), cy
            elif event_data.sym in [tcod.event.K_KP_4, tcod.event.K_j]:
                new_cursor_position = max(cx - step, 0), cy
            elif event_data.sym == tcod.event.K_KP_7:
                new_cursor_position = max(cx - step, 0), max(cy - step, 0)
            elif event_data.sym == tcod.event.K_KP_9:
                new_cursor_position = min(cx + step, w - step), max(cy - step, 0)
            elif event_data.sym == tcod.event.K_KP_1:
                new_cursor_position = max(cx - step, 0), min(cy + step, h - step)
            elif event_data.sym == tcod.event.K_KP_3:
                new_cursor_position = min(cx + step, w - step), min(cy + step, h - step)
            elif event_data.sym == tcod.event.K_r:
                PlaceFormationOnMapPanel._cursor_rotation = (PlaceFormationOnMapPanel._cursor_rotation - (1 if lshift_held else -1)) % 4
            elif event_data.sym == tcod.event.K_ESCAPE:
                self._cursor_position = None
                self._cursor_rotation = None
                self._done(menu)
            elif event_data.type == "KEYDOWN" and event_data.sym == tcod.event.K_r:
                self._cursor_rotation = (PlaceFormationOnMapPanel._cursor_rotation - \
                                        (1 if lshift_held else -1)) % 4
                return True
            elif event_data.type == "KEYDOWN" and event_data.sym == tcod.event.K_e:
                menu.resolve((self._cursor_position, PlaceFormationOnMapPanel._cursor_rotation))
                return True
            if self._max_range is None or self._user_position is None or distance(self._user_position, new_cursor_position) <= self._max_range:
                self._cursor_position = new_cursor_position
                PlaceFormationOnMapPanel._last_position = new_cursor_position
            return True
        return False

class MessagePanel(Panel):
    def __init__(self, height):
        super().__init__()
        self._log = []
        self._scroll_y = 0
        self._height = height

    def _max_scroll(self):
        return max(0, len(self._log) - self._height)

    def info(self, msg, colour=tcod.white):
        self._log.append((msg, colour))
        if self._scroll_y == self._max_scroll() - 1:
            self._scroll_y += 1

    def _render(self, console, origin):
        x, y = origin
        yy = 1
        console.print_(x=x, y=y, string="Messages")
        old_fg = console.default_fg
        for msg, colour in self._log[self._scroll_y : self._height + self._scroll_y]:
            console.default_fg = colour
            console.print_(x=x, y=yy+y, string=msg)
            yy += 1
        console.default_fg = old_fg

    def handle_event(self, event, menu):
        if not self._has_focus:
            return False
        event_type, event_data = event
        if event_type == "TCOD" and len(self._log) > 0:
           if event_data.type == "KEYDOWN" and event_data.sym == tcod.event.K_w:
               self._scroll_y = max(self._scroll_y - 1, 0)
           if event_data.type == "KEYDOWN" and event_data.sym == tcod.event.K_s:
               self._scroll_y = min(self._scroll_y + 1, self._max_scroll())

class EquipmentSlotPanel(Panel):
    def __init__(self, entity_ident, mapp):
        super().__init__()
        self._entity_ident = entity_ident
        self._mapp = mapp
        self._selection_index = 0

    def _selected_entity(self):
        entity = self._mapp.entity(self._entity_ident)
        slots = entity.component('EquipmentSlots').slots()
        index = 0
        for slot_type in slots:
            for slot in slots[slot_type]:
                if index == self._selection_index:
                    return slot
                index += 1

    def _selected_slot(self):
        entity = self._mapp.entity(self._entity_ident)
        slots = entity.component('EquipmentSlots').slots()
        index = 0
        for slot_type in slots:
            slot_index = 0
            for slot in slots[slot_type]:
                if index == self._selection_index:
                    return (slot_type, slot_index)
                slot_index += 1
                index += 1
        return None

    def set_map(self, mapp):
        self._mapp = mapp

    def _render(self, console, origin):
        x, y = origin
        yy = 1
        entity = self._mapp.entity(self._entity_ident)
        old_fg = console.default_fg
        console.print_(x=x, y=y, string='Equipment slots')
        slots = entity.component('EquipmentSlots').slots()
        index = 0
        for slot_type in slots:
            for slot in slots[slot_type]:
                if self._selection_index == index and self._has_focus:
                    console.default_fg = tcod.orange
                console.print_(x=x, y=yy+y, string="({})".format(slot_type) if slot is None else slot.component('Item').name())
                console.default_fg = old_fg
                yy += 1
                index += 1

    def handle_event(self, event, menu):
        if not self._has_focus:
            return False
        entity = self._mapp.entity(self._entity_ident)
        equipment_slots = entity.component('EquipmentSlots')
        slots_size = sum(len(v) for v in equipment_slots.slots().values())
        event_type, event_data = event
        if event_type == "TCOD" and slots_size > 0:
            if event_data.type == "KEYDOWN" and event_data.sym in [tcod.event.K_KP_8, tcod.event.K_i]:
                self._selection_index = max(self._selection_index - 1, 0)
            if event_data.type == "KEYDOWN" and event_data.sym in [tcod.event.K_KP_2, tcod.event.K_k]:
                self._selection_index = min(self._selection_index + 1, slots_size-1)
            if event_data.type == "KEYDOWN" and event_data.sym == tcod.event.K_e:
                item_ent = self._selected_entity()
                if item_ent is None:
                    return False
                equipment_slots.unequip(entity, item_ent, self._selected_slot(), settings.current_map)
        item_ent = self._selected_entity()
        menu.panel('EntityStatsPanel')[1].set_entity(item_ent)
        menu.panel('ModSlotPanel')[1].set_entity(item_ent)

class ModSlotPanel(Panel):
    def __init__(self, equipment_entity):
        super().__init__()
        self._equipment_entity = equipment_entity
        self._selection_index = 0

    def set_entity(self, equipment_entity):
        self._equipment_entity = equipment_entity

    def _render(self, console, origin):
        x, y = origin
        yy = 1
        old_fg = console.default_fg
        console.print_(x=x, y=y, string='Mod slots')
        if self._equipment_entity is None or self._equipment_entity.component('Equipment') is None:
            return
        slots = self._equipment_entity.component('Equipment').mod_slots()
        index = 0
        for mod in slots:
            if self._selection_index == index and self._has_focus:
                console.default_fg = tcod.orange
            if mod is not None:
                mod.component('Render').render(mod, console, (x, yy+y))
            console.print_(x=x+2, y=yy+y, string="(Empty)" if mod is None else mod.component('Item').name())
            console.default_fg = old_fg
            yy += 1
            index += 1

    def _selected_entity(self):
        equipment = self._equipment_entity.component('Equipment')
        mod_slots = equipment.mod_slots()
        if self._selection_index >= len(mod_slots):
            return None
        return mod_slots[self._selection_index]

    def handle_event(self, event, menu):
        if not self._has_focus or not self._equipment_entity:
            return False
        equipment = self._equipment_entity.component('Equipment')
        mod_slots = equipment.mod_slots()
        event_type, event_data = event
        if event_type == "TCOD" and len(mod_slots) > 0:
            if event_data.type == "KEYDOWN" and event_data.sym in [tcod.event.K_KP_8, tcod.event.K_i]:
                self._selection_index = max(self._selection_index - 1, 0)
            if event_data.type == "KEYDOWN" and event_data.sym in [tcod.event.K_KP_2, tcod.event.K_k]:
                self._selection_index = min(self._selection_index + 1, len(mod_slots)-1)
        item_ent = self._selected_entity()
        if menu.panel('EntityStatsPanel') is not None:
            menu.panel('EntityStatsPanel')[1].set_entity(item_ent)

class ChooseModSlotPanel(ModSlotPanel):
    def __init__(self, equipment_entity):
        super().__init__(equipment_entity)

    def _finalise_selection(self, menu):
        menu.resolve(self._selection_index)

    def _cancel_selection(self, menu):
        menu.resolve()

    def handle_event(self, event, menu):
        if not self._has_focus:
            return False
        super().handle_event(event, menu)
        if self._equipment_entity is None:
            print("ChooseModSlotPanel: equipment_entity is None")
            return
        equipment = self._equipment_entity.component('Equipment')
        slots = equipment.mod_slots()
        event_type, event_data = event
        if event_type == "TCOD" and event_data.type == "KEYDOWN":
           if event_data.sym == tcod.event.K_e:
               self._finalise_selection(menu)
               return
           elif event_data.sym == tcod.event.K_ESCAPE:
               self._cancel_selection(menu)

class ChooseEquipmentSlotPanel(EquipmentSlotPanel):
    def _finalise_selection(self, menu):
        entity = self._mapp.entity(self._entity_ident)
        slots = entity.component('EquipmentSlots').slots()
        index = 0
        for slot_type in slots:
            slot_index = 0
            for slot in slots[slot_type]:
                if index == self._selection_index:
                    menu.resolve((slot_type, slot_index))
                    return
                index += 1
                slot_index += 1
        menu.resolve()

    def _cancel_selection(self, menu):
        menu.resolve()

    def handle_event(self, event, menu):
        if not self._has_focus:
            return False
        entity = self._mapp.entity(self._entity_ident)
        equipment_slots = entity.component('EquipmentSlots')
        slots_size = sum(len(v) for v in equipment_slots.slots().values())
        event_type, event_data = event
        if event_type == "TCOD" and slots_size > 0:
           if event_data.type == "KEYDOWN" and event_data.sym in [tcod.event.K_i, tcod.event.K_KP_8]:
               self._selection_index = max(self._selection_index - 1, 0)
           if event_data.type == "KEYDOWN" and event_data.sym in [tcod.event.K_k, tcod.event.K_KP_2]:
               self._selection_index = min(self._selection_index + 1, slots_size-1)
           if event_data.type == "KEYDOWN" and event_data.sym == tcod.event.K_e:
               self._finalise_selection(menu)
               return
           if event_data.type == "KEYDOWN" and event_data.sym == tcod.event.K_ESCAPE:
               self._cancel_selection(menu)

class InventoryPanel(Panel):
    def __init__(self, entity_ident, mapp, console):
        super().__init__()
        self._entity_ident = entity_ident
        self._mapp = mapp
        self._console = console
        self._selection_index = 0
        self._bindings = {}
        self._bindings_disabled = False

    def set_key_bind(self, tcod_keysym, index):
        self._bindings[tcod_keysym] = index

    def set_map(self, mapp):
        self._mapp = mapp

    def focus(self):
        super().focus()
        settings.root_menu.panel('EntityStatsPanel')[1].set_entity(None)
        settings.root_menu.panel('ModSlotPanel')[1].set_entity(None)
        self._bindings_disabled = True

    def unfocus(self):
        super().unfocus()
        settings.root_menu.panel('EntityStatsPanel')[1].set_entity(None)
        settings.root_menu.panel('ModSlotPanel')[1].set_entity(None)
        self._bindings_disabled = False

    def set_entity_ident(self, entity_ident):
        self._entity_ident = entity_ident

    def _render(self, console, origin):
        x, y = origin
        yy = 1
        old_fg = console.default_fg
        console.print_(x=x, y=y, string='Inventory')
        entity = self._mapp.entity(self._entity_ident)
        if entity is None:
            return
        itms = entity.component('Inventory').items().as_list()
        index = 0
        for ent in itms:
            ent_origin = (x, yy + y)
            console.default_fg = tcod.cyan if (self._has_focus and self._selection_index == index) else \
                                 tcod.orange if index in self._bindings.values() else \
                                 console.default_fg

            if index in self._bindings.values():
                sym = [k for k in self._bindings if self._bindings[k] == index][0]
                console.print_(x=x, y=yy+y, string=self._key_name(sym))
            else:
                ent.component('Render').render(ent, console, ent_origin)
            console.print_(x=x+2, y=yy+y, string=ent.component('Item').name())
            console.default_fg = old_fg
            yy += 1
            index += 1

    def _remove_binding_for(self, index):
        removed_key = None
        for key, b_index in self._bindings.items():
            if b_index == index:
                removed_key = key
            elif b_index > index:
                self._bindings[key] -= 1
        if removed_key is not None:
            self._bindings.pop(removed_key, None)

    def _disable_bindings(self):
        self._bindings_disabled = True

    def _enable_bindings(self):
        self._bindings_disabled = False

    def _key_name(self, sym):
        return str(sym - tcod.event.K_0)

    def _use_item(self, index, menu):
        entity = self._mapp.entity(self._entity_ident)
        inventory = entity.component('Inventory')
        item_ent = inventory.items().as_list()[index]
        usable = item_ent.component('Usable')
        is_paralyzed = entity.component('Stats').has_status('PARALYZE')
        if usable is not None and not is_paralyzed:
            remove = usable.use(item_ent, entity, self._mapp, menu)
            if remove:
                self._remove_binding_for(index)
                inventory.remove(item_ent)
                return True
        self._mapp.end_turn()
        return False

    def handle_event(self, event, menu):
        # Run key bindings
        event_type, event_data = event
        if not self._bindings_disabled and event_type == "TCOD" and event_data.type == "KEYDOWN":
            binding = self._bindings.get(event_data.sym)
            if binding is not None:
                self._use_item(binding, menu)
                return True
       
        if not self._has_focus:
            return False
       
        entity = self._mapp.entity(self._entity_ident)
        if not entity:
            return False
        inventory = entity.component('Inventory')
        inventory_size = inventory.items().size()
        if event_type == "TCOD" and event_data.type == "KEYDOWN" and inventory_size > 0:
            items = inventory.items().as_list()
            item_ent = items[self._selection_index] if self._selection_index < len(items) else None
            lshift_held = event_data.mod & tcod.event.KMOD_LSHIFT == 1
            step = 5 if lshift_held else 1
            if event_data.sym in [tcod.event.K_KP_8, tcod.event.K_i]:
                self._selection_index = max(self._selection_index - step, 0)
                item_ent = items[self._selection_index] if self._selection_index < len(items) else None
                settings.root_menu.panel('EntityStatsPanel')[1].set_entity(item_ent)
                settings.root_menu.panel('ModSlotPanel')[1].set_entity(item_ent)
                menu.panel('HelpPanel')[1].set_text(item_ent.component('Item').description())
                return True
            elif event_data.sym in [tcod.event.K_KP_2, tcod.event.K_k]:
                self._selection_index = min(self._selection_index + step, inventory_size-1)
                item_ent = items[self._selection_index] if self._selection_index < len(items) else None
                settings.root_menu.panel('EntityStatsPanel')[1].set_entity(item_ent)
                settings.root_menu.panel('ModSlotPanel')[1].set_entity(item_ent)
                menu.panel('HelpPanel')[1].set_text(item_ent.component('Item').description())
                return True
            elif event_data.sym == tcod.event.K_d:
                item_ent = inventory.items().as_list()[self._selection_index]
                position = entity.component("Position").get()
                self._remove_binding_for(self._selection_index)
                inventory.drop(entity, item_ent, self._mapp, position)
                self._selection_index = max(self._selection_index - 1, 0)
                return True
            elif event_data.sym == tcod.event.K_f:
                res = self._use_item(self._selection_index, menu)
                if res:
                    self._selection_index = max(self._selection_index - 1, 0)
                return True
            elif event_data.sym >= tcod.event.K_0 and event_data.sym <= tcod.event.K_9:
                key = event_data.sym
                self.set_key_bind(key, self._selection_index)
            if event_data.sym == tcod.event.K_e:
                if item_ent.component('Equipment') is not None:
                    equipment_slots = entity.component('EquipmentSlots')
                    choose_slot_menu = Menu({
                        'ChooseEquipmentSlotPanel': ((0,0), ChooseEquipmentSlotPanel(self._entity_ident, self._mapp))
                    }, ['ChooseEquipmentSlotPanel'])
                    chosen_slot = choose_slot_menu.run(self._console)
                    if chosen_slot is not None:
                        equipment_slots.equip(entity, item_ent, chosen_slot, self._mapp)
                        self._selection_index -= 1
                    return True
                elif item_ent.component('Mod') is not None:
                    choose_item_menu = Menu({
                        'ChooseItemPanel': ((0,0), ChooseItemPanel(entity, ['Equipment']))
                    }, ['ChooseItemPanel'])
                    chosen_item = choose_item_menu.run(self._console)
                    if chosen_item is None or len(chosen_item.component('Equipment').mod_slots()) == 0:
                        return True
                    choose_mod_slot_menu = Menu({
                        'ChooseModSlotPanel': ((0,0), ChooseModSlotPanel(chosen_item))
                    }, ['ChooseModSlotPanel'])
                    chosen_slot_index = choose_mod_slot_menu.run(self._console)
                    if chosen_slot_index is None:
                        return True
                    chosen_item.component('Equipment').attach_mod(chosen_item, item_ent, chosen_slot_index, self._mapp)
                    self._selection_index = max(self._selection_index - 1, 0)
                    self._remove_binding_for(self._selection_index)
                    inventory.remove(item_ent)
                    return True
                return False
            item_ent = items[self._selection_index] if self._selection_index < len(items) else None
            menu.panel('EntityStatsPanel')[1].set_entity(item_ent)
            menu.panel('ModSlotPanel')[1].set_entity(item_ent)
            menu.panel('HelpPanel')[1].set_text(item_ent.component('Item').description())
        return False

class ChooseItemPanel(Panel):
    def __init__(self, entity, with_all_components=[], title="Choose an item"):
        self._entity = entity
        self._with_all_components = with_all_components
        self._selection_index = 0
        self._title = title

    def handle_event(self, event, menu):
        event_type, event_data = event
        inventory = self._entity.component('Inventory')
        inventory_size = inventory.items().size()
        eligible_items = inventory.items().with_all_components(self._with_all_components).as_list()
        if event_type == "TCOD" and event_data.type == "KEYDOWN" and inventory_size > 0:
            selected_item = inventory.items().as_list()[self._selection_index]
            if event_data.sym in [tcod.event.K_KP_8, tcod.event.K_i]:
                self._selection_index = max(self._selection_index - 1, 0)
                return True
            elif event_data.sym in [tcod.event.K_KP_2, tcod.event.K_k]:
                self._selection_index = min(self._selection_index + 1, inventory_size-1)
                return True
            elif event_data.sym == tcod.event.K_e and selected_item in eligible_items:
                menu.resolve(selected_item)
                return True
            elif event_data.sym == tcod.event.K_ESCAPE:
                menu.resolve()
                return True
        return False

    def _render(self, console, origin):
        old_fg = console.default_fg
        inventory = self._entity.component('Inventory')
        items = inventory.items().as_list()
        index = 0
        x, y = origin
        yy = 0
        console.print_(x=x, y=yy+y, string=self._title)
        yy += self._title.count("\n") + 1
        for item in items:
            console.default_fg = tcod.cyan if self._has_focus and self._selection_index == index else console.default_fg
            item.component('Render').render(item, console, (x,yy+y))
            console.print_(x=x+2, y=yy+y, string=item.component('Item').name())
            console.default_fg = old_fg
            yy += 1
            index += 1

class StatsPanel(Panel):
    def __init__(self, mapp, entity_ident):
        super().__init__()
        self._mapp = mapp
        self._entity_ident = entity_ident
        self._page = 0

    def _keys(self, entity):
        import entity as entity_module
        stats = entity.component('Stats')
        all_stats = entity_module.Stats.all_stats - \
            entity_module.Stats.primary_stats - \
            entity_module.Stats.cur_stats - \
            entity_module.Stats.resistance_stats - \
            set(['level', 'max_exp'])
        resistances = entity_module.Stats.resistance_stats
        shown_stats = all_stats - set([s for s in all_stats if stats.get(s) == 0])
        return ['atk', 'dfn', 'itl', 'res', 'spd', 'hit'] + sorted(list(resistances)) + [None] * 2 + sorted(list(shown_stats))

    def set_map(self, mapp):
        self._mapp = mapp

    def _name(self, entity):
        item = entity.component('Item')
        npc = entity.component('NPC')
        player = entity.component('PlayerLogic')
        if item is not None:
            return item.name()
        if npc is not None:
            return npc.name()
        if player is not None:
            return 'Player'
        return 'Unknown object'

    def _get_entity(self):
        return self._mapp.entity(self._entity_ident)

    def _render(self, console, origin):
        import entity as entity_module
        page = self._page
        x, y = origin
        console.print_(x=x, y=y, string="Statistics")
        y = y + 1
        entity = self._get_entity()
        if entity is None:
            return
        stats = entity.component('Stats')
        keys = self._keys(entity)
        console.print_(x=x, y=y, string=self._name(entity))
        y = y + 1
        console.print_(x=x, y=y, string="Level : " + abbrev(stats.get_value('level')))
        y = y + 1
        old_fg = console.default_fg
        if stats.get_value('max_hp') > 0:
            ratio = stats.get_value('cur_hp') / stats.get_value('max_hp')
            if ratio < 0.25:
                console.default_fg = tcod.red
            elif ratio < 1.0:
                console.default_fg = tcod.yellow
        console.print_(x=x, y=y, string="HP : " + abbrev(stats.get_value('cur_hp')) + " / " + abbrev(stats.get_value('max_hp')))
        console.default_fg = old_fg
        y = y + 1
        if stats.get_value('max_sp') > 0:
            ratio = stats.get_value('cur_sp') / stats.get_value('max_sp')
            if ratio < 0.25:
                console.default_fg = tcod.red
            elif ratio < 1.0:
                console.default_fg = tcod.yellow
        console.print_(x=x, y=y, string="SP : " + abbrev(stats.get_value('cur_sp')) + " / " + abbrev(stats.get_value('max_sp')))
        console.default_fg = old_fg
        y = y + 1
        for key in keys[(page*6):(page*6+6)]:
            if key is not None:
                label = key.upper()
                value = stats.get_value(key)
                console.print_(x=x, y=y, string=label + ": " + abbrev(value))
            y = y + 1

    def handle_event(self, event, menu):
        import entity as entity_module
        if not self._has_focus:
            return False
        event_type, event_data = event
        if event_type == 'TCOD' and event_data.type == 'KEYDOWN' and self._get_entity() is not None:
            if event_data.sym in [tcod.event.K_KP_4, tcod.event.K_j]:
                self._page = max(self._page-1, 0)
            elif event_data.sym in [tcod.event.K_KP_6, tcod.event.K_l]:
                self._page = min(self._page+1, math.ceil(len(self._keys(self._get_entity()))/6)-1)
        return True


class EntityStatsPanel(StatsPanel):
    def __init__(self, entity=None):
        super().__init__(None, None)
        self._entity = entity

    def set_entity(self, entity):
        self._entity = entity

    def _get_entity(self):
        return self._entity

class TextInputPanel(TextPanel):
    def handle_event(self, event, menu):
        if not self._has_focus:
            return False
        event_type, event_data = event
        if event_type == 'TCOD' and event_data.type == 'KEYDOWN' and event_data.sym in [tcod.event.K_ESCAPE]:
            menu.resolve(None)
            return True
        if event_type == 'TCOD' and event_data.type == 'KEYDOWN' and event_data.sym in [tcod.event.K_RETURN]:
            menu.resolve(self._text)
            return True
        if event_type == 'TCOD' and event_data.type == 'KEYDOWN' and event_data.sym in [tcod.event.K_BACKSPACE]:
            self._text = self._text[:-1]
            return True
        if event_type == 'TCOD' and event_data.type == 'TEXTINPUT':
            self._text += event_data.text
            return True

def text_prompt(prompt):
    text_input_menu = Menu({
        'TextInputPanel': ((0,0), TextInputPanel(prompt))
    }, ['TextInputPanel'])
    result = text_input_menu.run(settings.root_console)
    return result
