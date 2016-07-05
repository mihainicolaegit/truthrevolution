import time
import re
import os

from flask import request,send_from_directory
from flask import Flask, Response
import pymongo
from flask import jsonify
from pymongo import MongoClient
from bson.json_util import dumps
from bson.objectid import ObjectId


app = Flask(__name__,static_folder='static')
app.config.update(SEND_FILE_MAX_AGE_DEFAULT=1209600)

type_authors=401
type_articles=501
type_request=601
STATUS_OK=200
STATUS_FAIL=300
access_key= '18476131800607698914373271477371810087L'
DB_ADDRESS = os.environ['OPENSHIFT_MONGODB_DB_URL']
DB = 'ws'

@app.route("/")
def index():
    response={}
    response['content']="How may I help you?"
    response['type']=type_request
    response['status']=STATUS_OK
    return jsonify(response)

@app.route("/images/v1/<path:filename>")
def send_images(filename):
    response={}
    if '..' in filename or filename.startswith('/'):
        response['content'] = {}
        response['status'] = STATUS_FAIL
        response['type'] = type_request
        return jsonify(response)
    return send_from_directory(app.static_folder,filename, as_attachment=True)

@app.route('/data/v1',methods=['POST'])
def data():
    response={}
    if re.search('application/json',request.headers['Content-Type']) is None:
        response['status'] = STATUS_FAIL
        response['type'] = type_request
        response['content'] = {}
        return jsonify(response)

    try:
        request_type = int(request.json.get('type'))
    except:
        request_type = int(type_request)

    if request_type != 401 and request_type != 501:
        request_type = int(type_request)

    try:
        filters = request.json.get('filters')
    except:
        filters = {}

    try:
        key = request.json.get('key')
    except:
        key = ''

    if key == access_key:

        if request_type == type_authors:

            try:
                authId = filters['authId']
            except:
                authId = 0

            try:
                authName = filters['authName']
            except:
                authName = None

            try:
                returnAbout = filters['returnAbout']
            except:
                returnAbout = False

            try:
                returnImg = filters['returnImg']
            except:
                returnImg = False

            try:
                zone = filters['zone']
            except:
                zone = None

            array_view_fields={'_id':0,'authId': 1,'zone': 1,'about':1,'authName':1,'authImgUrl':1}

            if returnAbout is False:
                del array_view_fields['about']
            if returnImg is False:
                del array_view_fields['authImgUrl']

            array_search_fields = {'disabled': 0, 'authId': authId,
                               'authName': {'$regex': '%s' % authName, '$options': '-i'},
                               'zone': {'$regex': '%s' % zone, '$options': '-i'}}
            if authId == 0:
                del array_search_fields['authId']
            if authName is None:
                del array_search_fields['authName']
            if zone is None:
                del array_search_fields['zone']

            client = MongoClient(DB_ADDRESS)
            db = client[DB]

            response['content']=list(db["author"].find(array_search_fields, array_view_fields).sort('authName', pymongo.ASCENDING))
            response['timestamp'] = int(time.time())
            response['type'] = type_authors
            response['status'] = STATUS_OK
            return jsonify(response)

        if request_type == type_articles:

            try:
                authId = filters['authId']
            except:
                authId = 0

            try:
                authName = filters['authName']
            except:
                authName = None

            try:
                artId = filters['artId']
            except:
                artId = None

            try:
                artName = filters['artName']
            except:
                artName = None

            try:
                returnTags = filters['returnTags']
            except:
                returnTags = False

            try:
                returnArtBody = filters['returnArtBody']
            except:
                returnArtBody = False

            try:
                returnArtDate = filters['returnArtDate']
            except:
                returnArtDate = False

            try:
                returnImg = filters['returnImg']
            except:
                returnImg = False

            try:
                returnAuthName = filters['returnAuthName']
            except:
                returnAuthName = False

            try:
                returnSentiment = filters['returnSentiment']
            except:
                returnSentiment = False

            try:
                withTags = filters['withTags']
            except:
                withTags = None

            try:
                afterDate = filters['afterDate']
            except:
                afterDate = 0

            try:
                beforeDate = filters['beforeDate']
            except:
                beforeDate = 0

            array_view_fields={'tags':1,'content':1,'artName':1,'authName':1,'authId':1,'artDate':1,
                               'date':1,'authImgUrl':1,'artSentiment':1,'summary':1,'artSource':1,'artCategory.content':{'$slice':3},'artCategory.content':1}

            if returnTags == False:
                del array_view_fields['tags']
            if returnArtBody == False:
                del array_view_fields['content']
            if returnArtDate == False:
                del array_view_fields['date']
            if returnImg == False:
                del array_view_fields['authImgUrl']
            if returnAuthName == False:
                del array_view_fields['authName']
            if returnSentiment == False:
                del array_view_fields['artSentiment']

            array_search_fields = {'date': {'$lt': beforeDate, '$gt': afterDate}, 'authId': authId,
                                   'authName': {'$regex': '%s' % authName, '$options': '-i'}, '_id': ObjectId(artId),
                                   'artName': {'$regex': '%s' % artName, '$options': '-i'},
                                   'tags': {'$regex': '%s' % withTags, '$options': '-i'}}

            if authId == 0:
                del array_search_fields['authId']
            if authName is None:
                del array_search_fields['authName']
            if artId is None:
                del array_search_fields['_id']
            if artName is None:
                del array_search_fields['artName']
            if beforeDate is 0:
                del array_search_fields['date']['$lt']
            if afterDate == 0:
                del array_search_fields['date']['$gt']
            if withTags is None:
                del array_search_fields['tags']
            if beforeDate == 0:
                if afterDate == 0:
                    del array_search_fields['date']

            client = MongoClient(DB_ADDRESS)
            db = client[DB]

            output=db["article"].find(array_search_fields, array_view_fields).sort('date', pymongo.ASCENDING)
            output2=[]
            for id in output:
                i=0
                while i < len(id['artCategory']):
                    id['artCategory'][i]['content']=id['artCategory'][i]['content'].lower()
                    i+=1
                if len(id['artCategory'])<3:
                    i=0
                    while i < 4-len(id['artCategory']):
                        id['artCategory'].append({'content':''})
                        i+=1
                output2.append(id)

            response['content'] = output2
            response['timestamp'] = int(time.time())
            response['type'] = type_articles
            response['status'] = STATUS_OK

            return Response(dumps(response),mimetype='application/json;charset=utf-8')




    response['status'] = STATUS_FAIL
    response['type'] = request_type
    response['content'] = {}
    return jsonify(response)

