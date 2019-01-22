import csv
from pymongo import MongoClient
from settings import *

client = MongoClient()

db = client[MONGO_DB]
collection = db[MONGO_NEWS_SOURCE_COLLECTION]

with open('news_source.csv') as csv_file:

    csv_reader = csv.reader(csv_file)

    for row in csv_reader:
        source = {"twitter_handle": row[0], "link_pattern": row[1]}

        if collection.count(source) == 0:

            print(source)

            collection.insert_one(source)
