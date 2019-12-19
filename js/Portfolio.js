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