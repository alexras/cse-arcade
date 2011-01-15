from django.db import models

class Platform(models.Model):
    name = models.CharField(max_length=200)
    
    def __unicode__(self):
        return self.name

    def ordered_games_list(self):
        return self.game_set.all().order_by('name')
    
    
class Game(models.Model):
    name = models.CharField(max_length=300)
    plays = models.IntegerField()
    total_time = models.IntegerField()
    platform = models.ForeignKey(Platform)
    
    def __unicode__(self):
        return "'%s' for %s (%d plays, %d seconds)" % \
            (self.name, self.platform, self.plays, self.total_time)
    
    def total_time_in_hours(self):
        return "%d:%02d:%02d" % (self.total_time / 3600, 
                             (self.total_time / 60) % 60, 
                             self.total_time % 60)
