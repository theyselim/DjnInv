from django.db import models
from django.utils import timezone
from datetime import datetime

class Inventory(models.Model):
	class Meta:
		verbose_name_plural = "inventories"

	#Model Attributes
	name = models.CharField(max_length=200)
	description = models.CharField(max_length=600)
	date_created = models.DateTimeField('Date Created', default=timezone.now())

	def __unicode__(self):
		return self.name + ': ' + self.description



class Item(models.Model):
	#Relationships with Inventory
	inventory = models.ForeignKey(Inventory)
	#Model Attributes
	item_number = models.IntegerField(blank=False)
	description = models.CharField(max_length=600)
	quantity = models.CharField(max_length=100, default=0)
	amount = models.CharField(max_length=100, default='1')
	cases = models.IntegerField(default=0)
	def_price = models.DecimalField(max_digits=5, decimal_places=2, null=False, verbose_name="default price")
	curr_price = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name="current price")
	last_modified = models.DateTimeField('Last Modified', default=timezone.now())

	def __unicode__(self):
		return 'Item#' + str(self.item_number) + ': '+ self.description


class Transaction(models.Model):
	#RelationShips with Inventory & Item
	#inventory = models.ForeignKey(Inventory)
	items = models.ManyToManyField(Item, through='ItemTransaction')
	#Model Attributes
	description = models.CharField(max_length=600)
	date_created = models.DateTimeField('Date Created', default=timezone.now())
	fees = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
	#Transaction Type
	TRANSACTION_TYPE = (('RE', 'Reciept'), ('TI', 'Ticket'),)
	t_type = models.CharField(max_length=2, choices=TRANSACTION_TYPE)
	
	#Return Current Transaction subtotal
	def _get_transaction_subtotal(self):
		trans_subtotal = 0
		for item in self.itemtransaction_set.all():
			trans_subtotal += float(item.subtotal)
		return trans_subtotal

	subtotal = property(_get_transaction_subtotal)

	def __unicode__(self):
		return 'Transaction#' + str(self.id) + ': ' + self.description + '- created on: ' + str(self.date_created.month) +'/' + str(self.date_created.day) +'/' + str(self.date_created.year) 


#Intermediatry Table ManyToMany Relation Transaction:Item
class ItemTransaction(models.Model):
	item = models.ForeignKey(Item)
	transaction = models.ForeignKey(Transaction)
	cases_dealt = models.IntegerField()

	#Return Current Item subtotal
	def _get_item_subtotal(self):
		if self.item.curr_price is None:
			return self.item.def_price * self.cases_dealt
		else:
			return self.item.curr_price * self.cases_dealt
	
	subtotal = property(_get_item_subtotal)
	
	def __unicode__(self):
		return 'Item-Transaction #' + str(self.id)

