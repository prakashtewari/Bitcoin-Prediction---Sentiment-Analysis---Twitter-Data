#Parameters for getting the Bitcoin history
from_symbol = 'BTC'
to_symbol = 'USD'
exchange = 'Bitstamp'


datetime_interval = 'minute'


import requests
from datetime import datetime 
from datetime import timedelta
import pandas as pd

#Function to download Bitcoin data
def download_data(from_symbol, to_symbol, exchange, datetime_interval):
    supported_intervals = {'minute', 'hour', 'day'}
    assert datetime_interval in supported_intervals,\
        'datetime_interval should be one of %s' % supported_intervals

    print('Downloading %s trading data for %s %s from %s' %
          (datetime_interval, from_symbol, to_symbol, exchange))
    base_url = 'https://min-api.cryptocompare.com/data/histo'
    url = '%s%s' % (base_url, datetime_interval)

    params = {'fsym': from_symbol, 'tsym': to_symbol,
              'limit': 10000, 'aggregate': 1,
              'e': exchange}
    request = requests.get(url, params=params)
    data = request.json()

    return data

#Function to convert the data to a python dataframe
def convert_to_dataframe(data):
    df = pd.io.json.json_normalize(data, ['Data'])
    df['datetime'] = pd.to_datetime(df.time, unit='s')
    df = df[['datetime',  'open', 'close', ]]
    
    print('Bitcoin data is extracted from ', min(df.datetime), 'till', max(df.datetime))
    print('Please make sure that tweet sentiments are available within this time range')
    
    return df

#Filter for any missing datapoints
def filter_empty_datapoints(df):
    indices = df[df.sum(axis=1) == 0].index
    print('Filtering %d empty datapoints' % indices.shape[0])
    df = df.drop(indices)
    return df

def BTC_Price(Start_date, Till_date, from_symbol = 'BTC', to_symbol = 'USD', exchange = 'Bitstamp', datetime_interval = 'minute'):
    #Download Price data for bitcoin
    data = download_data(from_symbol, to_symbol, exchange, datetime_interval)
    df = convert_to_dataframe(data)
    df = filter_empty_datapoints(df)
    
    #Add Percentage change
    df['pch']=(df.close-df.open)/df.open
    
    #The date time from the tweet trigger
    Till_date= Till_date.replace(second = 0)
    #Start_date= Trigger_date.replace(microsecond=0,second=0,minute=0)
    Start_date= Start_date.replace(second = 0)
    
    #Find the index corresponsing to the trigger time in the dataframe
    Start_point = (df.index[df['datetime'] == Start_date])
    End_point = (df.index[df['datetime'] == Till_date])
    
    df_1 = df[Start_point[0]:End_point[0]]
    #df_1['pch'][557]   
    alist = ['rel','lvl']
    BTC_Price = {k: [] for k in alist}
    """For Time snapping"""
    total_time = ((Till_date - Start_date).days)*24 + ((Till_date - Start_date).seconds)/60
    
    
    for time in range(int(total_time)):
        #print(type(time))
        BTC_Price['rel'].append(df_1['pch'][Start_point[0]+time])
        BTC_Price['lvl'].append(df_1['close'][Start_point[0]+time])
    
    
    return BTC_Price

#Start_date = btc_tweet_sentiment['min_date']
#Till_date = btc_tweet_sentiment['max_date']
#temp = BTC_Price(Start_date , Till_date ) 
#Start_date = datetime(2018,3,7, 23, 22)
#Till_date = datetime(2018,3,7, 23, 59)
#BTC_Price(Start_date , Till_date ) 
