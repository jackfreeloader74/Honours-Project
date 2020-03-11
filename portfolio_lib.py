from dateutil.relativedelta import relativedelta
from datetime import timedelta
import datetime as dt
import requests
api_key = "2M6F7YVUOQBLY4WF"

#import opt_algorithms as hp

#start_date = hp.global_start_date
#end_date = hp.global_end_date

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



# Function to calculate how much dividends would have been earned in this portfolio

def CalculateDividends(tickers, weights, cash_investment):

    # Loop all stocks and calculate dividend values for all
    cash_investment = float(cash_investment)
    print("This may have worked ", start_date, end_date )
    
    portfolio_dividends = 0

    i = 0

    for stock in tickers:

        url= "https://www.alphavantage.co/query?function=TIME_SERIES_MONTHLY_ADJUSTED&symbol={}&apikey={}".format( stock ,api_key )
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
        stock_weight = float(weights[i])
        stock_cash_investment = cash_investment*stock_weight
        i += 1

        number_of_shares = stock_cash_investment / float(starting_close)


        
        # Find total cash in dividends for this stock
        dividend_value = 0
        dividend_cash = 0
        
        for key in keys:
    
            if key > start_date and key < end_date:
                dividend_value = float(a[key]['7. dividend amount'])
                dividend_cash += (dividend_value *number_of_shares)


        # Add this stocks dividend value to the portfolio's
        print( "Stock ", stock, " Dividends ", dividend_cash )
        portfolio_dividends += dividend_cash

    return portfolio_dividends


        
