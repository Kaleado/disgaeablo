from map import Vault

class ScrollRoomVault(Vault):
    width = 5
    height = 5

    def terrain(self):

        def is_internal_tile(x, y):
            return x != 0 and x != ScrollRoomVault.width-1 and y != 0 and y != ScrollRoomVault.height-1
        
        terrain = [['.' if is_internal_tile(x, y) else '#' for x in range(ScrollRoomVault.width)] for y in range(ScrollRoomVault.height)]
        return terrain

    def entities(self):
        import loot
        entities = []

        for x in range(1, ScrollRoomVault.width-1):
            for y in range(1, ScrollRoomVault.height-1):
                if random.randint(0, 20) != 0:
                    entities.append(loot.TownPortal((x, y)))
                else:
                    entities.append(loot.GrimmsvillePortal((x, y)))

        return entities