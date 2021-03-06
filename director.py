#!/usr/bin/env python
import loot
import monster
import settings
import socket
from map import *

class MapDirector:
    ITEM_WORLD_TURN_LIMIT = 300
    MAIN_DUNGEON_TURN_LIMIT = 300

    def __init__(self):
        self._current_floor = 0
        self._item_world = None # item_world = none indicates we are in the main dungeon

    def current_map_name(self):
        if self._current_floor == 0:
            return "Town"
        if self._current_floor == -1:
            return "Grimmsville"
        if self._item_world is None:
            return f"Dungeon {self._current_floor}"
        if self._item_world is not None:
            item_name = self._item_world.component('Item').name()
            return f"{item_name} World {self._current_floor}"

    def set_item_world(self, item):
        self._item_world = item

    def _item_world_map(self, level):
        w,h=30,30
        if self._current_floor == 10:
            mapp = TheTowerArena(w, h)
        else:
            mvd = None if random.randint(0, 6) < 4 else random.randint(3, 8)
            roll = random.randint(0,8)
            if roll in range(0, 1):
                mapp = Ring(w, h, turn_limit=MapDirector.ITEM_WORLD_TURN_LIMIT, max_view_distance=mvd)
            elif roll in range(1, 2):
                mapp = Rooms(w, h, turn_limit=MapDirector.ITEM_WORLD_TURN_LIMIT, max_view_distance=mvd)
            elif roll in range(2, 3):
                mapp = Checkerboard(w, h, turn_limit=MapDirector.ITEM_WORLD_TURN_LIMIT, max_view_distance=mvd)
            elif roll in range(3, 4):
                mapp = Posts(w, h, turn_limit=MapDirector.ITEM_WORLD_TURN_LIMIT, max_view_distance=mvd)
            elif roll in range(5, 6):
                mapp = TwoRooms(w, h, turn_limit=MapDirector.ITEM_WORLD_TURN_LIMIT, max_view_distance=mvd)
            else:
                mapp = Grid(w, h, turn_limit=MapDirector.ITEM_WORLD_TURN_LIMIT, max_view_distance=mvd)
        return mapp, w, h

    def _spawn_the_tower(self, level, mapp):
        import entity
        width, height = mapp.dimensions()
        the_tower = monster.BossTheTower.generator(tier=settings.monster_tier, level=level)((width // 2, 5))
        mapp.add_entity(the_tower)
        for _ in range(10):
            the_tower_minion = monster.BossTheTowerMinion.generator(tier=settings.monster_tier, level=level)((12, 12))
            x, y = mapp.random_passable_position_for(the_tower_minion)
            the_tower_minion.component('Position').set(x, y)
            mapp.add_entity(the_tower_minion)

    def _spawn_ultimate_beholder(self, level, mapp):
        import entity
        beholder_boss = monster.BossUltimateBeholder.generator(tier=settings.monster_tier, level=level)((15,15))
        x, y = mapp.random_passable_position_for(beholder_boss)
        beholder_boss.component('Position').set(x, y)
        mapp.add_entity(beholder_boss)
        for _ in range(6):
            bhld = monster.Eye.generator(tier=settings.monster_tier, level=level)((3,3))
            x, y = mapp.random_passable_position_for(bhld)
            bhld.component('Position').set(x, y)
            bhld.set_component('UltimateBeholderAdd', entity.Combat())
            mapp.add_entity(bhld)

    def _spawn_the_sneak(self, level, mapp):
        import entity
        the_sneak_boss = monster.BossTheSneak.generator(tier=settings.monster_tier, level=level)((15,15))
        x, y = mapp.random_passable_position_for(the_sneak_boss)
        the_sneak_boss.component('Position').set(x, y)
        mapp.add_entity(the_sneak_boss)

    def _spawn_minotaur(self, level, mapp):
        import entity
        minotaur_boss = monster.BossMinotaur.generator(tier=settings.monster_tier, level=level)((15,15))
        mapp.add_entity(minotaur_boss)
        for _ in range(3):
            fake_wall = monster.MinotaurWall((3,3))
            x, y = mapp.random_passable_position_for(fake_wall)
            fake_wall.component('Position').set(x, y)
            fake_wall.set_component('MinotaurWall', entity.Combat())
            mapp.add_entity(fake_wall)

    def _main_dungeon_map(self, level):
        mapp = Grid(30,30)
        w,h=30,30
        if self._current_floor == -1:
            mapp = Grimmsville(30, 30, [monster.UptierShopNPC, monster.MultiplayerItemNPC, monster.ItemEnhancerNPC] + [monster.GrimmsvilleSkeleton] * 12)
            w,h=30,30
        elif self._current_floor == 0:
            mapp = Town(30, 30, [monster.MailmanNPC, monster.ItemWorldClerkNPC, monster.ModShopNPC, monster.EquipmentShopNPC, monster.SkillShopNPC, monster.FoodShopNPC])
            w,h=30,30
        elif self._current_floor == 10:
            mapp = TheSneakArena(30, 30)
            w,h=30,30
        elif self._current_floor == 20:
            mapp = BeholderArena(30, 30)
            w,h=30,30
        elif self._current_floor == 30:
            mapp = Labyrinth(30, 30, max_view_distance=5)
            w,h=30,30
        elif self._current_floor % 5 == 0:
            mapp = TwoRooms(30, 30, room_size=9, turn_limit=MapDirector.MAIN_DUNGEON_TURN_LIMIT)
            w,h=30,30
        elif self._current_floor in range(0, 5):
            mapp = Cave(30, 30, turn_limit=MapDirector.MAIN_DUNGEON_TURN_LIMIT)
            w,h=30,30
        elif self._current_floor % 10 == 1:
            mapp = Corridors(30, 30, room_size=5, turn_limit=MapDirector.MAIN_DUNGEON_TURN_LIMIT)
            w,h=30,30
        elif self._current_floor in range(5, 10):
            mapp = Rivers(w, h, turn_limit=MapDirector.MAIN_DUNGEON_TURN_LIMIT)
            w,h=30,30
        return mapp, w, h

    def vault(self, difficulty):
        """
        Returns a random, difficulty-appropriate vault.
        """
        import vault

        vaults = [
            vault.beehive.BeehiveVault(difficulty),
            vault.rooms.RoomsAVault(difficulty),
            vault.rooms.RoomsBVault(difficulty),
            vault.rooms.RoomsCVault(difficulty),
            vault.rooms.RoomsDVault(difficulty),
        ]

        return random.choice(vaults)

    def map(self, level):
        if self._item_world is not None:
            mapp, w, h = self._item_world_map(level)
        else:
            mapp, w, h = self._main_dungeon_map(level)

        if self._current_floor <= 0 and self._item_world is None:
            return mapp

        difficulty = self.difficulty()

        # Add vaults
        n_vaults = random.randint(0, 3)
        for _ in range(n_vaults):
            vault = self.vault(difficulty)
            position = (random.randint(1, w-2), random.randint(1, h-2))
            mapp.add_vault(vault, position)

        # Add items
        n_items = random.randint(2, 7)
        for _ in range(n_items):
            item = loot_director.ground_loot(level)
            x, y = random.randint(0, w-1), random.randint(0,h-1)
            while not mapp.is_passable_for(item((0,0)), (x, y)):
                x, y = random.randint(0, w-1), random.randint(0,h-1)
            mapp.add_entity(item((x, y)))

        if self._item_world is None:
            if self._current_floor == 10:
                self._spawn_the_sneak(level, mapp)
                return mapp
            elif self._current_floor == 20:
                self._spawn_ultimate_beholder(level, mapp)
                return mapp
            elif self._current_floor == 30:
                self._spawn_minotaur(level, mapp)
                return mapp
        else:
            if self._current_floor == 10:
                self._spawn_the_tower(level, mapp)
                return mapp

        if difficulty < 15:
            n_monst = random.randint(2, 5)
        else:
            n_monst = random.randint(5, 10)
        
        monster_set = monster_director.choose_random_monster_set(difficulty, random.randint(1, 3))
        for _ in range(n_monst):
            monst = monster_director.monster_from_set(level, monster_set)
            x, y = random.randint(0, w-1), random.randint(0,h-1)
            while not mapp.is_passable_for(monst((0,0)), (x, y)):
                x, y = random.randint(0, w-1), random.randint(0,h-1)
            mapp.add_entity(monst((x, y)))
        return mapp

    def difficulty(self):
        if self._item_world == None:
            return math.floor(3 + (self._current_floor - 1) * 4)
        else:
            import entity
            stats = self._item_world.component('Stats')
            primaries = entity.Stats.primary_stats - set(['max_hp', 'max_sp', 'max_hunger'])
            tot = sum([stats.get_base(stat) for stat in primaries])
            return 3 + (self._current_floor - 1) * 3 + math.floor(tot / 3)

    def _change_floor(self):
        if self._item_world is None:
            settings.main_dungeon_lowest_floor = max(settings.main_dungeon_lowest_floor, self._current_floor)
        player = settings.current_map.entity('PLAYER')
        if len(settings.pending_curses_received) > 0:
            curse_map, sender, message = settings.pending_curses_received[0]
            settings.pending_curses_received = settings.pending_curses_received[1:]
            settings.message_panel.info("Oh no! This floor has been cursed by {}!".format(sender), tcod.cyan)
            settings.message_panel.info("{} says, \"{}\"".format(sender, message), tcod.cyan)
            settings.set_current_map(curse_map)
        else:
            settings.set_current_map(self.map(self.difficulty()))
        x, y = settings.current_map.player_start_position(player)
        player.component('Position').set(x, y)

    def return_to_town(self):
        # Replenish HP and SP
        player = settings.current_map.entity('PLAYER')
        max_hp = player.component('Stats').get_value('max_hp')
        max_sp = player.component('Stats').get_value('max_sp')
        player.component('Stats').set_base('cur_hp', max_hp)
        player.component('Stats').set_base('cur_sp', max_sp)
        # Return to town
        settings.set_item_world(None)
        self.move_to_floor(0)

    def return_to_grimmsville(self):
        # Replenish HP and SP
        player = settings.current_map.entity('PLAYER')
        max_hp = player.component('Stats').get_value('max_hp')
        max_sp = player.component('Stats').get_value('max_sp')
        player.component('Stats').set_base('cur_hp', max_hp)
        player.component('Stats').set_base('cur_sp', max_sp)
        # Return to town
        settings.set_item_world(None)
        self.move_to_floor(-1)

    def move_to_floor(self, floor):
        if floor > 0:
            settings.message_panel.info("You move to floor {}".format(floor))
        self._current_floor = floor
        self._change_floor()

    def descend(self):
        # If entering the main dungeon, return to the lowest floor in the dungeon
        if self._current_floor == 0:
            if self._item_world is None:
                self.move_to_floor(settings.main_dungeon_lowest_floor)
            else:
                item = self._item_world
                self.move_to_floor(item.component('Item').item_world_floor(item))
            return

        settings.message_panel.info("You descend to floor {}".format(self._current_floor+1))
        if self._item_world is not None:
            self._item_world.component('Stats').increase_level(1)
        self._current_floor += 1
        self._change_floor()

map_director = MapDirector()

class MonsterDirector:
    monsters = {
        0: [
            monster.Slime,
        ],
        20: [
            monster.Mage,
            monster.Golem,
            monster.Scorpion,
            monster.Spider,
            monster.Eye,
        ],
        35: [
            monster.Wyvern,
            monster.Beholder,
            monster.Giant,
            monster.Gremlin,
        ],
        55: [
            monster.Inferno,
            monster.Beehive,
            monster.Lavamoeba,
            monster.Witchdoctor,
        ],
    }

    bosses = {
        0: [
            monster.BossTheSneak,
        ],
        10: [
            monster.BossUltimateBeholder,
        ],
    }

    def __init__(self):
        self._item_world = None

    def set_item_world(self, item):
        self._item_world = item

    def choose_random_monster_set(self, difficulty, n_mons):
        monster_set = set()
        ls = sum([v for (k, v) in MonsterDirector.monsters.items() if k <= difficulty], [])
        available_set = list(set(ls))
        n_mons = min(n_mons, len(available_set))
        while len(monster_set) < n_mons:
            monster_set = monster_set | set([random.choice(available_set)])
        return list(monster_set)

    def monster_from_set(self, level, monster_set):
        tier = settings.monster_tier
        if random.randint(0, 100) <= 1:
            tier += 1
            # level = math.floor(level * 0.1)
        return random.choice(monster_set).generator(tier=tier, level=level)

    def monster(self, difficulty, level):
        available_set = sum([v for (k, v) in MonsterDirector.monsters.items() if k <= difficulty], [])
        tier = settings.monster_tier
        if random.randint(0, 100) == 1:
            tier += 1
            # level = math.floor(level * 0.1)
        return random.choice(available_set).generator(tier=tier, level=level)

monster_director = MonsterDirector()

class LootDirector:

    food = set([
        loot.Food
    ])

    items = set([
        loot.Healing,
        loot.Refreshing,
        loot.Food,
        loot.Sword,
        loot.Staff,
        loot.Cleave,
        loot.Pierce,
        loot.Fire,
        loot.Ice,
        loot.Lightning,
        loot.Paralyze,
        loot.Poison,
        loot.GuardBreak,
        loot.MindBreak,
        loot.Weaken,
        loot.Stoneskin,
        loot.Blink,
        loot.Invincible,
        loot.Unstoppable,
    ])

    equipment = set([
        loot.Staff,
        loot.Sword,
        loot.DfnArmour,
        loot.ResArmour,
        loot.DfnAtkArmour,
        loot.ResItlArmour,
    ])

    attack_skills = set([
        loot.Cleave,
        loot.Pierce,
        loot.Fire,
        loot.Ice,
        loot.Lightning,
        loot.RollingStab,
        loot.AerialDrop,
        loot.WhipSlash,
        loot.Bypass,
        loot.PoisonDetonation,
        loot.LightningBreath,
        loot.StaticShock,
        loot.Combustion,
        loot.SummonThunderTotem,
    ])

    support_skills = set([
        loot.Paralyze,
        loot.Poison,
        loot.GuardBreak,
        loot.MindBreak,
        loot.Weaken,
        loot.Stoneskin,
        loot.Blink,
        loot.Dash,
        loot.Invincible,
        loot.Unstoppable,
    ])

    mods = set([
        loot.AtkMod,
        loot.DfnMod,
        loot.ItlMod,
        loot.MaxHPMod,
        loot.MaxSPMod,
        # loot.SpdMod,
        # loot.HitMod,
        loot.MeleeLifeDrainMod,
        loot.MeleeDeathblowMod,
        loot.SPRegenMod,
        loot.HPRegenMod,
        loot.SpellSoulDrainMod,
        loot.PoisonHealMod,
        loot.SoulConversionMod,
        loot.LightningDamageMod,
        loot.FireDamageMod,
        loot.IceDamageMod,
        loot.PhysicalDamageMod,
        loot.AssaultMod,
        loot.BlazeMod,
        loot.EnergisingColdMod,
        loot.InvigoratingPowerMod,
        loot.EmpoweringFlameMod,
        loot.EnvenomedBladeMod,
        loot.LightningResistanceMod,
        loot.FireResistanceMod,
        loot.IceResistanceMod,
        loot.PhysicalResistanceMod,
        loot.MindchillMod,
        loot.StupefyMod,
        loot.StrideMod,
        loot.CoupDeGraceMod,
        loot.SurvivalTechniquesMod,
    ])

    skull = set([
        loot.CharredSkull,
    ])

    gville_portal = set([
        loot.GrimmsvillePortal,
    ])

    multiplayer = set([
        loot.CurseBees,
        loot.CurseMages,
    ])

    rare = set([
        loot.ToxicForceMod,
        loot.ToxicPowerMod,
        loot.RampageMod,
        loot.SuddenDeathMod,
        loot.WillpowerMod,
        loot.BrutalStrengthMod,
        loot.ItemLeveler10,
        loot.BloodMagicMod,
    ])

    def __init__(self):
        self._item_world = None

    def set_item_world(self, item):
        self._item_world = item

    def monster_loot(self, level):
        return random.choice(list(LootDirector.items))

    def loot_from_set(self, level, custom_set):
        return random.choice(list(custom_set))

    def ground_loot(self, level):
        roll = random.randint(0,500)
        if roll < 5:
            return random.choice(list(LootDirector.skull))
        if roll < 10:
            return random.choice(list(LootDirector.gville_portal))
        if roll < 15:
            return random.choice(list(LootDirector.rare))
        elif roll < 50:
            return loot.Healing.generator(tier=settings.loot_tier)
        elif roll < 110:
            return loot.Refreshing.generator(tier=settings.loot_tier)
        elif roll < 150:
            return loot.TownPortal
        elif roll < 170:
            return loot.Food
        elif roll < 300:
            return random.choice(list(LootDirector.mods))
        elif roll < 350:
            return random.choice(list(LootDirector.equipment)).generator(tier=settings.loot_tier)
        elif roll < 450:
            return random.choice(list(LootDirector.attack_skills))
        else:
            return random.choice(list(LootDirector.support_skills))
        return random.choice(list(LootDirector.items))

loot_director = LootDirector()

class NetDirector:
    TRANSMISSION_BYTES = 512

    def __init__(self):
        self._queued_events = []
        with open('config.json', mode='r') as f:
            self._config = json.load(f)
            self._host = self._config['server_host']
            self._port = self._config['server_port']
            self._network_disabled = False
            if self._config['net_name'] == 'CHANGE_ME':
                settings.message_panel.info('WARNING: your net_name is not set in config.json!', tcod.red)
                self._network_disabled = True
            if self._config['net_key'] == 'CHANGE_ME':
                settings.message_panel.info('WARNING: your net_key is not set in config.json!', tcod.red)
                self._network_disabled = True
        if self._network_disabled:
            settings.message_panel.info('WARNING: network features will be disabled!', tcod.red)
        else:
            try:
                self.log_in()
                settings.message_panel.info('Logged in with net_name: {}'.format(self.net_name()), tcod.cyan)
            except ConnectionRefusedError:
                settings.message_panel.info('WARNING: unable to connect to server', tcod.red)
                settings.message_panel.info('WARNING: network features will be disabled!', tcod.red)
                self._network_disabled = True


    def _recv_from_server(self, s):
        data_chunk = s.recv(NetDirector.TRANSMISSION_BYTES)
        data = data_chunk
        print("DATA:", data_chunk)
        while b'END_MESSAGE' not in data:
            data_chunk = s.recv(NetDirector.TRANSMISSION_BYTES)
            data += data_chunk
            print("DATA:", data_chunk)
        data = data[:-11]
        return data

    def log_in(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((self._host, self._port))
            msg_object = {
                'command': 'log_in',
                'net_name': self.net_name(),
                'net_key': self.net_key(),
            }
            s.sendall(json.dumps(msg_object).encode('utf-8'))
            s.sendall('END_MESSAGE'.encode('utf-8'))
            data = self._recv_from_server(s)
        print(data)

    def net_name(self):
        return self._config['net_name']

    def net_key(self):
        return self._config['net_key']

    def propagate_events(self):
        events = self.recv_events()
        for event in events:
            print(event)
            event = event[0]
            event = (event[0], event[1])
            settings.current_map.entities()\
                                .transform(lambda ent: ent.handle_event(event, settings.current_map))

    def queue_events(self, events: [(str, object)]):
        self._queued_events.append(events)

    def recv_events(self):
        if self._network_disabled:
            return []
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((self._host, self._port))
            msg_object = {
                'command': 'recv_events',
                'net_key': self.net_key(),
            }
            s.sendall(json.dumps(msg_object).encode('utf-8'))
            s.sendall('END_MESSAGE'.encode('utf-8'))
            data = self._recv_from_server(s)
        return json.loads(data)

    def send_events(self):
        if self._network_disabled:
            return
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((self._host, self._port))
            msg_object = {
                'command': 'send_events',
                'events': self._queued_events[:5],
                'net_key': self.net_key(),
            }
            s.sendall(json.dumps(msg_object).encode('utf-8'))
            s.sendall('END_MESSAGE'.encode('utf-8'))
            self._queued_events = self._queued_events[5:]
            data = self._recv_from_server(s)
        #print(data)

    def send_remaining_events(self):
        if self._network_disabled:
            return
        while len(self._queued_events) > 0:
            self.send_events()

net_director = NetDirector()
