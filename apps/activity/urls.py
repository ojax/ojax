from django.conf.urls.defaults import *

urlpatterns = patterns('activity.parsers',
                       (r'^update_delicious/$', 'delicious_fetch', {}, 'update_delicious'),
                       (r'^update_delicious/all/$', 'all_delicious_accounts', {}, 'update_all_delicious'),
                       (r'^make_comment/$', 'make_comment', {}, 'make_comment'),
                      )
