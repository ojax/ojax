from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template
from django.shortcuts import redirect

def my_view(request):
    if request.user.get_profile().name:
        return redirect('/projects/')
    else:
        return redirect('/profiles/edit')

urlpatterns = patterns("",
    url(r"^$", direct_to_template, {"template": "about/about.html"}, name="about"),
    
    url(r"^terms/$", direct_to_template, {"template": "about/terms.html"}, name="terms"),
    url(r"^privacy/$", direct_to_template, {"template": "about/privacy.html"}, name="privacy"),
    url(r"^dmca/$", direct_to_template, {"template": "about/dmca.html"}, name="dmca"),
    
    url(r"^what_next/$", my_view, name="what_next"),
)
