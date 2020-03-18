#!/usr/bin/env python
import entity
import random
from util import *

class AIState:
    def __init__(self):
        # Handlers are of the type: (AIState, Entity, AI, EventData) -> Boolean
        self._handlers = {}
        self._turns_in_state = 0

    def handle_event(self, entity, ai, event):
        event_type, event_data = event
        if event_type in self._handlers:
            if event_type == 'NPC_TURN':
                self._turns_in_state += 1
            for handler in self._handlers[event_type]:
                should_stop = handler(self, entity, ai, event_data)
                if should_stop:
                    break

    def _add_handler(self, event_type, handler):
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)

    def reset_turns_in_state(self):
        self._turns_in_state = 0

    # Factory methods

    def every_n_turns(self, n, handler, should_stop=True):
        def f(self, entity, ai, event_data):
            stats = entity.component('Stats')
            if self._turns_in_state % n == 0:
                handler(entity, ai, event_data)
                return should_stop
            return False
        self._add_handler('NPC_TURN', f)
        return self

    def after_n_turns(self, num_turns, handler, should_stop=True):
        def f(self, entity, ai, event_data):
            stats = entity.component('Stats')
            if self._turns_in_state == num_turns:
                handler(entity, ai, event_data)
                return should_stop
            return False
        self._add_handler('NPC_TURN', f)
        return self

    def when_under_proportion_hp(self, proportion, handler, should_stop=True):
        def f(self, entity, ai, event_data):
            stats = entity.component('Stats')
            hp_prop = stats.get('cur_hp') / stats.get('max_hp')
            if hp_prop < proportion:
                handler(entity, ai, event_data)
                return should_stop
            return False
        self._add_handler('NPC_TURN', f)
        return self

    def when_player_within_distance(self, distance, handler, should_stop=True):
        def f(self, entity, ai, event_data):
            if ai.distance_to_player(entity) <= distance:
                handler(entity, ai, event_data)
                return should_stop
            return False
        self._add_handler('NPC_TURN', f)
        return self

    def when_player_beyond_distance(self, distance, handler, should_stop=True):
        def f(self, entity, ai, event_data):
            if ai.distance_to_player(entity) > distance:
                handler(entity, ai, event_data)
                return should_stop
            return False
        self._add_handler('NPC_TURN', f)
        return self

    def when_damaged(self, handler, should_stop=True):
        def f(self, entity, ai, event_data):
            target, amount = event_data
            if target.ident() == entity.ident():
                handler(entity, ai, event_data)
                return should_stop
            return False
        self._add_handler('DAMAGE_DEALT', f)
        return self

    def when_killed(self, handler, should_stop=True):
        def f(self, entity, ai, event_data):
            if event_data.ident() == entity.ident():
                handler(entity, ai, event_data)
                return should_stop
            return False
        self._add_handler('ENTITY_KILLED', f)
        return self

    def on_turn_randomly(self, proportion, handler, should_stop=True):
        def f(self, entity, ai, event_data):
            roll = random.randint(0, 1000)
            if roll / 1000 <= proportion:
                handler(entity, ai, event_data)
                return should_stop
            return False
        self._add_handler('NPC_TURN', f)
        return self


    def on_turn_otherwise(self, handler, should_stop=True):
        def f(self, entity, ai, event_data):
            handler(entity, ai, event_data)
            return should_stop
        self._add_handler('NPC_TURN', f)
        return self


class AI(entity.Component):
    def __init__(self, initial_state='IDLE'):
        self._current_state = initial_state
        self._states = {}
        self._skills = {}
        self._blackboard = {}
        self._delayed_attack = None
        self._delay = None
        self._delayed_targets = None
        self._passive_attacks = [] # Items of the form (usable, delay, (entitylistview, [positions]))

    def bb_get(self, key):
        return self._blackboard.get(key)

    def bb_set(self, key, value):
        old_value = self.bb_get(key)
        self._blackboard[key] = value
        return old_value

    def change_state(self, new_state):
        old_state = self._current_state
        self._current_state = new_state
        self._states[self._current_state].reset_turns_in_state()
        return old_state

    def handle_event(self, entity, event, resident_map):
        event_type, event_data = event
        is_paralyzed = entity.component('Stats').has_status('PARALYZE')

        # Remove this creature's threatened positions after they die
        if event_type == 'ENTITY_KILLED' and event_data == entity and self._delayed_targets is not None:
            targeted_positions = self._delayed_targets[1]
            resident_map.remove_threatened_positions(entity.ident())
            return False

        if event_type == 'NPC_TURN':
            self._handle_passive_attacks(entity, resident_map)
            if is_paralyzed:
                return False
            elif self._delayed_attack is not None:
                if self._handle_delayed_attack(entity, resident_map) is False:
                    return False

        # If no delayed attack, get action from state instead
        state = self._states.get(self._current_state)
        if state is not None:
            return state.handle_event(entity, self, event)
        return False

    def _handle_passive_attacks(self, entity, resident_map):
        new_passive_attacks = []
        for passive_attack, delay, passive_targets in self._passive_attacks:
            delay -= 1
            if delay == 0:
                targeted_positions = passive_targets[1]
                # TODO: make this work with / without friendly fire
                targets = resident_map.entities().without_components(['Item', 'NPC'])\
                                                 .with_component('Position')\
                                                 .where(lambda ent: ent.component('Position').get() in targeted_positions), targeted_positions
                passive_attack.use_on_targets(entity, entity, resident_map, targets, None)
            else:
                new_passive_attacks.append((passive_attack, delay, passive_targets))
        self._passive_attacks = new_passive_attacks
        return False

    def _handle_delayed_attack(self, entity, resident_map):
        self._delay -= 1
        if self._delay > 0:
            return False
        targeted_positions = self._delayed_targets[1]
        # TODO: make this work with / without friendly fire
        targets = resident_map.entities().without_components(['Item', 'NPC'])\
                                         .with_component('Position')\
                                         .where(lambda ent: ent.component('Position').get() in targeted_positions), targeted_positions
        self._delayed_attack.use_on_targets(entity, entity, resident_map, targets, None)
        self._delay = None
        self._delayed_attack = None
        return False

    # Helpers

    def step_towards_player(self, entity):
        import settings
        passmap = settings.current_map.passability_map_for(entity)
        player = settings.current_map.entity('PLAYER')
        player_pos = player.component('Position').get()
        ent_pos = entity.component('Position').get()
        path = find_path(passmap, ent_pos, player_pos)
        if len(path) > 1 and not player_pos == path[1]:
            entity.component('Position').set(path[1][0], path[1][1])

    def step_away_from_player(self, entity):
        import settings
        passmap = settings.current_map.passability_map_for(entity)
        player = settings.current_map.entity('PLAYER')
        player_pos = player.component('Position').get()
        ent_pos = entity.component('Position').get()
        (x, y) = ent_pos
        dx, dy = (player_pos[0] - ent_pos[0], player_pos[1] - ent_pos[1])
        dx, dy = (-1 if dx < 0 else 1 if dx > 0 else 0, -1 if dy < 0 else 1 if dy > 0 else 0)
        if settings.current_map.is_passable_for(entity, (x-dx, y-dy)):
            entity.component('Position').sub(x=dx, y=dy)

    def step_randomly(self, entity):
        import settings
        x, y = entity.component('Position').get()
        possible_steps = [(dx, dy) for dx in range(-1, 2) for dy in range(-1, 2) \
                          if settings.current_map.is_passable_for(entity, (x+dx, y+dy))]
        if len(possible_steps) != 0:
            dx, dy = random.choice(possible_steps)
            entity.component('Position').add(x=dx, y=dy)

    def distance_to_player(self, entity):
        import settings
        player = settings.current_map.entity('PLAYER')
        my_position = entity.component('Position').get()
        player_position = player.component('Position').get()
        return distance(player_position, my_position)

    def perform_attack_against(self, entity, target):
        import settings
        my_combat = entity.component('Combat')
        my_combat.attack(entity, settings.current_map, target.component('Position').get())

    '''
    Delayed attacks delay other actions (e.g. movement, other attacks, etc.)
    aside from passive attacks until they are performed.
    '''
    def perform_delayed_attack_against(self, entity, target, usable, delay):
        import settings
        if delay == 0:
            usable.use(entity, entity, settings.current_map, None)
            return
        self._delayed_attack = usable
        self._delay = delay
        self._delayed_targets = usable.choose_targets(entity, entity, settings.current_map, None)
        settings.current_map.add_threatened_positions(self._delayed_targets[1], delay, entity.ident())

    '''
    Passive attacks can be performed even whilst performing other actions such
    as moving, using delayed attacks, etc.
    '''
    def perform_passive_attack_against(self, entity, target, usable, delay):
        import settings
        if delay == 0:
            usable.use(entity, entity, settings.current_map, None)
            return
        passive_targets = usable.choose_targets(entity, entity, settings.current_map, None)
        self._passive_attacks.append((usable, delay, passive_targets))
        settings.current_map.add_threatened_positions(passive_targets[1], delay, entity.ident())

    # Factory methods

    def use_skill(self, entity, skill_ident):
        import settings
        usable, delay, is_passive = self._skills[skill_ident]
        player = settings.current_map.entity('PLAYER')
        if is_passive:
            self.perform_passive_attack_against(entity, player, usable, delay)
        else:
            self.perform_delayed_attack_against(entity, player, usable, delay)

    def add_skill(self, skill_ident, usable, delay=0, is_passive=False):
        self._skills[skill_ident] = usable, delay, is_passive
        return self

    def with_state(self, state_name, state):
        self._states[state_name] = state
        return self
