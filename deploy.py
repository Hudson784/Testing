from flask import Flask 

app = Flask(__name__)


@app.route('/')
def index(): 
    return '<h1> Web Project Members </h1> <br <h1> Hudson, Chantel, Kmani, Maya </h1>'