$(function() {
    $('#generatePortfolioBtn').click(function() {
		
		
		
        $.ajax({
            url: '/generatePortfolio',
            data: "",
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