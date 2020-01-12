$(function() {
    $('#generatePortfolioBtn').click(function() {
		
	
        /*$.ajax({
            url: '/generatePortfolio',
            data: $('form').serialize(),
            type: 'POST',
            success: function(response) {
                console.log(response);
            },
            error: function(error) {
                console.log(error);
            }
        }); */
    });
});



$(function() {
    $('#exportToPdfBtn').click(function() {	
		
		var exp_return = $('expectedReturn').val()
		console.log("Return " + exp_return)
		
		
        $.ajax({
            url: '/generatePDF',
            data: "stuff",
            type: 'GET',
            success: function(response) {
                window.location.href = '/generatePDF'
				console.log(response);
				
            },
            error: function(error) {
                console.log(error);
            }
        });  
    });
});