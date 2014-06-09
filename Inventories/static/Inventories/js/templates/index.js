/************************************************************
Binding popover to report a problem button as doucment is ready
***************************************************************/
var $reportPopover = $('a.text-muted');

$(document).ready(function()
{

	$reportPopover.popover(
	{
		trigger: 'click',
		html: true,
		placement: 'top',
		content: popover_content
	});
	
});

/************************************************************
Reporting a problem Notification
***************************************************************/
function sendProblem(){
	var $headerTag = $('#divalicious');

	$headerTag.addClass( "alert-success" );
	$headerTag.html('<button type="button" class="close" data-dismiss="alert" aria-hidden="true">&times;</button><strong>Sent!</strong> Your problem has been reported. This message will be dismissed in 5s');
	$headerTag.css('display', 'block');

	setTimeout(function(){
		$headerTag.fadeOut("slow", function () {
		});

	}, 5000);

	$reportPopover.popover('hide');
}

/************************************************************
Drawing most consumed items chart
***************************************************************/
new Chart(document.getElementById("canvas").getContext("2d")).Line(lineChartData);
legend(document.getElementById("lineLegend"), lineChartData);
