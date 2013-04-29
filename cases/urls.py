from django.views.generic import ListView
from django.conf.urls import patterns, url
from .models import Case

urlpatterns = patterns('',
    url(r'list/$', ListView.as_view(model=Case, context_object_name='list')),

)