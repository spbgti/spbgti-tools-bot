#! /usr/bin/env python
# -*- coding: utf-8 -*-
from django.conf.urls import url
from . import views
from . import bot

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^(?P<token>.+)/$', bot.webhook),
]


