import pandas as pd
import numpy as np
import pandas_datareader.data as web
import datetime as dt
import matplotlib.pyplot as plt
from dateutil.relativedelta import relativedelta

url = "https://finance.yahoo.com/quote/{}/history"


def OptimizePortfolio(tickers, user_expected_return, FindBestRatio):

     
    stocks = [ tickers[0], tickers[1], tickers[2], tickers[3] ]
    stocks = sorted(stocks)
    

    data = web.DataReader( stocks, data_source="yahoo", start='01/01/2010', end='01/01/2020')['Adj Close']
    data.sort_index(inplace=True)

    # Validate user provided tickers

    for ticker in stocks:
        if data[ticker].isnull().all():
            return False, ticker, None


    # Start Optimization (MPT)

    num_portfolios = 1000

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
        weights = np.random.random(4) 
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

        
    # Efficient frontier graph
    plot_efficient_chart( pd, results)

    # Pie Chart
    labels = tickers[0],tickers[1],tickers[2], tickers[3]
    plot_pie_chart(labels, BestWeights)

  
    return BestReturn, BestWeights, currentRisk




def CalculateShareVolume( tickers, weights, cash ):

    share_list = [];

    i=0
    
    for w in weights:

        stock_cash_value = float(w) * float(cash)

        #print("Stock cash value", stock_cash_value)
        share_volume = round(stock_cash_value / share_price( tickers[i]), 2)
        #print("Share volume ", tickers[i], share_volume)
        share_list.append(share_volume)
        i += 1


    print("Share Volume list", share_list)
                
    
    return share_list


def share_price( ticker ):

    one = dt.datetime.now()
    date_formated = one.strftime("%d/%m/%Y")

    stocks = [ticker]
    
    data = web.DataReader( stocks , data_source="yahoo", start=date_formated, end=date_formated)['Adj Close']
    data.sort_index(inplace=True)


   
    
    value = data.loc[data.index[0], ticker]



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
    colors = ['yellowgreen', 'gold', 'lightskyblue', 'lightcoral']
    patches, texts = plt.pie(BestWeights, colors=colors, startangle=90)
    plt.legend(patches, labels, loc="best")
    ax1.axis('equal')
    plt.tight_layout()
    plt.savefig('static\\images\\pie_chart.png', bbox_inches='tight')




def round_list(param_list):
    
    param_list = [ round(elem, 2) for elem in param_list ]

    return param_list


