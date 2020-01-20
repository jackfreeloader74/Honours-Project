


$(function() {
		init();
});


function init()
{
	
	$("#expectedReturn").hide();
	$("#expectedReturnLabel").hide();
	$("#returnHelp").hide();
	$("#expectedReturn").prop('required', false );
	return true;
};





function checkIfArrayContainsDuplicates(arr) {
   
   for(i=0; i < arr.length; i++)
   {  
	   ticker = arr[i];
	   
	   // Remove element
	   arr.splice(i,1)
	   
	   // Check if string is still in array
	   
	   if( arr.includes(ticker) )
	   {
		   return true;
	   }
	   else
	   {
			arr.splice(i, 0, ticker)
	   }
   }
   
   return false;
}



/* Need to check that the user has not put the same ticker in more than once */

function validateForm() {
	
	//var ticker1 = $('#inputTicker1').val()
	var exp_return = document.forms["myForm"]["expectedReturn"].value;
	
	var t1 = document.forms["myForm"]["inputTicker1"].value;
	var t2 = document.forms["myForm"]["inputTicker2"].value;
	var t3 = document.forms["myForm"]["inputTicker3"].value;
	var t4 = document.forms["myForm"]["inputTicker4"].value;
	
	tickers = [t1, t2, t3, t4]
	
	
	
	if( checkIfArrayContainsDuplicates(tickers) )
	{
		alert("Please do not include the same ticker more than once");
		return false;
	}
	else if( exp_return < 0 )
	{
		alert("The portfolio's expectd return must be positive.");
		return false;
	}
	else if (exp_return > 100 )
	{
		alert( "The portfolio's expected return must be below 100." );
		return false;
	}
	else
		return true;
}


$(function() {
	
	$('#checkBox').click(function() {
		
		if(  $("#checkBox").is(":checked") ){
			$("#expectedReturn").show();
			$("#expectedReturnLabel").show();
			$("#returnHelp").show();
			
			//$("#expectedReturn").prop('required', true );
		}
		else
		{
			$("#expectedReturn").hide();
			$("#expectedReturnLabel").hide();
			$("#returnHelp").hide();
			$("#expectedReturn").val("")
			$("#expectedReturn").prop('required', false );
		}
			
	});
	
});



$(function() {
	
	$("#preset").click(function() {
		
		$("#inputTicker1").val("AAPL");
		$("#inputTicker2").val("AMZN");
		$("#inputTicker3").val("TLSA");
		$("#inputTicker4").val("XOM");
	});
});



$(function() {
    $('#exportToPdfBtn').click(function() {	
		
		var exp_return = $("#return").text()
		var risk = $("#risk").text()
		
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
			Risk: risk,
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