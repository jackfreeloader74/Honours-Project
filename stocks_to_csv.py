
import pandas as pd
import numpy as np
import pandas_datareader.data as web
import datetime as dt
import matplotlib.pyplot as plt
from dateutil.relativedelta import relativedelta
from datetime import timedelta

symbols = ['AAPL', 'AMZN', 'GOOG', 'IBM', 'MSFT', 'SBUX','TSLA', 'XOM' ]



#for i in symbols:


web.DataReader(symbols,'yahoo','01/01/2011','01/01/2020')['Adj Close'].to_csv('stocks.csv')



data = pd.read_csv( 'stocks.csv')


print(data.columns[1])


data2 = web.DataReader( symbols, data_source="yahoo", start='01/01/2011', end='01/01/2020')['Adj Close']
data2.sort_index(inplace=True)


print(data2.columns[0])
