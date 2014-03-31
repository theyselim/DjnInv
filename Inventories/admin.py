from django.contrib import admin
from Inventories.models import Inventory, Item, Transaction

class ItemInline(admin.TabularInline):
	model = Item
	extra = 5

class InventoryAdmin(admin.ModelAdmin):
	fieldsets = [
		(None,	{'fields':['name', 'description']}),
		('Date Information', {'fields': ['date_created'], 'classes': ['collapse']}),
	]
	# list_display = ('question', 'pub_date', 'was_published_recently')
	inlines = [ItemInline]
	# list_filter = ['pub_date']
	# search_fields = ['question', 'id']


admin.site.register(Inventory, InventoryAdmin)
