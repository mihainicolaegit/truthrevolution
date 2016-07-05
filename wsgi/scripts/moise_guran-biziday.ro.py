import time
import os
from bs4 import BeautifulSoup

import feedparser
from pymongo import MongoClient
from datetime import datetime

import ws_functions as ws

DB_ADDRESS = os.environ['OPENSHIFT_MONGODB_DB_URL']
DB = 'ws'

d = feedparser.parse('http://www.biziday.ro/feed/')

update_returnArticlesListVersion = 0


for post in d.entries:
    if ws.article_freshness(post.published_parsed,3600) is True:
        if post.summary != '':
            try:
                summary=(post.summary).split('de Moise Guran')[1]
            except:
                summary=post.summary
            if 'Moise'in post.author or 'de Moise Guran' in post.content[0].value:
                if ws.article_exists(post.title,summary,32) == False:
                    update_returnArticlesListVersion = 1

                    #extract article tags

                    tag = post.tags
                    tag_counter=0
                    tags=''
                    while tag_counter<len(tag):
                        tags=tags+(tag[tag_counter].term).lower()+", "
                        tag_counter=tag_counter+1


                    #extract article content
                    content_text=post.content[0].value
                    for img in BeautifulSoup(post.content[0].value).findAll('img'):
                        width=img['width']
                        height=img['height']
                        content_text=content_text.replace('width=\"%s\"' % width,'width=\"100%\"').replace('height=\"%s\"' % height,'height=\"auto\"')

                    try:
                        content_text = ((content_text).split('de Moise Guran')[1]).encode('utf-8')
                    except:
                        content_text = (content_text).encode('utf-8')

                    if tags == '':
                        tags=ws.extract_tags_ro(content_text)+', '


                    #extract artCategory

                    artCategory=ws.return_artcategory_ro(tags,content_text)
                    if artCategory == '':
                        artCategory=[{"content":"Diverse","score":"1"}]

                    #add sentiment

                    sentiment=ws.return_sentiment_ro(content_text)

                    #continue content manipulation

                    content = "<div align=\"justify\">"+content_text.replace('<br />',' ')+"</div>"
                    content = ws.remove_br(content)

                    client = MongoClient(DB_ADDRESS)
                    db = client[DB]
                    db['article'].insert({"date_ttl":datetime.utcnow(),"authId":int(32),"authName":"Moise Guran",
                                          "artName":post.title,"url":post.link,"summary":summary,
                                          "content":content,"tags":tags[:-2],"date":int(time.time()),
                                          "artDate":datetime.utcnow().strftime("%d%b%Y"),
                                          "authImgUrl" : "https://ws-truthrevolution.rhcloud.com/images/v1/moise-guran.png",
                                          "artSentiment":int(sentiment),"comments":[],"artSource":"biziday.ro",
                                          "artCategory":artCategory})

ws.update_articlelistversion(update_returnArticlesListVersion,32)

