from django.conf.urls.defaults import *

urlpatterns = patterns('activity.parsers',
                       (r'^update_delicious/$', 'delicious', {}, 'update_delicious'),
                       (r'^make_comment/$', 'make_comment', {}, 'make_comment'),
                       )
