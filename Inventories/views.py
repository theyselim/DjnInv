from django.http import HttpResponseRedirect, HttpResponse, StreamingHttpResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from Inventories.models import Inventory, Item, Transaction, ItemTransaction
from django.shortcuts import redirect
from django.core.urlresolvers import reverse
from django.core.mail import send_mail, BadHeaderError
from django.utils import timezone
import json, re, datetime
from decimal import *


########## RENDERING VIEWS #####################
s = 'Inventories/'
#Homepage view: Showing inventories
#@login_required
def index(request):
	date_now = timezone.now()
	date_past = date_now - datetime.timedelta(days=90)
	# Transactions that happened during the past  90 days, only tickets sorted by recent
	transactions_list = Transaction.objects.all().filter(t_type='TI', date_created__range=(date_past, date_now)).order_by('-date_created')
	# Each of the top items with values for each - month (#, names), to be added to context
	top_items_list = getTopItems(transactions_list)
	top_items_months_list = []
	
	for i in range(3):
		that_date = date_now - datetime.timedelta(days=30)*i
		top_items_months_list.append((that_date.strftime('%B'), that_date.month, getItemsMonth(that_date.month, top_items_list, transactions_list)))
	
	# print top_items_list
	print top_items_months_list

	inventories_list = Inventory.objects.all().order_by('date_created')
	context = {'inventories_list': inventories_list,
	'top_items_list': top_items_list, 
	'top_items_months_list': reversed(top_items_months_list)
	}
	return render(request, s+'index.html', context)


#Inventory view according to the one selected from index view
@login_required
def inventory(request, inventory_id):
	inventory = get_object_or_404(Inventory, pk=inventory_id)
	all_inven_items = inventory.item_set.all()#Uncomment for Alpha ordering .order_by('description')
	items_price_diff = getPriceDifference(all_inven_items)
	final_list = zip(all_inven_items, items_price_diff)
	# Get propsective transaction id, according to the last id in the transactions table
	transaction_id = 1 if Transaction.objects.all().count() == 0 else Transaction.objects.all()[Transaction.objects.all().count()-1].id + 1
	date_now =  str(timezone.now().month) + '/' + str(timezone.now().day) + '/'+ str(timezone.now().year)

	context = {'inventory_object': inventory, 
	'inventory':  final_list, 
	'transaction_num': transaction_id, 
	'date_now': date_now
	}

	# Checking on the referer, last function explains this part
	if (request.META.get('HTTP_REFERER') is None) or (len(re.sub('^https?:\/\/', '', request.META.get('HTTP_REFERER')).split('/')) < 4):
		request.session['error_msg'] = ''

	return render(request, s+'inventory.html', context)


#Perform transaction operation from Order POST form, redirect to updated inventory
@login_required
def transaction(request, inventory_id):
	inventory = get_object_or_404(Inventory, pk=inventory_id)
	items_list = request.POST.getlist('item')
	cases_dealt_list = request.POST.getlist('cases')
	t_type=request.POST.get('transactionType')
	fees = request.POST.get('fees')
	# reseting fees if null
	if not fees:
		fees = 0.0
	# replacing item id with their corresponding objects
	for i,item in enumerate(items_list):
		items_list[i] = Item.objects.get(id=item)

	if Decimal(fees) < 0:
		request.session['message'] = 'Make sure your fees are not negative'
		request.session['error_msg'] = 'true'
		return HttpResponseRedirect(reverse('Inventories:inventory', args=(inventory.id,)))

	for i,item in enumerate(items_list):
		if t_type == 'RE':
			item.cases += int(cases_dealt_list[i])
		else:
			item.cases -= int(cases_dealt_list[i])
		#Make sure that cases are in inventory
		if item.cases < 0:
			request.session['message'] = 'You don\'t have enough cases'
			request.session['error_msg'] = 'true'
			return HttpResponseRedirect(reverse('Inventories:inventory', args=(inventory.id,))) 
		item.save()

	new_transaction = Transaction(description=request.POST.get('description'), fees=fees, t_type=t_type)
	new_transaction.save()
	
	for i,item in enumerate(items_list):
		itemsToTransaction = ItemTransaction(item=item, transaction=new_transaction, cases_dealt=int(cases_dealt_list[i]))
		itemsToTransaction.save()

	request.session['message'] = 'Your new order has been submitted successfully'
	request.session['error_msg'] = 'false'
	return HttpResponseRedirect(reverse('Inventories:inventory', args=(inventory.id,))) 


# Reporting problem sent to my default email
@login_required
def reportProblem(request):
	subject = 'Inventory Managemnt Problem Reported'
	message = request.POST.get('reportMessage')
	from_email = 'webmaster@localhost'
	
	try:
		send_mail(subject, message, from_email, ['youssefahmed91@hotmai.com'], fail_silently=False)
	except BadHeaderError:
		return HttpResponse('Invalid header found.')

	return HttpResponse()
	#HttpResponseRedirect(reverse('Inventories:index'))
 
#Viewing orders/transactions archive

def archive(request):
	last_15_transactions = Transaction.objects.all().order_by('-id')[:15]

	#Google facebook news feed stories/feed load
	context = {'last_15_transactions': last_15_transactions,
	}
	return render(request, s+'archive.html', context)

##########################################
######### ADDITIONAL OPERATIONS ##########
def getPriceDifference(inv_list):
	price_diff_list = []
	
	for item in inv_list:
		if (item.curr_price is None) or (item.curr_price == item.def_price):
			price_diff_list.append('-')
		else: #item.curr_price - item.def_price > 0:
			price_diff_list.append(str(item.curr_price - item.def_price))
		# else:
		# 	price_diff_list.append(str(item.curr_price - item.def_price))
	
	return price_diff_list


# Returns Top 3 items in the last 90 period
def getTopItems(transactions_list):
	# Items - Transaction relation table corresponding to the last 90 days
	itemTransaction_list = ItemTransaction.objects.all().filter(transaction__in=transactions_list)
	top_items_list = []

	# Looping through all transactions & items least, adding a list with corresponding items and all 
	# cases that were taken out of the inventory, returning a sorted list of top 3 items
	for itemTrans in itemTransaction_list:
		if any(itemTrans.item in current_item for current_item in top_items_list):
			index = [i for i, saved_item in enumerate(top_items_list) if saved_item[0] == itemTrans.item]
			top_items_list[index[0]] = (itemTrans.item, top_items_list[index[0]][1] + itemTrans.cases_dealt)
		else:
			top_items_list.append((itemTrans.item, itemTrans.cases_dealt))

	return sorted(top_items_list, key=lambda x:x[1], reverse=True)[:3]


# Returns item cases values per month
def getItemsMonth(month, items_list, transactions_list):
	month_data = []
	# get for each item per month, the cases dealt amount
	for item in items_list:
		transactions_month_list = transactions_list.filter(date_created__month = month)
		item_per_trans_list = ItemTransaction.objects.all().filter(transaction__in = transactions_month_list, item__in = item)
		if len(item_per_trans_list) == 0:
			month_data.append(0)
		else:
			total_cases = 0
			for i in item_per_trans_list:
				total_cases += i.cases_dealt
			month_data.append(total_cases)

	return month_data

'''
def get_referer_view(request, default=None):
   
   	#Return the referer view of the current request
    # if the user typed the url directly in the browser's address bar
    referer = request.META.get('HTTP_REFERER')
    if not referer:
        return default

    # remove the protocol and split the url at the slashes
    referer = re.sub('^https?:\/\/', '', referer).split('/')
    #if referer[0] != request.META.get('SERVER_NAME'):
     #   return default

    # add the slash at the relative path's view and finished
    referer = u'/' + u'/'.join(referer[1:])
    return referer
'''