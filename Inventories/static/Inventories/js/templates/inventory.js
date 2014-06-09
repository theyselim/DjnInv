//////////////////////////////////////////
// Notifications Alerts/Updates
//////////////////////////////////////////
$(document).ready(function(){
	var $headerTag = $('#divalicious');
	
	if(usr_msg_status === false){
		$headerTag.addClass( "alert-success" );
		$headerTag.append('<strong>Updated!</strong> ' + usr_msg+ '. This message will be dismissed in 5s');
		$headerTag.css('display', 'block');
	}
	if(usr_msg_status === true){
		$headerTag.addClass( "alert-danger" );
		$headerTag.append('<strong>Sorry!</strong> ' + usr_msg + '. This message will be dismissed in 5s');
		$headerTag.css('display', 'block');
	}

	setTimeout(function(){
		$headerTag.fadeOut("slow", function () {
		});

	}, 5000);

});

//////////////////////////////////////////
// Filter/Search on Inventory Items
//////////////////////////////////////////
$('input.filter').on('keyup', function() {
	var rex = new RegExp($(this).val(), 'i');
	$('.searchable tr').hide();
	$('.searchable tr').filter(function() {
		return rex.test($(this).text());
	}).show();
});

///////////////////////////////////////////////
// Order Modal: Cases # * Price = Subtotal col
///////////////////////////////////////////////
function calcSubCol(){
   // Get Item Price via obtaining the item id prefix
   var id_prefix;
   if((this.id).charAt(((this.id).length-1)) === '_' ){
   	id_prefix = this.id;
   }else{
   	id_prefix = (this.id).substring(0,(this.id).length-5);
   }
   var item_price = $('#' + id_prefix + 'price').val();
   var item_cases = $('#' + id_prefix + 'cases').val();
   var $item_subtotal = $('#' + id_prefix +'subtotal');

	// In case case number was entered before the item description
	if((item_cases>0) && (($('#'+id_prefix).val()).length > 4) && (item_price.length > 0)){
		$item_subtotal.val('$' + Math.round((parseFloat(item_price.substring(1))
			*parseFloat(item_cases))*100)/100);
		// Hide remove popover in case item desc & cases are just being added
		hideRemPop();
	}else{
		$item_subtotal.val('');
	}
	calcSubTot();
}

$('table').on({
	keyup: calcSubCol,
	change: calcSubCol,
	click: calcSubCol
},'input[id$="_"], input[id$="cases"]');

//////////////////////////////////////////////////////
// Order Modal: Adding items (extra row) + Autocomplete
//////////////////////////////////////////////////////
var currentItemCount = 0, currentItemID=0;
var $itemCounter = $('#itemCounter');
var $orderTable = $('#addItem tr');

function addItem(){
	currentItemCount++;
	currentItemID++;
	$itemCounter.html('Total Items: ' + currentItemCount);

	var remove_option = ' onclick="currentItemCount--;'
	+'(this.parentNode.parentNode).parentNode.removeChild(this.parentNode.parentNode);'
	+'$itemCounter.html(\'Total Items: \' + currentItemCount);"';

	$orderTable.last().before('<tr class="item"><td class="order-comp" >'
		+'<input type="text" placeholder="Item Description" id="item'+ currentItemID +'_"/>'
		+'<input type="hidden" name="item" id="item'+ currentItemID +'_ID" value=""></td>'
		+'<td class="order-comp"><input type="text" readonly="readonly" size="6" id="item'+ currentItemID +'_quantity"/></td>'
		+'<td class="order-comp"><input type="text" name="cases" placeholder="Cases #" maxlength="4" id="item'+ currentItemID +'_cases" size="5"/></td>'
		+'<td class="order-comp"><input type="text" readonly="readonly" id="item'+ currentItemID +'_price"size="5"/></td>'
		+'<td class="order-comp"><input type="text" readonly="readonly" id="item'+ currentItemID +'_subtotal"size="6"/></td>'
		+'<td><a href="#" class="item-remove"'
		+ remove_option +'><div style="height:100%; width:100%;"></div></a</td></tr>');

	$('input[id$="_"]').autocomplete({
		source: inventory_items,
		minLength: 0,
		maxShowItems: 5,
		select: function( event, ui ) {
			event.preventDefault();
			this.value = ui.item.value;
			$('#'+ this.id +'price').val('$' + ui.item.price);
			$('#' + this.id +'quantity').val(ui.item.quantity);
			$('#' + this.id +'ID').val(ui.item.id);
		}
	});
	
}

//////////////////////////////////////////////////////
// Order Modal: Calculating subtotals & total in one field
//////////////////////////////////////////////////////
var $final_subtotal = $('#subtotal');
var $fees = $('#fees');
var $total = $('#total');
function calcSubTot(){
	var itemCol_subtotals = $('input[id$="subtotal"]');
	var subtotal = 0;
	var total = 0;
	for(var i = itemCol_subtotals.length-1; i>= 0; i--){
		if((itemCol_subtotals[i].value).length > 0){
			subtotal += parseFloat((itemCol_subtotals[i].value).substring(1));
		}
	}
	$final_subtotal.html('Subtotal: $' + Math.round(subtotal*100)/100);
	
	if($fees.val() > 0){
		total += parseFloat($fees.val());
	}

	total+= subtotal; 
	$total.html('Total: $' + Math.round(total*100)/100);

}

$('input[id="fees"]').on({
	keyup: calcSubTot,
	change: calcSubTot
});

//////////////////////////////////////////////////////
// Order Modal: Validation
//////////////////////////////////////////////////////
var $order_type_sel = $('#transactionType');
var $add_item_btn = $('#addItemBtn');
var $remove_item_linkH = $('#removeItemLnkH');
function validate(){
	var validated = true;
	// Validating the selection on order type
	if($order_type_sel.val() === null){
		$order_type_sel.popover('show');
		validated = false;
	}
	var $items = $('.item');

	// Validating that at least 1 item is added
	var i = $items.length-1;
	if(i < 0){
		$add_item_btn.popover('show');
		validated = false;
	}else{
		var item_id, item_val, item_cases;
		// Validating any missing cases # or item desciption
		for(i; i >= 0; i--){
			item_id = $items[i].getElementsByTagName('input')[0].id;
			item_val = $items[i].getElementsByTagName('input')[0].value;
			item_cases = $items[i].getElementsByTagName('input')[2].value;
			// Extra check that correct item description is entered, in case of
			// wrong description, the corresponding subtotal value will be empty
			item_subtotal = $items[i].getElementsByTagName('input')[5].value;

			if((item_val === '') || (item_cases.length < 1) || (item_subtotal === '')){
				$remove_item_linkH.popover('show');
				validated = false;
			}
		}
	}

	console.log("Validation Check: " + validated);
	return validated;
}

// Hide Popover when order is selected
$order_type_sel.change(function(){
	$(this).popover('hide');
})

// Hide Popover when item is added
$add_item_btn.click(function() {
	$( this ).popover('hide');
});

$(document).on('click', "a.item-remove", hideRemPop);
// Hide Popover above remove column, after item remove
// and if both item desc & cases are added
function hideRemPop() {
	$remove_item_linkH.popover('hide');    
}

// Submit Order Form
$('#transactionSubmitBtn').on('click', validate);
