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
		
		var exp_return = $("p").eq(1).text()
		
		console.log("Return " + exp_return)
		
		var data = {
			Return: exp_return
		}
		
        $.ajax({
            url: '/generatePDF',
            data: data,
            type: 'GET',
            success: function(response) {
                window.location.href = '/ShowPDF'
				console.log(response);
            },
            error: function(error) {
               
            }
        });  
    });
});