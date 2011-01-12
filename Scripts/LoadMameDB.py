#!/usr/bin/env python

import os
import re
import subprocess
import sqlite3

db = sqlite3.connect('/home/arcade/Arcade/Data/Arcade.db')

blacklisted = set()
blist_file = open('Blacklist', 'r')
for line in blist_file:
    blacklisted.add(line.split()[0])

roms = []
for filename in os.listdir('/home/arcade/mame/roms'):
    roms.append(filename.split('.')[0])

in_db = set()
for row in db.execute('select path from Games where emulator == 0'):
    in_db.add(row[0])

for rom in roms:
    if rom not in blacklisted and rom not in in_db:
        #Check to see if it's already in db
        #If not, get
        pipe = subprocess.Popen('/usr/games/mame -listfull %s' % rom, shell=True, bufsize=1, stdout=subprocess.PIPE).stdout
        metadata = re.sub(' +', ' ', pipe.readlines()[1]).split(' ', 1)

        romname = metadata[0]
        description = metadata[1].replace('"', '')

        print 'Adding %s' % str(romname)

        values = (romname, romname, description, 'mame-images/%s.png' % romname, 480)

        db.execute('insert into Games values (0, ?, ?, "", ?, ?, ?, 0, 0)', values)

db.commit()
db.close()
