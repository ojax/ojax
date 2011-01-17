from django.conf.urls.defaults import *

urlpatterns = patterns('projects.views',
                       # (r'^()/$', 'callback', {}, 'pubsubhubbub_callback'),
                       (r'^(?P<project_id>\d+)/$', 'project_view', {}, 'project_view'),
                       (r'^$', 'project_list', {}, 'project_list'),
                       (r'^new/$', 'new_project', {}, 'new_project'),
                       (r'^json/$', 'json_project_activities', {}, 'json_project_activities'),
                       )
