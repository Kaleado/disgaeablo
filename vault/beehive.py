from map import Vault

class BeehiveVault(Vault):
    width = 5
    height = 5

    def terrain(self):

        def is_internal_tile(x, y):
            return x != 0 and x != BeehiveVault.width-1 and y != 0 and y != BeehiveVault.height-1
        
        terrain = [['.' if is_internal_tile(x, y) else '#' for x in range(BeehiveVault.width)] for y in range(BeehiveVault.height)]
        return terrain

    def entities(self):
        import monster
        entities = []

        for x in range(1, BeehiveVault.width-1):
            for y in range(1, BeehiveVault.height-1):
                entities.append(monster.Bee.generator(level=self._difficulty)((x, y)))

        return entities