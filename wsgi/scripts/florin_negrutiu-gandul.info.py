import time
import re
import os

import feedparser
from pymongo import MongoClient
from datetime import datetime
from bs4 import BeautifulSoup

import ws_functions as ws

DB_ADDRESS = os.environ['OPENSHIFT_MONGODB_DB_URL']
DB = 'ws'

d = feedparser.parse('http://www.gandul.info/rss/autor/florin-negrutiu')

update_returnArticlesListVersion = 0

for post in d.entries:
    if ws.article_freshness(post.published_parsed,3600) is True:

        #extract article summary
        summary = ws.extract_summary_gandul(post.link)

        #check article existance
        if ws.article_exists(post.title,summary,4) == False:
            update_returnArticlesListVersion = 1

            #extract article tags
            tags = ws.extract_tags_gandul(post.link)

            #extract article content
            content=ws.extract_content_gandul(post.link)

            #add tags if are not found in article link
            if tags == '':
                tags=ws.extract_tags_ro(content)

            #extract artCategory
            artCategory=ws.return_artcategory_ro(tags,content)
            if artCategory == '':
                artCategory=[{"content":"Diverse","score":"1"}]

            #add sentiment
            sentiment=ws.return_sentiment_ro(content)

            #insert in db
            client = MongoClient(DB_ADDRESS)
            db = client[DB]
            db['article'].insert({"authId":int(4),"authName":"Florin Negru\xc5\xa3iu","artName":post.title,
                                  "url":post.link,"summary":summary,"content":content,"tags":tags,"date":int(time.time()),
                                  "artDate":datetime.utcnow().strftime("%d%b%Y"),
                                  "authImgUrl" : "https://ws-truthrevolution.rhcloud.com/images/v1/florin-negrutiu.png",
                                  "artSentiment":int(sentiment),"comments":[],"artSource":"gandul.info",
                                  "artCategory":artCategory})

ws.update_articlelistversion(update_returnArticlesListVersion,4)
