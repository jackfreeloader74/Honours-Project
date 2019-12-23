from flask import Flask, render_template, redirect, request, json, send_file, current_app as app, send_from_directory
import HonoursProjectStart as hp
import flask

app = Flask(__name__, static_folder='static')

@app.route("/")
def main():
    print("Hello world")
    return render_template('index.html')

@app.route('/ShowPortfolio')
def ShowPortfolio():
    print("Showing")
    return render_template('portfolio_summary.html')


@app.route('/generatePortfolio', methods=['POST'])
def generatePortfolio():
    _ticker1 = request.form['inputTicker1']
    _ticker2 = request.form['inputTicker2']
    _ticker3 = request.form['inputTicker3']
    
    print("Tickers ", _ticker1, _ticker2, _ticker3)
    #Sharpe = hp.OptimizePortfolio(_ticker1, _ticker2, _ticker3 )
    print("The sharp ratio is ")
    print("Render Template")
    var1 = "test str"
    return render_template('portfolio_summary.html', name = 'Portfolio Weights', url ='/static/images/img.jpg')
    #return redirect('/ShowPortfolio')



@app.route('/generatePDF', methods=['POST'])
def generatePDF():
    #return send_from_directory(app.config['/static/images'], 'stuff.pdf')
    return flask.redirect(flask.url_for('static', filename='images/' + 'stuff.pdf'), code=301)

    
    


if __name__ == "__main__":
    app.run(debug=True)





