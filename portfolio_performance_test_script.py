import pandas as pd
import numpy as np
import pandas_datareader.data as web
import datetime as dt
import matplotlib.pyplot as plt
from dateutil.relativedelta import relativedelta
from datetime import timedelta







"""
TEST1 3 Years    2012-2015    2015-2016

6 monthes Jan - June

"""
stocks = [ 'AAPL', 'AMZN','ATLO','BUD','GBT','TSLA','XOM','XTLB' ]

stocks = [ 'AAPL', 'AMZN', 'TSLA','XOM' ]

mpt_weights = [ 0.512, 0.018, 0.239, 0.012, 0.018, 0.144, 0.032, 0.025 ]
pmpt_weights = [ 0.612, 0.018, 0.139, 0.012, 0.018, 0.144, 0.032, 0.025 ]
#weights = [ 0.2, 0.2, 0.4 , 0.2]

print( sum(pmpt_weights))
cash = 10000


time_frame = [ 1, 2, 3, 4, 5, 6 ]
exp_return = 0.34




algorithm_weights = [mpt_weights, pmpt_weights ]


for w in algorithm_weights:

    avg_first = 0
    avg_end_val = 0
    avg_realised_return = 0
    avg_discrep_perc = 0
    avg_expected_value = 0       


    for year in time_frame:

        start_date = "{}/01/2015".format( year )
        end_date = "{}/01/2019".format( year )

        try:
            data = web.DataReader( stocks, data_source="yahoo", start=start_date, end=end_date)['Adj Close']
            data = data.dropna()
            data.reset_index(inplace=True,drop=False)
        except:
            print("Testing")


        data['Total'] = 0
        i = 0

        for tick in stocks:
            data['Total'] = data['Total'] + data[tick] * w[i]
            i += 1

        data['pct_change'] = data['Total'].pct_change()
        data['Portfolio_Total'] = 0
        data.loc[0,'Portfolio_Total'] = cash

        for i in range(1, len(data) ):
             data.loc[i, 'Portfolio_Total'] = data.loc[i-1, 'Portfolio_Total'] + data.loc[i, 'pct_change']*cash
        

        # Calculate table values
        first = data['Portfolio_Total'].iloc[0]
        avg_first += data['Portfolio_Total'].iloc[0]

        avg_expected_value += first + first*exp_return
        expected_value = first + first*exp_return

        end_val = data['Portfolio_Total'].iloc[-1]
        avg_end_val += data['Portfolio_Total'].iloc[-1]

        realised_return = ((end_val - first)/ first)*100
        avg_realised_return += ((end_val - first)/ first)*100

        discrep_perc = (exp_return*100 - realised_return) 
        avg_discrep_perc += (exp_return*100 - realised_return) 


    print("Average Initial Value ", avg_first/6 )
    print("Average End Value ", avg_end_val/6 )
    print("Average Expected Return ", (exp_return)*100 )
    print("Average Realised Return %", avg_realised_return/6 )
    print("Average Expected Future Value ", avg_expected_value/6 )
    print("Average Realised Value ", avg_end_val/6 )
    print("Average Discrepancy % ", avg_discrep_perc/6 )
    print("Average Discrepancy ",  (avg_expected_value - avg_end_val)/6 )


# Only record every 50 rows for graph



