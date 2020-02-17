import pandas as pd
import numpy as np
import pandas_datareader.data as web
import datetime as dt
import matplotlib.pyplot as plt
from dateutil.relativedelta import relativedelta
from datetime import timedelta

import portfolio_lib as pl

url = "https://finance.yahoo.com/quote/{}/history"


yahoo_up = True


def OptimizePortfolio(tickers, user_expected_return, FindBestRatio, cash):

    stocks = tickers
    stocks = sorted(stocks)
    

    print( "The final stocks ", stocks )
    
    if yahoo_up:
        data = web.DataReader( stocks, data_source="yahoo", start='01/01/2018', end='01/01/2020')['Adj Close']
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



"""
Find and return the current share value for the stock

Had lots of issued with dates because the stock market closes on weekends, holidays and
doesnt open in the UK until late afternoon
"""

def share_price( ticker ):

    one = dt.datetime.now()

    open_time = dt.time(15, 0, 0 )
    
    # If its before 3pm, use the price from the day before
    # If its a holiday, use the previous available day

    if pl.isHoliday( one ):
        one = pl.find_suitable_date( one )
    elif one.time() < open_time:
        if one.weekday() == 0:
            one = one - timedelta(days=2)
        else:
            one = one - timedelta(days=1)

    elif( one.weekday() == 5 ):
        one = one - timedelta(days=1)

    elif( one.weekday() == 6 ):
        one = one - timedelta(days=2)
 

    # Format date for the datareader
    date_formated = one.strftime("%m/%d/%Y")

    print( "This is the date ", date_formated )

    stocks = [ticker]

    # Read the Adj Close for the 1 stock on a single day
    data = web.DataReader( stocks, data_source="yahoo", start=date_formated, end=date_formated)['Adj Close']

    data.sort_index(inplace=True)

    # Obtain the adj close
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


def find_stock_names( tickers ):

    data = pd.read_csv("C:\\Users\\marc.smith\\AppData\\Local\\Programs\\Python\\Python37-32\\static\\symbols\\industries.csv")

    stock_name_list = []

    for item in tickers:
        stock_name = data.loc[data['Symbol'] == item, 'Name'].iloc[0]

        stock_name_list.append( stock_name )

    return stock_name_list


def find_sectors( symbols ):
    
    data = pd.read_csv("C:\\Users\\marc.smith\\AppData\\Local\\Programs\\Python\\Python37-32\\static\\symbols\\industries.csv")

    sector_list = []
    stock_name_list = []

    for item in symbols:
        # Find the companies sector and official name (not ticker)
        sector = data.loc[data['Symbol'] == item, 'Sector'].iloc[0]
        stock_name = data.loc[data['Symbol'] == item, 'Name'].iloc[0]

        sector_list.append(sector)

    return sector_list

def plot_sector_chart( sector_list, weights ):

    plt.cla()
    plt.clf()

    
   
    sector_list, sector_weights = calculate_sector_weights( sector_list, weights )

   
    
    fig1, ax1 = plt.subplots()
    colors = ['yellowgreen', 'gold', 'lightskyblue', 'lightcoral', 'm', 'k', 'c', 'r']
    patches, texts = plt.pie(sector_weights, colors=colors, startangle=90)
    plt.legend(patches, sector_list, loc="best")
    ax1.axis('equal')
    plt.tight_layout()
    plt.savefig('static\\images\\sector_makeup.png', bbox_inches='tight')
    



"""
Combine weights of stocks that belong to the same sector so
the user can see how much they have invested in each sector

"""

def calculate_sector_weights(sector_list, weights):

    sector_weights = perform_sector_count( sector_list, weights )

    labels = [ "Capital Goods",  "Consumer Non-Durables", "Consumer Services" ,"Energy", "Finance", "Health Care", "Technology" ]


    i = 0
  
    for w in sector_weights:
       
        if w == 0:
            labels[i] = ""

        i += 1

    sector_weights = (list(filter(None, sector_weights)))

   
    sector_weights = round_list(sector_weights)
    labels = list(filter(None, labels))

 
    
    return labels, sector_weights




                      
def perform_sector_count( sector_list, weights ):

    technology = 0
    energy = 0
    finance = 0
    energy= 0
    consumer_services = 0
    capital_goods = 0
    health_care = 0
    consumer_non_durables = 0

    i =0

    
    for sector in sector_list:    
   
        if sector == "Technology":
            technology += weights[i]

        elif sector == "Healthcare":
            energy += weights[i]

        elif sector == "Finance":
            finance += weights[i]

        elif sector == "Consumer Non-Durables":
            consumer_non_durables += weights[i]

        elif sector == "Energy":
            energy += weights[i]
            
        elif sector == "Consumer Services":
            consumer_services += weights[i]

        elif sector == "Capital Goods":
            capital_goods += weights[i]

        elif sector == "Health Care":
            health_care += weights[i]

        i += 1

    
    sector_weights = [capital_goods, consumer_non_durables, consumer_services, energy, finance, health_care, technology ]

    return sector_weights




def add_stocks( num_stocks, tickers, sectors ):

    found_stocks = []
    found_sectors = []

    sector_list = sectors.copy()
    
   
    labels = [ "Capital Goods",  "Consumer Non-Durables", "Consumer Services" ,"Energy", "Finance", "Health Care", "Technology" ]
    
    
    i = 0

    #Used to hold a list of all sectors that the user does not have in their portfolio
    missing_sectors = []

    for label in labels:
        if label not in sector_list:
          
            missing_sectors.append( labels[i] )
        i += 1


    #print( "Missing ", missing_sectors )

    # Add stocks that have sectors that have 0 occurences in the current portfolio
    # What if there are more misisng sectors than new stocks required???
    
    for x in range(0,len(missing_sectors)):

        # Find random stock belonging to that sector       
        stock = find_stock_in_sector( missing_sectors[x])

        found_stocks.append( stock )
        found_sectors.append( missing_sectors[x] )

        sector_list.append( missing_sectors [x] )
        num_stocks -= 1


    # If there are still more stocks to find, use the least occuring sector

    #print( "After the first find, this is how many are left ", num_stocks )
    #print( "Stocks ", stocks )
    #print( "Sectors ", sectors )

    
    if num_stocks != 0:
        
        for x in range( 0, num_stocks ):       
            c, least = len(sector_list), 0

            for x in sector_list:
                if sector_list.count(x) <= c :
                    c = sector_list.count(x)
                    least = x


            stock = find_stock_in_sector( least )        

            found_sectors.append(least)
            found_stocks.append( stock )
       
    

  
        
        
    return found_stocks, found_sectors

def find_stock_in_sector( sector ):
    
    data = pd.read_csv("C:\\Users\\marc.smith\\AppData\\Local\\Programs\\Python\\Python37-32\\static\\symbols\\industries.csv")

   
      
    data = data.loc[data['Sector'] == sector, 'Symbol']


    symbol = data.sample().iloc[0]



    return symbol



















