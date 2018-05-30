# -*- coding: utf-8 -*-
"""
Created on Thu Mar  8 11:39:34 2018

@author: Prakash.Tiwari
"""
import os 

os.chdir('C:\Work\Daily Tasks\Machine Learning Udemy\Bitcoin')

import time 
import json
import tweepy
import datetime 
import pdb
from datetime import datetime, timedelta
from textblob import TextBlob
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import requests
import json
from sklearn.ensemble import RandomForestRegressor
from sklearn.cross_validation import train_test_split
from sklearn.metrics import mean_squared_error
from sklearn.metrics import r2_score
from math import sqrt
from pylab import figure, text, scatter, show
#Call original bitcoin prices
from Bitcoin_data import BTC_Price
from Twitter_0307 import get_sentiments 

'''Main'''

#def main():
    
'''SEARCH QUERY'''
searchquery = "bitcoin since:2018-04-02 until:2018-05-11 -filter:retweets"
#searchquery = "bitcoin since:2018-03-06 until:2018-03-15 -filter:retweets"
    
'''GET TWEETS WITH SENTIMENTS'''
btc_tweet_sentiment = get_sentiments(query = searchquery)

'''USE TWEETS TO FILL X VARIABLE'''
P_postweets1 = pd.DataFrame(btc_tweet_sentiment['positive']).transpose()
P_negtweets1 = pd.DataFrame(btc_tweet_sentiment['negative']).transpose()

X = pd.concat((P_postweets1, P_negtweets1), axis = 1).values

'''BITCOIN PRICE'''
Prices = BTC_Price(Start_date = btc_tweet_sentiment['min_date'], Till_date = btc_tweet_sentiment['max_date']) 

'''USE TWEETS TO FILL Y VARIABLE'''   
y = Prices['rel']
y_lvl = Prices['lvl']

"""VALIDATION"""
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.3, random_state = 0)
X_train, X_test, y_lvl_train, y_lvl_test = train_test_split(X, y_lvl, test_size = 0.3, random_state = 0)

assert (len(y_train) == len(X_train)),"X and Y variables are not of the same length"

'''PERFORM MODELING'''
regressor = RandomForestRegressor(n_estimators = 10, random_state = 0)
regressor.fit(X_train, y_train)
#X_new = np.array([[0.5 , 0.1]])
y_insample = regressor.predict(X_train)
y_pred = regressor.predict(X_test)

'''STATISTICS'''
r_square = r2_score(y_train, y_insample)*100
print('R square for this model: %.2f' %(r2_score(y_train, y_insample)*100))    
   
'''Convert to the level values'''
y_lvl_pred = []
for i in range(len(y_test)):
    if i == 0:
        y_lvl_pred.append((y_pred[i] +1)*(y_lvl_train[len(y_train) - 1]))
    else:
        y_lvl_pred.append((y_pred[i] +1)*(y_lvl_pred[i-1]))
 
'''Visualisation '''
plt.figure()
plt.suptitle('Actual vs Predicted Bitcoin Prices- Validation')
plt.title('Model trained on data pulled in the last hour')
plt.ylabel('BTC Prices in USD')
plt.xlabel('time (mins)')
plt.plot(y_lvl_test, ls = 'solid', label = 'Actual')
plt.plot(y_lvl_pred, ls = 'dashed', label = 'Predicted')
plt.legend(['Actual Bitcoin Prices', 'Predicted Bitcoin Prices'])
plt.text(len(y_lvl_test) , max(y_lvl_test), 'R_square %.0f'%r_square, withdash = True)
plt.show()


#    regressor.predict([[0.8, 0.1]])
    
#    return Bitcoin_Price

#Final_Price = main()

    

###Ignore 
"""
x_temp = pd.DataFrame(X)
x_temp.to_csv('sentimentData.csv')

y_temp =pd.DataFrame(y)
y_temp.to_csv('BitcoinData.csv')


"""