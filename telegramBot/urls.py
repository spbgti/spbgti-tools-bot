#! /usr/bin/env python
# -*- coding: utf-8 -*-
from django.conf.urls import url

from bot import start
from spbgtitoolsbot import settings
from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^%s/$' % settings.TOKEN, start.webhook),
]


