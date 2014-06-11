from django.http import HttpResponseRedirect, HttpResponse, StreamingHttpResponse, Http404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from Inventories.models import Inventory, Item, Transaction, ItemTransaction
from django.shortcuts import redirect
from django.core.urlresolvers import reverse
from django.core.mail import EmailMessage, BadHeaderError
from django.utils import timezone
import json, re, datetime
from django.utils import simplejson as json
from django.core import serializers
from decimal import *


########## RENDERING VIEWS #####################
s = 'Inventories/'
#Homepage view: Authenticating users and displaying current inventories
def index(request):
	# Redirect to login page
	if request.user.is_anonymous() and request.method != 'POST':
		return render(request, 'registration/login.html')

	# Authenticate submitted credentials
	elif request.method == 'POST':
		if loginInv(request, request.POST.get('username'), request.POST.get('password')):
			return loadIndex(request)
		else:
			context = {'err_message': 'Invalid credentials. Please try again'}
			return render(request, 'registration/login.html', context)
	elif request.user.is_authenticated():
		return loadIndex(request)
		
#Homepage view: Inventories View / Helper Function
def loadIndex(request):
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
	
	inventories_list = Inventory.objects.all().order_by('date_created')
	context = {'inventories_list': inventories_list,
	'top_items_list': top_items_list, 
	'top_items_months_list': reversed(top_items_months_list)
	}
	return render(request, s+'index.html', context)
		

#Logout function
@login_required(login_url='/')
def logoutInv(request):
	logout(request)
	context = {'forgot': 'Logged Out!'}
	return render(request, 'registration/login.html', context)


#Inventory view according to the one selected from index view
@login_required(login_url='/')
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
@login_required(login_url='/')
def transaction(request, inventory_id):
	inventory = get_object_or_404(Inventory, pk=inventory_id)

	# Avoid guest account from messing with orders
	if request.user.username == 'guest':
		request.session['message'] = 'Guest account can\'t create orders'
		request.session['error_msg'] = 'true'
		return HttpResponseRedirect(reverse('Inventories:inventory', args=(inventory.id,)))

	items_list = request.POST.getlist('item')
	cases_dealt_list = request.POST.getlist('cases')
	t_type = request.POST.get('transactionType')
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


#Reporting problem sent to my default email
@login_required(login_url='/')
def reportProblem(request):
	message = request.POST.get('reportMessage')
	
	try:
		email = EmailMessage('Inventory Managemnt Problem Reported', message, to=['youssefahmed91@hotmail.com'])
		email.send()
	except BadHeaderError:
		return HttpResponse('Invalid header found.')

	# Just send the email amigo
	return HttpResponse()


#Viewing orders/transactions archive
@login_required(login_url='/')
def archive(request):
	# If user is asking to view more orders
	if request.is_ajax() and request.method == 'POST':
		latest_transaction_id = int(request.POST.get('latest_id'))
		next_5_transactions = []

		# Get the 5 objects available after the current one
		for x in range(1,6):
			if latest_transaction_id-x > 0:
				current_transaction = Transaction.objects.all().values_list('id', 'description').filter(id=latest_transaction_id-x)[0]
				next_5_transactions.append(current_transaction)

		return HttpResponse(json.dumps(next_5_transactions), mimetype="application/json")

	# get latest orders for first page load
	last_5_transactions = Transaction.objects.all().order_by('-id')[:5]
	print last_5_transactions
	context = {'last_5_transactions': last_5_transactions,
	}
	return render(request, s+'archive.html', context)

#Retrieving certain transaction info / Archive helper function
@login_required(login_url='/')
def getTransactionInfo(request):
	data = {}
	if request.is_ajax() and request.method == 'POST':
		requested_transaction_info = Transaction.objects.get(pk=int(request.POST.get('order_id')))
		data['fees'] = requested_transaction_info.fees
		data['trans_desc'] = requested_transaction_info.description
		data['t_type'] =  requested_transaction_info.t_type
		data['date'] =  requested_transaction_info.date_created.strftime('%m/%d/%Y')
		data['subtotal'] = requested_transaction_info.subtotal
		
		itemTransaction_list = ItemTransaction.objects.all().filter(transaction=requested_transaction_info).values_list('item', 'cases_dealt')
		items = []
		for item in itemTransaction_list:
			itemObj = Item.objects.get(pk=item[0])
			price = itemObj.curr_price
			if itemObj.curr_price is None:
				price = itemObj.def_price
			items.append((itemObj.description, itemObj.quantity, item[1], float(price), (itemObj.inventory).name))
		data['items'] = items

	else:
		raise Http404

	return HttpResponse(json.dumps(data, default=handleDecimal), mimetype="application/json")

# Handling Decimal fields with JSON
def handleDecimal(obj):
	if isinstance(obj, Decimal):
		return float(obj)
	else:
		return obj



##########################################
######### ADDITIONAL OPERATIONS ##########
def getPriceDifference(inv_list):
	price_diff_list = []
	
	for item in inv_list:
		if (item.curr_price is None) or (item.curr_price == item.def_price):
			price_diff_list.append('-')
		else:
			price_diff_list.append(str(item.curr_price - item.def_price))
	
	return price_diff_list


# Returns Top 3 items in the last 90 period
def getTopItems(transactions_list):
	# Items - Transaction relation table corresponding to the last 90 days
	itemTransaction_list = ItemTransaction.objects.all().filter(transaction__in=transactions_list)
	top_items_list = []

	# Looping through all transactions & items lists, adding a list with corresponding items and all 
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

#Login function: Verifying user's credentials
def loginInv(request, username, password):
	user = authenticate(username=username, password=password)
	if user is not None:
		if user.is_active:
			login(request, user)
			return True
			print("User is valid, active and authenticated")
		else:
			return False
			print("The password is valid, but the account has been disabled!")
	else:
		return False
		print("The username and password were incorrect.")
