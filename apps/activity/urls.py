from django.conf.urls.defaults import *

urlpatterns = patterns('activity.parsers',
    (r'^update_delicious/$', 'delicious_fetch', {}, 'update_delicious'),
    (r'^update_delicious/all/$', 'all_delicious_accounts', {}, 'update_all_delicious'),

    (r'^update_myexperiment/$', 'myexperiment_fetch', {}, 'update_myexperiment'),
    (r'^update_myexperiment/all/$', 'all_myexperiment_accounts', {}, 'update_all_myexperiment'),

    (r'^update_twitter/$', 'twitter_fetch', {}, 'update_twitter'),
    (r'^update_twitter/all/$', 'all_twitter_accounts', {}, 'update_all_twitter'),


    (r'^make_comment/$', 'make_comment', {}, 'make_comment'),
)
