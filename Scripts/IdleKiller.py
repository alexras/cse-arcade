#!/usr/bin/env python

import json
import os
import select
import subprocess
import sqlite3
import time

SELECT_WAIT_TIME = 10

idle_time = 0
busy_time = 0
STATUS_IDLE = 0
STATUS_BUSY = 1

status = STATUS_IDLE
needs_update = True

port = os.open("/dev/input/by-id/usb-Ultimarc_I-PAC_Ultimarc_I-PAC-event-kbd", os.O_RDONLY | os.O_NONBLOCK)

while 1:
    (reads, writes, excepts) = select.select([port], [], [], SELECT_WAIT_TIME)

    pid = subprocess.Popen(['pgrep', 'mame|snes|gens|mednafen'], stdout=subprocess.PIPE, close_fds=True).communicate()[0].strip()

    if pid == '':
        game = 'Idle'
    else:
        if game == 'Idle':
            needs_update = True

        try:
            ps = subprocess.Popen(['ps', '-p', pid, '-o', 'args:70'], stdout=subprocess.PIPE, close_fds=True).communicate()[0]
            game = ps.strip().split('\n')[1]
        except:
            continue

    if reads == []:
        if status == STATUS_BUSY:
            needs_update = True

        idle_time += SELECT_WAIT_TIME
        busy_time = 0
        status = STATUS_IDLE
    else:
        try:
            val = os.read(port, 4096)
        except:
            time.sleep(SELECT_WAIT_TIME)
            continue

        if status == STATUS_IDLE:
            needs_update = True

        time.sleep(SELECT_WAIT_TIME)
        idle_time = 0
        busy_time += SELECT_WAIT_TIME
        status = STATUS_BUSY

    if idle_time >= 180 and game != 'Idle':
        os.system('kill %s' % pid)
        needs_update = True

    if (idle_time > 180 and idle_time % 300 == 0) or (busy_time > 0 and busy_time % 300 == 0):
        needs_update = True

    if needs_update:
        try:
            db = sqlite3.connect('/home/arcade/Arcade/Data/Arcade.db')
            db.row_factory = sqlite3.Row

            plays = db.execute('select name,plays from Games order by plays desc')
            times = db.execute('select name,total_time from Games order by total_time desc')
        except:
            needs_update = True
            continue

        count = 0

        plays_dict = {}
        times_dict = {}

        for row in plays:
            if 'Volume' in row['name'] or 'interface' in row['name']:
                continue

            count += 1
            plays_dict[count] = (row['name'], row['plays'])

        count = 0
        total_time = 0

        for row in times:
            if 'Volume' in row['name'] or 'interface' in row['name']:
                continue

            count += 1
            times_dict[count] = (row['name'], row['total_time'])
            total_time += row['total_time']

        db.close()

        json_dict = {'status': status, 'current_game': game, 'times': times_dict, 'plays': plays_dict, 'total_time': total_time, 'last_update': int(time.time())}

        outfile = open('/home/arcade/status_update', 'w')
        json.dump(json_dict, outfile)
        outfile.close()

        needs_update = False
