__author__ = 'mihai'
import urllib2, goslate,json, urllib, os,re
from datetime import datetime
from pymongo import MongoClient
from bs4 import BeautifulSoup
DB_ADDRESS = os.environ['OPENSHIFT_MONGODB_DB_URL']
DB = 'ws'

def query(url):
    try:
        return urllib2.urlopen(url).read()
    except:
        return "Unable to reach %s" % url

def query_cookie(url):

    try:
        return urllib2.build_opener(urllib2.HTTPCookieProcessor).open(url).read()
    except:
        return "Unable to reach %s" % url



def find_between(string, first, last):
    try:
        start = string.index(first) + len(first)
        end = string.index(last, start)
        return string[start:end]
    except ValueError:
        return ""


def article_exists(title, summary,authid):
    try:
        client = MongoClient(DB_ADDRESS)
    except:
        return "Unable to connect to MongoDB"

    db = client[DB]

    exists_title = db['article'].find({"artName": title, "authId": authid}).count()
    exists_summary = db['article'].find({"summary": summary, "authId": authid}).count()

    if exists_title == 0 and exists_summary == 0:
        return False
    else:
        return True

def return_sentiment_ro(text):
    gs = goslate.Goslate()
    content_text_translated=gs.translate(text,'en','ro')
    values = {'text':content_text_translated.encode('utf-8','ignore')}
    data = urllib.urlencode(values)
    try:
        req = urllib2.Request('http://text-processing.com/api/sentiment/', data)
        response = urllib2.urlopen(req)
        data = json.load(response)
        matrix_sentiment={"pos":2,"neg":1,"neutral":0}
        sentiment=int(matrix_sentiment[str(data['label'])])
    except:
        sentiment=0
    return sentiment

def return_sentiment_en(text):
    values = {'text':text}
    data = urllib.urlencode(values)
    try:
        req = urllib2.Request('http://text-processing.com/api/sentiment/', data)
        response = urllib2.urlopen(req)
        data = json.load(response)
        matrix_sentiment={"pos":2,"neg":1,"neutral":0}
        sentiment=int(matrix_sentiment[str(data['label'])])
    except:
        sentiment=0
    return sentiment

def return_sentiment_uk(text):
    values = {'text':text}
    data = urllib.urlencode(values)
    try:
        req = urllib2.Request('http://text-processing.com/api/sentiment/', data)
        response = urllib2.urlopen(req)
        data = json.load(response)
        matrix_sentiment={"pos":2,"neg":1,"neutral":0}
        sentiment=int(matrix_sentiment[str(data['label'])])
    except:
        sentiment=0
    return sentiment

def return_artcategory_ro(tags,text):

    #extract concepts
    gs = goslate.Goslate()
    baseurl='http://access.alchemyapi.com/calls/text/TextGetRankedConcepts'
    data={}
    data['apikey']='7ce531080aff94794962811c91bd6bb4df7b86b7'
    data['text']='%s' % (gs.translate(text,'en','ro')).encode('utf-8','ignore')
    data['linkedData'] = '0'
    data['outputMode'] = 'json'
    try:
        req = urllib2.Request(baseurl, urllib.urlencode(data))
        result = json.load(urllib2.urlopen(req))
    except:
        pass
    concepts=''
    i=0
    try:
        while i < len(result['concepts']):
            concepts=concepts+result['concepts'][i]['text']+', '
            i+=1
    except:
        pass


    #extract artCategory
    to_send=concepts.encode('utf-8','ignore')
    baseurl='https://query.yahooapis.com/v1/public/yql?'
    yql_query = "select * from contentanalysis.analyze where text='%s' and unique='true' " \
                    "and show_metadata='true' and enable_categorizer='true' " \
                    "and related_entities='true' " % to_send.replace('\'','&#39;')
    yql_url = baseurl + urllib.urlencode({'q':yql_query}) + "&format=json"
    data = {}
    data['name'] = 'ds'
    try:
        req = urllib2.Request(yql_url, urllib.urlencode(data))
        result = json.load(urllib2.urlopen(req))
    except:
        pass
    try:
        artCategory=result['query']['results']['yctCategories']['yctCategory']
    except:
        to_send=gs.translate(tags,'en','ro').encode('utf-8','ignore')
        baseurl='https://query.yahooapis.com/v1/public/yql?'
        yql_query = "select * from contentanalysis.analyze where text='%s' and unique='true' " \
                    "and show_metadata='true' and enable_categorizer='true' " \
                    "and related_entities='true' " % to_send.replace('\'','&#39;')
        yql_url = baseurl + urllib.urlencode({'q':yql_query}) + "&format=json"
        data = {}
        data['name'] = 'ds'
        try:
            req = urllib2.Request(yql_url, urllib.urlencode(data))
            result = json.load(urllib2.urlopen(req))
        except:
            pass
        try:
            artCategory=result['query']['results']['yctCategories']['yctCategory']
        except:
            to_send=gs.translate(text,'en','ro').encode('utf-8','ignore')
            baseurl='https://query.yahooapis.com/v1/public/yql?'
            yql_query = "select * from contentanalysis.analyze where text='%s' and unique='true' " \
                        "and show_metadata='true' and enable_categorizer='true' " \
                        "and related_entities='true' " % to_send.replace('\'','&#39;')
            yql_url = baseurl + urllib.urlencode({'q':yql_query}) + "&format=json"
            data = {}
            data['name'] = 'ds'
            try:
                req = urllib2.Request(yql_url, urllib.urlencode(data))
                result = json.load(urllib2.urlopen(req))
            except:
                pass
            try:
                artCategory=result['query']['results']['yctCategories']['yctCategory']
            except:
                to_send=gs.translate(tags,'en','ro').encode('utf-8','ignore')+concepts.encode('utf-8','ignore')
                baseurl='https://query.yahooapis.com/v1/public/yql?'
                yql_query = "select * from contentanalysis.analyze where text='%s' and unique='true' " \
                            "and show_metadata='true' and enable_categorizer='true' " \
                            "and related_entities='true' " % to_send.replace('\'','&#39;')
                yql_url = baseurl + urllib.urlencode({'q':yql_query}) + "&format=json"
                data = {}
                data['name'] = 'ds'
                try:
                    req = urllib2.Request(yql_url, urllib.urlencode(data))
                    result = json.load(urllib2.urlopen(req))
                except:
                    pass
                try:
                    artCategory=result['query']['results']['yctCategories']['yctCategory']
                except:
                    artCategory={"content":"Diverse","score":"1"}

    if type(artCategory)==type({}):
        artCategory=[artCategory]

    return artCategory

def return_artcategory_en(tags,text):

    #extract concepts
    baseurl='http://access.alchemyapi.com/calls/text/TextGetRankedConcepts'
    data={}
    data['apikey']='7ce531080aff94794962811c91bd6bb4df7b86b7'
    data['text']='%s' % text
    data['linkedData'] = '0'
    data['outputMode'] = 'json'
    try:
        req = urllib2.Request(baseurl, urllib.urlencode(data))
        result = json.load(urllib2.urlopen(req))
    except:
        pass
    concepts=''
    i=0
    try:
        while i < len(result['concepts']):
            concepts=concepts+result['concepts'][i]['text']+', '
            i+=1
    except:
        pass


    #extract artCategory
    to_send=concepts
    baseurl='https://query.yahooapis.com/v1/public/yql?'
    yql_query = "select * from contentanalysis.analyze where text='%s' and unique='true' " \
                    "and show_metadata='true' and enable_categorizer='true' " \
                    "and related_entities='true' " % to_send.replace('\'','&#39;')
    yql_url = baseurl + urllib.urlencode({'q':yql_query}) + "&format=json"
    data = {}
    data['name'] = 'ds'
    try:
        req = urllib2.Request(yql_url, urllib.urlencode(data))
        result = json.load(urllib2.urlopen(req))
    except:
        pass
    try:
        artCategory=result['query']['results']['yctCategories']['yctCategory']
    except:
        to_send=tags
        baseurl='https://query.yahooapis.com/v1/public/yql?'
        yql_query = "select * from contentanalysis.analyze where text='%s' and unique='true' " \
                    "and show_metadata='true' and enable_categorizer='true' " \
                    "and related_entities='true' " % to_send.replace('\'','&#39;')
        yql_url = baseurl + urllib.urlencode({'q':yql_query}) + "&format=json"
        data = {}
        data['name'] = 'ds'
        try:
            req = urllib2.Request(yql_url, urllib.urlencode(data))
            result = json.load(urllib2.urlopen(req))
        except:
            pass
        try:
            artCategory=result['query']['results']['yctCategories']['yctCategory']
        except:
            to_send=text
            baseurl='https://query.yahooapis.com/v1/public/yql?'
            yql_query = "select * from contentanalysis.analyze where text='%s' and unique='true' " \
                        "and show_metadata='true' and enable_categorizer='true' " \
                        "and related_entities='true' " % to_send.replace('\'','&#39;')
            yql_url = baseurl + urllib.urlencode({'q':yql_query}) + "&format=json"
            data = {}
            data['name'] = 'ds'
            try:
                req = urllib2.Request(yql_url, urllib.urlencode(data))
                result = json.load(urllib2.urlopen(req))
            except:
                pass
            try:
                artCategory=result['query']['results']['yctCategories']['yctCategory']
            except:
                to_send=tags+concepts
                baseurl='https://query.yahooapis.com/v1/public/yql?'
                yql_query = "select * from contentanalysis.analyze where text='%s' and unique='true' " \
                            "and show_metadata='true' and enable_categorizer='true' " \
                            "and related_entities='true' " % to_send.replace('\'','&#39;')
                yql_url = baseurl + urllib.urlencode({'q':yql_query}) + "&format=json"
                data = {}
                data['name'] = 'ds'
                try:
                    req = urllib2.Request(yql_url, urllib.urlencode(data))
                    result = json.load(urllib2.urlopen(req))
                except:
                    pass
                try:
                    artCategory=result['query']['results']['yctCategories']['yctCategory']
                except:
                    artCategory={"content":"Diverse","score":"1"}

    if type(artCategory)==type({}):
        artCategory=[artCategory]

    return artCategory

def update_articlelistversion(update_returnArticlesListVersion,authid):
    if update_returnArticlesListVersion == 1:
        try:
            client = MongoClient(DB_ADDRESS)
        except:
            return "Unable to connect to MongoDB"

        db = client[DB]
        db['articleslistversion'].update({'articleslistversion':{'$gte':1}},{'$inc':{'articleslistversion':1}})

        for cursor in db['author'].find({'authId':authid},{'_id':0,'disabled':1}):
            if cursor['disabled'] == 1:
                db['author'].update({'authId':authid},{'$set':{'disabled':0}})

def text_exists(what,where):
    if what in where:
        return True
    else:
        return False

def article_freshness(art_publised_parsed,difference_in_seconds):
    if  (datetime.utcnow()-datetime(*art_publised_parsed[:7])).total_seconds() < difference_in_seconds:
        return True
    else:
        return False

def extract_tags_ro(content_text):
    gs = goslate.Goslate()
    baseurl='http://access.alchemyapi.com/calls/text/TextGetRankedConcepts'
    data={}
    data['apikey']='7ce531080aff94794962811c91bd6bb4df7b86b7'
    data['text']='%s' % (gs.translate(content_text,'en','ro')).encode('utf-8','ignore')
    data['maxRetrieve'] = '10'
    data['linkedData'] = '0'
    data['outputMode'] = 'json'
    try:
        req = urllib2.Request(baseurl, urllib.urlencode(data))
        result = json.load(urllib2.urlopen(req))
    except:
        pass
    tags_english=''
    i=0
    while i < len(result['concepts']):
        tags_english=tags_english+result['concepts'][i]['text']+', '
        i+=1
    tags=gs.translate(tags_english,'ro','en').lower()[:-1]
    return tags

def extract_tags_en(content_text):
    baseurl='http://access.alchemyapi.com/calls/text/TextGetRankedConcepts'
    data={}
    data['apikey']='7ce531080aff94794962811c91bd6bb4df7b86b7'
    data['text']='%s' % content_text
    data['maxRetrieve'] = '10'
    data['linkedData'] = '0'
    data['outputMode'] = 'json'
    req = urllib2.Request(baseurl, urllib.urlencode(data))
    result = json.load(urllib2.urlopen(req))
    tags=''
    i=0
    while i < len(result['concepts']):
        tags=tags+result['concepts'][i]['text'].lower()+', '
        i+=1
    return tags[:-2]

def extract_tags_uk(content_text):
    baseurl='http://access.alchemyapi.com/calls/text/TextGetRankedConcepts'
    data={}
    data['apikey']='7ce531080aff94794962811c91bd6bb4df7b86b7'
    data['text']='%s' % content_text
    data['maxRetrieve'] = '10'
    data['linkedData'] = '0'
    data['outputMode'] = 'json'
    req = urllib2.Request(baseurl, urllib.urlencode(data))
    result = json.load(urllib2.urlopen(req))
    tags=''
    i=0
    while i < len(result['concepts']):
        tags=tags+result['concepts'][i]['text'].lower()+', '
        i+=1
    return tags[:-2]


def remove_br(content):
    content = content.replace('<br /><br /><br /><br /><br />', '<br />').replace('<br /><br /><br /><br />',
                                                                                  '<br />').replace(
        '<br /><br /><br />', '<br />').replace('//</p>', '</p>').replace('\n', '').replace('\r', '').replace('\t',
                                                                                                              '').replace(
        '<p>\xc2\xa0</p>', '').replace('<br/><br/>\xc2\xa0</p>', '</p>').replace('<p><br/>\xc2\xa0</p>', '').replace(
        '</p>, <p>', '</p><p>').replace('<br/><br/>','').replace('</br></br>','').replace('<p><br/></p>','')
    return content

def extract_summary_gandul(link):
    summary = BeautifulSoup(query(link)).find("meta",{"name":"description"})['content']
    return summary

def extract_tags_gandul(link):
    tags = (BeautifulSoup(query(link)).find("meta", {"name": "news_keywords"})['content'].replace(',',
                                                                                                                  ', ')).replace(
                '  ', ' ').lower()
    return tags

def extract_content_gandul(link):
    content=''
    text_dirty=BeautifulSoup(query(link)).find('div',{"class":"article"}).findAll('p')
    paragraph=0
    while paragraph < len(text_dirty)-1:
        content=content+str(text_dirty[paragraph])
        paragraph+=1
    content = "<div align=\"justify\">" + str(BeautifulSoup(query(link)).find("meta", {"name": "description"})).replace(
        '<meta content=\"', '<p>').replace('\" name=\"description\"/>', '</p>') + content.replace('</p>, <p>',
                                                                                                  '</p> <p>').replace(
        '<p>\n\xc2\xa0</p>', '').replace('<p>\n<br/>\n\xc2\xa0\xc2\xa0</p>','').replace('<p class=\"description\">FOTO: Agerpres</p>','') + "</div>"
    return content

def extract_link_revista22(url,number_of_articles_to_extract):
    link = "http://www.revista22.ro/" + str(
        BeautifulSoup(query(url)).findAll('p', {"style": "color:#8b0000;"})[
            number_of_articles_to_extract].a['href'])
    return link

def extract_title_revista22(url):
    title=BeautifulSoup(query(url)).title.get_text()
    return title

def extract_summary_revista22(text):
    summary=text[1].get_text()
    return summary

def extract_tags_revista22(text):
    tags=''
    try:
        tags=text[len(text)-1].get_text().split('Cuvinte cheie:')[1].replace(',',', ').replace('  ',' ').lower().strip()
    except:
        pass
    return tags

def extract_content_revista22(text):
    par=1
    while par<len(text):
        if "Cuvinte cheie:" in text[par].encode('utf-8') or "CITI\xc8\x9aI \xc8\x98I" in text[par].encode(
                'utf-8') or "<em>Articol publicat \xc8\x99i pe " in text[par].encode(
                'utf-8').strip() or "<strong>Articol publicat de" in text[par].encode('utf-8').strip():
            text[par]=''
        par+=1
    content_text=str(text[1:]).replace('</p>, <p','</p><p')
    content_text = "<div align=\"justify\">"+content_text.replace(", ''",'').split('[')[1].split(']')[0]+"</div>"
    content = remove_br(content_text)
    return content

def extract_content_hotnews(url):
    content=BeautifulSoup(query(url)).find('div',{"id":"articleContent"})
    content = "<div align=\"justify\">" + re.sub(r'<iframe.*</iframe>', '', remove_br(
        str(content).replace('style=\"font-size:12px;\">', '')) + "</div>")
    return (remove_br(content)).replace('<img','<img height=\"auto\" width=\"100%\"')

def extract_content_romanialibera(url):
    content=str(BeautifulSoup(query(url)).find('div',{"class":"article-text"}).findAll('p'))
    content = "<div align=\"justify\">"+content[1:len(content)-1    ]+"</div>"
    content = remove_br(content)
    return content.replace('<span style=\"line-height: 1.6em;\">', '').replace('</p>, , <p', '</p><p').replace(
        '</p>, <p', '</p><p').replace('<p class=\"title\">Mai puteti citi si:</p>', '')


