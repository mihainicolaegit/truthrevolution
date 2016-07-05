import time
import os

import feedparser
from pymongo import MongoClient
from datetime import datetime
from bs4 import BeautifulSoup

import ws_functions as ws

DB_ADDRESS = os.environ['OPENSHIFT_MONGODB_DB_URL']
DB = 'ws'

d = feedparser.parse('http://www.tolo.ro/feed/')

update_returnArticlesListVersion = 0

for post in d.entries:
    if ws.article_freshness(post.published_parsed,3600) is True:


        #check article existance
        if ws.article_exists(post.title,post.summary,39) == False:
            update_returnArticlesListVersion = 1

            #extract article content
            text_dirty=BeautifulSoup(ws.query(post.link)).find('div',{"id":"contentmiddle"}).findAll('p')[1:]
            text_dirty=str(text_dirty)
            text_dirty=text_dirty[1:len(str(text_dirty))-1].replace('</p>, <p','</p><p')
            content="<div align=\"justify\">"+ws.remove_br(text_dirty)+"</div>"
            if 'REAC\xc8\x9aIE' in text_dirty:
                text_dirty2=BeautifulSoup(ws.query(post.link)).findAll('div',{"dir":"ltr"})
                text_dirty2=str(text_dirty2)
                text_dirty2=text_dirty2[1:len(str(text_dirty2))-1].replace('</div>, <div','</div><div')
                content="<div align=\"justify\">"+ws.remove_br(text_dirty+text_dirty2)+"</div>"




            #extract article tags
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
            db['article'].insert({"date_ttl":datetime.utcnow(),"authId":int(39),
                                  "authName":"C\xc4\x83t\xc4\x83lin Tolontan","artName":post.title,
                                  "url":post.link,"summary":post.summary,"content":content,"tags":tags,"date":int(time.time()),
                                  "artDate":datetime.utcnow().strftime("%d%b%Y"),
                                  "authImgUrl" : "https://ws-truthrevolution.rhcloud.com/images/v1/catalin-tolontan.png",
                                  "artSentiment":int(sentiment),"comments":[],"artSource":"tolo.ro",
                                  "artCategory":artCategory})

ws.update_articlelistversion(update_returnArticlesListVersion,39)
