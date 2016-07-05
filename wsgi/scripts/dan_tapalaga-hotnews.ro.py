import time
import os
import feedparser
from pymongo import MongoClient
from datetime import datetime
from bs4 import BeautifulSoup

import ws_functions as ws

DB_ADDRESS = os.environ['OPENSHIFT_MONGODB_DB_URL']
DB = 'ws'

d = feedparser.parse('http://www.hotnews.ro/Dan-Tapalaga/rss')

update_returnArticlesListVersion = 0


for post in d.entries:
    if ws.article_freshness(post.published_parsed,3600) is True:
        if ws.article_exists(post.title,BeautifulSoup(post.summary).get_text(),7) == False:
            update_returnArticlesListVersion = 1


            #extract article content
            content = ws.extract_content_hotnews(post.link)

            #extract article tag

            tags = (
            (ws.find_between(BeautifulSoup(ws.query(post.link)).get_text(), "currentArticleTags = '", "';").strip()).replace(
                ',', ', ')).replace('  ', ' ').lower()

            if tags == '':
                tags=ws.extract_tags_ro(content)


            #extract artCategory
            artCategory=ws.return_artcategory_ro(tags,content)

            #add sentiment
            sentiment=ws.return_sentiment_ro(content)

            #insert article in DB
            client = MongoClient(DB_ADDRESS)
            db = client[DB]
            db['article'].insert({"date_ttl":datetime.utcnow(),"authId":int(7),"authName":"Dan Tapalaga",
                                  "artName":post.title,"url":post.link,"summary":BeautifulSoup(post.summary).get_text(),"content":content,
                                  "tags":tags,"date":int(time.time()),"artDate":datetime.utcnow().strftime("%d%b%Y"),
                                  "authImgUrl" : "https://ws-truthrevolution.rhcloud.com/images/v1/dan-tapalaga.png",
                                  "artSentiment":int(sentiment),"comments":[],"artSource":"hotnews.ro",
                                  "artCategory":artCategory})

ws.update_articlelistversion(update_returnArticlesListVersion,7)


