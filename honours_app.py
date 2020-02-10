from flask import Flask, render_template, redirect, request, json, send_file, current_app as app, send_from_directory
from flask import url_for, make_response
from functools import wraps, update_wrapper
from datetime import datetime
import opt_algorithms as hp
import flask
import pdfkit
import ast


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

    Return = request.args['Return']
    Risk = request.args['Risk']
    Weights = request.args['weights']
    Tickers = request.args['tickers']
    cash = request.args['cash']
    cash = "{:,.2f}".format(float(cash))
    share_volume_list = request.args['share_volume_list']
    sectors = request.args['sectors']

    Sharpe= round(float(Return)/float(Risk),2)

    # url_for converts the array to a string, literal_eval converts it back to an array
    Weights = ast.literal_eval(Weights)
    Weights = [ weight * 100 for weight in Weights ]
    # Round weights to 2 dec places, maybe should do this in OPT code?
    Weights = [ round(weight,3) for weight in Weights ]


    Tickers = ast.literal_eval(Tickers)
    sectors = ast.literal_eval(sectors)
    share_volume_list = ast.literal_eval(share_volume_list)

    # Table on summary page is of dynamic length so we create the html here
    table = render_table( Tickers, Weights, share_volume_list, cash, sectors)
  
   
    return render_template('portfolio_summary.html', name = 'Portfolio Weights',
                           Return = Return,
                           Sharpe = Sharpe,
                           Risk= Risk,
                           table=table,
                           cash=cash,    
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

    cash = request.form['cash']
    if(cash == "" ):
        cash = 10000


 
    
    # Transorm tickers to appropriate format (Sort + Capitalize)
    tickers = [_ticker1,_ticker2, _ticker3, _ticker4, _ticker5
               , _ticker6, _ticker7, _ticker8]
    tickers = filter_tickers( tickers, portfolio_size )
    tickers = [ element.upper() for element in tickers ]
    tickers = sorted(tickers)

    
    
    """if tickers_contain_duplicates(tickers):
        # Duplicate tickers
        message = "Please do not include the same ticker more than once."     
        return redirect(url_for('.Invalid', message=message) )"""
        
    if (BestRatio==False) and invalid_return(expected_return):   
        message = "Expected Return for portfolio must be positive"     
        return redirect(url_for('.Invalid', message=message) )
    
    
    # Perform Optimization 
    #tickers = Auto_select_stocks(tickers, portfolio_size)
    Return, weights, Risk = hp.OptimizePortfolio(tickers, expected_return, BestRatio, cash)  

 
    # Check if any of the tickers entered by the user is invalid
    if Return == False:
        
        # Optimization failed - Invalid ticker
        message = "Invalid Ticker Entered: %s" % weights     
        return redirect(url_for('.Invalid', message=message) )
        
    else:

        share_volume_list = hp.CalculateShareVolume(tickers, weights, cash)

        sectors = list(hp.find_sectors( tickers, weights) )
        
        weights = list(weights)        
        return redirect(url_for('.ShowPortfolio',
                                Return=Return,
                                Risk=Risk,
                                cash=cash,
                                sectors=str(sectors),
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
    expected_return = request.args.get('Return')
    risk = request.args.get('Risk')
    table = request.args.get('table')


    #print( "Row Data", rowData)
    Sharpe = round(float(expected_return)/float(risk),2)
    
    tickers = request.args.get('Tickers')
    weights = request.args.get('Weights')


    # Convert tickers and weights from string format to arrays
    tickers = ast.literal_eval(tickers);
    weights = ast.literal_eval(weights);


   

    
    # Render html file with all required data
    rendered = render_template('portfolio_pdf.html',
                               Return=expected_return,
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
   
    html = "<table class=\"table table\"><thead><tr><th scope=\"col\">#</th><th scope=\"col\">Stock</th><th scope=\"col\">Sector</th><th scope=\"col\">Weight (%)</th><th scope=\"col\">Share Count (£{})</th></tr></thead><tbody>".format(cash)   

    for tick in tickers:

        html = html + '<tr> <th scope=\"row\">{}</th> <td id=\"t1\">{}</td> <td id=\"t1\">{}</td> <td id=\"w1\">{}</td> <td id=\"sv1\">{}</td> </tr>'.format(i+1, tick, sectors[i],weights[i], share_count[i] )
        i += 1


    html = html + "</tbody></table>"
				
    return html


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



def filter_tickers( tickers, size ):

    size = int(size)
   
    # Remove empty strings from the list
    tickers = list(filter(None, tickers))
    missing_stock_count = size - len(tickers)
    
    tickers = tickers[:size]

    new_stocks = []

   
    if missing_stock_count > 0:

        new_stocks = auto_select_stocks( missing_stock_count )
        tickers.append(new_stocks)

 

    
    return tickers    

def auto_select_stocks( missing_stock_count):

    stocks = 'COKE'
    return stocks



if __name__ == "__main__":
    app.run(debug=True)

@app.after_request
def add_header(response):
    # response.cache_control.no_store = True
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, public, max-age=0, revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    return response








