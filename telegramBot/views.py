from django.shortcuts import render
from django.http import HttpResponse
from . import bot

def index(request):
    if bot.start() == True:
       return HttpResponse("Это работает!")




