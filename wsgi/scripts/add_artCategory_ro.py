from pymongo import MongoClient
import goslate,urllib2,json,urllib

client = MongoClient('mongodb://admin:mmURZYYxluXV@5346701b5004463769000154-mihainicolae.rhcloud.com:49331')
db = client['ws']
output=db['article'].find({"artSource":{'$regex':'(.info|.ro)', '$options': '-i'}})

for id in output:
            #extract article tags for artCategory

            gs = goslate.Goslate()
            baseurl='http://access.alchemyapi.com/calls/text/TextGetRankedConcepts'
            data={}
            data['apikey']='0f96cf1f78f78e64c4d13f1006e85956b6fe3272'
            data['text']='%s' % (gs.translate(id['content'],'en','ro')).encode('utf-8')
            data['maxRetrieve'] = '10'
            data['linkedData'] = '0'
            data['outputMode'] = 'json'
            req = urllib2.Request(baseurl, urllib.urlencode(data))
            result = json.load(urllib2.urlopen(req))
            tags_english=''
            i=0
            while i < len(result['concepts']):
                tags_english=tags_english+result['concepts'][i]['text']+', '
                i+=1


            #extract artCategory

            to_send=tags_english.encode('utf-8','ignore')
            baseurl='https://query.yahooapis.com/v1/public/yql?'
            yql_query = "select * from contentanalysis.analyze where text='%s' and unique='true' " \
                    "and show_metadata='true' and enable_categorizer='true' " \
                    "and related_entities='true' " % to_send.replace('\'','&#39;')
            yql_url = baseurl + urllib.urlencode({'q':yql_query}) + "&format=json"
            data = {}
            data['name'] = 'ds'
            req = urllib2.Request(yql_url, urllib.urlencode(data))
            result = json.load(urllib2.urlopen(req))
            try:
                artCategory=result['query']['results']['yctCategories']['yctCategory']
            except:
                to_send=gs.translate(id['tags'],'en','ro').encode('utf-8','ignore')
                baseurl='https://query.yahooapis.com/v1/public/yql?'
                yql_query = "select * from contentanalysis.analyze where text='%s' and unique='true' " \
                        "and show_metadata='true' and enable_categorizer='true' " \
                        "and related_entities='true' " % to_send.replace('\'','&#39;')
                yql_url = baseurl + urllib.urlencode({'q':yql_query}) + "&format=json"
                data = {}
                data['name'] = 'ds'
                req = urllib2.Request(yql_url, urllib.urlencode(data))
                result = json.load(urllib2.urlopen(req))
                try:
                    artCategory=result['query']['results']['yctCategories']['yctCategory']
                except:
                    to_send=gs.translate(id['content'],'en','ro').encode('utf-8','ignore')
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
                        to_send=gs.translate(id['tags'],'en','ro').encode('utf-8','ignore')+tags_english.encode('utf-8','ignore')
                        baseurl='https://query.yahooapis.com/v1/public/yql?'
                        yql_query = "select * from contentanalysis.analyze where text='%s' and unique='true' " \
                                        "and show_metadata='true' and enable_categorizer='true' " \
                                        "and related_entities='true' " % to_send.replace('\'','&#39;')
                        yql_url = baseurl + urllib.urlencode({'q':yql_query}) + "&format=json"
                        data = {}
                        data['name'] = 'ds'
                        req = urllib2.Request(yql_url, urllib.urlencode(data))
                        result = json.load(urllib2.urlopen(req))
                        try:
                            artCategory=result['query']['results']['yctCategories']['yctCategory']
                        except:
                            artCategory={"content":"Diverse","score":"1"}
            if type(artCategory)==type({}):
                artCategory=[artCategory]
            db['article'].update({"_id":id["_id"]},{"$set":{"artCategory":artCategory}     }        )
#print(id['artSource'])
#    no_of_articles=db['article'].find({'authId':id['authId']}).count()
#    if no_of_articles!=0:
#        db["author"].update( { "authId":id["authId"] }   ,  { "$set":{"disabled":int(0)} }    )

