# Requires pymongo
# pip install --upgrade pymongo

from pymongo import MongoClient

class Database:
    def __init__(self, key, database):
        self.collection = 'videos'
        self.client = MongoClient(key)
        self.db = self.client[database]
        
    def addVideo(self, id, payload):
        self.db[self.collection].update_one({'_id': id}, {"$set": payload}, upsert=True)
        
    def getAllVideos(self):
        res = self.db[self.collection].find()
        return [x for x in res]
    
    def clearCollection(self, msg=''):
        if (msg == 'yes'):
            self.db[self.collection].delete_many({})
            print("Colelction was cleared.")
        else:
            print("Pass 'yes' into clearCollection() method to really clear it.")
            
    def close(self):
        self.client.close()