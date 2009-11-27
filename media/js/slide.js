$(document).ready(function() {
	
	// Expand Panel
	$("#open").click(function(){
                $("#header").css("z-index", 0);
		$("div#panel").slideDown("slow");
	});	
	
	// Collapse Panel
	$("#close").click(function(){
		$("div#panel").slideUp("slow", function(){
                    $("#header").css("z-index", 1000);
                });
	});		
	
	// Switch buttons from "Log In | Register" to "Close Panel" on click
	$("#toggle a").click(function () {
		$("#toggle a").toggle();
	});		
		
});