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

    link = str(BeautifulSoup(ws.query_cookie('http://www.newyorker.com/contributors/dexter-filkins')).findAll('h2')[
        numberoflinks + 4].a['href'])
    title = \
    BeautifulSoup(ws.query_cookie('http://www.newyorker.com/contributors/dexter-filkins')).findAll('h2')[numberoflinks + 4].a[
        'title']
    summary = BeautifulSoup(ws.query_cookie('http://www.newyorker.com/contributors/dexter-filkins')).findAll('p', {
    "class": "p-summary"})[numberoflinks].get_text()

    if ws.article_exists(title,summary,21) == False:
        update_returnArticlesListVersion = 1

        #extract article tags

        tags = ''

        for tag in BeautifulSoup(ws.query_cookie(link)).findAll('meta', {"property":"article:tag"}):
            tags=tag['content'].lower()+", "+tags

        #extract article content

        number_of_paragraphs_with_txt=0
        content_text=''
        while True:
            content_try=''
            try:
                content_try=(BeautifulSoup(ws.query_cookie(link))).findAll('p')[number_of_paragraphs_with_txt]
            except:
                break

            if "Dexter Filkins joined" in str(content_try):
                break

            if "Dexter Filkins" in str(content_try):
                content_try=''

            content_text=content_text+str(content_try)

            number_of_paragraphs_with_txt=number_of_paragraphs_with_txt+1

        if tags == '':
            tags=ws.extract_tags_en(content_text)

        #extract artCategory

        artCategory = ws.return_artcategory_ro(tags,content_text)
        if  artCategory == '':
            artCategory=[{"content":"Diverse","score":"1"}]


        #add sentiment
        sentiment=ws.return_sentiment_en(content_text)


        #continue content manipulation

        content_dirty = "<div align=\"justify\">"+("<br />".join((content_text.replace('\n','\n\n')).split("\n"))).replace('\t','')+"</div>"
        content = ws.remove_br(content_dirty)
        client = MongoClient('mongodb://admin:mmURZYYxluXV@5346701b5004463769000154-mihainicolae.rhcloud.com:49331')
        db = client['ws']
        db['article'].insert({"date_ttl":datetime.utcnow(),"authId":int(21),"authName":"Dexter Filkins",
                              "artName":title,"url":link,"summary":summary,"content":content,"tags":tags[:-2],
                              "date":int(time.time()),"artDate":datetime.utcnow().strftime("%d%b%Y"),
                              "authImgUrl" : "https://ws-truthrevolution.rhcloud.com/images/v1/dexter-filkins.png",
                              "artSentiment":int(sentiment),"comments":[],"artSource":"newyorker.com",
                              "artCategory":artCategory})
    numberoflinks=numberoflinks+1

ws.update_articlelistversion(update_returnArticlesListVersion,21)
