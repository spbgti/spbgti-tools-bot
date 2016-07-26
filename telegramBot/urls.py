from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
]




#from .views import CommandReceiveView

#urlpatterns = [
#    url(r'^bot/(?P<bot_token>.+)/$', CommandReceiveView.as_view(), name='command'),
#]


