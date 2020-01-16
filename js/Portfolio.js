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
		
		
		// Obtain portfolio tickers		
		var t1= $("#t1").text()
		var t2 = $("#t2").text()
		var t3 = $("#t3").text()
		var t4 = $("#t4").text()
		
		tickers = [t1, t2, t3, t4]
		tickers = JSON.stringify(tickers);
		
		
		// Obtain corresponding weights
		var w1 = $("#w1").text()
		var w2 = $("#w2").text()
		var w3 = $("#w3").text()
		var w4 = $("#w4").text()
		
		weights = [w1, w2, w3, w4]	
		weights = JSON.stringify(weights);
		
		
		
		/* Add them as parameters to request */
		var data = {
			Return: exp_return,
			Tickers: tickers,
			Weights: weights
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