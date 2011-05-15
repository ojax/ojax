from django.db import models
from taggit.managers import TaggableManager
import datetime
import dateutil.parser
import dateutil.tz

# from djpubsubhubbub import signals
from django.contrib.auth.models import User



class Activity(models.Model):
    """(Modelname description)"""
    title = models.TextField(blank=True)
    subtitle = models.TextField(blank=True)
    type = models.TextField(blank=True)
    url = models.TextField(blank=True)
    username = models.TextField(blank=True)
    user = models.ForeignKey(User)
    source = models.TextField(blank=True)
    created = models.DateTimeField(blank=True, default=datetime.datetime.now)
    
    tags = TaggableManager()
    
    def save(self, *args, **kwargs):
        ea_model = models.get_model('external_applications', 'ExternalApplication')
        ea = ea_model.objects.filter(application=self.source, username=self.username)
        if ea:
            self.user = ea[0].user
            
        super(Activity, self).save(*args, **kwargs)

            

    class Meta:
        verbose_name_plural = "Activities"
        
    def __unicode__(self):
        return "(%s) - %s" % (self.title, self.subtitle)
        
        
class ActivityComment(models.Model):
    belongs_to = models.ForeignKey(Activity)
    author = models.ForeignKey(User)
    comment = models.TextField(blank=False)
    pub_date = models.DateTimeField(blank=True, default=datetime.datetime.now)
    
    class Meta:
        get_latest_by = "pub_date"
    
    def __unicode__(self):
        return "%s - %s" % (self.author, self.comment)
    
    
        
def parse_activitystream(sender, **kwargs):
    """docstring for print_it"""
    
    def parse_date(s):
        """
        Convert a string into a (local, naive) datetime object.
        """
        dt = dateutil.parser.parse(s)
        if dt.tzinfo:
            dt = dt.astimezone(dateutil.tz.tzlocal()).replace(tzinfo=None)
        return dt
    
    print "received something"
    print kwargs['update']
        
    title = kwargs['update']['entries'][0]['title']
    created = parse_date(kwargs['update']['entries'][0]['published'])
    
    subtitle = ""
    
    try:
        summary = kwargs['update']['entries'][0]['summary_detail']['value']
    except:
        summary = ""
        
    try:
        subtitle = kwargs['update']['entries'][0]['subtitle']
    except:
        subtitle = ""
        
    url = kwargs['update']['entries'][0]['links'][0]['href']
    username = kwargs['update']['entries'][0]['author_detail']['name']
    
    for tag in kwargs['update']['entries'][0]['tags']:
        if tag['scheme'] == "http://schemas.cliqset.com/activity/categories/1.0":
            act_type = tag['label']      

    act = Activity.objects.create(
        title = title,
        subtitle = subtitle or summary,
        url = url,
        username = username,
        type = act_type,
        created = created
    )
    
    for tag in kwargs['update']['entries'][0]['tags']:
        if tag['scheme'] == "http://schemas.cliqset.com/activity/tags/1.0":
            act.tags.add(tag['label'])
            
    [Ac.tags.add(tag) for tag in ['fds', 'dferf', 'fd2rfw']]
    

# signals.updated.connect(parse_activitystream)