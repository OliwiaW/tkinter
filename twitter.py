# -*- coding: utf-8 -*-
"""
Created on Thu Dec  7 19:26:05 2017

@author: Właściciel
"""

import tweepy
from tweepy import OAuthHandler
import datetime
from urllib.request import urlopen, Request, urlretrieve
from requests import get
import time, json
import re
import shutil

def twitter_authenticate():

    consumer_key = #
    consumer_secret = #
    access_token = #
    access_secret = #
     
    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_secret)
    
    return auth


def search_tweets(query):
    
    auth = twitter_authenticate()
    
    api = tweepy.API(auth)
    tweets = api.search(q=query)

    #tweet_strings = []
    tweet_string = ""
    media_url = ""
    limit = 1
    counter = 0
    
    for tweet in tweets:
        if counter<limit:
            if 'media' in tweet.entities.keys():
                tweet_content = re.sub(r'http[s]?:\/\/.*[\W]*', '', tweet.text, flags=re.MULTILINE) # remove urls
                tweet_content = re.sub(r'@[\w]*', '', tweet_content, flags=re.MULTILINE) # remove the @twitter mentions 
                tweet_content = re.sub(r'RT.*','', tweet_content, flags=re.MULTILINE)  # delete the retweets
     
                tweet_string += str(tweet.created_at) + ", " + tweet.user.location + ", " + tweet.user.screen_name + " : \n"
                tweet_string += tweet_content + "\n"
                tweet_string += '\n\n'
                
                media_url = dict(tweet.entities['media'][0])['media_url']  
                #tweet_strings.append(tweet_string)
            
                counter += 1
    
    urlretrieve(media_url, "image_twitter.png")
#    response = get(media_url, stream=True)
#    with open('image_twitter.png', 'wb') as out_file:
#        shutil.copyfileobj(response.raw, out_file)
#    del response

    return tweet_string

def request_until_succeed(post_url):
    req = Request(post_url)
    success = False
    while success is False:
        try: 
            response = urlopen(req)
            if response.getcode() == 200:
                success = True
        except Exception as e:
            print(e)
            time.sleep(5)
            
            print("Error for URL %s: %s") % (post_url, e)

    return response.read().decode('windows-1250')
    
def format_date(date):
    status_published = datetime.datetime.strptime(date, '%Y-%m-%dT%H:%M:%S+0000')
    status_published = status_published + datetime.timedelta(hours=1)
    status_published = status_published.strftime('%Y-%m-%d %H:%M:%S')
    
    return status_published
    
def facebook():
    
    APP_ID = "147064772594417"
    APP_SECRET = "14b372c2d0b2fa9bc069b6d22b0e6c6b"
    page_id = 'BMW'#'topgear'#'carsloverspoland'
    limit = 1
    counter = 0

    graph_url = "https://graph.facebook.com/" + page_id
    post_args = "/posts/?key=value&access_token=" + APP_ID + "|" + APP_SECRET
    base_fields = "&fields=message,type,source,full_picture"
    post_url = graph_url + post_args +base_fields
    
    result = json.loads(request_until_succeed(post_url))
    
    data = result['data']

    fb_string = ""
        
    for post in data:
        if counter<limit:
            if post['type']=="photo":
                #fb_string += format_date(post['created_time']) + "\n"
                fb_string += '' if 'message' not in post else post['message']
                fb_string += "\n\n"
                
                fb_img = post["full_picture"]
                counter +=1
     
    urlretrieve(fb_img, "image_fb.png")
#    response = get(fb_img, stream=True)
#    with open('image_fb.png', 'wb') as out_file:
#       shutil.copyfileobj(response.raw, out_file)
#    del response
    
    return fb_string
        
#fb_string, fb_img = facebook()
#print(fb_string)
#print("\n\n")
#print(fb_img)
#print("\n\n")
#
#tweet_string, media_url =   search_tweets("cars")  
#print(tweet_string)
#print("\n\n")
#print(media_url)
    
    