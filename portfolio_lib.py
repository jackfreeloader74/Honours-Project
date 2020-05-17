from dateutil.relativedelta import relativedelta
from datetime import timedelta
import datetime as dt
import requests
import time
import ast
import clearbit
import opt_algorithms as hp
import pandas as pd

from portfolio_classes.portfolio import Portfolio
from portfolio_classes.asset import Asset

api_key1 = "2M6F7YVUOQBLY4WF"
api_key2 = 'NEMPJL3V114R3DW8'


clearbit.key = "sk_34b33f60cc6cb5f54ee9033cfe4bf757"


start_date = "2010-01-01"
end_date = "2020-01-01"


def create_portfolio_object(request):

    # Obtain all input from the user
    user_expected_return = request['expectedReturn']
    algorithm = request['algorithm']
    mar_value = request['mar_value'] # Only relevant to PMPT
    cash = request['cash']
    portfolio_size = request['portfolioSize']
    tickers = retrieve_user_stocks(request)

    # If the checkbox is off, the request form will throw an error if you try to access it
    BestRatio = True;
    try:
        Checked = request.form['checkBox']
        BestRatio = False
    except:
        Checked = "off"

    # Default cash to 10,000 if none is provided
    if(cash == "" ):
        cash = 10000

    # Calculate what sectors these belong to as well as the stocks official name
    sector_list = list(hp.find_sectors( tickers ) ) # What sectors do they belong to
    tickers = sorted(auto_select_stocks( portfolio_size, tickers, sector_list) ) # Find stocks to add to portfolio
    sector_list = list(hp.find_sectors( tickers ) ) # Find all the sectors again but with the newly added stocks

    # Create the portfolio and asset objects
    portfolio = Portfolio(cash=cash, algorithm=algorithm, mar_value=mar_value, user_expected_return=user_expected_return)

    # Format algorithm and MAR value
    portfolio.algorithm = calculate_algorithm( algorithm )
    portfolio.mar_value = calculate_mar( mar_value ) # Use the dropdown number option to calculate what MAR was selected
    portfolio.BestRatio = BestRatio

    assets = createAssets(tickers, sector_list, portfolio)
    portfolio.assets = assets

    return portfolio


# Place all user provided stocks into a list and filter out the empty inputs
def retrieve_user_stocks(request):

    tickers = []

    _ticker1 = request['inputTicker1']
    _ticker2 = request['inputTicker2']
    _ticker3 = request['inputTicker3']
    _ticker4 = request['inputTicker4']
    _ticker5 = request['inputTicker5']
    _ticker6 = request['inputTicker6']
    _ticker7 = request['inputTicker7']
    _ticker8 = request['inputTicker8']
    portfolio_size = request['portfolioSize']

    # Transorm tickers to appropriate format (Sort + Capitalize)
    tickers = [_ticker1,_ticker2, _ticker3, _ticker4, _ticker5
               , _ticker6, _ticker7, _ticker8]
    tickers = filter_tickers( tickers, portfolio_size ) # Filter out empty inputs

    return tickers




def recreate_portfolio(request):

    Return = float(request['Return'])
    Risk = request['Risk']
    weights = request['weights']
    tickers = request['tickers']
    algorithm = request['algorithm']
    cash = request['cash']
    cash_str = "{:,.2f}".format(float(cash))
    share_volume_list = request['share_volume_list']
    sectors = request['sectors']
    cash = request['cash']
    cash_str = "{:,.2f}".format(float(cash))

    # Format these variables back into the appropriate format
    weights = process_weights( weights )
    tickers = ast.literal_eval(tickers)
    sectors = ast.literal_eval(sectors)
    algorithm = calculate_ratio(algorithm)
    share_volume_list = ast.literal_eval(share_volume_list)

    # Recreate the Portfolio object
    portfolio = Portfolio(cash=float(cash), algorithm=algorithm, mar_value=0, user_expected_return="")
    portfolio.exp_return = Return
    portfolio.risk = Risk
    portfolio.cash_str = cash_str

    # Recreate the asset objects
    assets = createAssets(tickers, sectors, portfolio)
    assets = add_weights_to_assets(assets, weights)
    assets = add_share_volume_to_assets(assets, share_volume_list)
    assets = add_names_to_assets( assets )

    # Link portfolio back to assets
    portfolio.assets = assets

    return portfolio



# Create and return a list of asset objects
def createAssets(tickers, sector_list, portfolio):

    asset_list = []
    i=0

    for tick in tickers:
        asset = Asset(ticker=tick, sector=sector_list[i], portfolio=portfolio)
        asset_list.append(asset)

        i += 1

    return asset_list

def add_weights_to_assets( assets, weight_list):

    i = 0
    for a in assets:
        a.weight = weight_list[i]
        i += 1

    return assets

def add_share_volume_to_assets( assets, share_volume_list ):

    i = 0
    for a in assets:
        a.share_volume = share_volume_list[i]
        i += 1

    return assets

# Is today one of the several holidays in which the stock market is closed

def isHoliday( today ):

    presidents = dt.date(2020, 2, 17)

    memorial = dt.date( 2020, 4, 10 )

    independance = dt.date( 2020, 7, 4 )

    labor = dt.date( 2020, 10, 7 )

    thanksgiving = dt.date( 2020, 11, 26 )

    christmas = dt.date(2020, 12, 25 )

    holiday_list = [ presidents, memorial, independance, labor, thanksgiving, christmas ]

    for holiday in holiday_list:



        if today.day == holiday.day and today.month == holiday.month:
            return True

        if today.day == holiday.day + 1 and today.month == holiday.month:

            return True

    return False





# Reduce the list of tickers to the size provided by the user
def filter_tickers( tickers, size ):

    size = int(size)

    # Remove empty strings from the list
    tickers = list(filter(None, tickers))
    tickers = tickers[:size]

    tickers = [ element.upper() for element in tickers ] # Convert to uppercase
    tickers = sorted(tickers)

    return tickers




def find_suitable_date(date):

    date = date - timedelta(days = 1)

    if date.weekday() == 6 :

        date = date - timedelta(days = 2)

    elif date.weekday() == 5:
        date = date - timedelta(days = 1)

    # Add catch for the morning after a holiday
    elif isHoliday( date ):


        date = date - timedelta(days = 1)

        if date.weekday() == 6 :

            date = date - timedelta(days = 2)

        elif date.weekday() == 5:
            date = date - timedelta(days = 1)

    return date





"""
missing_stock_count = How many stocks the app needs to choose for the user
"""

def auto_select_stocks( size, tickers,  sectors ):

    new_stocks = []

    missing_stock_count = int(size) - len(tickers)
    tickers = sorted(tickers)


    # If we need to select any stocks
    if missing_stock_count > 0:

        # Put newly found stocks into a list
        new_stocks = hp.add_stocks( missing_stock_count, tickers, sectors )


        # Add new stocks to our original list of stocks
        tickers.extend(new_stocks)
        tickers = sorted(tickers)



    return tickers



"""
    Using the ClearBit API and the stocks full name, retrieve the stocks
    logo + other info and return it.
"""

def find_company_info( stock_name ):

    img = ""

    # Filter out any Incs, Ltd's etc that will cause the api query to fail
    stock_name = stock_name.replace(',', '' )
    stock_name = stock_name.replace('Inc.', '')
    stock_name = stock_name.replace('Ltd', '' )
    stock_name = stock_name.replace('Corporation', '' )
    stock_name = stock_name.replace('.com', '' )
    #stock_name = stock_name.replace('Consolidated', '' )


    try:
        response = clearbit.NameToDomain.find(name=stock_name)

        domain = response['domain']
        img = response['logo']

        # Now use the domain to perform the more detailed domain request
        company = clearbit.Company.find(domain=domain,stream=True)

        metrics = company['metrics']
        foundedYear = company['foundedYear']


        marketCap = metrics['marketCap']
        employees = metrics['employees']
        annual = metrics['estimatedAnnualRevenue']

        detail_dict = { 'img': img,
                        'domain' : domain,
                        'employees' : employees,
                        'marketCap' : marketCap,
                        'foundedYear' : foundedYear,
                        'annual' : annual
                      }


    except:
        return False

    return detail_dict





def process_weights( Weights ):

    # url_for converts the array to a string, literal_eval converts it back to an array
    Weights = ast.literal_eval(Weights)
    Weights = [ weight * 100 for weight in Weights ]

    # Round weights to 2 dec places, maybe should do this in OPT code?
    Weights = [ round(weight,3) for weight in Weights ]

    return Weights



#def render_weights_table( tickers, stock_names, weights, share_count, cash, sectors ):
def render_weights_table( tickers, stock_names, weights, share_count, cash, sectors ):
    i = 0

    html = '''<table style="background-color: #eee;" id="weights_table" class=\"table table\">
            <thead><tr><th scope=\"col\">#</th>
            <th scope=\"col\">Stock</th>
            <th scope=\"col\">Sector</th>
            <th scope=\"col\">Weight (%)</th>
            <th scope=\"col\">Share Count</th>
            </tr></thead><tbody>'''.format(cash)

    for tick in tickers:

        stock_name_id = tick + "_name_id"
        sector_id = tick + "_sector_id"

        html = html + '''
                <tr id="{}">
                    <th>{}</th>
                    <td id="{}">{}</td>
                    <td id="{}">{}</td>
                    <td id=\"w1\">{}</td>
                    <td id="">{}</td>
                </tr>'''.format(
            tick, i+1, stock_name_id, stock_names[i], sector_id ,sectors[i],weights[i], share_count[i] )

        i += 1


    html = html + "</tbody></table>"

    return html




# Function to calculate how much dividends would have been earned in this portfolio

def CalculateDividends(portfolio):

    # Loop all stocks and calculate dividend values for all
    cash_investment = float(portfolio.cash)
    stock_dividend_list = []
    api_count = 0
    wait = True


    try:
        assets = portfolio.assets

        for asset in assets:
            if api_count > 4 and wait:
                wait = False
                time.sleep(60)

            url= "https://www.alphavantage.co/query?function=TIME_SERIES_MONTHLY_ADJUSTED&symbol={}&apikey={}".format( asset.ticker , api_key1 )

            r = requests.get(url=url )
            data = r.json()
            a = (data['Monthly Adjusted Time Series'])
            keys = a.keys()

            starting_close = 0

            # Find the initial closing value
            for key in keys:
                if key < start_date:
                    starting_close = a[key]['5. adjusted close']
                    break;

            if starting_close == 0:
                my_list = list( keys )
                key = list(a.keys())[-1]
                starting_close = a[key]['5. adjusted close']


            # Calculate how many shares could have been bought at this time
            stock_weight = float(asset.weight)/100
            stock_cash_investment = cash_investment*stock_weight

            api_count += 1
            number_of_shares = stock_cash_investment / float(starting_close)

            # Find total cash in dividends for this stock
            dividend_value = 0
            dividend_cash = 0

            for key in keys:

                if key > start_date and key < end_date:
                    dividend_value = float(a[key]['7. dividend amount'])
                    dividend_cash += (dividend_value * number_of_shares)


            """
                Add to a list of stock dividends (to be displayed in a summary table)
            """
            dividend_cash = round(dividend_cash,2)
            asset.dividend_earning = dividend_cash
            stock_dividend_list.append( dividend_cash )

        portfolio.total_dividend_earnings = round(sum(stock_dividend_list),2)

        return portfolio

    except:

        portfolio.dividend_fail = True
        return portfolio



def render_dividend_table( portfolio ):


    portfolio_dividends = sum(stock_dividend_list)
    portfolio_dividends = "{:,.2f}".format(portfolio_dividends)

    html = ""
    i = 0

    # Create a row for each stock in portfolio
    for tick in tickers:

        # If there is no dividends, replace dividend cash value with a message
        if stock_dividend_list[i] == 0:
            stock_dividend_list[i] = "This stock does not pay dividends."
        else:
            # Format number to have commas (E.g. 10,000)
            stock_dividend_list[i] = "{:,.2f}".format(stock_dividend_list[i])


        html +=  '''<tr>
                    <td id=\"\">{}</td>
                    <td id=\"\">{}</td>
                    </tr>'''.format( tick, stock_dividend_list[i] )
        i += 1


    # Create 1 row for the portfolio total
    html +=  '''<tr>
                    <td id=\"\">{}</td>
                    <td id=\"\">{}</td>
                    </tr>'''.format( "Portfolio Dividends", portfolio_dividends )



    return html



# Based on the int value from the dropdown, find what MAR they selected

def calculate_mar( mar_dropdown_val ):

    mar_dropdown_val = int(mar_dropdown_val )

    mar_value = 0

    if mar_dropdown_val == 1:
        # 0%
        mar_value = 0

    elif mar_dropdown_val == 2:

        #1%
        mar_value = 0.01

    elif mar_dropdown_val == 3:
        # 2%
        mar_value = 0.02
    else:
        # 5%
        mar_value = 0.05

    return mar_value

# Based on the int value from the dropdown, find what algorithm they selected
def calculate_algorithm( algorithm ):

    algorithm = int(algorithm)

    if algorithm == 1:
        return "MPT"
    elif algorithm == 2:
        return "PMPT"
    else:
        return "MPT"


def calculate_ratio( algorithm ):

    if algorithm == "MPT":
        return "Sharpe"
    else:
        return "Sortino"



# Find the stocks names from the symbols AAPL -> Apple Inc

def add_names_to_assets(assets):

    data = pd.read_csv("..\\static\\symbols\\filtered_stocks.csv")

    for a in assets:
        # Find the stocks names from the symbols AAPL -> Apple Inc
        a.stock_name = data.loc[data['Symbol'] == a.ticker, 'Name'].iloc[0]

    return assets



def future_cash_value( cash, Return ):

    # convert cash to float
    cash = float(cash)
    Return = float(Return)

    profit = cash * Return

    future_cash = profit + cash

    future_cash = "{:,.2f}".format(future_cash)
    return future_cash
