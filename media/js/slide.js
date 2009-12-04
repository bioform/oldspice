$(document).ready(function() {

        change_panel_link = function () {
		$("#toggle a").toggle();
	}
        collapse_panel = function(){
		$("div#panel").slideUp("fast", function(){
                    $("#header").css("z-index", 1000);
                });
	}

        is_panel_open = function(){
            return $("#toggle #close").css('display') == 'block'
        }

	// Expand Panel
	$("#open").click(function(){
                $("#header").css("z-index", 0);
		$("div#panel").slideDown("fast");
	});	
	
	// Collapse Panel
	$("#close").click(collapse_panel);
	
	// Switch buttons from "Log In | Register" to "Close Panel" on click
	$("#toggle a").click(change_panel_link);
		
});