from activity.models import Activity, ActivityComment
from external_applications.models import ExternalApplication
import datetime
import dateutil.parser
import dateutil.tz
from django.utils import simplejson
import urllib2
from django.http import HttpResponse, HttpResponseRedirect

from django.shortcuts import render_to_response, get_object_or_404


def make_comment(request):
    comment = request.POST.get('comment', '')
    activity_id = request.POST.get('activity_id', '')
    
    # try:
    if comment != "":
        activity = get_object_or_404(Activity, id=activity_id)
        ActivityComment.objects.create(author=request.user, belongs_to=activity, comment=comment)
        if request.is_ajax:
            return HttpResponse(simplejson.dumps(True), mimetype='application/javascript')
        else:
            return HttpResponseRedirect(reverse("project_list"))
    else:
        return HttpResponse(simplejson.dumps(False), mimetype='application/javascript')
    # except:
    #     return HttpResponse(simplejson.dumps(False), mimetype='application/javascript')
    
def parse_date(s):
    """
    Convert a string into a (local, naive) datetime object.
    """
    dt = dateutil.parser.parse(s)
    if dt.tzinfo:
        dt = dt.astimezone(dateutil.tz.tzlocal()).replace(tzinfo=None)
    return dt

def delicious_fetch(request):
    return delicious(request.GET['username'])

def delicious(username):
    """
    Query the delicious JSON feed for user and populate a new activity object
    """
    
    # Request JSON feed for user
    url = "http://feeds.delicious.com/v2/json/%s" % username
    data = urllib2.urlopen(url).read()
    delicious_bookmarks = simplejson.loads(data)
    
    new_activities = 0 # Initialise number of new activities for user
    
    try:
        # Set the `latest` date to the most recently created bookmark for the user
        latest = Activity.objects.filter(username=username, source='delicious').order_by('-created')[0].created
    except IndexError:
        # If there are no entries then set the latest date to 0
        latest = datetime.datetime.fromtimestamp(0)
    
    # For each bookmark object parse the following details
    for bookmark in delicious_bookmarks:
        title = bookmark['d'].encode('utf8')
        subtitle = bookmark['n'].encode('utf8')
        type = "bookmark"
        source = "delicious"
        username = bookmark['a'].encode('utf8')
        url = bookmark['u'].encode('utf8')
        created = parse_date(bookmark['dt'].encode('utf8'))
        
        # If the bookmark was created *after* the previous update then:
        if created > latest:
            # add the bookmark as a new activity object
            act = Activity.objects.create(
                title = title,
                subtitle = subtitle,
                type = type,
                source = source,
                username = username,
                url = url,
                created = created
            )
            
            # Add the tags to the activity object
            for tag in bookmark['t']:
                if tag[-1] == ',':
                    clean_tag = tag[:-1].lower().encode('utf8')
                else:
                    clean_tag = tag.lower().encode('utf8')
                    
                act.tags.add(clean_tag)
            
            # Increase the new activities counter
            new_activities += 1
    
    # return the amount of activities that have been updated
    return HttpResponse(simplejson.dumps(new_activities), mimetype='application/javascript')
    
def all_delicious_accounts(request):
    for account in ExternalApplication.objects.filter(application='delicious'):
        delicious(account.username)
        
    return HttpResponse(simplejson.dumps(True), mimetype='application/javascript')