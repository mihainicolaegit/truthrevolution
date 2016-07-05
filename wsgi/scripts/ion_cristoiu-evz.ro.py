import time
import re
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

    link = str(BeautifulSoup(ws.query('http://www.evz.ro/author/ion.cristoiu')).findAll('h3')[numberoflinks].a['href'])
    title_dirty = BeautifulSoup(ws.query(link)).findAll('h3')[0].get_text()
    title=re.sub(r'^.*NIA LUI CRISTOIU.','',title_dirty)

    #extract article summary

    summary_html = BeautifulSoup(ws.query(link)).find('strong')
    summary = summary_html.get_text()

    if ws.article_exists(title,summary,10) == False:
        update_returnArticlesListVersion = 1

        #extract article tags

        tags = (((ws.find_between(BeautifulSoup(ws.query(link)).get_text(), 'Tag-uri:', '//<![CDATA').replace(',',
                                                                                                        ', ')).replace(
            '  ', ' ').lower()).replace('\n', '')).replace('\t', '').strip()


        #extract article content

        text_dirty=BeautifulSoup(ws.query(link)).find('div',{"class":"content-box first"}).findAll('p')
        par=0
        while par<len(text_dirty):
            if str(text_dirty[par].span) == "<span>+</span>":
                text_dirty[par]=''
            par+=1
        content_text=str(text_dirty).replace('</p>, <p','</p><p')
        content_text = "<div align=\"justify\">"+str(summary_html)+content_text.replace(", ''",'').split('[')[1].split(']')[0]+"</div>"
        content = ws.remove_br(content_text)

        if tags == '':
            tags=ws.extract_tags_ro(content_text)


        #extract artCategory

        artCategory=ws.return_artcategory_ro(tags,content)
        if artCategory == '':
            artCategory=[{"content":"Diverse","score":"1"}]

        #add sentiment

        sentiment=ws.return_sentiment_ro(content_text)

        client = MongoClient(DB_ADDRESS)
        db = client[DB]
        db['article'].insert({"date_ttl":datetime.utcnow(),"authId":int(10),"authName":"Ion Cristoiu",
                              "artName":title,"url":link,"summary":summary,"content":content,"tags":tags,
                              "date":int(time.time()),"artDate":datetime.utcnow().strftime("%d%b%Y"),
                              "authImgUrl" : "https://ws-truthrevolution.rhcloud.com/images/v1/ion-cristoiu.png",
                              "artSentiment":int(sentiment),"comments":[],"artSource":"evz.ro",
                              "artCategory":artCategory})

    numberoflinks=numberoflinks+1

ws.update_articlelistversion(update_returnArticlesListVersion,10)
