from pymongo import MongoClient

token = '' #your bot token
database_name = ''
db = getDB()

def getDB():
    return MongoClient()[database_name] #change connect settings