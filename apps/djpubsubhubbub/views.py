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

from datetime import datetime
import feedparser
from django.views.decorators.csrf import csrf_exempt

from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404

from djpubsubhubbub.models import Subscription
from djpubsubhubbub.signals import verified, updated

@csrf_exempt
def callback(request, pk):
    if request.method == 'GET':
        mode = request.GET['hub.mode']
        topic = request.GET['hub.topic']
        challenge = request.GET['hub.challenge']
        lease_seconds = request.GET.get('hub.lease_seconds')
        verify_token = request.GET.get('hub.verify_token', '')

        if mode == 'subscribe':
            if not verify_token.startswith('subscribe'):
                raise Http404
            subscription = get_object_or_404(Subscription,
                                             pk=pk,
                                             topic=topic,
                                             verify_token=verify_token)
            subscription.verified = True
            subscription.set_expiration(int(lease_seconds))
            verified.send(sender=subscription)

        return HttpResponse(challenge, content_type='text/plain')
    elif request.method == 'POST':
        subscription = get_object_or_404(Subscription, pk=pk)
        parsed = feedparser.parse(request.raw_post_data)
        if parsed.feed.links: # single notification
            hub_url = subscription.hub
            self_url = subscription.topic
            for link in parsed.feed.links:
                if link['rel'] == 'hub':
                    hub_url = link['href']
                elif link['rel'] == 'self':
                    self_url = link['href']

            needs_update = False
            if hub_url and subscription.hub != hub_url:
                # hub URL has changed; let's update our subscription
                needs_update = True
            elif self_url != subscription.topic:
                # topic URL has changed
                needs_update = True

            if needs_update:
                expiration_time = subscription.lease_expires - datetime.now()
                seconds = expiration_time.days*86400 + expiration_time.seconds
                Subscription.objects.subscribe(
                    self_url, hub_url,
                    callback=request.build_absolute_uri(),
                    lease_seconds=seconds)

            updated.send(sender=subscription, update=parsed)
            return HttpResponse('')
    return Http404
