#! /usr/bin/env python
# -*- coding: utf-8 -*-
from django.conf.urls import url

from spbgtitoolsbot import settings
from . import bot

urlpatterns = [
    url(r'^%s/$' % settings.TOKEN, bot.webhook),
]


