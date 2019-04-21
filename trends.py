# -*- coding: utf-8 -*-
import tweepy
import json

#Autenticações
access_token = '1117652982475239424-TqGEsktbN74s0OGG6IqKKkXUArnSCi'
access_token_secret  = 'Xtf4rLv3z0N6nHt7yJvYsYPOjZwEC45N3oqRhKo87XVdb'
consumer_key = 'uWrEWX2bhsMtN8hnpd12HjMfl'
consumer_secret= 'bdcvgAI6xRTYvoHJeNf1nkDsl9oDylOkJr1gqkwXEasY3qK1EF'

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)

# Where On Earth ID for Brazil is 23424768.
BRAZIL_WOE_ID = 23424768
UNITED_STATES = 2458410

brazil_trends = api.trends_place(UNITED_STATES)
trends = json.loads(json.dumps(brazil_trends, indent=1))

def getTrends(country): 
    if country == "USA":
        print("Getting USA trends...")
        USA = api.trends_place(UNITED_STATES)
        trends = json.loads(json.dumps(USA, indent=1))
    return trends

for trend in trends[0]["trends"]:
	print (trend["name"])
