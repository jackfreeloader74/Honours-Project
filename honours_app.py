from flask import Flask, render_template, redirect, request, json, send_file, current_app as app, send_from_directory
import HonoursProjectStart as hp
import flask
import pdfkit


app = Flask(__name__, static_folder='static')
config = pdfkit.configuration(wkhtmltopdf='C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe')

Return = 0

@app.route("/")
def main():
    print("Hello world")
    return render_template('index.html')

@app.route('/ShowPortfolio')
def ShowPortfolio():
    print("Showing")
    return render_template('portfolio_summary.html', name = 'Portfolio Weights', expected = Return, 
                           url ='static/images/pie_chart.png')
    
@app.route('/generatePortfolio', methods=['POST'])
def generatePortfolio():

    # Obtain expected return from input
    expected_return = request.form['expectedReturn']

    print("Expected return ", expected_return);
    
    # Obtain tickers from user input
    _ticker1 = request.form['inputTicker1']
    _ticker2 = request.form['inputTicker2']
    _ticker3 = request.form['inputTicker3']
    
   
    Return = hp.OptimizePortfolio(_ticker1, _ticker2, _ticker3, expected_return )
    
    return redirect('/ShowPortfolio')
  

@app.route('/generatePDF', methods=['POST'])
def generatePDF():
    pdfkit.from_file('templates/portfolio_summary.html', 'static/images/portfolio.pdf',configuration=config)
    return flask.redirect(flask.url_for('static', filename='images/' + 'portfolio.pdf'), code=301)
    

if __name__ == "__main__":
    app.run(debug=True)










