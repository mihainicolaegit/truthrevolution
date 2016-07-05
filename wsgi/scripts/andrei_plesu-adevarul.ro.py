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

    link = "http://adevarul.ro" + str(BeautifulSoup(ws.query('http://adevarul.ro/blogs/andrei.plesu')).findAll('h2', {"itemprop": "headline", "class": ""})[numberoflinks].a['href'])
    title = BeautifulSoup(ws.query(link)).find('h1').get_text()


    #initialize extraction
    summary_html=BeautifulSoup(ws.query(link)).find('h2',{"class":"articleOpening"})
    text_dirty=BeautifulSoup(ws.query(link)).find('div',{"class":"article-body"}).findAll('p')

    #extract summary
    summary = summary_html.get_text()

    #extract article content
    content_text=text_dirty[1:len(text_dirty)-1]
    content_text=str(content_text).split('[')[1].split(']')[0]

    #check if article exists, otherwise insert it
    if ws.article_exists(title,summary,11) == False:
        update_returnArticlesListVersion = 1

        #extract article tags
        tags=''
        tag=BeautifulSoup(ws.query('http://adevarul.ro/blogs/andrei.plesu')).find_all('aside',{"class":"keywords"})[numberoflinks].find_all('li')
        counter=0
        while counter < len(tag):
            tags=tags + tag[counter].get_text().lower() + ", "
            counter += 1

        if tags == '':
            tags=ws.extract_tags_ro(content_text)+', '

        #extract artCategory
        artCategory=ws.return_artcategory_ro(tags,content_text)

        #add sentiment
        sentiment=ws.return_sentiment_ro(content_text)

        #continue content manipulation
        content = ws.remove_br("<div align=\"justify\">"+content_text+"</div>")

        client = MongoClient(DB_ADDRESS)
        db = client[DB]
        db['article'].insert({"date_ttl":datetime.utcnow(),"authId":int(11),"authName":"Andrei Ple\xc5\x9fu",
                              "artName":title,"url":link,"summary":summary,"content":content,"tags":tags[:-2],
                              "date":int(time.time()),"artDate":datetime.utcnow().strftime("%d%b%Y"),
                              "authImgUrl" : "https://ws-truthrevolution.rhcloud.com/images/v1/andrei-plesu.png",
                              "artSentiment":int(sentiment),"comments":[],"artSource":"adevarul.ro",
                              "artCategory":artCategory})
    numberoflinks += 1

ws.update_articlelistversion(update_returnArticlesListVersion,11)

