import pandas as pd
import numpy as np
import pandas_datareader.data as web
import datetime as dt
import matplotlib.pyplot as plt
from dateutil.relativedelta import relativedelta
from datetime import timedelta


url = "https://finance.yahoo.com/quote/{}/history"


yahoo_up = True


def OptimizePortfolio(tickers, user_expected_return, FindBestRatio, cash):

    stocks = tickers
    stocks = sorted(stocks)
    
    
    if yahoo_up:
        data = web.DataReader( stocks, data_source="yahoo", start='01/01/2010', end='01/01/2020')['Adj Close']
        data.sort_index(inplace=True)
    else:
        data = pd.read_csv('stocks.csv')
        data.sort_index(inplace=True)
        data = data.drop(columns=['Date'])
       

    

    

    # Validate user provided tickers
    for ticker in stocks:
        if data[ticker].isnull().all():
            return False, ticker, None


    # Start Optimization (MPT)

    num_portfolios = 500

    # convert daily stock prices into daily returns
    returns = data.pct_change()

    # Calculate mean daily return and covariance of daily returns
    # These have nothing to do with portfolio weights so can do before the loop
    mean_daily_returns = returns.mean()
    cov_matrix = returns.cov()


    results = np.zeros((3, num_portfolios))
    currentSharpe = -4000
    lowest_current_risk = 4000
    BestReturn = 0
    
    print("Starting optimization...")

    for i in range(num_portfolios):


        
    
        #select random weights for portfolio assets
        weights = np.random.random(len(stocks)) 
        weights /= np.sum(weights)

        # anualised portfolio return
        portfolio_return = round(np.sum(mean_daily_returns * weights) * 252, 2)

        # annualised portfolio volatility
        portfolio_std_dev = round(np.sqrt( np.dot(weights.T, np.dot(cov_matrix, weights)))
                              * np.sqrt(252),2)   

        # Store results in an array
        results[0,i] = portfolio_return
        results[1,i] = portfolio_std_dev

        
        # Store Sharpe Ratio  ( return / volatility )
        results[2,i] = results[0,i] / results[1,i]
   
        ## Find the portfolio with the best sharpe ratio
        if FindBestRatio:
             if( results[2,i] > currentSharpe ):
                currentSharpe = results[2,i]
                BestWeights = round_list(weights)
                BestReturn = portfolio_return
                currentRisk = round(results[1,i],2)
            
        else:
            ## Find the portfolio with the expected return that is greater than or equal to the specified return
                ## but also has the lowest risk    
            if( portfolio_return > float(user_expected_return) and
                portfolio_std_dev < lowest_current_risk ):

            
                BestWeights = round_list(weights)
                BestReturn = portfolio_return
                currentRisk = round(results[1,i],2)


    labels = []

    for item in stocks:
        labels.append( item )
  
    #labels = tickers[0],tickers[1],tickers[2], tickers[3]

    # Plot Graphs
    plot_efficient_chart( pd, results)

    plot_pie_chart(labels, BestWeights)

    plot_line_chart(data, stocks, BestWeights, float(cash) )
  
    return BestReturn, BestWeights, currentRisk



"""

Use the stocks, weights, cash value and the current share value to calculate how
many shares of each stock can be bought.


User inputs cash in pounds but stock value is in USD. Need to convert currency

"""
from currency_converter import CurrencyConverter


def CalculateShareVolume( tickers, weights, cash ):

    share_list = [];

    i=0
    
    for w in weights:

        stock_cash_value_pounds = float(w) * float(cash)

        c = CurrencyConverter()

        stock_cash_value_dollars = c.convert (stock_cash_value_pounds, 'GBP', 'USD')
        
        share_volume = round( stock_cash_value_dollars / share_price( tickers[i]), 2)
       
        share_list.append(share_volume)
        i += 1

    return share_list




def share_price( ticker ):

    one = dt.datetime.now()

    open_time = dt.time(15, 0, 0 )
    
    # If its before 3pm, use the price from the day before
    # If its a monday or monday use info from saturday

    if one.time() < open_time:
        if one.weekday() == 0:
            one = one - timedelta(days=2)
        else:
            one = one - timedelta(days=1)

    elif( one.weekday() == 5 ):
        one = one - timedelta(days=1)

    elif( one.weekday() == 6 ):
        one = one - timedelta(days=2)

    
    date_formated = one.strftime("%m/%d/%Y")

   
   
    
    stocks = [ticker]
    
    data = web.DataReader( stocks, data_source="yahoo", start=date_formated, end=date_formated)['Adj Close']

    data.sort_index(inplace=True)

    


    value = data[ticker].iloc[0]

   
    
    return value


def plot_efficient_chart( pd, results):

    plt.cla()
    plt.clf()
    results_frame = pd.DataFrame(results.T, columns=['ret', 'stdev', 'sharpe'] )
    plt.scatter(results_frame.stdev,results_frame.ret,c=results_frame.sharpe,cmap='RdYlBu')
    plt.colorbar()
    plt.savefig('static\\images\\efficient_frontier.png')

def plot_pie_chart(labels, BestWeights):

    plt.cla()
    plt.clf()
    
    fig1, ax1 = plt.subplots()
    colors = ['yellowgreen', 'gold', 'lightskyblue', 'lightcoral', 'm', 'k', 'c', 'r']
    patches, texts = plt.pie(BestWeights, colors=colors, startangle=90)
    plt.legend(patches, labels, loc="best")
    ax1.axis('equal')
    plt.tight_layout()
    plt.savefig('static\\images\\pie_chart.png', bbox_inches='tight')



""" Warning, this function severely alters the data frame so
any more graphs and logic that involve the df should be done before this function call
"""

def plot_line_chart(data, tickers, weights, cash):

 
    i = 0

    data['Total'] = data[tickers[0]]

   

    for tick in tickers:
        data[tick] = data[tick].pct_change()

        data['Total'] = data['Total'] + ( weights[i]*cash*(1+data[tick]) )

        i += 1
        

    # Only record every 50 rows for graph
    data = data.iloc[::50,:]

    plt.cla()
    plt.clf()
    ax = data['Total'].plot(label='Portfolio',figsize=(16,8), title="Portfolio Performance")

    ax.set_ylabel("Portfolio Value ($)")
    
    plt.savefig('static\\images\\portfolio_value_chart.png', bbox_inches='tight')



def round_list(param_list):
    
    param_list = [ round(elem, 3) for elem in param_list ]

    return param_list






