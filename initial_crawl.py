from datetime import datetime
import json
from pprint import pprint
import pytz
import time
from pymongo import MongoClient
import tweepy
from subscriber import limit_handled, tweet_generator, get_most_recent_tweet_id
from settings import *

twitter_authentication = json.load(open("twitter-auth.json"))

consumer_key = twitter_authentication["consumer_key"]
consumer_secret = twitter_authentication["consumer_secret"]
access_token = twitter_authentication["access_token"]
access_token_secret = twitter_authentication["access_token_secret"]

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

api = tweepy.API(auth)


client = MongoClient()
db = client[MONGO_DB]

news_source_collection = db[MONGO_NEWS_SOURCE_COLLECTION]
article_collection = db[MONGO_COLLECTION]

for news_source in news_source_collection.find():

    twitter_handle = news_source["twitter_handle"]
    link_pattern = news_source["link_pattern"]

    print(twitter_handle)

    for tweet in tweet_generator(api, twitter_handle, link_pattern, items=5):


        if article_collection.count({"url": tweet["url"]}) == 0:

            article_collection.insert_one(tweet)
            pprint(tweet)
