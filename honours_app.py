from flask import Flask, render_template, redirect, request, json, send_file, current_app as app, send_from_directory
from flask import url_for, make_response
from functools import wraps, update_wrapper
from datetime import datetime
import opt_algorithms as hp
import flask
import pdfkit
import ast
import portfolio_lib as pl
from portfolio_classes.portfolio import Portfolio

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

    portfolio = pl.recreate_portfolio(request.args)

    # Calculate dividend earnings for each asset and overall portfolio
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

    # Use user input to create portfolio and asset objects
    portfolio = pl.create_portfolio_object(request.form)

    # Perform Optimization - Any error details are stored in message variable
    Success, message = hp.OptimizePortfolio( portfolio )

    # Check if any of the tickers entered by the user is invalid or an API problem
    if Success == False :
        return redirect(url_for('.Invalid', message=message) )
    else:
        # Calculate the number of shares that can be bought
        share_volume_list = hp.CalculateShareVolume(portfolio)

        # Make pie chart from the list of sectors
        hp.plot_sector_chart( portfolio )
        tickers = list(a.ticker for a in portfolio.assets)
        weights= list(a.weight for a in portfolio.assets)
        sectors = list(a.sector for a in portfolio.assets)

        # Redirect to the Show Portfolio URL and pass it the required parameters so it can show the summary page
        return redirect(url_for('.ShowPortfolio',
                                Return=portfolio.exp_return,
                                Risk=portfolio.risk,
                                cash=portfolio.cash,
                                sectors=str(sectors),
                                algorithm = portfolio.algorithm,
                                share_volume_list=str(share_volume_list),
                                weights=str(weights),
                                tickers=str(tickers) ) )





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
