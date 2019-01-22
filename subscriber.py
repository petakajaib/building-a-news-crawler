import tweepy
import json
from pprint import pprint
from datetime import datetime
import pytz
from pymongo import MongoClient
from settings import *
import time

def limit_handled(cursor):
    while True:
        try:
            yield cursor.next()
        except tweepy.RateLimitError as err:
            print(err)
            print("sleep")
            time.sleep(15 * 60)
        except tweepy.error.TweepError as err:
            print(err)
            print("sleep")
            time.sleep(15 * 60)

def tweet_generator(api, newsource_twitter_handle, newsource_link_pattern, most_recent_tweet_id=None, items=200):

    if most_recent_tweet_id:

        kwargs = {
            "id": newsource_twitter_handle,
            "since_id": most_recent_tweet_id
        }
    else:
        kwargs = {
            "id": newsource_twitter_handle,
        }

    for status in limit_handled(tweepy.Cursor(api.user_timeline, **kwargs).items(items)):

        tweet = status._json
        # pprint(tweet)
        text = tweet["text"]
        tweet_id = tweet["id"]
        created_at = tweet["created_at"]
        urls = tweet["entities"]["urls"]
        datetime_obj = datetime.strptime(created_at, '%a %b %d %H:%M:%S +0000 %Y')

        if urls:
            for url in urls:

                expanded_url = url["expanded_url"]

                if newsource_link_pattern in expanded_url:

                    d = {

                        "twitter_handle": newsource_twitter_handle,
                        "tweet_text": text,
                        "tweet_id": tweet_id,
                        "url": expanded_url,
                        "created_at": created_at,
                        "month": datetime_obj.month,
                        "year": datetime_obj.year,
                        "day": datetime_obj.day,
                        "hour": datetime_obj.hour,
                        "minute": datetime_obj.minute,
                        "tweet": tweet
                    }

                    yield d


def get_most_recent_tweet_id(article_collection, twitter_handle):

    sorted_articles = article_collection.find({"twitter_handle": twitter_handle}).sort([("tweed_id", -1)])[:1]

    most_recent_article = sorted_articles[0]

    return most_recent_article["tweet_id"]


if __name__ == '__main__':


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

        most_recent_tweet_id = get_most_recent_tweet_id(article_collection, twitter_handle)

        for tweet in tweet_generator(api, twitter_handle, link_pattern, most_recent_tweet_id=most_recent_tweet_id):

            if article_collection.count({"url": tweet["url"]}) == 0:

                article_collection.insert_one(tweet)
                pprint(tweet)
