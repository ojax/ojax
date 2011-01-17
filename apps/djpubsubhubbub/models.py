# Copyright 2009 - Participatory Culture Foundation
# 
# This file is part of djpubsubhubbub.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
# 
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
# 
# THIS SOFTWARE IS PROVIDED BY THE AUTHOR ``AS IS'' AND ANY EXPRESS OR
# IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES
# OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
# IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT
# NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF
# THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

from datetime import datetime, timedelta
import feedparser
from urllib import urlencode
import urllib2
from urllib2 import URLError

from django.conf import settings
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse, Resolver404
from django.db import models
from django.utils.hashcompat import sha_constructor

from djpubsubhubbub import signals

DEFAULT_LEASE_SECONDS = 2592000 # 30 days in seconds

class SubscriptionManager(models.Manager):

    def subscribe(self, topic, hub=None, callback=None,
                  lease_seconds=None):
        if hub is None:
            hub = self._get_hub(topic)

        if hub is None:
            raise TypeError(
                'hub cannot be None if the feed does not provide it')

        if lease_seconds is None:
            lease_seconds = getattr(settings, 'PUBSUBHUBBUB_LEASE_SECONDS',
                                   DEFAULT_LEASE_SECONDS)

        subscription, created = self.get_or_create(
            hub=hub, topic=topic)
        signals.pre_subscribe.send(sender=subscription, created=created)
        subscription.set_expiration(lease_seconds)

        if callback is None:
            try:
                callback_path = reverse('pubsubhubbub_callback',
                                        args=(subscription.pk,))
            except Resolver404:
                raise TypeError(
                    'callback cannot be None if there is not a reverable URL')
            else:
                callback = 'http://' + str(Site.objects.get_current()) + \
                    callback_path
                    
        print callback                            
        response = self._send_request(hub, {
                'mode': 'subscribe',
                'callback': callback,
                'topic': topic,
                'verify': ('async', 'sync'),
                'verify_token': subscription.generate_token('subscribe'),
                'lease_seconds': lease_seconds,
                })

        info = response.info()
        print info.status
        if info.status == 204:
            subscription.verified = True
        elif info.status == 202: # async verification
            subscription.verified = False
        else:
            error = response.read()
            raise urllib2.URLError('error %s subscribing to %s on %s:\n%s' % (
                    info.status, topic, hub, error))

        subscription.save()
        if subscription.verified:
            signals.verified.send(sender=subscription)
        return subscription


    def _get_hub(self, topic):
        parsed = feedparser.parse(topic)
        for link in parsed.feed.links:
            if link['rel'] == 'hub':
                return link['href']

    def _send_request(self, url, data):
        def data_generator():
            for key, value in data.items():
                key = 'hub.' + key
                if isinstance(value, (basestring, int)):
                    yield key, str(value)
                else:
                    for subvalue in value:
                        yield key, subvalue
        encoded_data = urlencode(list(data_generator()))
        try:
            return urllib2.urlopen(url, encoded_data)
        except URLError, e:
            print e.code
            print e.read()

class Subscription(models.Model):

    hub = models.URLField()
    topic = models.URLField()
    verified = models.BooleanField(default=False)
    verify_token = models.CharField(max_length=60)
    lease_expires = models.DateTimeField(default=datetime.now)

    objects = SubscriptionManager()

    # class Meta:
    #     unique_together = [
    #         ('hub', 'topic')
    #         ]

    def set_expiration(self, lease_seconds):
        self.lease_expires = datetime.now() + timedelta(
            seconds=lease_seconds)
        self.save()

    def generate_token(self, mode):
        assert self.pk is not None, \
            'Subscription must be saved before generating token'
        token = mode[:20] + sha_constructor('%s%i%s' % (
                settings.SECRET_KEY, self.pk, mode)).hexdigest()
        self.verify_token = token
        self.save()
        return token

    def __unicode__(self):
        if self.verified:
            verified = u'verified'
        else:
            verified = u'unverified'
        return u'to %s on %s: %s' % (
            self.topic, self.hub, verified)

    def __str__(self):
        return str(unicode(self))