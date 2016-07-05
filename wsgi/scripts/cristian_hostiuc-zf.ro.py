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

    link = "http://www.zf.ro/"+str(BeautifulSoup(ws.query('http://www.zf.ro/autor/cristian-hostiuc/')).findAll('a',{"class":"title"})[numberoflinks]['href'])
    title = BeautifulSoup(ws.query(link)).title.get_text().split('|')[0]

    #extract article tags

    tags = (((str(BeautifulSoup(ws.query(link)).findAll('dl',{"class":"tags"})[0].get_text())).replace(',',', ')).replace('  ',' ')).replace('\n','').split(':')[1].lower()

    #extract article content

    text_dirty=BeautifulSoup(ws.query(link)).find('div',{"id":"content"}).findAll('p',{"class":""})


    par=0

    while par < len(text_dirty):
        if '\xc3\x8enscrie-te la newsletter-ul ZF.ro ca s\xc4\x83 prime\xc5\x9fti' in (text_dirty[par]).encode('utf-8') or 'Articol publicat \xc3\xaen edi\xc5\xa3ia tip\xc4\x83rit\xc4\x83' in (text_dirty[par]).encode('utf-8'):
            text_dirty[par]=''
        par+=1

    for img in BeautifulSoup(str(text_dirty)).findAll('img'):
        img_old=str(img)
        img['style']='height=\"auto\" width=\"100%\"'
        img=str(img).replace('style=\'','')
        text_dirty=str(text_dirty).replace(img_old,img)

    content_text=str(text_dirty)


    summary = BeautifulSoup(ws.query('http://www.zf.ro/autor/cristian-hostiuc/')).find('ul',{"class":"SearchList"}).findAll('li')[numberoflinks].find('p',{"class":""}).get_text().replace('\t','').replace('\n','')


    if tags == '':
        tags=ws.extract_tags_ro(content_text)


    if ws.article_exists(title,summary,16) is False and "ZF Corporate" not in content_text:
        update_returnArticlesListVersion = 1

        #extract artCategory
        artCategory=ws.return_artcategory_ro(tags,content_text)
        if artCategory == '':
            artCategory=[{"content":"Diverse","score":"1"}]

        #add sentiment
        sentiment=ws.return_sentiment_ro(content_text)

        #continue content manipulation
        try:
            content_text=content_text.split('[')[1]
        except:
            pass
        content = "<div align=\"justify\">"+content_text.replace('</p>, <p>','</p><p>').replace('<p>\n\xc2\xa0</p>','').replace(", ''",'').split(']')[0]+"</div>"

        #insert in db
        client = MongoClient(DB_ADDRESS)
        db = client[DB]
        db['article'].insert({"date_ttl":datetime.utcnow(),"authId":int(16),"authName":"Cristian Hostiuc",
                              "artName":title,"url":link,"summary":summary,"content":content,"tags":tags,
                              "date":int(time.time()),"artDate":datetime.utcnow().strftime("%d%b%Y"),
                              "authImgUrl" : "https://ws-truthrevolution.rhcloud.com/images/v1/cristian-hostiuc.png",
                              "artSentiment":int(sentiment),"comments":[],"artSource":"zf.ro",
                              "artCategory":artCategory})
    numberoflinks=numberoflinks+1

ws.update_articlelistversion(update_returnArticlesListVersion,16)
