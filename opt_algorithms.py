import pandas as pd
import numpy as np
import pandas_datareader.data as web
import datetime as dt
import matplotlib.pyplot as plt
from dateutil.relativedelta import relativedelta
from datetime import timedelta
import time

from random import randint
import portfolio_lib as pl

from portfolio_classes.portfolio import Portfolio
from portfolio_classes.asset import Asset



yahoo_up = True

global_start_date = '01/01/2010'
global_end_date = '01/01/2020'
TRADING_DAYS = 252

clear_bit_api_key = "sk_34b33f60cc6cb5f54ee9033cfe4bf757"


# Specify number of iterations to create
num_portfolios = 250



# Method to produce the weight allocation deemed optimal by the algorithm

def OptimizePortfolio( portfolio ):

    assets = portfolio.assets

    # Extract a list of the ticker names to pass to pandas datareader
    ticker_list = list(a.ticker for a in assets)

    # Has yahoo API been taken down?
    if yahoo_up:
        try:
            #Read adj close data from api for each stock into a dataframe
            data = web.DataReader( ticker_list, data_source="yahoo", start=global_start_date, end=global_end_date)['Adj Close']
            data.sort_index(inplace=True)
        except:
            # Server side API problem -> Bail out and tell user somethig went wrong
            return False, "Something went wrong :("
    else:
        # If API goes down, use csv file
        data = pd.read_csv('stocks.csv')
        data.sort_index(inplace=True)
        data = data.drop(columns=['Date'])


    # Validate user provided tickers
    for asset in assets:
        if data[asset.ticker].isnull().all():
            message = "Invalid Ticker Entered: %s" % asset.ticker
            return False, message

    # Calculate the sharpe ratio for each stock in the portfolio and put it into a list
    # This list will be used to plot points on the efficient frontier graph
    stock_sharpe_list = find_stock_sharpes(data, assets)
    data = data.dropna()

    # convert daily stock prices into daily returns
    returns = data.pct_change()

    # Calculate mean daily return and covariance of daily returns
    mean_daily_returns = returns.mean()


    # If we are using PMPT, use downside derivation instead of just normal stdev.
    # The downside derivation (MAR) is defined by the user and held in variable mar_value
    if portfolio.algorithm == "PMPT":
        for asset in assets:
           ticker = asset.ticker
           returns[returns[ticker] > portfolio.mar_value ] = 0

    cov_matrix = returns.cov()

    results = np.zeros((3, num_portfolios))


    currentSharpe = -4000

    lowest_current_risk = 4000
    BestReturn = 0


    print("Starting optimization...")
    for i in range(num_portfolios):

        #select random weights for portfolio assets
        weights = np.random.random(len(assets))
        weights /= np.sum(weights)

        # anualised portfolio return
        portfolio_return = round(np.sum(mean_daily_returns * weights) * TRADING_DAYS, 2)

        # annualised portfolio volatility
        portfolio_std_dev = round(np.sqrt( np.dot(weights.T, np.dot(cov_matrix, weights)))
                              * np.sqrt(TRADING_DAYS),2)

        # Store results in an array
        results[0,i] = portfolio_return
        results[1,i] = portfolio_std_dev

        # Store Sharpe/Sortino Ratio  ( return / volatility )
        results[2,i] = results[0,i] / results[1,i]

        # Find the portfolio with the best sharpe ratio
        if portfolio.BestRatio:
            if results[2,i] > currentSharpe:
                currentSharpe = results[2,i]
                BestWeights = round_list(weights)
                BestReturn = portfolio_return
                currentRisk = round(results[1,i],2)
        else:
            # Find the portfolio with the expected return that is greater than or equal to the specified return
            # but also has the lowest risk
            if portfolio_return > float(portfolio.user_expected_return) and portfolio_std_dev < lowest_current_risk:
                BestWeights = round_list(weights)
                BestReturn = portfolio_return
                currentRisk = round(results[1,i],2)

    # Add the newly found weights to the asset objects
    assets = pl.add_weights_to_assets(assets, BestWeights)

    # Add the exp return and risk to portfolio object
    portfolio.exp_return = BestReturn
    portfolio.risk = currentRisk


    labels = []

    # Get a list of the stocks to be used as labels for the pie charts
    for asset in assets:
            labels.append( asset.ticker )

    # Plot Graphs
    plot_efficient_chart( results, portfolio, stock_sharpe_list)

    plot_pie_chart(labels, BestWeights)

    plot_line_chart( ticker_list, BestWeights, float(portfolio.cash) )

    return True, ""



"""
Use the stocks, weights, cash value and the current share value to calculate how
many shares of each stock can be bought.

User inputs cash in pounds but stock value is in USD. Need to convert currency
"""
from currency_converter import CurrencyConverter


def CalculateShareVolume( portfolio ):

    cash = portfolio.cash
    assets = portfolio.assets
    share_volume_list = []

    # For each asset, convert GBP to USD, calculate current share price and divide to find number shares
    for a in assets:
        stock_cash_value_pounds = float(a.weight) * float(cash)
        c = CurrencyConverter()
        stock_cash_value_dollars = c.convert (stock_cash_value_pounds, 'GBP', 'USD')
        share_price = calculate_share_price( a.ticker )

        # If share price is valid, add it to asset object
        if share_price:
            a.share_volume = round( stock_cash_value_dollars / share_price, 2)
        else:
            # API call to get share price failed, return n/a instead
            a.share_volume = "N/A"

        share_volume_list.append( a.share_volume )

    return share_volume_list


class StockSharpe:
    risk = 0
    exp_return = 0
    ticker = ""


# Find the sharpe ratio for each stock in the tickers list
# The data param contains the adjusted closes for each stock in the tickers list
def find_stock_sharpes( data, assets):

    stock_list = []

    for asset in assets:

        sharpeObj = StockSharpe()

        # convert daily stock prices into daily returns
        returns = data[asset.ticker].pct_change()

        # Calculate mean daily return and covariance of daily returns
        mean_daily_returns = returns.mean()


        # anualised portfolio return
        portfolio_return = round(np.sum(mean_daily_returns) * TRADING_DAYS, 2)

        # annualised portfolio volatility
        portfolio_std_dev = round(np.sqrt( mean_daily_returns)
                              * np.sqrt(TRADING_DAYS),2 )


        sharpeObj.risk =portfolio_std_dev

        sharpeObj.exp_return = portfolio_return

        sharpeObj.ticker = asset.ticker


        stock_list.append( sharpeObj )

    return stock_list


"""
Find and return the current share value for the stock

Had lots of issued with dates because the stock market closes on weekends, holidays and
doesnt open in the UK until late afternoon
"""

def calculate_share_price( ticker ):

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




    stock_value = 0

    # Read the Adj Close for the 1 stock on a single day
    try:
        # Format date for the datareader
        date_formated = one.strftime("%m/%d/%Y")
        data = web.DataReader( [ticker], data_source="yahoo", start=date_formated, end=date_formated)['Adj Close']
        data.sort_index(inplace=True)

        # Obtain the adj close
        stock_value = data[ticker].iloc[0]
    except:
        # API Call failed for some reason
        stock_value = False

    return stock_value


def plot_efficient_chart( results, portfolio, stock_sharpe_list):

    plt.cla()
    plt.clf()
    results_frame = pd.DataFrame(results.T, columns=['ret', 'stdev', 'sharpe'] )

    plt.xlabel('Volatility')
    plt.ylabel('Returns')


    plt.scatter(results_frame.stdev,results_frame.ret,c=results_frame.sharpe,cmap='RdYlBu')
    plt.colorbar()

    # Best Sharpe Ratio
    plt.scatter(portfolio.risk, portfolio.exp_return, marker=(5,1,0),color='r',s= 100)


    # Plot indivudual stock sharpe values
    for obj in stock_sharpe_list:

        plt.annotate( "Stock", (obj.risk, obj.exp_return), xytext=(0,10))
        plt.scatter( obj.risk, obj.exp_return, marker=(5,1,0), color='g', s=100)

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



def query_ticker_data( ticker ):



    today = time.strftime("%m/%d/%Y")

    data = web.DataReader( [ticker], data_source="yahoo", start=global_start_date, end=today)


    close_row = data['Close'].iloc[-1]
    close = round(close_row[ticker],2)

    # Draw Graph
    plt.cla()
    plt.clf()

    ax = data['Close'].plot(label='Portfolio',figsize=(16,8), title="Stock Performance")
    ax.set_ylabel("Portfolio Value ($)")


    line_chart_file = "static\\images\\stock_value_chart_{}.png".format(randint(100, 999))
    plt.savefig(line_chart_file, bbox_inches='tight')


    return close, line_chart_file



""" Warning, this function severely alters the data frame so
any more graphs and logic that involve the df should be done before this function call
"""

def plot_line_chart(tickers, weights, cash):

    index = ['NYA']

    # Index fund df


    # The data for NYA stock would change between API calls? Some days were missing and different etc...
    # Best solution for this was to read the correct values from an index fund
    index_data = pd.read_csv("index.csv")


    # Portfolio df
    data = web.DataReader( tickers, data_source="yahoo", start=global_start_date, end= '03/14/2019')['Adj Close']
    data = data.dropna()
    data.reset_index(inplace=True,drop=False)


    # First stock in portfolio df
    first_stock = tickers[0]
    first_stock_data = web.DataReader( [ tickers[0]], data_source="yahoo", start=global_start_date, end= '03/14/2020')['Adj Close']
    first_stock_data = data.dropna()

    first_stock_data.reset_index(inplace=True,drop=False)


    # Find the earliest date that our portfolio prices start at.

    start_date = data['Date'].loc[data.first_valid_index()]
    start_date = "2010-01-04"


    fund_start_index = index_data.loc[index_data['Date'] == start_date ]


    fund_start_index = fund_start_index.index[0]


    """
    Index fund df may not be the same length as the portfolio dataframe
    Need to shorten index fund data so that it starts on the same date as the portfolio data
    """

    for i in range(0, len(index_data)):

        if i < fund_start_index:

            index_data = index_data.drop( [i])

    #Calculate the total value of the stocks (not including cash)
    data['Total'] = 0
    i = 0

    for tick in tickers:
        data['Total'] = data['Total'] + data[tick] * weights[i]
        i += 1


    # Configure Index fund dataframe
    index_data['pct_change'] = index_data['NYA'].pct_change()
    index_data['Index_Total'] = 0
    index_data.reset_index(inplace=True,drop=False)
    index_data.loc[0,'Index_Total'] = cash

    # Configure 1 stock dataframe
    first_stock_data['pct_change'] = first_stock_data[first_stock].pct_change()
    first_stock_data['Portfolio_Total'] = 0
    first_stock_data.loc[0,'Portfolio_Total'] = cash

    #Configure Portfolio dataframe
    data['pct_change'] = data['Total'].pct_change()
    data['Portfolio_Total'] = 0
    data.loc[0,'Portfolio_Total'] = cash



    # To monitor changes in cash, need to look at the previous row ( df.loc[i-1] ) and add it to the % change in cash

    graph_length = 0

    if len(index_data) > len(data):
        graph_length = len(data)
    else:
        graph_length = len(index_data)


    for i in range(1, graph_length ):
        index_data.loc[i, 'Index_Total'] = index_data.loc[i-1, 'Index_Total'] + index_data.loc[i, 'pct_change']*cash
        data.loc[i, 'Portfolio_Total'] = data.loc[i-1, 'Portfolio_Total'] + data.loc[i, 'pct_change']*cash
        first_stock_data.loc[i, 'Portfolio_Total'] = first_stock_data.loc[i-1, 'Portfolio_Total'] + first_stock_data.loc[i, 'pct_change']*cash


    # Create the df that will be used to plot the line graph
    plot_frame = pd.DataFrame(columns=['Index Value' ] )

    plot_frame['Index Value'] = index_data['Index_Total']
    plot_frame['Portfolio Value'] = data['Portfolio_Total']
    plot_frame[first_stock] = first_stock_data['Portfolio_Total']

    plot_frame.index = index_data['Date']
    plot_frame = plot_frame[plot_frame['Index Value'] != 0]


    # Draw Graph
    plt.cla()
    plt.clf()

    ax = plot_frame.plot(label='Portfolio',figsize=(16,8), title="Past Portfolio Performance")
    ax.set_ylabel("Portfolio Value ($)")

    plt.savefig('static\\images\\portfolio_value_chart.png', bbox_inches='tight')






def round_list(param_list):

    param_list = [ round(elem, 3) for elem in param_list ]

    return param_list


def find_stock_names( tickers ):

    data = pd.read_csv("..\\static\\symbols\\filtered_stocks.csv")

    stock_name_list = []

    for item in tickers:
        stock_name = data.loc[data['Symbol'] == item, 'Name'].iloc[0]

        stock_name_list.append( stock_name )

    return stock_name_list



def find_sectors( symbols ):

    data = pd.read_csv("..\\static\\symbols\\filtered_stocks.csv")

    sector_list = []
    stock_name_list = []

    for item in symbols:
        # Find the companies sector and official name (not ticker)
        try:
            sector = data.loc[data['Symbol'] == item, 'Sector'].iloc[0]
            stock_name = data.loc[data['Symbol'] == item, 'Name'].iloc[0]

        except:
            sector = ""

        if( sector == "" ):
            return item
        else:
            sector_list.append(sector)

    return sector_list


"""
Plots and saves the Pie chart that shows sector breakdown
"""


def plot_sector_chart( portfolio ):

    plt.cla()
    plt.clf()

    # Find each sectors total makeup of the portfolio is
    sector_list, sector_weights = calculate_sector_weights( portfolio )

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

def calculate_sector_weights(portfolio):


    sector_weights = perform_sector_count( portfolio )
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



""" Counts how many of each sector are in the portfolio """

def perform_sector_count( portfolio ):

    technology = 0
    energy = 0
    finance = 0
    energy= 0
    consumer_services = 0
    capital_goods = 0
    health_care = 0
    consumer_non_durables = 0

    assets = portfolio.assets
    i =0

    for a in assets:

        if a.sector == "Technology":
            technology += a.weight

        elif a.sector == "Healthcare":
            energy += a.weight

        elif a.sector == "Finance":
            finance += a.weight

        elif a.sector == "Consumer Non-Durables":
            consumer_non_durables += a.weight

        elif a.sector == "Energy":
            energy += a.weight

        elif a.sector == "Consumer Services":
            consumer_services += a.weight

        elif a.sector == "Capital Goods":
            capital_goods += a.weight

        elif a.sector == "Health Care":
            health_care += a.weight

        i += 1

    sector_weights = [capital_goods, consumer_non_durables, consumer_services, energy, finance, health_care, technology ]

    return sector_weights




def add_stocks( num_stocks, tickers, sectors ):

    found_stocks = []
    sector_list = sectors.copy()

    labels = [ "Capital Goods",  "Consumer Non-Durables", "Consumer Services" ,"Energy", "Finance", "Health Care", "Technology" ]


    #Used to hold a list of all sectors that the user does not have in their portfolio
    missing_sectors = []

    i = 0
    for label in labels:
        if label not in sector_list:

            missing_sectors.append( labels[i] )
        i += 1


    # Add stocks that have sectors that have 0 occurences in the current portfolio
    # What if there are more misisng sectors than new stocks required???

    max_iterator = len(missing_sectors)

    if len(missing_sectors) > num_stocks:
        max_iterator = num_stocks


    for x in range(0,max_iterator):

        # Find random stock belonging to that sector
        stock = find_stock_in_sector( missing_sectors[x])

        found_stocks.append( stock )
        sector_list.append( missing_sectors [x] )
        num_stocks -= 1


    # If there are still more stocks to find, use the least occuring sector


    if num_stocks != 0:

        for x in range( 0, num_stocks ):
            c, least = len(sector_list), 0

            for x in sector_list:
                if sector_list.count(x) <= c :
                    c = sector_list.count(x)
                    least = x


            stock = find_stock_in_sector( least )
            found_stocks.append( stock )


    return found_stocks




def find_stock_in_sector( sector ):

    data = pd.read_csv("..\\static\\symbols\\filtered_stocks.csv")



    data = data.loc[data['Sector'] == sector, 'Symbol']


    symbol = data.sample().iloc[0]



    return symbol
