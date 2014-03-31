from django.conf.urls import patterns, url

from Inventories import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^(?P<inventory_id>\d+)/$', views.inventory, name='inventory'),
    # url(r'^(?P<inventory_id>\d+)/results/$', views.ResultsView.as_view(), name='results'),
    # url(r'^(?P<poll_id>\d+)/vote/$', views.vote, name='vote'),
    )