#!/usr/bin/env python

import os
import select
import subprocess
import time
from struct import unpack

SELECT_WAIT_TIME = 5

idle_time = 0

port = os.open("/dev/input/by-id/usb-Ultimarc_I-PAC_Ultimarc_I-PAC-event-kbd", os.O_RDONLY | os.O_NONBLOCK)

while 1:
    (reads, writes, excepts) = select.select([port], [], [], SELECT_WAIT_TIME)

    pid = subprocess.Popen(['pgrep', 'mame|snes|gens'], stdout=subprocess.PIPE, close_fds=True).communicate()[0].strip()

    if pid == '':
        game = 'Nothing'
    else:
        ps = subprocess.Popen(['ps', '-p', pid, '-o', 'args:70'], stdout=subprocess.PIPE, close_fds=True).communicate()[0]
        game = ps.strip().split('\n')[1]

    if reads == []:
        idle_time += SELECT_WAIT_TIME
    else:
        try:
            val = os.read(port, 4096)
        except:
            time.sleep(SELECT_WAIT_TIME)
            continue

        time.sleep(SELECT_WAIT_TIME)
        idle_time = 0

    #print 'Idle time: %d seconds, game: %s' % (idle_time, game)

    if idle_time >= 180 and game != 'Nothing':
        os.system('kill %s' % pid)
