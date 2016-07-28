#! /usr/bin/env python
# -*- coding: utf-8 -*-

from django.shortcuts import render
from django.http import HttpResponse
from . import bot


def index(request):
    if bot.start():
        return HttpResponse("Это работает!")