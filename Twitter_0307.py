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

#Call original bitcoin prices
from Bitcoin_data import BTC_Price

#Variables that contains the user credentials to access Twitter API 
consumer_key = 'xxx'
consumer_secret = 'xxx'
access_token = 'xxx'
access_token_secret = 'xxx'
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

api = tweepy.API(auth)
#api.rate_limit_status()

'''Tweets Extraction'''
def get_tweets(query): 
        #Put your search term
    users =tweepy.Cursor(api.search,q= query, lang = 'en', result_type='recent', exclude_replies = True).items(10000)
    count = 0
    errorCount=0 
    user = next(users)
    
    tweets_data = {'id':[], 'time':[], 'text':[], 'lang':[]} 
    while len(user._json) > 0:
        try:
            user = next(users)
            count += 1
            #use count-break during dev to avoid twitter restrictions
            #if (count>10):
            #    break
        except tweepy.TweepError:
            #catches TweepError when rate limiting occurs, sleeps, then restarts.
            #nominally 15 minnutes, make a bit longer to avoid attention.
            print("sleeping....")
            time.sleep(2)
            break
            #user = next(users)
        except StopIteration:
            break
        finally:
            print("Writing to tweets_data tweet number:"+str(count))
            #print(user.text)
            tweets_data['id'].append(count)
            tweets_data['time'].append(user.created_at)
            tweets_data['text'].append(user.text)
            tweets_data['lang'].append(user.lang)
                
    print("completed, errorCount ="+str(errorCount)+" total tweets="+str(count))
    
    length = len(tweets_data['id'])
    min_date = min(tweets_data['time']).replace(microsecond=0,second=0)
    max_date = max(tweets_data['time']).replace(microsecond=0,second=0)
    #tweets_data = {'tweets': tweets_data, '#tweets': length, 'min_date': min_date,'max_date' : max_date}

    return {'tweets': tweets_data, '#tweets': length, 'min_date': min_date,'max_date' : max_date}

'''
Get Sentiments for these tweets
'''
def get_tweet_sentiment(tweet):
    '''
    Utility function to classify sentiment of passed tweet
    using textblob's sentiment method
    '''
    # create TextBlob object of passed tweet text
    analysis = TextBlob(tweet)
    # set sentiment
    if analysis.sentiment.polarity > 0:
        return 'positive'
    elif analysis.sentiment.polarity == 0:
        return 'neutral'
    else:
        return 'negative'


def get_sentiments(query):
    
    tweets_data = get_tweets(query)
    
    arranged_tweets = []
    
    for i in range(tweets_data['#tweets']): 
        #print(((tweets_data['time'][0]) - min_date).seconds)
        parsed_tweet = {}
        #if (tweets_data['tweets']['time'][i] - tweets_data['min_date']).seconds > 0:
        diff = tweets_data['tweets']['time'][i] - tweets_data['min_date'] 
        days = diff.days
        mins = round(diff.seconds/60,0)
        total_mins = days*24*60 + mins
        parsed_tweet['snap'] = (total_mins) 
        parsed_tweet['id'] = tweets_data['tweets']['id'][i]
        parsed_tweet['text'] = tweets_data['tweets']['text'][i]
        parsed_tweet['sentiment'] = get_tweet_sentiment(tweets_data['tweets']['text'][i])
            
        arranged_tweets.append(parsed_tweet)
    print("%d Tweets are assigned sentiments " %(tweets_data['#tweets']))
                                                             
    #pdb.set_trace()
    
    """For Time snapping"""
    total_time = ((tweets_data['max_date']  - tweets_data['min_date'] ).days)*24 + ((tweets_data['max_date']  - tweets_data['min_date']).seconds)/60
    #temp1 = {'tweets': arranged_tweets, 'time': total_time} 
    #temp1['time']  

    """Put minute wise tweet sentiments""" 

    postweets =[]
    negtweets =[]
    neutweets = [] 
    tottweets = []
    P_postweets = []
    P_negtweets = []
    P_neutweets = []
            
    for time in range(int(total_time)):
        #print type(time)
        postweets.append(len([tweet for tweet in arranged_tweets if tweet['sentiment'] == 'positive' and tweet['snap'] == time]))
        negtweets.append(len([tweet for tweet in arranged_tweets if tweet['sentiment'] == 'negative' and tweet['snap'] == time]))
        neutweets.append(len([tweet for tweet in arranged_tweets if tweet['sentiment'] == 'neutral' and tweet['snap'] == time]))
        tottweets.append(len([tweet for tweet in arranged_tweets if tweet['snap'] ==time]))
        P_postweets.append(postweets[time]/tottweets[time] if tottweets[time] != 0 else 0)
        P_negtweets.append(negtweets[time]/tottweets[time] if tottweets[time] != 0 else 0)
        P_neutweets.append(neutweets[time]/tottweets[time] if tottweets[time] != 0 else 0)
    
    Sentiments = {'positive': [P_postweets], 'negative': [P_negtweets], 'min_date':tweets_data['min_date'],'max_date':tweets_data['max_date']}
    print('Sentiment assigned for each minute going from '+ str(tweets_data['min_date'])+' till' + str(tweets_data['max_date']))
    
    return Sentiments

    
def plot_func(actual, predicted):
    
    plt.figure()
    plt.ylabel('BTC Prices in USD')
    plt.plot(actual, ls = 'solid', label = 'Actual')
    plt.plot(predicted, ls = 'dashed', label = 'Predicted')
    plt.legend(['Actual Bitcoin Prices', 'Predicted Bitcoin Prices'])
    return plt.show()

    




