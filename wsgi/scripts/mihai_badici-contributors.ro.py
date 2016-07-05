import time
import urllib2
import re
import string
import json
import urllib
import os
import goslate

import feedparser
from pymongo import MongoClient
from datetime import datetime
from bs4 import BeautifulSoup

import ws_functions as ws

DB_ADDRESS = os.environ['OPENSHIFT_MONGODB_DB_URL']
DB = 'ws'

d = feedparser.parse('http://www.contributors.ro/?author=2231&feed=rss')

update_returnArticlesListVersion = 0

for post in d.entries[:1]:
    if ws.article_exists(post.title, post.summary,14) == False:
        update_returnArticlesListVersion = 1


        #extract article content

        content_text1 = ws.find_between(BeautifulSoup(ws.query(post.link)).get_text(), "jssdk'));",
                                     "Ai informatii despre tema de mai sus").strip().encode('iso8859-2', 'ignore')
        content_text2 = (content_text1).replace('\xe2\x80\x9c', '"')
        content_text = content_text2.decode('utf8')

        # extract article tags
        tags=ws.extract_tags_ro(content_text)

        #extract artCategory
        artCategory=ws.return_artcategory_ro(tags,content_text)

        #add sentiment
        sentiment=ws.return_sentiment_ro(content_text)


        #continue content manipulation

        for i in BeautifulSoup(ws.query(post.link)).findAll('strong'):
            content_text = string.replace(content_text, i.get_text(), "<strong>" + i.get_text() + "</strong>", 1)

        pat1 = re.compile(r"(^|[\n ])(([\w]+?://[\w\#$%&~.\-;:=,?@\[\]+]*)(/[\w\#$%&~/.\-;:=,?@\[\]+]*)?)",
                          re.IGNORECASE | re.DOTALL)
        content_url = pat1.sub(r'\1<a href="\2">\2</a>', content_text)
        content = "<p align=\"justify\">" + ("<br />".join(content_url.split("\n"))).replace('\t', '') + "</p>"
        content=content.replace('<br />','<br /><br />')

        client = MongoClient(DB_ADDRESS)
        db = client[DB]
        db['article'].insert(
            {"date_ttl": datetime.utcnow(), "authId": int(14), "authName": "Mihai Badici", "artName": post.title,
             "url": post.link, "summary": post.summary, "content": content, "tags": tags, "date": int(time.time()),
             "artDate": datetime.utcnow().strftime("%d%b%Y"),
             "authImgUrl": "https://ws-truthrevolution.rhcloud.com/images/v1/mihai-badici.png",
             "artSentiment": int(sentiment), "comments": [],"artSource":"contributors.ro",
             "artCategory":artCategory})

ws.update_articlelistversion(update_returnArticlesListVersion,14)
