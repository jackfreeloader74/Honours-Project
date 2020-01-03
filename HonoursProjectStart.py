import pandas as pd
import numpy as np
import pandas_datareader.data as web
import datetime as dt
import matplotlib.pyplot as plt


def OptimizePortfolio(stock1, stock2, stock3, user_expected_return):

    #stocks = [ 'AAPL','AMZN', 'MSFT', 'TSLA' ]

    print(stock1, stock2, stock3)
    stocks = [ 'AAPL', stock1, stock2, stock3]

    data = web.DataReader( stocks, data_source="yahoo", start='01/01/2015', end='01/01/2018')['Adj Close']
    data.sort_index(inplace=True)

    num_portfolios = 250


    # convert daily stock prices into daily returns
    returns = data.pct_change()

    # Calculate mean daily return and covariance of daily returns

    # These have nothing to do with portfolio weights so can do before the loop
    mean_daily_returns = returns.mean()
    cov_matrix = returns.cov()


    results = np.zeros((3, num_portfolios))
    currentSharpe = -4000
    lowest_current_risk = -4000
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

        if( results[2,i] > currentSharpe ):
            currentSharpe = results[2,i]
            
            # Save weights #
            BestWeights = weights


        ## Find the portfolio with the expected return that matches the specified one
            ## but also has the lowest risk
        
        if( portfolio_return > int(user_expected_return) and
            portfolio_std_dev < lowest_current_risk ):

            BestWeights = weights
            BestReturn = portfolio_return
    
        
    # Record and plot results
    results_frame = pd.DataFrame(results.T, columns=['ret', 'stdev', 'sharpe'] )

    labels = 'AMZN', stock1, stock2, stock3
   
    fig1, ax1 = plt.subplots()
    colors = ['yellowgreen', 'gold', 'lightskyblue', 'lightcoral']
    patches, texts = plt.pie(BestWeights, colors=colors, startangle=90)
   
    plt.legend(patches, labels, loc="best")
    ax1.axis('equal')
    plt.tight_layout()

    plt.savefig('static/images/pie_chart.png', bbox_inches='tight')

    
    return BestReturn














