from dateutil.relativedelta import relativedelta
from datetime import timedelta
import datetime as dt


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

    return False



def find_suitable_date(date):

    date = date - timedelta(days = 1)

    if date.weekday() == 6 :  

        date = date - timedelta(days = 2)

    elif date.weekday() == 5:
        date = date - timedelta(days = 1)


    return date
