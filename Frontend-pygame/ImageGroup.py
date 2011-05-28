import pygame

from MovingSprite import MovingSprite

class ImageGroup(pygame.sprite.LayeredDirty):
    def __init__(self, locations, sizes, start_at, *sprites):
        pygame.sprite.LayeredDirty.__init__(self, *sprites)

        self.backing = []
        for sprite in sprites:
            self.backing.append(sprite)

        self.locations = locations
        self.sizes = sizes

        self.current = (start_at % len(self.backing))
        view = set([self.backing[self.current], self.backing[(self.current - 1) % len(self.backing)], self.backing[(self.current + 1) % len(self.backing)]])

        self.backing[self.current].draw(locations['current'], sizes['current'])
        self.backing[(self.current - 1) % len(self.backing)].draw(locations['before'], sizes['before'])
        self.backing[(self.current + 1) % len(self.backing)].draw(locations['after'], sizes['after'])

        for sprite in self.backing:
            if sprite not in view:
                self.remove(sprite)

    def __getitem__(self, index):
        return self.backing[index]

    def get_current(self):
        return self.backing[self.current]

    def move(self, direction, group):
        self.current = (self.current + direction) % len(self.backing)

        view = set([self.backing[self.current], self.backing[(self.current - 1) % len(self.backing)], self.backing[(self.current + 1) % len(self.backing)]])

        self.backing[self.current].set_target(self.locations['current'], self.sizes['current'], direction, group)
        self.backing[(self.current - 1) % len(self.backing)].set_target(self.locations['before'], self.sizes['before'], direction, group)
        self.backing[(self.current + 1) % len(self.backing)].set_target(self.locations['after'], self.sizes['after'], direction, group)

        self.empty()

        for sprite in self.backing:
            if sprite in view:
                self.add(sprite)
            else:
                sprite.hide()

class EmulatorImageGroup(ImageGroup):
    def __init__(self, locations, sizes, db, *sprites):
        ImageGroup.__init__(self, locations, sizes, 0, *sprites)

        self.games_group = None
        self.db = db
        self.last_game_indexes = [0 for sprite in sprites]

    def get_current(self):
        return (self.backing[self.current], self.games_group.get_current())

    def move(self, direction, group):
        if self.games_group is not None:
            self.last_game_indexes[self.current] = self.games_group.current

        ImageGroup.move(self, direction, group)

        current_emulator = self.backing[self.current]
        values = (current_emulator.data['id'],)

        games = []
        for row in self.db.execute('select * from Games where emulator == ? order by name', values):
            games.append(MovingSprite(row, current_emulator.datadir))

        game_locations = { 'current': (712 - .5 * games[0]['image_width'], 308), 'before': (425, 50), 'after': (999 - (games[0]['image_width'] / 2), 50) }
        game_sizes = { 'current': (games[0]['image_width'], 360), 'before': (games[0]['image_width'] / 2, 180), 'after': (games[0]['image_width'] / 2, 180) }

        self.games_group = ImageGroup(game_locations, game_sizes, self.last_game_indexes[self.current], *games)

        return self.games_group
