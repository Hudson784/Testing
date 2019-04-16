from flask import Flask 
import json
#Import the necessary methods from tweepy library

app = Flask(__name__)


@app.route('/')
def index(): 
    tweets_data = []
    tweets_data_path = 'twitter_data.txt.'
    tweets_file = open(tweets_data_path, "r")
    for line in tweets_file:
        tweet = json.loads(line)
        test = tweet['id']
        print("First line of data: \n")
        print("Tweet ID: ", tweet['id'])
        print("Tweet: ", tweet['text'])
        user = tweet['user']
        print("Name: ", user['name'])
        print("Screen Name: ", user['screen_name'])
        tweets_data.append(tweet)
    return jsonify(tweets_data)