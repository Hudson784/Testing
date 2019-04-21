from models import Person
import tweepy
from datetime import datetime, date, time, timedelta

people = []

def twitter(screen_name):
    for person in people:
        if person.screen_name == screen_name:
            return person.__dict__

    api = get_api()

    user = None
    try:
        user = api.get_user(screen_name)
    except tweepy.error.TweepError:
        return {"Error":"Username Not Found"}
    tweets_count = user.statuses_count
    account_created_date = user.created_at
    followers_count = user.followers_count
    days = (datetime.utcnow() - account_created_date).days

    timeline = []
    stop = 20
    for status in tweepy.Cursor(api.user_timeline, screen_name='@'+screen_name).items():
        if stop > 0:
            timeline.append({"text":status._json["text"],"created_at":status._json["created_at"]})
            stop = stop - 1
        else:
            break

    avg = float(tweets_count)/float(days)
    person = Person(screen_name,tweets_count,followers_count,days,timeline,avg)
    people.append(person)
    return person.__dict__

def get_api():
    consumer_key = 'uWrEWX2bhsMtN8hnpd12HjMfl'
    consumer_secret = 'bdcvgAI6xRTYvoHJeNf1nkDsl9oDylOkJr1gqkwXEasY3qK1EF'

    access_token = '1117652982475239424-TqGEsktbN74s0OGG6IqKKkXUArnSCi'
    access_token_secret = 'Xtf4rLv3z0N6nHt7yJvYsYPOjZwEC45N3oqRhKo87XVdb'

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)

    return tweepy.API(auth)
