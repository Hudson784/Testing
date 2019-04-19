from flask import Flask, jsonify, request, render_template
import json
from flask_mysqldb import MySQL
#Import the necessary methods from tweepy library

app = Flask(__name__)
app.config['MYSQL_HOST'] = 'remotemysql.com'
app.config['MYSQL_USER'] = 'pPEd17bA5B'
app.config['MYSQL_PASSWORD'] = 'qIhMyEEHjc'
app.config['MYSQL_DB'] = 'pPEd17bA5B'

mysql = MySQL(app)

@app.route('/')
def index():
    tweets_data = []
    tweets_data_path = 'twitter_data.txt'
    tweets_file = open(tweets_data_path, 'r')
    for line in tweets_file:
        if len(line) > 1:
            data = json.loads(line)
            tweets_data.append(data)
    return render_template('home.html', records = tweets_data)

@app.route('/test', methods=['GET', 'POST'])
def form():
    if request.method == "POST":
        details = request.form
        firstName = details['fname']
        lastName = details['lname']
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO MyUsers(firstName, lastName) VALUES (%s, %s)", (firstName, lastName))
        mysql.connection.commit()
        cur.close()
        return 'success'
    return render_template('home.html')

@app.route('/about', methods=['GET']) 
def get(): 
    return render_template('about.html')

if __name__ == '__main__':
    app.run()


