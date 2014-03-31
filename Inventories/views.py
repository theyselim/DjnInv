from django.shortcuts import render, get_object_or_404
from Inventories.models import Inventory, Item, Transaction
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse

s = 'Inventories/'

#Homepage view: Showing inventories
def index(request):
	inventories_list = Inventory.objects.all().order_by('-date_created')
	context = {'inventories_list': inventories_list}
	return render(request, s+'index.html', context)


#Inventory view according to the one selected from index view
def inventory(request, inventory_id):
	inventory = get_object_or_404(Inventory, pk=inventory_id)
	context = {'inventory': inventory}
	return render(request, s+'inventory.html', context)

