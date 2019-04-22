from __future__ import print_function
import tweepy
import json
import MySQLdb 
from dateutil import parser
from flask import Flask, jsonify, request, render_template, redirect, url_for, session, g, flash, abort

from userstream import streamUserRequest, trackTweet
from streaming import stream

from trends import getTrends
import twitter_tools as tt

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

consumer_key = 'uWrEWX2bhsMtN8hnpd12HjMfl'
consumer_secret= 'bdcvgAI6xRTYvoHJeNf1nkDsl9oDylOkJr1gqkwXEasY3qK1EF'
callback = 'https://stark-savannah-30879.herokuapp.com/callback'

import uuid
import hashlib

def register_user(username): 
    db=MySQLdb.connect(host=HOST, user=USER, passwd=PASSWD, db=DATABASE, charset="utf8")
    cursor = db.cursor()
    query = "SELECT * FROM Users WHERE username = %s"
    session.pop('user', None)
    try:
        cursor.execute(query, ([username]))
        cursor.close()
        db.commit()
        db.close()
        print("Passed")
        return True
    except MySQLdb.IntegrityError: 
        print("Failed")
        cursor.close()
        db.commit()
        db.close()
        return False 

def store_user(username, password, email): 
    db=MySQLdb.connect(host=HOST, user=USER, passwd=PASSWD, db=DATABASE, charset="utf8")
    cursor = db.cursor()
    query = "INSERT INTO Users (username, password, email, img) VALUES (%s, %s, %s, %s)"
    img = "https://www.lifewire.com/thmb/mpNFwf_VNbIj5vZNLbufvgmVlyU=/494x495/filters:fill(auto,1)/Screen-Shot-2013-03-23-at-3.00.33-PM-56a99ba73df78cf772a8d6ae.png"
    try:
        cursor.execute(query,(username, password, email, img))
        session['user'] = username
        g.user = username
        cursor.close()
        db.commit()
        db.close()
        return True
    except MySQLdb.IntegrityError: 
        cursor.close()
        db.commit()
        db.close()
        return False 

def hash_password(password):
    salt = uuid.uuid4().hex
    return hashlib.sha256(salt.encode() + password.encode()).hexdigest() + ':' + salt

def check_password(hashed_password, user_password):
    password, salt = hashed_password.split(':')
    return password == hashlib.sha256(salt.encode() + user_password.encode()).hexdigest()

@app.route('/auth')
def auth():
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret, callback)
    url = auth.get_authorization_url()
    print("URL", url)
    session['request_token'] = auth.request_token
    return redirect(url)

@app.route('/callback')
def twitter_callback():
    request_token = session['request_token']
    del session['request_token']
    
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret, callback)
    auth.request_token = request_token
    verifier = request.args.get('oauth_verifier')
    auth.get_access_token(verifier)
    session['token'] = (auth.access_token, auth.access_token_secret)
    return redirect('/app')

def update_profile_image(screen_name, img):
    db=MySQLdb.connect(host=HOST, user=USER, passwd=PASSWD, db=DATABASE, charset="utf8")
    cursor = db.cursor()
    query = "UPDATE Users SET img = %s WHERE username = %s"
    cursor.execute(query, (img, screen_name))
    db.commit()
    db.close()
    cursor.close()

def request_auth(): 
    token, token_secret = session['token']
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret, callback)
    auth.set_access_token(token, token_secret)
    api = tweepy.API(auth)
    return api

def if_user_exist(username):
    db=MySQLdb.connect(host=HOST, user=USER, passwd=PASSWD, db=DATABASE, charset="utf8")
    cursor = db.cursor()
    query = "SELECT * FROM Users WHERE username = %s"
    cursor.execute(query, ([username]))
    results = cursor.fetchall()
    if not results:
        cursor.close()
        db.commit()
        db.close()
        return False
    cursor.close()
    db.commit()
    db.close()
    return True

@app.route('/app')
def request_twitter():
    token, token_secret = session['token']
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret, callback)
    auth.set_access_token(token, token_secret)
    api = tweepy.API(auth)
    User = api.me()
    g.user = User.screen_name
    if if_user_exist(User.screen_name):
        update_profile_image(User.screen_name, User.profile_image_url_https)
    session.pop('user', None)
    session['user'] = User.screen_name
    g.user = User.screen_name
    Trends = getTrends("USA")
    return render_template("tracking_user_tweets.html", user = User.screen_name, trends = Trends)

#If the user calls the link directly
@app.route('/search/<name>', methods =['GET', 'POST'])
def get(name):
    person = tt.twitter(name)
    timeline = person['timeline']
    user = person
    return render_template("search_user.html", user = person, timeline = timeline)

#If the link is called via a form 
@app.route('/search/', methods =['POST'])
def search_user(): 
    if request.method == 'POST':
        name = request.form["search_user_on_twitter"]
        person = tt.twitter(name)
        if not person:
            return redirect(url_for('display_timeline'))
        else:
            timeline = person['timeline']
            user = person
            return render_template("search_user.html", user = person, timeline = timeline)
    return redirect(url_for('display_timeline'))

def authenticate(username, password):
    db=MySQLdb.connect(host=HOST, user=USER, passwd=PASSWD, db=DATABASE, charset="utf8")
    cursor = db.cursor()
    cursor.execute("SELECT * FROM Users")
    data = cursor.fetchall()
    for user in data:
        if user[1] == username:
           if check_password(user[2], password):
               cursor.close()
               db.commit()
               db.close()
               return True
    cursor.close()
    db.commit()
    db.close()
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
            query = "SELECT * FROM twitter"
            cursor.execute(query)
            timeline = cursor.fetchall() 
            session['user'] = username
            g.user = username
            Trends = getTrends("USA")
            cursor.close()
            db.close()
            return render_template("tracking_user_tweets.html", records = timeline, user = username, trends = Trends) 
        else:
            return render_template("login.html")
    return render_template("login.html")

@app.before_request
def before_request(): 
    g.user = None
    if 'user' in session: 
        g.user = session['user']

def get_g_user():
    return g.user

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
        password =hash_password(password)
        if register_user(username):
           if store_user(username, password, email):
                current_trends = getTrends("USA")
                return render_template("tracking_user_tweets.html", user = username, trends = current_trends)
        return render_template("login.html", error = "Username already exists") 
    else:
        return render_template("login.html")

@app.route('/track_tweet', methods=['POST'])
def track_tweet():
    if getsession()!= None: 
        if request.method == 'POST':
            track_word = request.form["track_tweet"]
            if track_word not in banned:
                trackTweet(track_word)
            return redirect(url_for('get_user_timeline'))
    return redirect(url_for('login'))

@app.route('/load_user_timeline', methods=['GET'])
def get_user_timeline(): 
    db=MySQLdb.connect(host=HOST, user=USER, passwd=PASSWD, db=DATABASE, charset="utf8")
    cursor = db.cursor()
    cursor.execute("SELECT created_at, screen_name, text, img, id FROM tweets")
    user_records = cursor.fetchall()  
    cursor.close()
    db.commit()
    db.close() 
    return render_template("tweets.html", records = user_records, user = getsession())

@app.route('/update_tweet_page', methods =['GET'])
def get_update_tweet_page(): 
    return render_template("update.html")

@app.route('/get_tweet_details', methods=['POST'])
def get_tweet_details():
    update_id = request.form["get_tweet_id"]
    if update_id != None:
        db=MySQLdb.connect(host=HOST, user=USER, passwd=PASSWD, db=DATABASE, charset="utf8")
        cursor = db.cursor()
        query = "SELECT * FROM tweets WHERE id = %s"
        cursor.execute(query, ([update_id]))
        tweet_details = cursor.fetchall()
        cursor.close()
        db.commit()
        db.close()
        if not tweet_details:
            return redirect(url_for('get_update_tweet_page'), error = "ID does not exist")
        return render_template("update_tweet_details.html", records = tweet_details, user = getsession())
    return redirect(url_for('get_update_tweet_page'), error="ID Field Cannot Be Blank")

@app.route('/update_tweet_from_form', methods=['POST'])
def update_tweet(): 
    if getsession() != None:
        tweet_id = request.form["edit_ID"]
        screen_name = request.form["edit_screen_name"]
        text = request.form["edit_tweet"]
        db=MySQLdb.connect(host=HOST, user=USER, passwd=PASSWD, db=DATABASE, charset="utf8")
        cursor = db.cursor()
        cursor.execute("SELECT text, id, screen_name FROM tweets")
        data = cursor.fetchall()
        screen_name = getsession()
        if tweet_id in data and data:
            query = "UPDATE tweets SET text = %s WHERE screen_name = %s AND id = %s"
            cursor.execute(query, (text, screen_name, tweet_id))
            cursor.execute("SELECT created_at, screen_name, text, img FROM tweets")
            records = cursor.fetchall() 
            cursor.close()
            db.commit()
            db.close()
            return render_template("tweets.html", records = records)
    return redirect(url_for('login'))

@app.route('/delete_user_timeline', methods=['POST'])
def delete_user_timeline():
    db=MySQLdb.connect(host=HOST, user=USER, passwd=PASSWD, db=DATABASE, charset="utf8")
    cursor = db.cursor()
    cursor.execute("TRUNCATE TABLE tweets")
    data = cursor.fetchall() 
    cursor.close()
    db.commit()
    db.close()
    return render_template("tweets.html", records = data, delete = "Your timeline was cleared", user = getsession())

@app.route('/tracktweets', methods=['GET','POST']) 
def track_tweets():
    if request.method == 'POST': 
        track_word_1 = request.form["trending_1"]
        track_word_2 = request.form["trending_2"]
        if track_word_1 not in banned:
            if track_word_2 not in banned:  
                streamUserRequest(track_word_1, track_word_2)
                return redirect(url_for('get_user_timeline'))
    else:
        word = "USA"
        trends = getTrends(word)
        return render_template('tracking_user_tweets.html', user = getsession(), trends = trends)

@app.route('/delete_tweet<tweet_id>', methods=['GET', 'POST'])
def delete_tweet(tweet_id): 
    api = request_auth()
    User = api.me()
    db=MySQLdb.connect(host=HOST, user=USER, passwd=PASSWD, db=DATABASE, charset="utf8")
    cursor = db.cursor()
    if User.screen_name == getsession():
        try:
            api.destroy_status(tweet_id)
            query = "DELETE FROM twitter WHERE tweet_id = %s"
            cursor.execute(query, ([tweet_id]))
            query = "DELETE FROM tweets WHERE tweet_id = %s"
            cursor.execute(query, ([tweet_id]))
        except tweepy.TweepError as e:
            print(e)
    cursor.close()
    db.commit()
    db.close()
    return display_timeline()

#This app route deletes the entire timeline's database 
@app.route('/deletetimeline', methods=['POST'])
def delete_timeline(): 
    db=MySQLdb.connect(host=HOST, user=USER, passwd=PASSWD, db=DATABASE, charset="utf8")
    cursor = db.cursor()
    cursor.execute("TRUNCATE TABLE twitter")
    data = cursor.fetchall() 
    cursor.close()
    db.commit()
    db.close()
    return render_template("timeline.html", records = data, status = True, user = getsession())

def post_to_twitter(api,post): 
    User = api.me()
    try:
        status = api.update_status(status = post)
        return status
    except tweepy.TweepError as e:
        print(e)
        return None

#This app route takes the tweet the user enterred and adds it to the timeline & Twitter if logged in 
#This route stores to both the user's database and the timeline database  
@app.route("/createtweet", methods=['POST'])
def create_tweet():
    error = 'You must be logged in to post'
    if getsession() != None:
        screen_name = getsession()
        tweet = request.form['tweet']
        api = request_auth()
        User = api.me()
        db=MySQLdb.connect(host=HOST, user=USER, passwd=PASSWD, db=DATABASE, charset="utf8")
        cursor = db.cursor()
        if screen_name == User.screen_name:
           status = post_to_twitter(api, tweet)
           if status != None:
               img = User.profile_image_url_https
               insert_query = "INSERT INTO twitter (screen_name, text, tweet_id, img, created_at) VALUES(%s, %s,%s, %s, %s)"
               cursor.execute(insert_query, (screen_name, tweet, status.id_str, img, status.created_at))
               insert_query = "INSERT INTO tweets (screen_name, text, tweet_id, img, created_at) VALUES(%s, %s, %s, %s, %s)"
               cursor.execute(insert_query, (screen_name, tweet, status.id_str, img, status.created_at))
        else:  
            insert_query = "SELECT img FROM Users WHERE username = %s"
            cursor.execute(insert_query, ([screen_name]))
            img = cursor.fetchall()
            img = str(img[0])
            print(type(img))
            insert_query ="INSERT INTO twitter (screen_name, text, img) VALUES(%s, %s, %s)"
            cursor.execute(insert_query, (screen_name, tweet, img))
            insert_query = "INSERT INTO tweets (screen_name, text, img) VALUES(%s, %s, %s)"
            cursor.execute(insert_query, (screen_name, tweet, img))
        cursor.execute("select * from twitter order by id desc") 
        data = cursor.fetchall() 
        cursor.close()
        db.commit()
        db.close()
        error = None
        return render_template("timeline.html", records = data, error = error, user = getsession())
    return render_template("timeline.html", error = error, user = getsession())

#This app route takes the information enterred by the user and then pulls from the twitter api 
#Tracks the tweets specified by the user
@app.route('/searchtweets', methods=['GET', 'POST'])
def search_tweets_for_user(): 
    if request.method == 'POST': 
        criteria = request.form['criteria']
        if criteria not in banned:
            streamUserRequest(criteria, 'school')
            return redirect(url_for('load_user_tweets'))
    else: 
          return redirect(url_for('display_timeline'))

#This app route is responsible for loading the user tweets from the database
@app.route('/loadusertweets', methods= ['GET', 'POST'])
def load_user_tweets():
    db=MySQLdb.connect(host=HOST, user=USER, passwd=PASSWD, db=DATABASE, charset="utf8")
    cursor = db.cursor()
    query = "select * from tweets WHERE screen_name = %s"
    cursor.execute(query, ([g.user]))
    data = cursor.fetchall() 
    cursor.close()
    db.close()
    user = g.user
    return render_template("timeline.html", records = data, user = user)

#This app route is responsible for loading more tweets to the timeline
@app.route('/loadtimeline', methods=['GET'])
def getTweets():
    stream()
    return redirect(url_for('display_timeline'))

@app.route('/', methods=['GET'])
def redirect_login(): 
    return redirect(url_for('login'))

@app.route('/user_timeline', methods=['GET'])
def user_timeline(word1, word2): 
    streamUserRequest(word1, word2)
    return display_timeline() 

@app.route('/timeline&<page>')
def display_timeline_with_page(page):
    display = True
    db=MySQLdb.connect(host=HOST, user=USER, passwd=PASSWD, db=DATABASE, charset="utf8")
    cursor = db.cursor()
    if(int(page) <= 1):
        offset = int(1)
    else: 
        value = (int(page)*1) - ((int(page)*1) - 1)
        stop = 5 * ((int(page)*1) -  1)
        offset = stop + value
    limit = 5
    query = "select * from twitter order by id desc LIMIT %s OFFSET %s"
    cursor.execute(query, (limit, offset))
    records = cursor.fetchall() 
    cursor.close()
    db.close()
    return render_template("timeline.html", records = records, display = display, user = getsession())
 
@app.route('/timeline')
def display_timeline():
    return redirect("/timeline&1")

@app.route('/load_user_table<user>', methods=['GET', 'POST'])
def load_user_table(user):
    db=MySQLdb.connect(host=HOST, user=USER, passwd=PASSWD, db=DATABASE, charset="utf8")
    cursor = db.cursor()
    cursor.execute("SELECT * FROM tweets WHERE screen_name ="+ user)
    user_records = cursor.fetchall()  
    cursor.close()
    db.close()
    return render_template("tweets.html", records = user_records)

@app.route('/search_database', methods=['GET', 'POST'])
def search_database_for_tweets(): 
    if request.method == 'POST': 
        criteria = request.form['criteria']
        if criteria != None:
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
                return render_template("timeline.html", records = data, error = True, user = getsession())
    else:
        return redirect(url_for('display_timeline'))

@app.route('/search_database_for_user', methods=['POST'])
def search_database_for_user(): 
    screen_name = request.form["search_user_in_database"]
    db=MySQLdb.connect(host=HOST, user=USER, passwd=PASSWD, db=DATABASE, charset="utf8")
    cursor = db.cursor()
    query = "SELECT * FROM twitter WHERE screen_name = %s" 
    cursor.execute(query, ([screen_name]))
    data = cursor.fetchall()
    cursor.close()
    db.close()
    return render_template("timeline.html", records = data,user = getsession())
