import time
import string
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

    link = "http://www.capital.ro/"+str(BeautifulSoup(ws.query('http://www.capital.ro/articole-autor.html?id=880')).findAll('h3')[numberoflinks].a['href'])

    title=''
    try:
        title = BeautifulSoup(ws.query(link)).find('div',{"class":"content-box"}).find('h3').get_text()
    except:
        pass
    if title != '':
        text_dirty=BeautifulSoup(ws.query(link)).find('div',{"class":"content-box"}).findAll('p')

        #extract article content
        content_text=text_dirty[1:len(text_dirty)-1]
        content_dirty = str(content_text).replace('<strong>Bogdan Gl\xc4\x83van,</strong>','')
        content = "<div align=\"justify\">"+ws.remove_br(content_dirty[1:len(content_dirty)-1])+"</div>"

        #extract summary
        summary = text_dirty[1].get_text()


        #check if article exists else add it
        if ws.article_exists(title,summary,15) == False:
            update_returnArticlesListVersion = 1

            #extract tags
            tags=ws.extract_tags_ro(content)

            #extract artCategory
            artCategory=ws.return_artcategory_ro(tags,content)

            #add sentiment
            sentiment=ws.return_sentiment_ro(content)

            client = MongoClient(DB_ADDRESS)
            db = client[DB]
            db['article'].insert({"date_ttl":datetime.utcnow(),"authId":int(15),
                              "authName":"Bogdan Gl\xc4\x83van","artName":title,
                              "url":link,"summary":summary,"content":content,"tags":tags,
                              "date":int(time.time()),"artDate":datetime.utcnow().strftime("%d%b%Y"),
                              "authImgUrl" : "https://ws-truthrevolution.rhcloud.com/images/v1/bogdan-glavan.png",
                              "artSentiment":int(sentiment),"comments":[],"artSource":"capital.ro",
                              "artCategory":artCategory})

    numberoflinks=numberoflinks+1

ws.update_articlelistversion(update_returnArticlesListVersion,15)
