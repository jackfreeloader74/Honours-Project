from flask import Flask, render_template, redirect, request, json
import HonoursProjectStart as hp

app = Flask(__name__)

@app.route("/")
def main():
    print("Hello world")
    return render_template('index.html')

@app.route('/generatePortfolio', methods=['POST'])
def generatePortfolio():
    print("Hello")
    Sharpe = hp.OptimizePortfolio()
    print("The sharp ratio is ", Sharpe)
    return "HI"

if __name__ == "__main__":
    app.run(debug=True)





