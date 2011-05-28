import pygame

RATE = 30
SIZERATE=25

class MovingSprite(pygame.sprite.DirtySprite):
    def __init__(self, data, datadir):
        pygame.sprite.DirtySprite.__init__(self)
        self.datadir = datadir

        self.data = data
        self.loaded_image = None
        self.image = None
        self.rect = None
        self.target_location = None
        self.target_size = None
        self.visible = 0
        self.dirty = 0

    def __getitem__(self, key):
        return self.data[key]

    def draw(self, location, size):
        self.loaded_image = pygame.image.load(self.datadir + '/' + self.data['image']).convert()
        self.image = pygame.transform.scale(self.loaded_image, size).convert()
        self.rect = self.image.get_rect()
        self.rect.topleft = location
        self.target_location = location
        self.target_size = size
        self.visible = 1
        self.dirty = 1

    def update(self):
        if self.rect.topleft == self.target_location and self.rect.size == self.target_size:
            self.dirty = 0
            return

        if self.rect.size != self.target_size:
            new_width = self.rect.width
            new_height = self.rect.height
            if self.direction < 0:
                old_location = self.rect.topright
            elif self.direction > 0:
                old_location = self.rect.topleft

            if self.rect.width < self.target_size[0]:
                new_width = self.rect.width + min([SIZERATE, self.target_size[0] - self.rect.width])
            if self.rect.width > self.target_size[0]:
                new_width = self.rect.width - min([SIZERATE, self.rect.width - self.target_size[0]])

            if self.rect.height < self.target_size[1]:
                new_height = self.rect.height + min([SIZERATE, self.target_size[1] - self.rect.height])
            if self.rect.height > self.target_size[1]:
                new_height = self.rect.height - min([SIZERATE, self.rect.height - self.target_size[1]])

            self.image = pygame.transform.scale(self.loaded_image, (new_width, new_height))
            self.rect = self.image.get_rect()
            if self.direction < 0:
                self.rect.topright = old_location
            elif self.direction > 0:
                self.rect.topleft = old_location

        if self.rect.left < self.target_location[0]:
            self.rect.left = self.rect.left + min([RATE, self.target_location[0] - self.rect.left])
        if self.rect.left > self.target_location[0]:
            self.rect.left = self.rect.left - min([RATE, self.rect.left - self.target_location[0]])

        if self.rect.top < self.target_location[1]:
            self.rect.top = self.rect.top + min([RATE, self.target_location[1] - self.rect.top])
        if self.rect.top > self.target_location[1]:
            self.rect.top = self.rect.top - min([RATE, self.rect.top - self.target_location[1]])

        self.dirty = 1

    def hide(self):
        self.image = None
        self.rect = None
        self.visible = 0
        self.dirty = 1

    def set_target(self, location, size, direction, group):
        if self.loaded_image == None:
            self.loaded_image = pygame.image.load(self.datadir + '/' + self.data['image']).convert()
        if self.rect is not None:
            old_location = self.rect.topleft
            old_size = self.rect.size
        else:
            old_location = location
            old_size = size

        # This is a hack! Don't roll around the screen stupidly!
        if direction > 0 and location[1] > old_location[1] and group == 'emus':
            old_location = location
        if direction < 0 and location[1] < old_location[1] and group == 'emus':
            old_location = location

        self.target_location = location
        self.target_size = size
        self.image = pygame.transform.scale(self.loaded_image, old_size).convert()
        self.rect = self.image.get_rect()
        self.rect.topleft = old_location
        self.direction = direction
        self.visible = 1
        self.dirty = 1
