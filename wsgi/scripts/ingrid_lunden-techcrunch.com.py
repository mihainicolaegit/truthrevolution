import time
import os

import feedparser
from pymongo import MongoClient
from datetime import datetime
from bs4 import BeautifulSoup

import ws_functions as ws

DB_ADDRESS = os.environ['OPENSHIFT_MONGODB_DB_URL']
DB = 'ws'


d = feedparser.parse('http://techcrunch.com/author/ingrid-lunden/feed/')

update_returnArticlesListVersion = 0

for post in d.entries:
    if ws.article_freshness(post.published_parsed,3600) is True:
        if not ws.article_exists(post.title, BeautifulSoup(post.summary).get_text(),35):
            update_returnArticlesListVersion = 1

            # extract article tags

            tag = post.tags
            tag_counter = 0
            tags = ''
            while tag_counter < len(tag):
                tags = tags + tag[tag_counter].term.lower() + ", "
                tag_counter += 1

            # extract article content

            text_dirty = ''
            for paragraph in BeautifulSoup(ws.query_cookie(post.link)).find_all('p', {'class': '', 'id': ''}):
                if "id=" not in str(paragraph) and "Get every new post delivered to your Inbox." not in str(paragraph):
                    try:
                        width=paragraph.find('img')['width']
                        height=paragraph.find('img')['height']
                        paragraph=str(paragraph).replace('width=\"%s\"' % width,'width=\"100%\"').replace('height=\"%s\"' % height,'height=\"auto\"')
                    except:
                        pass
                    text_dirty += str(paragraph)

            if text_dirty != '':
                update_returnArticlesListVersion -= 1
                content_text = text_dirty.replace(', <p', '<p')

            if tags == '':
                tags=ws.extract_tags_en(content_text)


            #extract artCategory

            artCategory = ws.return_artcategory_ro(tags,content_text)
            if  artCategory == '':
                artCategory=[{"content":"Diverse","score":"1"}]


            #add sentiment
            sentiment=ws.return_sentiment_en(content_text)

            # continue content manipulation

            content = "<div align=\"justify\">" + content_text + "</div>"
            content = ws.remove_br(content)

            client = MongoClient('mongodb://admin:mmURZYYxluXV@5346701b5004463769000154-mihainicolae.rhcloud.com:49331')
            db = client['ws']
            db['article'].insert(
                {"date_ttl": datetime.utcnow(), "authId": int(35), "authName": "Ingrid Lunden", "artName": post.title,
                 "url": post.link, "summary": BeautifulSoup(post.summary).get_text(), "content": content,
                 "tags": tags[:-2], "date": int(time.time()), "artDate": datetime.utcnow().strftime("%d%b%Y"),
                 "authImgUrl": "https://ws-truthrevolution.rhcloud.com/images/v1/ingrid-lunden.png",
                 "artSentiment": int(sentiment), "comments": [], "artSource": "techcrunch.com",
                 "artCategory":artCategory})

ws.update_articlelistversion(update_returnArticlesListVersion,35)
