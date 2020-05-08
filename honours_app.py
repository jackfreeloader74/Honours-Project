from flask import Flask, render_template, redirect, request, json, send_file, current_app as app, send_from_directory
from flask import url_for, make_response
from functools import wraps, update_wrapper
from datetime import datetime
import opt_algorithms as hp
import flask
import pdfkit
import ast
import portfolio_lib as pl
from portfolio import Portfolio

app = Flask(__name__)

# Config for PDFKit
config = pdfkit.configuration(wkhtmltopdf='C:/Program Files/wkhtmltopdf/bin/wkhtmltopdf.exe')


app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0


# Url to return the index/portfolio input form

@app.route("/")
def main():
    return render_template('index.html')


# Url when the user has entered bad details on the portfolio form page

@app.route("/Invalid")
def Invalid():
    message = request.args['message']

    # The message depends on the errror (e.g. invalid ticker)
    return render_template('index.html', message=message)



# Url that returns the about page that gives details on the optimization algorithms

@app.route("/about")
def about():
    return render_template('about.html')



# Displays the portfolio summary page

@app.route('/ShowPortfolio')
def ShowPortfolio():

    Return = float(request.args['Return'])
    Risk = request.args['Risk']
    weights = request.args['weights']
    tickers = request.args['tickers']
    algorithm = request.args['algorithm']
    algorithm = pl.calculate_ratio(algorithm)
    cash = request.args['cash']
    cash_str = "{:,.2f}".format(float(cash))
    share_volume_list = request.args['share_volume_list']
    sectors = request.args['sectors']
    cash = request.args['cash']
    cash_str = "{:,.2f}".format(float(cash))

    # Convert weights from string back to a list
    weights = pl.process_weights( weights )
    tickers = ast.literal_eval(tickers)
    sectors = ast.literal_eval(sectors)
    share_volume_list = ast.literal_eval(share_volume_list)


    # Recreate the Portfolio and asset objects
    portfolio = Portfolio(cash=float(cash), algorithm=algorithm, mar_value=0, user_expected_return="")
    portfolio.exp_return = Return
    portfolio.risk = Risk
    portfolio.cash_str = cash_str


    assets = pl.createAssets(tickers, sectors, portfolio)
    assets = pl.add_weights_to_assets(assets, weights)
    assets = pl.add_share_volume_to_assets(assets, share_volume_list)
    assets = pl.add_names_to_assets( assets )

    portfolio.assets = assets
    portfolio = pl.CalculateDividends( portfolio )


    # Backup for when API limit is reached
    #stock_dividend_list = [ 4051.72, 0, 1078.34, 3019.38, 0, 0 , 0 , 0 ]

    return render_template('portfolio_summary.html', name = 'Portfolio Weights',
                                portfolio=portfolio )




"""
    URL for generating the users portfolio (called when the user selects the
    "Generate Portfolio" button on the intial portfolio form page.

"""

@app.route('/generatePortfolio', methods=['POST'])
def generatePortfolio():

    BestRatio = True;

    # If the checkbox is off, the request form will throw an error if you try to access it
    try:
        Checked = request.form['checkBox']
    except:
        Checked = "off";


    # If they selected the checkbox, dont use the expected return value in opt code
    if Checked == "on":
        BestRatio = False;


    # Obtain tickers from user input
    algorithm = request.form['algorithm']
    mar_value = request.form['mar_value']
    user_expected_return = request.form['expectedReturn']
    _ticker1 = request.form['inputTicker1']
    _ticker2 = request.form['inputTicker2']
    _ticker3 = request.form['inputTicker3']
    _ticker4 = request.form['inputTicker4']
    _ticker5 = request.form['inputTicker5']
    _ticker6 = request.form['inputTicker6']
    _ticker7 = request.form['inputTicker7']
    _ticker8 = request.form['inputTicker8']
    portfolio_size = request.form['portfolioSize']

    algorithm = request.form['algorithm']
    mar_value = request.form['mar_value'] # Only relevant to PMPT
    algorithm = pl.calculate_algorithm( algorithm )
    mar_value = pl.calculate_mar( mar_value ) # Use the dropdown number option to calculate what MAR was selected

    cash = request.form['cash']
    if(cash == "" ):
        cash = 10000 # Default cash to 10,000


    # Transorm tickers to appropriate format (Sort + Capitalize)
    tickers = [_ticker1,_ticker2, _ticker3, _ticker4, _ticker5
               , _ticker6, _ticker7, _ticker8]
    tickers = pl.filter_tickers( tickers, portfolio_size ) # Filter out empty inputs


    # Calculate what sectors these belong to as well as the stocks official name
    sector_list = list(hp.find_sectors( tickers ) ) # What sectors do they belong to
    tickers = sorted(pl.auto_select_stocks( portfolio_size, tickers, sector_list)) # Find stocks to add to portfolio
    sector_list = list(hp.find_sectors( tickers ) ) # Find all the sectors again but with the newly added stocks

    portfolio = Portfolio(cash=cash, algorithm=algorithm, mar_value=mar_value, user_expected_return=user_expected_return)
    assets = pl.createAssets(tickers, sector_list, portfolio)
    portfolio.assets = assets


    # Perform Optimization
    Return, weights, Risk = hp.OptimizePortfolio( BestRatio, portfolio )


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
        share_volume_list = hp.CalculateShareVolume(portfolio)
        #share_volume_list = [222, 222, 333, 33]

        # Make pie chart from the list of sectors
        hp.plot_sector_chart( portfolio )
        weights = list(weights)

        # Redirect to the Show Portfolio URL and pass it the required parameters so it can show the summary page
        #return render_template('portfolio_summary.html')

        return redirect(url_for('.ShowPortfolio',
                                Return=Return,
                                Risk=portfolio.risk,
                                cash=portfolio.cash,
                                sectors=str(sector_list),
                                algorithm = portfolio.algorithm,
                                share_volume_list=str(share_volume_list),
                                weights=str(weights),
                                tickers=str(tickers),
                                portfolio=portfolio ) )





# Returns a json object with extra details about a stock (e.g. net worth, logo etc)
@app.route('/stockDetail/<ticker>', methods=['GET'] )
def stockDetail(ticker):

    # Obtain full stock name from the GET request
    stock_name = request.args.get('stock_name')

    # Find the current share price of the stock as well as generate a graph for the portfolios value over time
    share_price, line_chart_file = hp.query_ticker_data(ticker)


    # Use clearbit API to find extra info about the company (logo, marketcap, founding year etc..)
    # This api call may fail since the company names can be off slightly
    detail_dict = pl.find_company_info( stock_name )


    if detail_dict != False:

        # Add share price to the dictionary that is being returned
        detail_dict['share_price'] = share_price

        detail_dict['line_chart_file'] = line_chart_file


    return json.dumps(detail_dict)






# This returns the PDF
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
    dividend_details = request.args.get('dividends')
    cash = request.args.get('cash')
    future_cash = request.args.get('future_cash')


    # Need to remove the % so the sharpe ratio can be calcluated
    exp_return = float(expected_return_str.replace("%", ""))
    Sharpe = round((exp_return/100)/float(risk),2)


    # Render html file with all required data
    rendered = render_template('portfolio_pdf.html',
                               Return=expected_return_str,
                               Risk=risk,
                               Sharpe=Sharpe,
                               cash=cash,
                               future_cash=future_cash,
                               url_pie='C:/Users/marc.smith/AppData/Local/Programs/Python/Python37-32/static/images/pie_chart.png',
                               sector_pie='C:/Users/marc.smith/AppData/Local/Programs/Python/Python37-32/static/images/sector_makeup.png',
                               url_efficient='C:/Users/marc.smith/AppData/Local/Programs/Python/Python37-32/static/images/efficient_frontier.png',
                               url_performance='C:/Users/marc.smith/AppData/Local/Programs/Python/Python37-32/static/images/portfolio_value_chart.png',
                               table=table,
                               dividends=dividend_details)



    # This only generates the PDF file. Once the user processes the response for their GET request,
    # they will be redirected to /ShowPDF
    pdf = pdfkit.from_string(rendered, 'static/images/portfolio.pdf', configuration=config)



    return "PDF Generated successfully"




if __name__ == "__main__":
    app.run(debug=True)

@app.after_request
def add_header(response):

    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, public, max-age=0, revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    return response
