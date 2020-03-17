from flask import Flask, render_template, redirect, request, json, send_file, current_app as app, send_from_directory
from flask import url_for, make_response
from functools import wraps, update_wrapper
from datetime import datetime
import opt_algorithms as hp
import flask
import pdfkit
import ast
import portfolio_lib as pl

app = Flask(__name__)
config = pdfkit.configuration(wkhtmltopdf='C:/Program Files/wkhtmltopdf/bin/wkhtmltopdf.exe')


app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0




@app.route("/")
def main():
    return render_template('index.html')

@app.route("/Invalid")
def Invalid():
    message = request.args['message']
    return render_template('index.html', message=message)

@app.route("/about")
def about():
    return render_template('about.html')


@app.route('/ShowPortfolio')
def ShowPortfolio():

    Return = float(request.args['Return'])
    Risk = request.args['Risk']
    weights = request.args['weights']
    tickers = request.args['tickers']
    algorithm = request.args['algorithm']
    cash = request.args['cash']
    cash_str = "{:,.2f}".format(float(cash))
    share_volume_list = request.args['share_volume_list']
    sectors = request.args['sectors']

    
    Ratio = round(float(Return)/float(Risk),2)
    Return = round(float(Return)*100,3)
    
    # Convert weights from string back to a list
    weights = process_weights( weights )

    tickers = ast.literal_eval(tickers)
    sectors = ast.literal_eval(sectors)
    share_volume_list = ast.literal_eval(share_volume_list)

    # Table on summary page is of dynamic length so we create the html here

    # Find the stocks names from the symbols AAPL -> Apple Inc
    stock_names = hp.find_stock_names( tickers )
    
    # Render the portfolio weights table
    table = render_table( stock_names, weights, share_volume_list, cash_str, sectors)
 
   

    # Are we using Sharpe or Sortino?
    algorithm = calculate_ratio( algorithm)

    # Calculate Stock dividends
    #stock_dividend_list = pl.CalculateDividends( tickers, weights, cash)

    stock_dividend_list = [ 4051.72, 0, 1078.34, 3019.38, 0, 0 , 0 , 0 ]
    
    dividend_table, dividend_dates = pl.render_dividend_table( stock_dividend_list, tickers)
   
    return render_template('portfolio_summary.html', name = 'Portfolio Weights',
                           Return = Return,
                           Ratio = Ratio,
                           Risk= Risk,
                           table=table,
                          # dividend_dates = dividend_dates,
                           dividend_table=dividend_table,
                           algorithm=algorithm,
                           Cash=cash_str,    
                           url_pie ='static/images/pie_chart.png',
                           url_efficient ='static/images/efficient_frontier.png')




"""
Checkboxe values only get posted in a form request if the checkbox is "on".
This means finding the value from the form needs to be wrapped in a try catch
"""
    
@app.route('/generatePortfolio', methods=['POST'])
def generatePortfolio():
    
    BestRatio = True;


    try:
        Checked = request.form['checkBox']
    except:
        Checked = "off";


    # If they selected the checkbox, dont use the expected return value in opt code
    if Checked == "on":
        BestRatio = False;

    

    # Obtain tickers from user input
    algorithm = request.form['algorithm']
    expected_return = request.form['expectedReturn']
    _ticker1 = request.form['inputTicker1']
    _ticker2 = request.form['inputTicker2']
    _ticker3 = request.form['inputTicker3']
    _ticker4 = request.form['inputTicker4']
    _ticker5 = request.form['inputTicker5']
    _ticker6 = request.form['inputTicker6']
    _ticker7 = request.form['inputTicker7']
    _ticker8 = request.form['inputTicker8']
    portfolio_size = request.form['portfolioSize']
    algorithm = calculate_algorithm( algorithm )
   
    
    cash = request.form['cash']
    if(cash == "" ):
        cash = 10000

    
    # Transorm tickers to appropriate format (Sort + Capitalize)
    tickers = [_ticker1,_ticker2, _ticker3, _ticker4, _ticker5
               , _ticker6, _ticker7, _ticker8]    
    tickers = filter_tickers( tickers, portfolio_size ) # Filter out empty inputs


    # Calculate what sectors these belong to as well as the stocks official name
    sector_list = list(hp.find_sectors( tickers ) ) # What sectors do they belong to
    tickers = auto_select_stocks( portfolio_size, tickers, sector_list) # Find stocks to add to portfolio  
    sector_list = list(hp.find_sectors( tickers ) ) # Find all the sectors again but with the newly added stocks

    
    # Perform Optimization 
    Return, weights, Risk = hp.OptimizePortfolio(tickers,
                                                 expected_return,
                                                 BestRatio,
                                                 cash,
                                                 algorithm)  

    
 
    # Check if any of the tickers entered by the user is invalid
    if Return == False :
        
        # Optimization failed - Invalid ticker
        if weights == "":
            message = "Something went wrong :("    
        else:
            message = "Invalid Ticker Entered: %s" % weights

        return redirect(url_for('.Invalid', message=message) )

    elif len(sector_list) == 1:
        # Optimization failed - Invalid ticker
        message = "Invalid Ticker Entered: %s" % sector_list     
        return redirect(url_for('.Invalid', message=message) )

    else:
        # Calculate the number of shares that can be bought
        share_volume_list = hp.CalculateShareVolume(tickers, weights, cash)

        # Make pie chart from the list of sectors
        hp.plot_sector_chart( sector_list, weights )

             
        weights = list(weights)        
        return redirect(url_for('.ShowPortfolio',
                                Return=Return,
                                Risk=Risk,
                                cash=cash,
                                sectors=str(sector_list),
                                algorithm = algorithm,
                                share_volume_list=str(share_volume_list),
                                weights=str(weights),
                                tickers=str(tickers)) )
  
  


@app.route('/ShowPDF')
def ShowPDF():
    return send_file('static/images/portfolio.pdf')
       
    

@app.route('/generatePDF', methods=['GET'])
def generatePDF():

    # Get portfolio details so they can be applied to the PDF

    # Grab parameters from get request
    expected_return_str = request.args.get('Return')
    risk = request.args.get('Risk')
    table = request.args.get('table')


    # Need to remove the % so the sharpe ratio can be calcluated
    exp_return = float(expected_return_str.replace("%", "")) 
    
    Sharpe = round((exp_return/100)/float(risk),2)
    
    tickers = request.args.get('Tickers')
    weights = request.args.get('Weights')


    # Convert tickers and weights from string format to arrays
    tickers = ast.literal_eval(tickers);
    weights = ast.literal_eval(weights);


   

    
    # Render html file with all required data
    rendered = render_template('portfolio_pdf.html',
                               Return=expected_return_str,
                               Risk=risk,
                               Sharpe=Sharpe,
                               url_pie='C:/Users/marc.smith/AppData/Local/Programs/Python/Python37-32/static/images/pie_chart.png',
                               url_efficient='C:/Users/marc.smith/AppData/Local/Programs/Python/Python37-32/static/images/efficient_frontier.png',
                               url_performance='C:/Users/marc.smith/AppData/Local/Programs/Python/Python37-32/static/images/portfolio_value_chart.png',
                               table=table)



    # This only generates the PDF file. Once the user processes the response for their GET request,
    # they will be redirected to /ShowPDF
    pdf = pdfkit.from_string(rendered, 'static/images/portfolio.pdf', configuration=config)
    


    return "PDF Generated successfully"





    

def render_table( tickers, weights, share_count, cash, sectors ):

    i = 0
   
    html = '''<table class=\"table table\"><thead><tr><th scope=\"col\">#</th>
            <th scope=\"col\">Stock</th>
            <th scope=\"col\">Sector</th>
            <th scope=\"col\">Weight (%)</th>
            <th scope=\"col\">Share Count</th>
            </tr></thead><tbody>'''.format(cash)   

    for tick in tickers:

        html = html + '<tr> <th>{}</th> <td id=\"t1\">{}</td> <td id=\"t1\">{}</td> <td id=\"w1\">{}</td> <td id=\"sv1\">{}</td> </tr>'.format(
            i+1, tick, sectors[i],weights[i], share_count[i] )
        i += 1


    html = html + "</tbody></table>"
				
    return html


def process_weights( Weights ):

    # url_for converts the array to a string, literal_eval converts it back to an array
    Weights = ast.literal_eval(Weights)
    Weights = [ weight * 100 for weight in Weights ]

    # Round weights to 2 dec places, maybe should do this in OPT code?
    Weights = [ round(weight,3) for weight in Weights ]

    return Weights

def tickers_contain_duplicates( tickers ):

    i = 0
    for item in tickers:
     
        ticker = item
	   
	# Remove element
        tickers.split(i,1)
	   
	#Check if string is still in array
	   
        if item in tickers and ticker != "":   
            return True	   
        else:   
            tickers.split(i, 0, ticker)
            i += 1
   
   
    return False



def invalid_return(expected_return):

    expected_return = float(expected_return)

    if(expected_return <= 0 ):
        return True;

    return False;



# Reduce the list of tickers to the size provided by the user

def filter_tickers( tickers, size ):

    size = int(size)
   
    # Remove empty strings from the list
    tickers = list(filter(None, tickers))
    tickers = tickers[:size]

    tickers = [ element.upper() for element in tickers ] # Convert to uppercase
    tickers = sorted(tickers)
  
    return tickers    


"""
missing_stock_count = How many stocks the app needs to choose for the user
"""

def auto_select_stocks( size, tickers,  sectors ):

    new_stocks = []

    missing_stock_count = int(size) - len(tickers)
    tickers = sorted(tickers)


    # If we need to select any stocks
    if missing_stock_count > 0:

        # Put newly found stocks into a list
        new_stocks = hp.add_stocks( missing_stock_count, tickers, sectors )


        # Add new stocks to our original list of stocks
        tickers.extend(new_stocks)
        tickers = sorted(tickers)


      
    return tickers



def calculate_algorithm( algorithm ):

    algorithm = int(algorithm)

    if algorithm == 1:
        return "MPT"
    elif algorithm == 2:
        return "PMPT"
    else:
        return "MPT"


def calculate_ratio( algorithm ):

    if algorithm == "MPT":
        return "Sharpe"
    else:
        return "Sortino"


if __name__ == "__main__":
    app.run(debug=True)

@app.after_request
def add_header(response):
    
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, public, max-age=0, revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    return response








