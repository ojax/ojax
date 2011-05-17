from activity.models import Activity, ActivityComment
from external_applications.models import ExternalApplication
import datetime
import dateutil.parser
import dateutil.tz
import re
from django.utils import simplejson
import urllib2
from xml.dom.minidom import parse, parseString
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
    type = "bookmark"
    source = "delicious"
    
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
    
def myexperiment_fetch(request):
    return myexperiment(request.GET['username'])
    
def myexperiment(username):
    page2 = urllib2.urlopen("http://www.myexperiment.org/user.xml?id=%s&elements=workflows,updated-at" % username)
    details = parse(page)
    
    new_activities = 0 # Initialise number of new activities for user
    type = "workflow"
    source = "myexperiment"
    
    try:
        # Set the `latest` date to the most recently created bookmark for the user
        latest = Activity.objects.filter(username=username, source='myexperiment').order_by('-created')[0].created
    except IndexError:
        # If there are no entries then set the latest date to 0
        latest = datetime.datetime.fromtimestamp(0)
        
    for workflow in details.getElementsByTagName('workflow'):
        uri = workflow.getAttribute('uri')
        workflow_page = urllib2.urlopen(uri)
        workflow_details = parse(workflow_page)
        
        dt = parse_date(workflow_details.getElementsByTagName('created-at')[0].childNodes[0].data)
    
        if dt > latest:
            
            wf_url = workflow_details.getElementsByTagName('workflow')[0].getAttribute('resource')
            try:
              wf_title = workflow_details.getElementsByTagName('title')[0].childNodes[0].data
            except:
              wf_title = ""
            try:
              wf_subtitle = workflow_details.getElementsByTagName('description')[0].childNodes[0].data
            except:
              wf_subtitle = ""

            wf_created = parse_date(workflow_details.getElementsByTagName('created-at')[0].childNodes[0].data)
            
            act = Activity.objects.create(
                title = wf_title,
                subtitle = wf_subtitle,
                type = type,
                source = source,
                username = username,
                url = wf_url,
                created = wf_created
            )
            
            # Add the tags to the activity object
            for tag in workflow_details.getElementsByTagName('tag'):
                clean_tag = tag.childNodes[0].data.lower()
                act.tags.add(clean_tag)
            
            # Increase the new activities counter
            new_activities += 1
    
    # return the amount of activities that have been updated
    return HttpResponse(simplejson.dumps(new_activities), mimetype='application/javascript')
    

def all_myexperiment_accounts(request):
    for account in ExternalApplication.objects.filter(application='myexperiment'):
        myexperiment(account.username)

    return HttpResponse(simplejson.dumps(True), mimetype='application/javascript')


def twitter_fetch(request):
    return twitter(request.GET['username'])

def twitter(username):
    # Request JSON feed for user
    url = "http://api.twitter.com/1/statuses/user_timeline.json?screen_name=%s" % username
    data = urllib2.urlopen(url).read()
    tweets = simplejson.loads(data)
    
    new_activities = 0 # Initialise number of new activities for user
    type = "status"
    source = "twitter"
    
    try:
        # Set the `latest` date to the most recently created bookmark for the user
        latest = Activity.objects.filter(username=username, source='twitter').order_by('-created')[0].created
    except IndexError:
        # If there are no entries then set the latest date to 0
        latest = datetime.datetime.fromtimestamp(0)
        
    for tweet in tweets:
        title = tweet['text'].encode('utf8')
        print title
        subtitle = ""
        username = tweet['user']['screen_name'].encode('utf8')
        print username
        url = "http://twitter.com/#!/"+username+"/status/"+str(tweet['id']).encode('utf8')
        print url
        created = parse_date(tweet['created_at'].encode('utf8'))
        print created
                
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
            
            tags = re.findall(r"#(\w+)", title)

            # Add the tags to the activity object
            for tag in tags:
                clean_tag = tag.lower().encode('utf8')
                act.tags.add(clean_tag)

            # Increase the new activities counter
            new_activities += 1

    # return the amount of activities that have been updated
    return HttpResponse(simplejson.dumps(new_activities), mimetype='application/javascript')

def all_twitter_accounts(request):
    for account in ExternalApplication.objects.filter(application='twitter'):
        twitter(account.username)

    return HttpResponse(simplejson.dumps(True), mimetype='application/javascript')

def connotea_fetch(request):
    return connotea(request.GET['username'])

def connotea(username):
    url = 'http://www.connotea.org/data/user/%s' % username
    auth_un = 'davej'
    auth_pw = 'travis'
    
    req = urllib2.Request(url)
    passman = urllib2.HTTPPasswordMgrWithDefaultRealm()
    passman.add_password(None, url, auth_un, auth_pw)
    
    authhandler = urllib2.HTTPBasicAuthHandler(passman) 
    opener = urllib2.build_opener(authhandler)
    
    data = opener.open(url)
    xml_data = parse(data)
    
    new_activities = 0 # Initialise number of new activities for user
    type = "citation"
    source = "connotea"
    
    try:
        # Set the `latest` date to the most recently created bookmark for the user
        latest = Activity.objects.filter(username=username, source='connotea').order_by('-created')[0].created
    except IndexError:
        # If there are no entries then set the latest date to 0
        latest = datetime.datetime.fromtimestamp(0)
   
        
    for post in xml_data.getElementsByTagName('Post'):
        title = post.getElementsByTagName('title')[0].childNodes[0].data
        print title
        
        try:
            url = post.getElementsByTagName('uri')[0].getElementsByTagName('link')[0].childNodes[0].data
        except:
            url = ""
        try:
            subtitle = post.getElementsByTagName('description')[0].childNodes[0].data
        except:
            subtitle = ""
        created = parse_date(post.getElementsByTagName('created')[0].childNodes[0].data)
        
        if created > latest:
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
            for tag in post.getElementsByTagName('dc:subject'):
                clean_tag = tag.childNodes[0].data.lower()
                act.tags.add(clean_tag)

            # Increase the new activities counter
            new_activities += 1
            
    return HttpResponse(simplejson.dumps(new_activities), mimetype='application/javascript')

def all_connotea_accounts(request):
    for account in ExternalApplication.objects.filter(application='connotea'):
        connotea(account.username)

    return HttpResponse(simplejson.dumps(True), mimetype='application/javascript')