import time
import os

import feedparser
from pymongo import MongoClient
from datetime import datetime
from bs4 import BeautifulSoup

import ws_functions as ws

DB_ADDRESS = os.environ['OPENSHIFT_MONGODB_DB_URL']
DB = 'ws'

d = [feedparser.parse('http://www.romanialibera.ro/rss/opinii-168.xml'),
     feedparser.parse('http://www.romanialibera.ro/rss/special-1007.xml')]

update_returnArticlesListVersion = 0

feeds=0
while feeds<2 :
    for post in d[feeds].entries:
        if post.author == "Sabina Fati (redactia@romanialibera.ro)":
            if ws.article_freshness(post.published_parsed,3600) is True:
                if ws.article_exists(post.title,post.summary,9) == False:
                    update_returnArticlesListVersion = 1

                    #extract article content
                    content=ws.extract_content_romanialibera(post.link)


                    #extract article tags
                    tags = ''
                    for tag in BeautifulSoup(ws.query(post.link)).find_all('a',{"class":"tag"}):
                        tags=tags+tag.get_text().strip()+', '
                    if tags == '':
                        tags=ws.extract_tags_ro(content)+', '

                    #extract artCategory
                    artCategory=ws.return_artcategory_ro(tags,content)

                    #add sentiment
                    sentiment=ws.return_sentiment_ro(content)

                    #insert article in DB
                    client = MongoClient(DB_ADDRESS)
                    db = client[DB]
                    db['article'].insert({"date_ttl":datetime.utcnow(),"authId":int(9),"authName":"Sabina Fati",
                                          "artName":post.title,"url":post.link,"summary":post.summary,"content":content,
                                          "tags":tags[:-2],"date":int(time.time()),
                                          "artDate":datetime.utcnow().strftime("%d%b%Y"),
                                          "authImgUrl" : "https://ws-truthrevolution.rhcloud.com/images/v1/sabina-fati.png",
                                          "artSentiment":int(sentiment),"comments":[],"artSource":"romanialibera.ro",
                                          "artCategory":artCategory})
    feeds=feeds+1

ws.update_articlelistversion(update_returnArticlesListVersion,9)
