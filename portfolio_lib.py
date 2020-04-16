from dateutil.relativedelta import relativedelta
from datetime import timedelta
import datetime as dt
import requests
import time
import ast
import clearbit
import opt_algorithms as hp

api_key1 = "2M6F7YVUOQBLY4WF"
api_key2 = 'NEMPJL3V114R3DW8'


clearbit.key = "sk_34b33f60cc6cb5f54ee9033cfe4bf757"

#import opt_algorithms as hp



start_date = "2010-01-01"
end_date = "2020-01-01"

def isHoliday( one ):

    presidents = dt.date(2020, 2, 17)

    memorial = dt.date( 2020, 4, 10 )

    independance = dt.date( 2020, 7, 4 )
    
    labor = dt.date( 2020, 10, 7 )

    thanksgiving = dt.date( 2020, 11, 26 )

    christmas = dt.date(2020, 12, 25 )

    holiday_list = [ presidents, memorial, independance, labor, thanksgiving, christmas ]

    for holiday in holiday_list:

       
        
        if one.day == holiday.day and one.month == holiday.month:
            return True

        if one.day == holiday.day + 1 and one.month == holiday.month:
               
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
    logo and return it. 
"""

def find_stock_logo( stock_name ):

    img = ""

    # Filter out any Incs, Ltd's etc that will cause the api query to fail
    stock_name = stock_name.replace(',', '' )
    stock_name = stock_name.replace('Inc.', '')
    stock_name = stock_name.replace('Ltd', '' )
    stock_name = stock_name.replace('Corporation', '' )
    stock_name = stock_name.replace('.com', '' )

   
    try:
        response = clearbit.NameToDomain.find(name=stock_name)

        img = response['logo']

    except:
        return False

    return img
    




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

def CalculateDividends(tickers, weights, cash_investment):

    # Loop all stocks and calculate dividend values for all
    cash_investment = float(cash_investment)
   
    stock_dividend_list = []

    i = 0
    api_count = 0
    wait = True

    try:

        for stock in tickers:

            if api_count > 4 and wait:
                wait = False
                time.sleep(60)

            url= "https://www.alphavantage.co/query?function=TIME_SERIES_MONTHLY_ADJUSTED&symbol={}&apikey={}".format( stock ,api_key1 )
    

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
            stock_weight = float(weights[i])/100
            stock_cash_investment = cash_investment*stock_weight

            i += 1
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
 
            stock_dividend_list.append( round(dividend_cash,2) )

        return stock_dividend_list
    except:
        return ""



def render_dividend_table( stock_dividend_list, tickers ):


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


        
