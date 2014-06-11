from django.conf.urls import patterns, url

from Inventories import views

urlpatterns = patterns('',
	url(r'^$', views.index, name='index'),
	url(r'^logout/$', views.logoutInv, name='logout'),
	url(r'^report/$', views.reportProblem, name='report'),
	url(r'^inventories/(?P<inventory_id>\d+)/$', views.inventory, name='inventory'),
	url(r'^archive/$', views.archive, name='archive'),
	url(r'^archive/order/$', views.getTransactionInfo, name='transactionInfo'),
	url(r'^inventories/(?P<inventory_id>\d+)/transaction/$', views.transaction, name='transaction'),
	)