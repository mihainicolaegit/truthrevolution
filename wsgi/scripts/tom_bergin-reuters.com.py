import time
import json
import os

import feedparser
from pymongo import MongoClient
from datetime import datetime
from bs4 import BeautifulSoup

import ws_functions as ws

DB_ADDRESS = os.environ['OPENSHIFT_MONGODB_DB_URL']
DB = 'ws'
d = feedparser.parse('http://blogs.reuters.com/tom-bergin/feed/')


update_returnArticlesListVersion = 0


for post in d.entries:
    if ws.article_freshness(post.published_parsed,3600) is True:
        if ws.article_exists(post.title,str(post.summary).split('(Reuters) &#8211; ')[1],31) is False:
            update_returnArticlesListVersion = 1

            #extract article tags

            tags=str(json.loads(BeautifulSoup(ws.query_cookie(post.link)).find('meta',{"name":"parsely-page"})['content'])['tags']) \
                .replace('[','').replace(']','').lower()

            #extract article content

            content_text = str(post.content[0].value).split('(Reuters) &#8211; ')[1]

            if tags == '':
                tags=ws.extract_tags_en(content_text)


            #extract artCategory

            artCategory = ws.return_artcategory_ro(tags,content_text)
            if  artCategory == '':
                artCategory=[{"content":"Diverse","score":"1"}]


            #add sentiment
            sentiment=ws.return_sentiment_en(content_text)

            #continue content manipulation

            content = "<div align=\"justify\">"+content_text.replace('<br />',' ')+"</div>"
            content = ws.remove_br(content)

            client = MongoClient(DB_ADDRESS)
            db = client[DB]
            db['article'].insert({"date_ttl":datetime.utcnow(),"authId":int(31),"authName":"Tom Bergin",
                                  "artName":post.title,"url":post.link,"summary":str(post.summary).split('(Reuters) &#8211; ')[1],
                                  "content":content,"tags":tags,"date":int(time.time()),
                                  "artDate":datetime.utcnow().strftime("%d%b%Y"),
                                  "authImgUrl" : "https://ws-truthrevolution.rhcloud.com/images/v1/tom-bergin.png",
                                  "artSentiment":int(sentiment),"comments":[],"artSource":"reuters.com",
                                  "artCategory":artCategory})

ws.update_articlelistversion(update_returnArticlesListVersion,31)

