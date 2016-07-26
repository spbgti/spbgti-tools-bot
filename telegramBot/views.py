from django.shortcuts import render
from django.http import HttpResponse
from telegramBot import bot
import urllib
import json
from spbgtitoolsbot import settings
from . import bot

import sys

import time
import telepot




def index(request):

    if bot.start() == True:

       return HttpResponse("Это работает!")




