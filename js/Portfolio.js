


$(function() {
		init();
});


function init()
{
	$("#returnHelpSmall").hide();	
	$("#expectedReturn").hide();
	$("#expectedReturnLabel").hide();
	
	$("#expectedReturn").prop('required', false );
	$("#cash").prop('required', false );
	
	$("#mar_div").hide();
	
	
	$("#specifyMinReturnLabel").css("font-weight", "normal")
	
	
	/* Hide the loading div, show it when the user successfully generates a portfolio */
	$("#loading_div").hide();
	
	$("#appointmentEditDialog").dialog({	modal:true,			//modal dialog to disable parent when dialog is active
	autoOpen:false,		//set autoOpen to false, hidding dialog after creation
	title: "Edit Appointment",	//set title of dialog box
	minWidth: 500,
	minHeight: 400
	});
	




	return true;
};







function checkIfArrayContainsDuplicates(arr) {
   
   
   arr = arr.map(function(x){ return x.toUpperCase() })
   
   
   for(i=0; i < arr.length; i++)
   {  
	   ticker = arr[i];
	   
	   // Remove element
	   arr.splice(i,1)
	   
	   // Check if string is still in array
	   
	   if( arr.includes(ticker) && ticker != "")
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
	
	
	var exp_return = document.forms["myForm"]["expectedReturn"].value;
	
	var t1 = document.forms["myForm"]["inputTicker1"].value;
	var t2 = document.forms["myForm"]["inputTicker2"].value;
	var t3 = document.forms["myForm"]["inputTicker3"].value;
	var t4 = document.forms["myForm"]["inputTicker4"].value;
	
	tickers = [t1, t2, t3, t4]
	
	var cash = document.forms["myForm"]["cash"].value;
	
	var portfolio_size = document.forms["myForm"]["portfolioSize"].value;
	
	if( portfolio_size == "" )	
		portfolio_size == 4;
	
	
	
	
	if( checkIfArrayContainsDuplicates(tickers) )
	{
		alert("Please do not include the same ticker more than once");
		return false;
	}
	else if( isNaN(portfolio_size))
	{
		alert("Portfolio Size must be a number" );
		return false;
	}
	else if( portfolio_size < 0 || portfolio_size > 8 )
	{
		alert( "Portfolio is an invalid size" );
		return false;
	}
	else if( cash && isNaN(cash))
	{
		alert("Cash value must be a valid number");
		return false;
	}
	else if( cash < 100 )
	{
		alert( "Cash value must be greater than 100." );
		return false;
	}
	else if(isNaN(exp_return) )
	{
		alert("Minumum expected return must be a number.");
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
	{	
		window.scrollTo(100, 100);
		$("#loading_div").show();
		$("#main_container").hide();
		$("#preset").hide();
		$("#preset2").hide();
		return true;
	}
}


$(function() {
	
	$('#checkBox').click(function() {
		
		if( $("#checkBox").is(":checked") ){
			$("#expectedReturn").show();
			$("#expectedReturnLabel").show();
			$("#returnHelpSmall").show();
			
			$("#specifyMinReturnLabel").css("font-weight", "bold")
			$("#checkBoxLabel").css("font-weight", "normal")
			//$("#checkBoxLabel").text("Find best risk-reward ratio ");
			
			
			$("#expectedReturn").prop('required', true );
		}
		else
		{
			$("#expectedReturn").hide();
			$("#expectedReturnLabel").hide();
			$("#returnHelpSmall").hide();
			$("#expectedReturn").val("")
			$("#expectedReturn").prop('required', false );
			
			$("#specifyMinReturnLabel").css("font-weight", "normal")
			$("#checkBoxLabel").css("font-weight", "bold")
			
			//$("#checkBoxLabel").text("Specify Minimum Return");
		}
			
	});
	
});


$(function() {
	$("#view_ticker_btn").click(function() {
		
		$(document).ready(function() {
			$("#MyModal").modal();
		});
	});
	
});



$(function() {
	$("#view_ticker_btn").click(function() {
		
		$(document).ready(function() {
			$("#MyModal").modal();
		});
	});
	
});

 
 
/* Create a listener for when the user changes the value of the algorithm dropdown menu */
 
$(function() {
	$("#myList").change(function() {
		var selectedVal = $(this).find(':selected').val();
		
		
		if( selectedVal == 1 )
		{
			$("#mar_div").hide();
		}
		else if( selectedVal == 2 )
		{
			$("#mar_div").show();
		}
	});
	
});
 

$(function() {
	$("#view_help_btn").click(function() {
		
		$(document).ready(function() {
			$("#helpModal").modal();
		});
	});
	
});
 
 

/* Preset that fills out the form with static values */
$(function() {
	
	$("#preset").click(function() {
		
		$("#portfolioSize").val("4");
		$("#inputTicker1").val("AAPL");
		$("#inputTicker2").val("AMZN");
		$("#inputTicker3").val("TSLA");
		$("#inputTicker4").val("XOM");
		$("#inputTicker5").val("GOOG");
		$("#inputTicker6").val("SBUX");
		$("#inputTicker7").val("IBM");
		$("#inputTicker8").val("MSFT");
		$("#cash").val("10000");
		
		$("#appointmentEditDialog").dialog("open",true);
	});
});



$(function() {
	
	$("#mpt_dropdown").click(function() {
		
		mpt = $("#mpt_dropdown").text()
		$("#dropdownBtn").text(mpt);
	});
});



$(function() {
	
	$("#pmpt_dropdown").click(function() {
		
		mpt = $("#pmpt_dropdown").text()
		$("#dropdownBtn").text(mpt);
	});
});




$(function() {
	
	$("#preset2").click(function() {
		
		$("#portfolioSize").val("8");
		$("#inputTicker1").val("AAPL");
		$("#inputTicker2").val("AMZN");
		$("#inputTicker3").val("TSLA");
		$("#inputTicker4").val("XOM");
		$("#inputTicker5").val("ATLO");
		$("#inputTicker6").val("GBT");
		$("#inputTicker7").val("ADM");
		$("#inputTicker8").val("XTLB");
		$("#cash").val("10000");
		
		$("#appointmentEditDialog").dialog("open",true);
	});
});






/* User is exporting portfolio to PDF. Call ajax function to provide server with html to produce the pdf */

$(function() {
    $('#exportToPdfBtn').click(function() {	
		
		var exp_return = $("#return").text()
		var risk = $("#risk").text();
		
		var cash = $("#cash").text();
		var table = $("#myTable").html();
	
		var dividends = $("#dividend_table").html();
		
		
		console.log(dividends);
		
		/* Add them as parameters to request */
		var data = {
			Return: exp_return,
			Risk: risk,
			cash: cash,
			table: table,
			dividends: dividends
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