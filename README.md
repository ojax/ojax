# OJAX++

OJAX++ is a Virtual Research Environment (VRE). It aims to help researchers work collaboratively by providing a project management and collaboration interface for research activity conducted using third party tools like Delicious, Gmail and MyExperiment.

See the website for more information: [http://www.ucd.ie/ojax/](http://www.ucd.ie/ojax/).

## Note

This is an old (but functional) branch of OJAX++. New changes are coming so it might be worth waiting until I have tested and committed the changes.
Features that I haven't fully tested (like websockets) have been turned off in this branch, it also relies on older code for fetching activity from third-party APIs. I am working at testing the new features properly and moving to a node.js backend for scraping activities. You can [follow development of the new activity scraper](http://github.com/davej/node-wsscraper) if you're interested.

## License

Licensed under the BSD license, see the `LICENSE` file for the full text.

## Installation

### Requirements

Before you get started, you must have the following installed:

* [Python](http://www.python.org/) 2.4+ — Most Linux distributions will have this installed already.
* [Virtualenv](http://pypi.python.org/pypi/virtualenv) — OJAX++ uses virtualenv to manage packages and dependancies. Assuming that you already have python installed you should be able to run it with `easy_install virtualenv`.
* SQLite/MySQL/PostreSQL — OJAX++ uses the Django ORM so any of these is fine.

### STEP 1: Activating Virtualenv

OJAX++ uses virtualenv to create isolated Python environments.

Create yourself a virtual environment and activate it:

	$ virtualenv ojax-env
	$ source ojax-env/bin/activate
	(ojax-env)$

### STEP 2: Installing Dependancies

We are now inside of the `ojax-env` virtual environment. While still inside of the virtual environment, navigate to the directory where you have checked out a copy of OJAX++ and run the following command:
	
	(ojax-env)$ pip install -r ojax-req.txt
	
This will install each of the dependancies from the ojax-req.txt, this may take a few minutes to complete.

### STEP 3: Customization

The settings.py allows for you to set the most common settings. OJAX++ is built using the [pinax platform](http://pinaxproject.com/) and it's worthwhile checking out the [customization options](http://pinaxproject.com/docs/dev/customization/). The `templates` directory gives you full control over the presentation and markup of OJAX++.

## Fetching activity from third-party services

Below is an example of a script for fetching data from delicious and storing the new activity using the current method. This area of the project is currently being rewritten, so it is likely to change soon.

	def delicious(request):
	    """
	    Query the delicious JSON feed for user and populate a new activity object
	    """
    
	    # Request JSON feed for user
	    url = "http://feeds.delicious.com/v2/json/%s" % request.GET['username']
	    data = urllib2.urlopen(url).read()
	    delicious_bookmarks = simplejson.loads(data)
    
	    new_activities = 0 # Initialise number of new activities for user
    
	    try:
	        # Set the `latest` date to the most recently created bookmark for the user
	        latest = Activity.objects.filter(username=request.GET['username'], source='delicious').order_by('-created')[0].created
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
	    return HttpResponse(simplejson.dumps(new_bookmarks), mimetype='application/javascript')

