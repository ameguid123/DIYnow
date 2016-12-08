// http://smallenvelop.com/display-loading-icon-page-loads-completely/
// creating a loading page icon
$(window).load(function() {
		// Animate loader off screen
		$(".preload").fadeOut("slow");;
	});

// execute when document fully loaded
$(document).ready(function() {
	// Modified from: http://befused.com/jquery/open-link-new-window
	// ensures that clicking href opens the page in a new window
	$("a[href].projects").click(function()
  	{
   		window.open(this.href);
    	return false;
  	});
});