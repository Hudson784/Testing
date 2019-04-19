from __future__ import print_function
import tweepy
import json
import MySQLdb 
from dateutil import parser
from flask import Flask, jsonify, request, render_template, redirect, url_for

WORDS = ['#GOT', '#GameOfThrones', '#Web', '#assignment', '#school', '#UWI']

ACCESS_TOKEN = '1117652982475239424-TqGEsktbN74s0OGG6IqKKkXUArnSCi'
ACCESS_TOKEN_SECRET  = 'Xtf4rLv3z0N6nHt7yJvYsYPOjZwEC45N3oqRhKo87XVdb'
CONSUMER_KEY = 'uWrEWX2bhsMtN8hnpd12HjMfl'
CONSUMER_SECRET = 'bdcvgAI6xRTYvoHJeNf1nkDsl9oDylOkJr1gqkwXEasY3qK1EF'

HOST = 'remotemysql.com'
USER = 'pPEd17bA5B'
PASSWD = 'qIhMyEEHjc'
DATABASE = 'pPEd17bA5B'

# This function takes the 'created_at', 'text', 'screen_name' and 'tweet_id' and stores it
# into a MySQL database
def store_data(created_at, text, screen_name, tweet_id, img):
    db=MySQLdb.connect(host=HOST, user=USER, passwd=PASSWD, db=DATABASE, charset="utf8")
    cursor = db.cursor()
    insert_query = "INSERT INTO twitter (tweet_id, screen_name, created_at, text, img) VALUES (%s, %s, %s, %s, %s)"
    cursor.execute(insert_query, (tweet_id, screen_name, created_at, text, img))
    db.commit()
    cursor.close()
    db.close()
    return

#Listener for default listening
class StreamListener(tweepy.StreamListener):
    def __init__(self, api=None):
        super(StreamListener, self).__init__()
        self.num_tweets = 0

    def on_connect(self):
        print("You are now connected to the streaming API.")
 
    def on_error(self, status_code):
        print('An Error has occured: ' + repr(status_code))
        return False

    def on_data(self, data):
        self.num_tweets += 1
        if self.num_tweets < 3:
            try:
                datajson = json.loads(data)
                text = datajson['text']
                screen_name = datajson['user']['screen_name']
                img = datajson['user']['profile_image_url']
                tweet_id = datajson['id']
                created_at = parser.parse(datajson['created_at']) 
                print("Tweet collected at " + str(created_at))
                store_data(created_at, text, screen_name, tweet_id, img)
            except Exception as e:
                print(e)
            return True
        else:
            return False 

def stream(): 
    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
    listener = StreamListener(api=tweepy.API(wait_on_rate_limit=True)) 
    streamer = tweepy.Stream(auth=auth, listener=listener)
    print("Tracking: " + str(WORDS))
    streamer.filter(track=WORDS)
