#! /usr/bin/env python
# -*- coding: utf-8 -*-

from django.http import HttpResponse

from bot import start


def index(request):
    if start.start():
        return HttpResponse("Это работает!")