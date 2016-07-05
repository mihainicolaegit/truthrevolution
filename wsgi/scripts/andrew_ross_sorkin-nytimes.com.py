import feedparser, os,time, urllib, urllib2, json
from pymongo import MongoClient
from datetime import datetime
from bs4 import BeautifulSoup
import ws_functions as ws
DB_ADDRESS = os.environ['OPENSHIFT_MONGODB_DB_URL']
DB = 'ws'

d = feedparser.parse('http://topics.nytimes.com/top/reference/timestopics/people/s/andrew_ross_sorkin/index.html?rss=1')

update_returnArticlesListVersion = 0


for post in d.entries:
    if ws.article_freshness(post.published_parsed,3600) is True:
        if ws.article_exists(post.title,BeautifulSoup(post.summary).get_text(),25) == False:
            update_returnArticlesListVersion = 1

            #extract article content

            replace1 = '<p class="story-body-text" itemprop="articleBody"><div class="inlineModule"><div class="entry"><div class="thumb"><img alt="The Conversation" height="50" src="http://graphics8.nytimes.com/images/blogs_v3/opinionator/pogs/theconversation45.gif" width="50"/></div><p class="summary">'
            text_dirty = str(BeautifulSoup(ws.query_cookie(post.link)).findAll('p',{"class":"story-body-text"})).replace(replace1,'')
            content_text=(text_dirty.split('[')[1].replace(', <p','<p')).split(']')[0]

            #extract article tags

            tags=''
            for tag in BeautifulSoup(ws.query_cookie(post.link)).findAll('meta', {"property":"article:tag"}):
                tags=tag['content'].lower()+", "+tags
            if tags == '':
                tags=ws.extract_tags_en(content_text)

            #extract artCategory

            artCategory = ws.return_artcategory_en(tags,content_text)
            if  artCategory == '':
                artCategory=[{"content":"Diverse","score":"1"}]


            #add sentiment
            sentiment=ws.return_sentiment_en(content_text)
            #continue content manipulation

            content = "<div align=\"justify\">"+content_text+"</div>"
            content = ws.remove_br(content)

            client = MongoClient(DB_ADDRESS)
            db = client[DB]
            db['article'].insert({"date_ttl":datetime.utcnow(),"authId":int(25),"authName":"Andrew Ross Sorkin",
                                  "artName":post.title,"url":post.link,"summary":BeautifulSoup(post.summary).get_text(),
                                  "content":content,"tags":tags[:-2],"date":int(time.time()),
                                  "artDate":datetime.utcnow().strftime("%d%b%Y"),
                                  "authImgUrl" : "https://ws-truthrevolution.rhcloud.com/images/v1/andrew-ross-sorkin.png",
                                  "artSentiment":int(sentiment),"comments":[],"artSource":"nytimes.com",
                                  "artCategory":artCategory})

ws.update_articlelistversion(update_returnArticlesListVersion,25)
