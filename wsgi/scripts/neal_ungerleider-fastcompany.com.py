import time
import os

import feedparser
from pymongo import MongoClient
from datetime import datetime
from bs4 import BeautifulSoup

import ws_functions as ws


DB_ADDRESS = os.environ['OPENSHIFT_MONGODB_DB_URL']
DB = 'ws'

d = feedparser.parse('http://www.fastcompany.com/user/neal-ungerleider.rss')

update_returnArticlesListVersion = 0


for post in d.entries:
    if ws.article_freshness(post.published_parsed,3600) is True:
        if ws.article_exists(post.title,BeautifulSoup(post.summary).get_text(),30) == False:
            update_returnArticlesListVersion = 1

            #extract article tags

            tags = BeautifulSoup(ws.query_cookie(post.link)).get_text().split('keywords\":{\"tags\":')[1].split(',\"socialtags\"')[
                0].replace('[', '').replace(']', '').replace('"', '').replace(',', ', ').lower()

            #extract article content

            if "fastcompany.com" in post.link:
                content_text = \
                    (str((BeautifulSoup(ws.query_cookie(post.link)).find('div', {"itemprop": "body"})).findAll('p'))).split('[')[1].split(
                        ']')[0].replace('</p>, <p>', '</p> <p>')
            if "fastcolabs.com" in post.link:
                content_text = \
                    (str((BeautifulSoup(ws.query_cookie(post.link)).find('div', {"itemprop": "body articleBody"})).findAll('p'))).split(
                        '[')[1].split(']')[0].replace('</p>, <p>', '</p> <p>')

            if tags == '':
                tags=ws.extract_tags_en(content_text)

            #extract artCategory

            artCategory = ws.return_artcategory_ro(tags,content_text)
            if  artCategory == '':
                artCategory=[{"content":"Diverse","score":"1"}]


            #add sentiment
            sentiment=ws.return_sentiment_en(content_text)


            #continue content manipulation

            content = "<div align=\"justify\">"+content_text+"</div>"
            content = ws.remove_br(content)

            client = MongoClient('mongodb://admin:mmURZYYxluXV@5346701b5004463769000154-mihainicolae.rhcloud.com:49331')
            db = client['ws']
            db['article'].insert({"date_ttl":datetime.utcnow(),"authId":int(30),"authName":"Neal Ungerleider",
                                  "artName":post.title,"url":post.link,"summary":BeautifulSoup(post.summary).get_text(),
                                  "content":content,"tags":tags,"date":int(time.time()),
                                  "artDate":datetime.utcnow().strftime("%d%b%Y"),
                                  "authImgUrl" : "https://ws-truthrevolution.rhcloud.com/images/v1/neal-ungerleider.png",
                                  "artSentiment":int(sentiment),"comments":[],"artSource":"fastcompany.com",
                                  "artCategory":artCategory})

ws.update_articlelistversion(update_returnArticlesListVersion,30)
