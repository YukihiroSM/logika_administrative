$('#selectAll').click(function() {
    $('#teachers option').attr("selected","selected");
});   

$('#deselectAll').click(function() {
    $('#teachers option').removeAttr("selected");
});
