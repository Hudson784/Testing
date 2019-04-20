from __future__ import print_function
import tweepy
import json
import MySQLdb 
from dateutil import parser
from flask import Flask, jsonify, request, render_template, redirect, url_for, session, g

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
banned = ['sex', 'porn', 'pussy', 'vagina', 'bitch', 'sexy', 'slut']

app = Flask(__name__)
app.secret_key = '#d\xe9X\x00\xbe~Uq\xebX\xae\x81\x1fs\t\xb4\x99\xa3\x87\xe6.\xd1_'

def authenticate(username, password):
    db=MySQLdb.connect(host=HOST, user=USER, passwd=PASSWD, db=DATABASE, charset="utf8")
    cursor = db.cursor()
    cursor.execute("SELECT * FROM Users")
    data = cursor.fetchall()
    for user in data:
        if user[1] == username and user[2] == password:
            return True
    return False 

@app.route('/login', methods=['GET', 'POST'])
def login(): 
    if request.method == 'POST':
        return redirect(url_for('verify_user'))
    else:
        return render_template("login.html")

#This app routes verifies the user attempting to login
@app.route('/verify_user', methods=['GET', 'POST'])
def verify_user( ): 
    if request.method == 'POST':
        username = request.form["login_username"]
        password = request.form["login_password"]
        if authenticate(username, password):
            session.pop('user', None) 
            db=MySQLdb.connect(host=HOST, user=USER, passwd=PASSWD, db=DATABASE, charset="utf8")
            cursor = db.cursor()
            query = "SELECT * FROM " + username
            cursor.execute(query)
            userdata = cursor.fetchall() 
            session['user'] = username
            return render_template("tracking_user_tweets.html", records = userdata, user = username) 
        else:
            return render_template("login.html")
    return render_template("login.html")

@app.route('/protected', methods=['GET', 'POST'])
def protected():
    if g.user:
        return 'well we here'
    return 'hard lucks bredda'

@app.before_request
def before_request(): 
    g.user = None
    if 'user' in session: 
        g.user = session['user']

def getsession(): 
    if 'user' in session:
        return session['user']
    return None

@app.route('/logout', methods=['GET', 'POST']) 
def logout(): 
    session.pop('user', None)
    g.user = None
    return render_template("login.html")

#This app route creates a user or fetches the create user login page
@app.route('/create_user', methods=['GET', 'POST'])
def create_user(): 
    if request.method == 'POST':
        username = request.form["create_username"]
        password = request.form["create_password"]
        email = request.form["create_email_address"]
        db=MySQLdb.connect(host=HOST, user=USER, passwd=PASSWD, db=DATABASE, charset="utf8")
        cursor = db.cursor()
        query = "CREATE TABLE IF NOT EXISTS " + username + " (id int(11) NOT NULL AUTO_INCREMENT, name varchar(45), password varchar(45), tweet varchar(150), PRIMARY KEY (id));"
        cursor.execute(query)
        query = "INSERT INTO Users (username, password, email) VALUES (%s, %s, %s)"
        cursor.execute(query,(username, password, email))
        query = "SELECT * from " +username
        cursor.execute(query)
        userdata = cursor.fetchall()
        cursor.close()
        db.commit()
        db.close()
        return render_template("tracking_user_tweets.html", records = userdata)
    else:
        return render_template("login.html")

@app.route('/tracktweets', methods=['GET','POST']) 
def track_tweets():
    if request.method == 'POST': 
        track_word_1 = request.form["trending_1"]
        track_word_2 = request.form["trending_2"]
        if track_word_1 not in banned:
            if track_word_2 not in banned:  
                streamUserRequest(track_word_1, track_word_2)
                return redirect(url_for('load_user_table')) 
    else:
        return render_template('tracking_user_tweets.html', user = getsession())

#This app route deletes the entire timeline's database 
@app.route('/deletetimeline', methods=['POST'])
def delete_timeline(): 
    db=MySQLdb.connect(host=HOST, user=USER, passwd=PASSWD, db=DATABASE, charset="utf8")
    cursor = db.cursor()
    cursor.execute("TRUNCATE TABLE twitter")
    data = cursor.fetchall() 
    cursor.close()
    db.close()
    return render_template("timeline.html", records = data, status = True)

#This app route takes the tweet the user enterred and adds it to the timeline 
#This route stores to both the user's database and the timeline database  
@app.route("/createtweet", methods=['POST'])
def create_tweet():
    error = 'You must be logged in to post'
    if getsession() != None:
        screen_name = session['user']
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
        error = None
        return render_template("timeline.html", records = data, error = error)
    return render_template("timeline.html", error = error)

#This app route takes the information enterred by the user and then pulls from the twitter api 
#Tracks the tweets specified by the user
@app.route('/searchtweets', methods=['GET', 'POST'])
def search_tweets_for_user(): 
    if request.method == 'POST': 
        criteria = request.form['criteria']
        if criteria not in banned:
            streamUserRequest(criteria, 'school')
            return redirect(url_for('load_user_table'))
    else: 
          return redirect(url_for('timeline'))

#This app route is responsible for loading the user tweets from the database
@app.route('/loadusertweets', methods= ['GET', 'POST'])
def load_user_table():
    db=MySQLdb.connect(host=HOST, user=USER, passwd=PASSWD, db=DATABASE, charset="utf8")
    cursor = db.cursor()
    cursor.execute("select * from tweets order by id desc") 
    data = cursor.fetchall() 
    cursor.close()
    db.close()
    user = g.user
    return render_template("timeline.html", records = data, user = user)

#This app route is responsible for loading more tweets to the timeline
@app.route('/loadtimeline', methods=['GET'])
def getTweets():
    stream()
    return redirect(url_for('timeline'))

@app.route('/', methods=['GET'])
def redirect_login(): 
    return redirect(url_for('login'))

@app.route('/timeline', methods=['GET'])
def timeline():
    stream()
    db=MySQLdb.connect(host=HOST, user=USER, passwd=PASSWD, db=DATABASE, charset="utf8")
    cursor = db.cursor()
    cursor.execute("select * from twitter order by id desc") 
    data = cursor.fetchall() 
    cursor.close()
    db.close()
    return render_template("timeline.html", records = data)

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
            return render_template("timeline.html", records = data, error = True)
    else:
        return redirect(url_for('timeline'))
