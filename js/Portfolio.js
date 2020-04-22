


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





//$(document).ready(function() {









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
			$("#MyModal").modal();
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
		var future_cash = $("#future_cash").text();
		var table = $("#myTable").html();
	
		var dividends = $("#dividend_table").html();
		
		
	
		/* Add them as parameters to request */
		var data = {
			Return: exp_return,
			Risk: risk,
			cash: cash,
			future_cash : future_cash,
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
				alert("Something went wrong");
            }
        });  
    });
});


/* Build up the html that will be placed in the stock detail popups header */
function build_stock_detail_header( ticker, stock_name, img )
{
			
	
		var header = "<div id='container'>" +

							"<div id='stock_logo' style='float: right;'  style='display:inline;'>" + 
							"</div>" + 
							
							"<div id='texts' style='display:inline;'>" +  
								"<h1 class='display-4'>" + stock_name + "</h1>" +
							"</div>" +	
						
											
						"</div>";
	
	
		return header;
}



/* Add commas to large numbers */
function formatNumber(num) {

  return num.toString().replace(/(\d)(?=(\d{3})+(?!\d))/g, '$1,')
}




/* Creates the html that goes into the stock popups body. If the API failed to retrieve certain data, it wont return anything */

function build_stock_detail_body( ticker, share_price, domain, employees, marketCap, foundingYear, line_chart_file, annual)
{
		var sector = stock + "_sector_id" 
		
				
		sector = $("#" + sector).text();	 
		var body = "<h3>Sector: " + sector + "</h3>"
		
		if( share_price != null )
			body += "<h3>Current Share Price: $" + share_price + "</h3>";
		
		
		if( marketCap != null )
		{
			marketCap = formatNumber( marketCap )
			body += "<h3>Market Capitilization: $" + marketCap
		}
		
	
		if( annual != null )
		{
			body += "<h3>Estimated Annual Revenue: " + annual + "</h3>";	
		}
		
		if( employees != null )
		{
			employees = formatNumber( employees )
			body += "<h3>Employee Count: " + employees + "</h3>";
		}
		
		if( foundingYear != null )
		{
			body += "<h3>Founding Year: " + foundingYear + "</h3>";
		}
		
		if( domain != null )
			body += "<h3>Domain: <a target='_blank' href='//" + domain + "'>" + domain + "</a></h3>";
		
		
		if( line_chart_file != null )
		{
			body += "<img src='" + line_chart_file + "' height='350' width='500' />";
		}
		
		return body
}


/* Event listener for weights table rows. Opens a popup that shows more info about a stock */

$(function() {
	
    $('#weights_table tr').click(function() {
       	
		/* Clear the popup of any previous info */
		$('#modal-head').html("");
		$('#modal-body').html("");
		
		/* Get the ticker symbol for this stock */
		stock = this.id;
		

		if( stock != "")
		{	
			var stock_name = stock + "_name_id" 
			stock_name = $("#" + stock_name).text();
			
			
			var header = build_stock_detail_header( stock, stock_name );
			
						
						
			/* Attatch html to the modal and display it */
			$('#modal-head').html(header);
			
			$('#stockModal').modal({show:true});
			

			var url = '/stockDetail/' + stock;
				
			var data =  {
				stock_name: stock_name
			}
			
	
			/* Request further stock details from server */
			$.ajax({
				url: url,
				type: 'GET',
				data: data, 
				success: function(response) {
				 					
					
					response = JSON.parse(response);
					var share_price = response['share_price'];
					var img = response['img'];
					var domain = response['domain'];
					var employees = response['employees'];
					var marketCap = response['marketCap'];
					var foundingYear = response['foundedYear'];
					var line_chart_file = response['line_chart_file'];
					var annual = response['annual'];
					
					
						
					if(img != null )
					{
						/* Prepare image */	
						logo = "<img src='" + img + "' height='100' width='100' />";
						$('#stock_logo').append(logo);				
					}
					
					var body = build_stock_detail_body( stock, share_price, domain, employees, marketCap, foundingYear, line_chart_file, annual );
					$('#modal-body').html(body);
					
				},
				error: function(error) {
					alert("Failed");
				}
			}); 
									
		}
		
		
    });
});







