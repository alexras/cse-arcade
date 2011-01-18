#!/usr/bin/env python

"""
Imports information from Arcade.db into Django's model.
"""

import sqlite3
import os, sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")

import WebStatus
os.environ["DJANGO_SETTINGS_MODULE"] = "WebStatus.settings"
import status
from status.models import Platform, Game
from optparse import OptionParser

option_parser = OptionParser(usage="importer.py [options] "
                            "<location of Arcade.db>")

(options, args) = option_parser.parse_args()

if len(args) != 1:
    option_parser.error("Invalid argument count")
    
arcade_db_loc = args[0]

if not os.path.exists(arcade_db_loc):
    print >>sys.stderr, "Can't find %s" % (arcade_db_loc)
    sys.exit(1)

db = sqlite3.connect(arcade_db_loc)
db.row_factory = sqlite3.Row

# Populate platforms with emulator names
for row in db.execute("SELECT * FROM Emulators"):
    curr_name = row['name']
    
    if curr_name != "Control":
        # If Platform table doesn't contain platform, add it
        try:
            Platform.objects.get(name=curr_name)
        except:
            print "Adding platform %s" % (curr_name)
            p = Platform(name=curr_name)
            p.save()

# Populate games with games and current statistics
for row in db.execute("SELECT E.name as platform_name, G.name as game_name, "
                      "G.plays, G.total_time FROM Emulators E, Games G WHERE "
                      "E.id == G.emulator"):
    platform_name = row['platform_name']
    game_name = row['game_name']
    plays = row['plays']
    total_time = row['total_time']
    
    if platform_name == "Control":
        continue    

    platform = Platform.objects.get(name=platform_name)
    
    # If the game doesn't exist, create it
    # Otherwise, set its play count and total time
    try:
        game = Game.objects.get(name=game_name, platform=platform)
        print >>sys.stderr, "Updating game %s for %s" % (game_name, platform.name)
        game.plays = plays
        game.total_time = total_time
        game.save()
        
    except:
        print >>sys.stderr, "Creating game %s for %s" % (game_name, platform.name)
        game = platform.game_set.create(name=game_name, plays=plays, 
                                        total_time=total_time)
        
db.close()
