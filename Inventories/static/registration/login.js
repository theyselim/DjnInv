// For Forgot password
$forgot_admn = $('#forgot');
$err_msn = $('#error_msg');

function forgot(){
	$forgot_admn.html('Please contact your adminstrator to reset your password');
}

// Reset Err & Forgot text
setTimeout(function(){
	$forgot_admn.html('');
	$err_msn.html('');
}, 8000);