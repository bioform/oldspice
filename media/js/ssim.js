var load_data = function(address,target){
    // store value in data variable
    var data = {};
    $.ajaxSetup({ cache: false });
    $.get(address,data,
        function(data){
            $(target).html(data);
        }
    );
    return false;
}

var post = function(address,target, data){
    // store value in data variable
    $.ajaxSetup({ cache: false });
    $.post(address,data,
        function(data){
            $(target).html(data);
        }
    );
    return false;
}
