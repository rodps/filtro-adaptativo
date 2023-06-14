import tweepy
from db import Database
import trackwords
from os import environ as env
from dotenv import load_dotenv

class MyStream(tweepy.Stream):

    def __init__(self, db, consumer_key, consumer_secret, access_token, access_token_secret):
        super().__init__(consumer_key, consumer_secret, access_token, access_token_secret)
        self.db = db

    def on_status(self, status):
        print(status.text)
        self.db.insert(status._json)
          
def main():
    load_dotenv()

    database = Database(env.get("DB_IP"), env.get("DB_NAME"))

    stream = MyStream(
        database,
        env.get("CONSUMER_KEY"), env.get("CONSUMER_SECRET"),
        env.get("ACCESS_TOKEN"), env.get("ACCESS_TOKEN_SECRET")
    )

    print("Coletando tweets...")
    stream.filter(languages=["en"], track = trackwords.base)

    print("Stream encerrada")
    
if __name__ == "__main__":
    main()