from django.conf import settings
from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template
from django.shortcuts import redirect

from django.contrib import admin
admin.autodiscover()

from pinax.apps.account.openid_consumer import PinaxConsumer



handler500 = "pinax.views.server_error"


if settings.ACCOUNT_OPEN_SIGNUP:
    signup_view = "pinax.apps.account.views.signup"
else:
    signup_view = "pinax.apps.signup_codes.views.signup"

def home_view(request):
    if request.user.is_authenticated():
        return redirect('/projects/')
    else:
        return redirect('/account/login/')

urlpatterns = patterns("",
    url(r"^$", home_view, name="home"),
    
    url(r"^admin/invite_user/$", "pinax.apps.signup_codes.views.admin_invite_user", name="admin_invite_user"),
    url(r"^account/signup/$", signup_view, name="acct_signup"),
    
    (r"^about/", include("about.urls")),
    (r"^account/", include("pinax.apps.account.urls")),
    (r"^openid/(.*)", PinaxConsumer()),
    (r"^profiles/", include("basic_profiles.urls")),
    (r"^notices/", include("notification.urls")),
    (r"^announcements/", include("announcements.urls")),    
    
    (r"^admin/", include(admin.site.urls)),
    
    # (r"^pshb/", include("djpubsubhubbub.urls")),
    
    (r"^projects/", include("projects.urls")),
    (r"^activity/", include("activity.urls")),
    
)


if settings.SERVE_MEDIA:
    urlpatterns += patterns("",
        (r"", include("staticfiles.urls")),
    )
