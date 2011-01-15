# Create your views here.

from django.http import HttpResponse
from django.shortcuts import render_to_response
from status.models import Platform, Game

def index(request):
    platform_list = Platform.objects.all().order_by('name')
    
    top_ten_by_total_time = Game.objects.all().order_by('-total_time')[:10]
    top_ten_by_play_count = Game.objects.all().order_by('-plays')[:10]
    
    total_play_time_seconds = sum([game.total_time for game in \
                                       Game.objects.all()])

    total_play_time = "%d days, %d hours, %02d minutes, %02d seconds" % \
        ((total_play_time_seconds / 86400,
          (total_play_time_seconds / 3600) % 24, 
          (total_play_time_seconds / 60) % 60, 
          total_play_time_seconds % 60))
         
    return render_to_response("status/index.html", 
                              {"platform_list" : platform_list,
                               "top_ten_by_total_time" : top_ten_by_total_time,
                               "top_ten_by_play_count" : top_ten_by_play_count,
                               "total_play_time" : total_play_time})
