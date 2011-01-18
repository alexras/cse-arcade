# Create your views here.

from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.conf import settings
import json
import os

class Game(object):
    def __init__(self, name, time=None, plays=None):
        self.name = name
        self.time = time
        self.plays = plays

def index(request):
    STATUS_UPDATE_FILE = "%s/status_updates/status_update" % (os.getenv("HOME"))
    assert(os.path.exists(STATUS_UPDATE_FILE))
    fp = open(STATUS_UPDATE_FILE, 'r')
    status = json.load(fp)
    fp.close()
    
    postprocessed_status = {}
    
    postprocessed_status['playing'] = bool(status['status'])
    postprocessed_status['current_game'] = status['current_game']
    
    top_ten_by_total_time = []
    top_ten_by_plays = []
    
    for i in xrange(10):
        time_info = status['times'][str(i + 1)]
        plays_info = status['plays'][str(i + 1)]
        
        time_game = Game(time_info[0], time=time_info[1])
        plays_game = Game(plays_info[0], plays=plays_info[1])
        
        top_ten_by_total_time.append(time_game)
        top_ten_by_plays.append(plays_game)
    
    postprocessed_status['top_ten_by_total_time'] = top_ten_by_total_time
    postprocessed_status['top_ten_by_plays'] = top_ten_by_plays
    postprocessed_status['total_time'] = status['total_time']
    
    return render_to_response("status/index.html",postprocessed_status)
