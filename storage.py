from pymongo import MongoClient
import requests
from readability.readability import Document
from bs4 import BeautifulSoup
import ssl
from settings import *

def download_via_url(url):
    response = requests.get(url)
    doc = Document(response.text)
    title = doc.title()
    summary = doc.summary()
    soup = BeautifulSoup(summary, "html.parser")

    return title, soup.text

def download_content(tweet):

    url = tweet["url"]
    title, content = download_via_url(url)

    return title, content

if __name__ == '__main__':

    client = MongoClient()

    db = client[MONGO_DB]

    article_collection = db[MONGO_COLLECTION]

    query = {"title": {"$exists":False}}

    for article in article_collection.find(query):
        article_id = article["_id"]

        print(article["url"])

        title, content = download_content(article)
        if not title or not content:
            article_collection.delete_one({"_id": article_id})
            continue

        article_collection.update_one({"_id": article_id}, {"$set": {"title": title, "content":content}})
