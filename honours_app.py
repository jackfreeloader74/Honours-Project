from flask import Flask, render_template, redirect, request, json
import HonoursProjectStart as hp

app = Flask(__name__)

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
    #Sharpe = hp.OptimizePortfolio()
    #print("The sharp ratio is ", Sharpe)
    print("Render Template")
  
    return redirect('/ShowPortfolio')



if __name__ == "__main__":
    app.run(debug=True)





