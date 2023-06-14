from pymongo import MongoClient

class Database:

    def __init__(self, ip_address, database):
        print("connecting database...")
        self.client = MongoClient(ip_address)
        self.db = self.client[database]
        print("ok.")

    def insert(self, tweet):
        return self.db.tweets.insert_one(tweet)
    
    def insert_many(self, collection, tweets):
        return self.db[collection].insert_many(tweets)

    def find_similar(self, text: str):
        return self.db.tweets.find(
            { "$text": { "$search": text } },
            { "score": { "$meta": "textScore" } }
        ).sort( { "score": { "$meta": "textScore" } } ).limit(5)

    def close(self):
        return self.client.close()