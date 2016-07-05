import time
import os

import feedparser
from pymongo import MongoClient
from datetime import datetime
from bs4 import BeautifulSoup

import ws_functions as ws


DB_ADDRESS = os.environ['OPENSHIFT_MONGODB_DB_URL']
DB = 'ws'


d = feedparser.parse('http://feeds.bbci.co.uk/news/correspondents/gavinhewitt/rss.sxml')

update_returnArticlesListVersion = 0


for post in d.entries:
    if ws.article_freshness(post.published_parsed,3600) is True:
        summary=BeautifulSoup(ws.query_cookie(post.link)).find('p',{'class':'introduction'}).get_text()
        if ws.article_exists(post.title,summary,36) == False:
            update_returnArticlesListVersion = 1


            #extract article content

            content_text = '<p class="introduction'+str(BeautifulSoup(ws.query_cookie(post.link)).findAll('div',{"class":"story-body"})).split('class="introduction')[1]
            for div in BeautifulSoup(content_text).findAll('div',{"class":"caption full-width"}):
                content_text=content_text.replace(str(div),'')
            content_text=content_text.split(']')[0]

            #extract article tags
            tags=ws.extract_tags_uk(content_text)

            #extract artCategory

            artCategory = ws.return_artcategory_ro(tags,content_text)
            if  artCategory == '':
                artCategory=[{"content":"Diverse","score":"1"}]


            #add sentiment
            sentiment=ws.return_sentiment_uk(content_text)

            #continue content manipulation

            content = "<div align=\"justify\">"+content_text+"</div>"
            content = ws.remove_br(content)

            client = MongoClient(DB_ADDRESS)
            db = client[DB]
            db['article'].insert({"date_ttl":datetime.utcnow(),"authId":int(36),
                              "authName":"Gavin Hewitt","artName":post.title,
                              "url":post.link,"summary":summary,"content":content,
                              "tags":tags[:-2],"date":int(time.time()),"artDate":datetime.utcnow().strftime("%d%b%Y"),
                              "authImgUrl" : "https://ws-truthrevolution.rhcloud.com/images/v1/gavin-hewitt.png",
                              "artSentiment":int(sentiment),"comments":[],
                              "artSource":"bbc.com","artCategory":artCategory})

ws.update_articlelistversion(update_returnArticlesListVersion,36)
