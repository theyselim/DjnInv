/****************************************************************************
@view_more: Ajax Call
	onSucess, returns 5 more orders to view until all orders are added.
	View More button is disabled
	****************************************************************************/
	function view_more(){
		$.ajax({
			type: "POST",
			url: views_url,
			data: { 
				'csrfmiddlewaretoken': document.getElementsByName('csrfmiddlewaretoken')[0].value,
				'latest_id': transactions[transactions.length-1][0],
			},
			success: function(response){
			// Check if there are still more orders
			if( response.length < 1 ){
				var $vm_btn = $('#vm_btn');
				$vm_btn.addClass("list-group-item-danger");
				$vm_btn.html('No more orders to view!');
			}

			// Add orders retrieved
			$.each(response, function(i) {
				var order_desc;
				if(response[i][1] == ''){
					order_desc = 'No Description';
				}else{
					order_desc = response[i][1];
				}
				// Update transactions global variable with the new added orders
				transactions.push([response[i][0], order_desc]);
				$orders_list.append('<a href="#" id="' + response[i][0] + '" onclick="get_order_info(this);" class="list-group-item"> Order# ' + response[i][0] + ' | ' + order_desc + '</a>');
			});

		},
		error: function(response){
			console.log('Archive viewing more error: ' + response);
		}
	});
}	

/****************************************************************************
@get_order_info: Ajax Call
	onSucess, 
	****************************************************************************/
	function get_order_info(objRef){
		// Display orders view and hide jumbotron
		$orders_view.css('display', 'block');
		$jumbo.css('display', 'none');
		
		var order_id = $(objRef).attr('id'), $items_list = $('#items_list');
		console.log();
		$.ajax({
			type: "POST",
			url: transactionInfo_url,
			data: { 
				'csrfmiddlewaretoken': document.getElementsByName('csrfmiddlewaretoken')[0].value,
				'order_id': order_id,
			},
			success: function(response){
				console.log(response);

				// Order# -> transaction.id, Reciept or Ticket -> transaction.t_type
				var order_type;
				if(response.t_type == 'RE')
					order_type = 'Reciept';
				else
					order_type = 'Ticket';
				$('#order_id').html('Order #' + order_id + ' <span class="label label-default">' + order_type + '</span>');
				
				// Date -> transaction.date_created
				$('#date').html('Date - <small>' + response.date + '</small>');

				// Description ->  Item Inventory name + Order description +
				var addtional_desc;
				if(response.trans_desc.length < 1)
					addtional_desc = 'No additional description';
				else
					addtional_desc = response.trans_desc;
				$('#trans_desc').html('Transaction in ' + response.items[0][4] + '<br/> ' + addtional_desc);
				
				// Loop on items list -> add them to order's items list
				$items_list.html('');
				$.each(response.items, function(i, item) {
					// Calculate subtotal per item
					var subtotal = Math.round((parseFloat(item[3])*parseFloat(item[2]))*100)/100;
					$items_list.append('<tr><td>' + item[0] + '</td><td class="center-t">' + item[1] 
						+ '</td><td class="center-t">' + item[2] + '</td><td class="center-t">' + item[3] + '</td><td class="center-t">' 
						+ subtotal + '</td>');
				});

				// Items count -> items in response length, fees and subtotal from response
				$('#items_count').html('Total Items: ' + response.items.length);
				$('#subtotal').html('Subtotal: $' + response.subtotal);
				$('#fees').html('Additional Fees: $' + response.fees);

				// Calculate total -> subtotal + fees
				var total = parseFloat(response.subtotal) + parseFloat(response.fees);
				$('#total').html('Total: $' + total);
			},
			error: function(response){
				console.log('ARCHIVE: Order Viewing error: ' + response);
			}
		});
}