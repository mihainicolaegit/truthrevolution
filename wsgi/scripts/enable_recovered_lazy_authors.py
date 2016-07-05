from pymongo import MongoClient
import os

DB_ADDRESS = os.environ['OPENSHIFT_MONGODB_DB_URL']
DB = 'ws'

client = MongoClient(DB_ADDRESS)
db = client[DB]
output=db['author'].find({},{'_id':0,'authId':1})
no_of_articles=-1
for id in output:
    no_of_articles=db['article'].find({'authId':id['authId']}).count()
    if no_of_articles!=0:
        db["author"].update( { "authId":id["authId"] }   ,  { "$set":{"disabled":int(0)} }    )

