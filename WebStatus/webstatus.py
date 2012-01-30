#!/usr/bin/env python

import os, sys, json, jinja2, time, datetime
from bottle import route, run, debug

status_update_file = "/home/arcade/status_updates/status_update"

jinja2_env = jinja2.Environment(
    loader = jinja2.FileSystemLoader(
        os.path.join(os.path.dirname(__file__), 'templates')),
    trim_blocks = True)

class Game(object):
    def __init__(self, name, time=None, plays=None):
        self.name = name
        self.time = time
        self.plays = plays

def readable_time(seconds):
    td = datetime.timedelta(seconds=seconds)
    return str(td)

def render_error(message):
    error_template =  jinja2_env.get_template('error.template')
    return error_template.render(message = message).strip()

def render_status_page(status_dict):
    status_page_template = jinja2_env.get_template('status_page.template')
    return status_page_template.render(**status_dict).strip()

@route('/')
def index():
    if not os.path.exists(status_update_file):
        return render_error("Can't find '%s'" % (status_update_file))

    fp = open(status_update_file, 'r')
    status = json.load(fp)
    fp.close()

    postprocessed_status = {}

    postprocessed_status['playing'] = bool(status['status'])
    postprocessed_status['current_game'] = status['current_game']
    postprocessed_status['pressing_buttons'] = postprocessed_status['playing'] \
        and postprocessed_status['current_game'] == "Idle"

    postprocessed_status['last_update'] = time.ctime(int(status['last_update']))

    top_ten_by_total_time = []
    top_ten_by_plays = []

    for i in xrange(10):
        time_info = status['times'][str(i + 1)]
        plays_info = status['plays'][str(i + 1)]

        time_game = Game(time_info[0], time=readable_time(time_info[1]))
        plays_game = Game(plays_info[0], plays=plays_info[1])

        top_ten_by_total_time.append(time_game)
        top_ten_by_plays.append(plays_game)

    postprocessed_status['top_ten_by_total_time'] = top_ten_by_total_time
    postprocessed_status['top_ten_by_plays'] = top_ten_by_plays
    postprocessed_status['total_time'] = readable_time(status['total_time'])

    return render_status_page(postprocessed_status)

def main():
    if len(sys.argv) < 2:
        sys.exit("Usage: webstatus.py <port>")

    run(host='0.0.0.0', port=sys.argv[1])

if __name__ == "__main__":
    main()
