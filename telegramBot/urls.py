#! /usr/bin/env python
# -*- coding: utf-8 -*-
from django.conf.urls import url
from . import views
from . import bot
from spbgtitoolsbot import settings
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^(?P<token>.+)/$', bot.webhook),
]


