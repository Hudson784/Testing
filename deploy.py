from flask import Flask, jsonify
import json
from flask import render_template 
#Import the necessary methods from tweepy library

app = Flask(__name__)

@app.route('/')
def index():
    tweets_data = []
    tweet = ''
    tweets_data_path = 'twitter_data.txt.'
    tweets_file = open(tweets_data_path, "r")
    for line in tweets_file:
        tweet += line
        tweets_data.append(tweet)
    return jsonify(tweet) 
    #render_template('home.html', records = tweets_data)