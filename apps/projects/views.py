from django.shortcuts import render_to_response, get_object_or_404
from projects.models import Project
from projects.forms import NewProjectForm
from themes.models import Theme
from django.template import RequestContext
import time
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.utils import simplejson


@login_required
def project_view(request, project_id, template_name="projects/project.html"):
    
    project = get_object_or_404(Project, id=project_id)
    theme = Theme.objects.get(active=True)
    
    items = project.items()
    # last_updated_stamp = str(int(time.mktime(items[0].created.timetuple())))
    try:
        delicious_username = request.user.externalapplication_set.get(application='delicious').username
    except:
        delicious_username = ""
    
    
    return render_to_response(template_name, {
        "theme": theme,
        "project": project,
        "items": items,
        "delicious_username": delicious_username,
    }, context_instance=RequestContext(request))
    

@login_required
def project_list(request, template_name="projects/project_list.html"):

    projects = Project.objects.all()


    return render_to_response(template_name, {
        "projects": projects,
    }, context_instance=RequestContext(request))
    
def json_project_activities(request):
    """docstring for json_project_activities"""
    
    timestamp = int(request.GET['dt'])
    pid = int(request.GET['id'])
    
    project = get_object_or_404(Project, id=pid)
    
    
    items = project.items(timestamp)
    
    objs = []
    for item in items:        
        # p.items()[0].tags.all().values()
        
        objs.append({
            "username": item.username,
            "tags": [tag['name'] for tag in item.tags.values()],
            "type": item.type,
            "source": item.source,
            "title":item.title,
            "subtitle": item.subtitle,
            "dt": "just now",
        })
        
    return HttpResponse(simplejson.dumps(objs), mimetype='application/javascript')
    
@login_required
def new_project(request, form_class=NewProjectForm, **kwargs):

    template_name = kwargs.get("template_name", "projects/project_new.html")

    if request.method == "POST":
        project_form = form_class(request.POST)
        if project_form.is_valid():
            project = project_form.save()
            return HttpResponseRedirect(reverse("project_view", args=[project.id]))
    else:
        project_form = form_class()

    return render_to_response(template_name, {
        "project_form": project_form,
    }, context_instance=RequestContext(request))
    
