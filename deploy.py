from __future__ import print_function
import tweepy
import json
import MySQLdb 
from dateutil import parser
from flask import Flask, jsonify, request, render_template, redirect, url_for

from userstream import streamUserRequest
from streaming import stream

ACCESS_TOKEN = '1117652982475239424-TqGEsktbN74s0OGG6IqKKkXUArnSCi'
ACCESS_TOKEN_SECRET  = 'Xtf4rLv3z0N6nHt7yJvYsYPOjZwEC45N3oqRhKo87XVdb'
CONSUMER_KEY = 'uWrEWX2bhsMtN8hnpd12HjMfl'
CONSUMER_SECRET = 'bdcvgAI6xRTYvoHJeNf1nkDsl9oDylOkJr1gqkwXEasY3qK1EF'

HOST = 'remotemysql.com'
USER = 'pPEd17bA5B'
PASSWD = 'qIhMyEEHjc'
DATABASE = 'pPEd17bA5B'

app = Flask(__name__)

@app.route('/deletetweets', methods=['POST'])
def delete_tweets(): 
    db=MySQLdb.connect(host=HOST, user=USER, passwd=PASSWD, db=DATABASE, charset="utf8")
    cursor = db.cursor()
    cursor.execute("TRUNCATE TABLE twitter")
    data = cursor.fetchall() 
    cursor.close()
    db.close()
    return render_template("homenew.html", records = data, status = True)

@app.route("/createtweet", methods=['POST'])
def create_tweet(): 
    screen_name = request.form['screen_name']
    tweet = request.form['tweet']
    db=MySQLdb.connect(host=HOST, user=USER, passwd=PASSWD, db=DATABASE, charset="utf8")
    cursor = db.cursor()
    insert_query ="INSERT INTO twitter (screen_name, text) VALUES(%s, %s)"
    cursor.execute(insert_query, (screen_name, tweet))
    cursor.execute("select * from twitter order by id desc") 
    data = cursor.fetchall() 
    cursor.close()
    db.commit()
    db.close()
    return render_template("homenew.html", records = data)

@app.route('/searchtweets', methods=['GET', 'POST'])
def searchUserTweets(): 
    if request.method == 'POST': 
        criteria = request.form['criteria']
        banned = ['sex', 'porn', 'pussy', 'vagina', 'bitch', 'sexy', 'slut']
        if criteria not in banned:
            streamUserRequest(criteria, 'school')
            return redirect(url_for('load_user_table'))
    else: 
          return redirect(url_for('form'))

@app.route('/loadusertweets', methods= ['GET', 'POST'])
def load_user_table():
    db=MySQLdb.connect(host=HOST, user=USER, passwd=PASSWD, db=DATABASE, charset="utf8")
    cursor = db.cursor()
    cursor.execute("select * from tweets order by id desc") 
    data = cursor.fetchall() 
    cursor.close()
    db.close()
    return render_template("homenew.html", records = data)

@app.route('/loadtimeline', methods=['GET'])
def getTweets():
    stream()
    return redirect(url_for('form'))

@app.route('/', methods=['GET'])
def form():
    stream()
    db=MySQLdb.connect(host=HOST, user=USER, passwd=PASSWD, db=DATABASE, charset="utf8")
    cursor = db.cursor()
    cursor.execute("select * from twitter order by id desc") 
    data = cursor.fetchall() 
    cursor.close()
    db.close()
    return render_template("homenew.html", records = data)

@app.route('/search_database', methods=['GET', 'POST'])
def search_database_for_tweets(): 
    if request.method == 'POST': 
        criteria = request.form['criteria']
        banned = ['sex', 'porn', 'pussy', 'vagina']
        if criteria not in banned:
            db=MySQLdb.connect(host=HOST, user=USER, passwd=PASSWD, db=DATABASE, charset="utf8")
            cursor = db.cursor()
            cursor.execute("SELECT created_at, screen_name, text, img,LOCATE(%s,text) FROM twitter WHERE locate(%s,text)>0", (criteria, criteria))
            data = cursor.fetchall() 
            cursor.close()
            db.close() 
            return render_template("tweets.html", records = data)
        else:
            db=MySQLdb.connect(host=HOST, user=USER, passwd=PASSWD, db=DATABASE, charset="utf8")
            cursor = db.cursor()
            cursor.execute("select * from twitter order by id") 
            data = cursor.fetchall() 
            data = list(reversed(data))
            cursor.close()
            db.close()
            return render_template("homenew.html", records = data, error = True)
    else:
        return redirect(url_for('form'))
