#!/usr/bin/env python

import os
import sys
import sqlite3

import pygame
from pygame.locals import *

from FrontendConfig import FrontendConfig

from MovingSprite import MovingSprite
from ImageGroup import *


NO_IMAGE = '/home/arcade/Frontend/no_preview.png'

class Frontend(object):
    def launch(self, emulator, game):
        launch_string = emulator['path']

        # Hack to make switching interfaces work.
        if game['name'] == 'PyGTK interface' or game['name'] == 'PyGame interface':
            # If we're switching interfaces, replace the executing image.
            os.execlp('python', 'python', self.config['RootDir'] + game['path'])
            return
        
        if game['args'] is None or game['args'] == '':
            launch_string += ' ' + emulator['args']
        else:
            launch_string += ' ' + game['args']

        launch_string += ' ' + game['path']

        if self.config['Launch']:
            os.system(launch_string)
        else:
            print launch_string

    def cleanup(self):
        self.db.close()
        if self.config['HidePointer']:
            os.system('kill -9 %d' % self.unclutter_child)

        print 'Goodbye!'

    def __init__(self):
        self.config = FrontendConfig('frontend-pygame')

        pygame.init()
        pygame.mixer.init()
        pygame.key.set_repeat(500, 150)

        self.screen = pygame.display.set_mode((1024,768))
        self.background = pygame.Surface(self.screen.get_size())
        self.game_font = pygame.font.Font(None, 48)
        self.click = pygame.mixer.Sound('%s/sounds/light2.wav' % self.config['DataDir'])
        self.clock = pygame.time.Clock()
        self.db = sqlite3.connect('%s/Arcade.db' % self.config['DataDir'])

        emu_locations = { 'current': (50,284), 'before': (100,50), 'after': (100,584) }
        emu_sizes = { 'current': (300,200), 'before': (201,134), 'after': (201,134) }

        self.background.fill((0,0,0))
        self.screen.blit(self.background, (0,0))

        self.db.row_factory = sqlite3.Row
        emus = []
        for row in self.db.execute('select * from Emulators order by name'):
            emus.append(MovingSprite(row, self.config['DataDir']))

        self.emulators = EmulatorImageGroup(emu_locations, emu_sizes, self.db, *emus)
        self.games = self.emulators.move(0, 'games')

        # Spawn an unclutter process to hide the mouse pointer.
        if self.config['HidePointer']:
            self.unclutter_child = os.fork()
            if self.unclutter_child == 0:
                while (True):
                    os.system('unclutter')

        # Set fullscreen.  TODO: Test this!  Doesn't work on mac, but docs say
        # it's only valid for X11.
        if self.config['Fullscreen']:
            pygame.display.toggle_fullscreen()

    def set_text(self):
        if self.text_rect is not None:
            self.screen.fill((0,0,0), rect=self.text_rect)
        (emulator, game) = self.emulators.get_current()
        text = self.game_font.render(game['name'], True, (255,255,255))
        self.text_rect = text.get_rect()
        self.text_rect.centerx = 712
        self.text_rect.centery = 720
        self.screen.blit(text, self.text_rect)

    def start(self):
        self.text_rect = None
        self.set_text()

        # Main loop
        while True:
            self.clock.tick(60)

            for event in pygame.event.get():
                if event.type == QUIT:
                    return

                if event.type == KEYDOWN:
                    key = pygame.key.name(event.key)

                    if self.config['PrintKeys']:
                        print key

                    if key in self.config['UP']:
                        self.click.play()
                        self.screen.blit(self.background, (0,0))
                        self.games = self.emulators.move(1, 'emus')
                        self.set_text()

                    if key in self.config['DOWN']:
                        self.click.play()
                        self.screen.blit(self.background, (0,0))
                        self.games = self.emulators.move(-1, 'emus')
                        self.set_text()

                    if key in self.config['LEFT']:
                        self.click.play()
                        self.games.move(1, 'games')
                        self.set_text()

                    if key in self.config['RIGHT']:
                        self.click.play()
                        self.games.move(-1, 'games')
                        self.set_text()

                    if key in self.config['GO']:
                        (emulator, game) = self.emulators.get_current()
                        self.launch(emulator, game)

            self.emulators.update()
            self.games.update()
            emulist = self.emulators.draw(self.screen)
            gamelist = self.games.draw(self.screen)
            pygame.display.update(emulist)
            pygame.display.update(gamelist)
            self.emulators.clear(self.screen, self.background)
            self.games.clear(self.screen, self.background)

if __name__ == "__main__":
    fend = Frontend()
    fend.start()
    fend.cleanup()
