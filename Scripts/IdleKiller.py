#!/usr/bin/env python

import os
import select
import subprocess
from struct import unpack

SELECT_WAIT_TIME = 10

idle_time = 0

port = open("/dev/input/by-id/usb-Ultimarc_I-PAC_Ultimarc_I-PAC-event-kbd","rb")

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
        a,b,c,d,e = unpack("llHHI",port.read(16))
        idle_time = 0

    #print 'Idle time: %d seconds, game: %s' % (idle_time, game)

    if idle_time >= 180 and game != 'Nothing':
        os.system('kill %s' % pid)
