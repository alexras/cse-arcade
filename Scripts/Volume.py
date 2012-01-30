#!/usr/bin/env python

import os
import sys

direction = sys.argv[1]

if direction == 'up':
    os.system('amixer set Master 5%+')
if direction == 'down':
    os.system('amixer set Master 5%-')

os.system('aplay /home/arcade/Arcade/Data/sounds/click2.wav')
