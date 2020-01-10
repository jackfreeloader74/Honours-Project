from flask import Flask, render_template, redirect, request, json, send_file, current_app as app, send_from_directory
from flask import url_for
import opt_algorithms as hp
import flask
import pdfkit
import ast


app = Flask(__name__, static_folder='static')
config = pdfkit.configuration(wkhtmltopdf='C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe')


@app.route("/")
def main():
    return render_template('index.html')

@app.route('/ShowPortfolio')
def ShowPortfolio():
    print("Showing")
    Return = request.args['Return']
    Weights = request.args['weights']
    Tickers = request.args['tickers']

    # url_for converts the array to a string, literal_eval converts it back to an array
    Weights = ast.literal_eval(Weights)
    Weights = [ weight * 100 for weight in Weights ]
    # Round weights to 2 dec places, maybe should do this in OPT code?
    Weights = [ round(weight,2) for weight in Weights ]

    Tickers = ast.literal_eval(Tickers)
    

    ## REMEMBER CURRENTLY USING STATIC apple ticker
    return render_template('portfolio_summary.html', name = 'Portfolio Weights', expected = Return, 
                           w1=Weights[0],w2=Weights[1],w3=Weights[2],w4=Weights[3],
                           t1="AAPL", t2=Tickers[0], t3=Tickers[1], t4=Tickers[2], url ='static/images/pie_chart.png')
    
@app.route('/generatePortfolio', methods=['POST'])
def generatePortfolio():

    # Obtain expected return from input
    expected_return = request.form['expectedReturn']

    print("Expected return ", expected_return);
    
    # Obtain tickers from user input
    _ticker1 = request.form['inputTicker1']
    _ticker2 = request.form['inputTicker2']
    _ticker3 = request.form['inputTicker3']

    tickers = [_ticker1,_ticker2, _ticker3 ]
    print("Tick", tickers)

    
    Return, weights = hp.OptimizePortfolio(_ticker1, _ticker2, _ticker3, expected_return )
  
    weights = list(weights)
    return redirect(url_for('.ShowPortfolio', Return=Return, weights=str(weights), tickers=str(tickers) ) )
  
  

@app.route('/generatePDF', methods=['POST'])
def generatePDF():
    pdfkit.from_file('templates/portfolio_summary.html', 'static/images/portfolio.pdf',configuration=config)
    return flask.redirect(flask.url_for('static', filename='images/' + 'portfolio.pdf'), code=301)
    

if __name__ == "__main__":
    app.run(debug=True)










