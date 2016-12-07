// execute when ready
// http://smallenvelop.com/display-loading-icon-page-loads-completely/
$(window).load(function() {
		// Animate loader off screen
		$(".preload").fadeOut("slow");;
	});
$(document).ready(function() {
	// Modified from: http://befused.com/jquery/open-link-new-window
	// clicking href opens the page in a new window
	$("a[href].projects").click(function()
  	{
   		window.open(this.href);
    	return false;
  	});
});