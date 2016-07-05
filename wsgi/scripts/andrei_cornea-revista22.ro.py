import time
import os
from pymongo import MongoClient
from datetime import datetime
from bs4 import BeautifulSoup

import ws_functions as ws

DB_ADDRESS = os.environ['OPENSHIFT_MONGODB_DB_URL']
DB = 'ws'


update_returnArticlesListVersion = 0
numberoflinks=0
while  numberoflinks<1:
    link=ws.extract_link_revista22('http://www.revista22.ro/autor-andrei-cornea-1',numberoflinks)
    title = ws.extract_title_revista22(link)

    text_dirty=BeautifulSoup(ws.query(link)).find('div',{"class":"doublebox_c"}).findAll('p')


    #extract summary
    summary=ws.extract_summary_revista22(text_dirty)

    #extract tags
    tags=ws.extract_tags_revista22(text_dirty)

    #extract content text
    content=ws.extract_content_revista22(text_dirty)

    #check if tags empty and if true extract from external source
    if tags == '':
        tags=ws.extract_tags_ro(content)

    #if article does not exist
    if ws.article_exists(title,summary,13) == False:

        #extract artCategory
        artCategory=ws.return_artcategory_ro(tags,content)

        #add sentiment
        sentiment=ws.return_sentiment_ro(content)

        #insert article in DB
        client = MongoClient(DB_ADDRESS)
        db = client[DB]
        db['article'].insert({"date_ttl":datetime.utcnow(),"authId":int(13),
                              "authName":"Andrei Cornea","artName":title,"url":link,"summary":summary,
                              "content":content,"tags":tags,"date":int(time.time()),
                              "artDate":datetime.utcnow().strftime("%d%b%Y"),
                              "authImgUrl" : "https://ws-truthrevolution.rhcloud.com/images/v1/andrei-cornea.png",
                              "artSentiment":int(sentiment),"comments":[],"artSource":"revista22.ro",
                              "artCategory":artCategory})

    numberoflinks=numberoflinks+1

ws.update_articlelistversion(update_returnArticlesListVersion,13)

