$(function() {
    $('#generatePortfolioBtn').click(function() {
		
		
		
        $.ajax({
            url: '/generatePortfolio',
            data: $('form').serialize(),
            type: 'POST',
            success: function(response) {
                console.log(response);
            },
            error: function(error) {
                console.log(error);
            }
        });
    });
});



$(function() {
    $('#exportToPdfBtn').click(function() 		
		
		alert("Hello");
		
        $.ajax({
            url: '/generatePDF',
            data: "stuff",
            type: 'POST',
            success: function(response) {
                console.log(response);
            },
            error: function(error) {
                console.log(error);
            }
        });
    });
});