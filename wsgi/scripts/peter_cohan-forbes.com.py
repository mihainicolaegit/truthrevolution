import time
import os
import re

import feedparser
from pymongo import MongoClient
from datetime import datetime
from bs4 import BeautifulSoup

import ws_functions as ws


DB_ADDRESS = os.environ['OPENSHIFT_MONGODB_DB_URL']
DB = 'ws'

d = feedparser.parse('http://www.forbes.com/sites/petercohan/feed/')

update_returnArticlesListVersion = 0
for post in d.entries:
    if ws.article_freshness(post.published_parsed,3600) is True:
        if ws.article_exists(post.title,post.summary,29) == False:
            update_returnArticlesListVersion = 1

            #extract article tags

            tags=''
            for tag in BeautifulSoup(ws.query_cookie(post.link)).findAll('meta', {"property":"article:tag"}):
                tags=tag['content'].lower()+", "+tags

            #extract article content

            content_text = \
                (str(BeautifulSoup(ws.query_cookie(post.link)).findAll('div', {"class": "body_inner"})).split('[')[
                     1]).split(']')[0]

            if str(BeautifulSoup(ws.query_cookie(post.link)).find('li',{"class":"next_page"})) != '':
                content_text=content_text.split('<!-- BEGIN PAGINATION -->')[0]+(str(BeautifulSoup(ws.query_cookie(post.link+"2")).findAll('div', {"class": "body_inner"})).split('[')[1]).split(']')[0].split('<!-- BEGIN PAGINATION -->')[0]

            pat1=re.compile(r'<figure class.*figure>',re.DOTALL)
            content_text=pat1.sub(r'',content_text)

            #extract artCategory

            artCategory = ws.return_artcategory_ro(tags,content_text)
            if  artCategory == '':
                artCategory=[{"content":"Diverse","score":"1"}]

            if tags == '':
                tags=ws.extract_tags_en(content_text)

            #add sentiment
            sentiment=ws.return_sentiment_en(content_text)


            #continue content manipulation

            content = "<div align=\"justify\">"+content_text+"</div>"
            content = ws.remove_br(content)

            client = MongoClient(DB_ADDRESS)
            db = client[DB]
            db['article'].insert({"date_ttl":datetime.utcnow(),"authId":int(29),"authName":"Peter Cohan",
                                  "artName":post.title,"url":post.link,"summary":BeautifulSoup(post.summary).get_text(),
                                  "content":content,"tags":tags[:-2],"date":int(time.time()),
                                  "artDate":datetime.utcnow().strftime("%d%b%Y"),
                                  "authImgUrl" : "https://ws-truthrevolution.rhcloud.com/images/v1/peter-cohan.png",
                                  "artSentiment":int(sentiment),"comments":[],"artSource":"forbes.com",
                                  "artCategory":artCategory})

ws.update_articlelistversion(update_returnArticlesListVersion,29)
