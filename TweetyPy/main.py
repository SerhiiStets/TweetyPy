#!/usr/bin/env python
# -*- coding: utf8 -*-

import tweepy
import markovify
from api import *
import re


def tweet_generator(api):
    # Get raw text as string.
    with open("data.txt", encoding="utf8") as f:
        text = f.read()

    # Build the model.
    text_model = markovify.Text(text)

    # Print randomly-generated sentence of no more than 280 characters for twitter
    for i in range(1):
        result = text_model.make_short_sentence(280)
        #api.update_status(result)
        print(result)

    print('________________')


def main():
    auth = tweepy.OAuthHandler(API_key, API_secret)
    auth.set_access_token(AT_token, AT_secret)
    auth.secure = True
    api = tweepy.API(auth)
    names = api.trends_place(id=23424977)[0]['trends']

    open('data.txt', 'w').close()
    print(names[0]['name'])
    print('________________ \n')
    request = names[0]['name']

    with open('data.txt', 'a', encoding="utf8") as the_file:
        open('data.txt', 'w').close()
        last_tweet = ""
        for tweet in tweepy.Cursor(api.search, q=request + "-filter:retweets", result_type="mixed", lang="en").items(1):
            print(tweet.text)

            text = tweet.text

            # check for repeated tweets
            if text == last_tweet:
                continue
            else:
                last_tweet = text

            # Can't work without it, not a joke
            text = text.encode('utf8')
            text = text.decode('utf8')

            end_text = str(text)

            # deleting all urls
            end_text = re.sub(r'http\S+', '', end_text, flags=re.MULTILINE)

            print('\n')
            the_file.write(end_text + "\n")

    tweet_generator(api)

if __name__ == "__main__":
    main()
