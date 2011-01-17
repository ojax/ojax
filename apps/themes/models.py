from django.db import models


def upload_location(instance, filename):
    return 'theme_files/%s' % (filename)
    
class Theme(models.Model):
    """(Modelname description)"""
    
    theme_name = models.TextField(blank=True)
    logo_small = models.FileField(upload_to = upload_location)
    logo_large = models.FileField(upload_to = upload_location)
    background_image = models.FileField(upload_to = upload_location)
    active = models.BooleanField(default=False)
    
    def __unicode__(self):
        return self.theme_name