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



@app.route('/ShowPortfolio')
def ShowPortfolio():

    Return = request.args['Return']
    Risk = request.args['Risk']
    Weights = request.args['weights']
    Tickers = request.args['tickers']

    Sharpe= round(float(Return)/float(Risk),2)

    # url_for converts the array to a string, literal_eval converts it back to an array
    Weights = ast.literal_eval(Weights)
    Weights = [ weight * 100 for weight in Weights ]
    # Round weights to 2 dec places, maybe should do this in OPT code?
    Weights = [ round(weight,2) for weight in Weights ]

    Tickers = ast.literal_eval(Tickers)
    

    ## REMEMBER CURRENTLY USING STATIC apple ticker
    return render_template('portfolio_summary.html', name = 'Portfolio Weights',
                           Return = Return,
                           Sharpe = Sharpe,
                           Risk= Risk,
                           w1=Weights[0],w2=Weights[1],w3=Weights[2],w4=Weights[3],
                           t1=Tickers[0], t2=Tickers[1], t3=Tickers[2], t4=Tickers[3],
                           url_pie ='static/images/pie_chart.png',
                           url_efficient ='static/images/efficient_frontier.png')




    
@app.route('/generatePortfolio', methods=['POST'])
def generatePortfolio():

    # Obtain expected return from input
    expected_return = request.form['expectedReturn']
  
    # Obtain tickers from user input
    _ticker1 = request.form['inputTicker1']
    _ticker2 = request.form['inputTicker2']
    _ticker3 = request.form['inputTicker3']
    _ticker4 = request.form['inputTicker4']

    
    
    # Transorm tickers to appropriate format (Sort + Capitalize)
    tickers = [_ticker1,_ticker2, _ticker3, _ticker4 ]
    tickers = [ element.upper() for element in tickers ]
    tickers = sorted(tickers)

    if len(tickers) != len(set(tickers)):

        # Duplicate tickers
        message = "Please do not include the same ticker more than once."     
        return redirect(url_for('.Invalid', message=message) )
        
    elif float(expected_return) < 0:
        ## Negative exp return
        message = "Expected Return for portfolio must be positive"     
        return redirect(url_for('.Invalid', message=message) )
    
   
    # Perform Optimization 
    Return, weights, Risk = hp.OptimizePortfolio(tickers, expected_return )  

    ## Check if any of the tickers entered by the user is invalid
    if Return == False:
        
        # Optimization failed - Invalid ticker
        message = "Invalid Ticker Entered: %s" % weights     
        return redirect(url_for('.Invalid', message=message) )
        
    else:
        weights = list(weights)        
        return redirect(url_for('.ShowPortfolio',
                                Return=Return,
                                Risk=Risk,
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

    print("Risk", float(risk))
    print("ret", expected_return)

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
                               t1=tickers[0], t2=tickers[1], t3=tickers[2], t4=tickers[3],
                               w1=weights[0],w2=weights[1],w3=weights[2],w4=weights[3])



    # This only generates the PDF file. Once the user processes the response for their GET request,
    # they will be redirected to /ShowPDF
    pdf = pdfkit.from_string(rendered, 'static/images/portfolio.pdf', configuration=config)
    


    return "PDF Generated successfully"
    





if __name__ == "__main__":
    app.run(debug=True)

@app.after_request
def add_header(response):
    # response.cache_control.no_store = True
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, public, max-age=0, revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    return response








