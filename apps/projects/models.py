from django.db import models
from taggit.managers import TaggableManager
import datetime
from django.utils.translation import ugettext_lazy as _


class Project(models.Model):
    """(Modelname description)"""
    title = models.CharField(_("name"), max_length=150, blank=True, help_text="Something short and snappy works best")
    description = models.TextField(_("description"), blank=True, help_text="A sentence or two about your project")
    created = models.DateTimeField(blank=True, default=datetime.datetime.now)
    
    tags = TaggableManager()
    
    def __unicode__(self):
        return self.title
    
    def items(self, after_timestamp = 0):
        """
        Returns Queryset containing all items that are:
                (a) associated with a project and approved
                (b) tagged with a projects tag and approved
        """

        activity_model = models.get_model('activity', 'Activity')
        project_tags = self.tags.all()
        
        project_tag_list = []
        
        for tag in project_tags.values():
            project_tag_list.append(tag['name'].lower())
                    
        if after_timestamp == 0:
            return activity_model.objects.filter(tags__name__in=project_tag_list).order_by('-created').distinct()
        else:
            after_datetime = datetime.datetime.fromtimestamp(after_timestamp+1)
            return activity_model.objects.filter(tags__name__in=project_tag_list, created__gt=after_datetime).order_by('-created').distinct()
        
