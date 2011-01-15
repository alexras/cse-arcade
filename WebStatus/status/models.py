from django.db import models

class Platform(models.Model):
    name = models.CharField(max_length=200)
    
    def __unicode__(self):
        return self.name
    
    
class Game(models.Model):
    name = models.CharField(max_length=300)
    plays = models.IntegerField()
    total_time = models.IntegerField()
    platform = models.ForeignKey(Platform)
    
    def __unicode__(self):
        return "'%s' for %s (%d plays, %d seconds)" % \
            (self.name, self.platform, self.plays, self.total_time)
    
