import feedparser, os,time
from pymongo import MongoClient
from datetime import datetime
from bs4 import BeautifulSoup
import ws_functions as ws
DB_ADDRESS = os.environ['OPENSHIFT_MONGODB_DB_URL']
DB = 'ws'
d = feedparser.parse('http://topics.nytimes.com/top/opinion/editorialsandoped/oped/columnists/thomaslfriedman/index.html?rss=1')

update_returnArticlesListVersion = 0
for post in d.entries:
    if ws.article_freshness(post.published_parsed,3600) is True:
        if ws.article_exists(post.title,BeautifulSoup(post.summary).get_text(),17) == False:
            update_returnArticlesListVersion = 1

            #extract article tags

            tags=''
            for tag in BeautifulSoup(ws.query_cookie(post.link)).findAll('meta', {"property":"article:tag"}):
                tags=tag['content'].lower()+", "+tags

            #extract article content

            text_dirty = str(BeautifulSoup(ws.query_cookie(post.link)).findAll('p',{"class":"story-body-text story-content"}))
            content_text=(text_dirty.split('[')[1].replace(', <p','<p')).split(']')[0]

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
            db['article'].insert({"date_ttl":datetime.utcnow(),"authId":int(17),"authName":"Thomas L. Friedman",
                                  "artName":post.title,"url":post.link,"summary":BeautifulSoup(post.summary).get_text(),
                                  "content":content,"tags":tags[:-2],"date":int(time.time()),
                                  "artDate":datetime.utcnow().strftime("%d%b%Y"),
                                  "authImgUrl" : "https://ws-truthrevolution.rhcloud.com/images/v1/thomas-friedman.png",
                                  "artSentiment":int(sentiment),"comments":[],"artSource":"nytimes.com",
                              "artCategory":artCategory})

ws.update_articlelistversion(update_returnArticlesListVersion,17)
