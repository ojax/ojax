from django.conf.urls.defaults import *



urlpatterns = patterns("",
    #url(r"^username_autocomplete/$", "pinax.apps.autocomplete_app.views.username_autocomplete_friends", name="profile_username_autocomplete"),
    url(r"^username_autocomplete/$", "pinax.apps.autocomplete_app.views.username_autocomplete_all", name="profile_username_autocomplete"),
    url(r"^$", "basic_profiles.views.profiles", name="profile_list"),
    url(r"^profile/(?P<username>[\w\._-]+)/$", "basic_profiles.views.profile", name="profile_detail"),
    url(r"^edit/$", "basic_profiles.views.profile_edit", name="profile_edit"),
    url(r"^edit/external_app/$", "external_applications.views.add_app", name="profile_app_add"),
)