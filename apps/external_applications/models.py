from django.db import models

from django.contrib.auth.models import User

class ExternalApplication(models.Model):
    
    user = models.ForeignKey(User)
    application = models.CharField(blank=False, max_length=100)
    username = models.CharField(blank=False, max_length=100)
    password = models.CharField(blank=True, max_length=100)

    class Meta:
        unique_together = ("user", "application")

    def __unicode__(self):
        return "(%s) - %s" % (self.application, self.user.username)
