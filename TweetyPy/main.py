#!/usr/bin/env python
# -*- coding: utf8 -*-

import tweepy
import markovify
from api import *
import re
import sys


def y_or_n(s):
    if s == "y" or s == "n" or s == "Y" or s == "N":
        return True
    else:
        return False


def is_int(s):
    try:
        int(s)
        return True
    except ValueError:
        return False


def tweet_generator(api):
    # Get raw text as string.
    with open("data.txt", encoding="utf8") as f:
        text = f.read()

    # Build the model.
    text_model = markovify.Text(text)

    # Print randomly-generated sentence of no more than 280 characters for twitter
    result = text_model.make_short_sentence(280)
    print(result)
    print("Do you want to post this (y/n)")

    s = input()

    while not y_or_n(s):
        print("\nWrong parameter--\n")
        print(result)
        print("Do you want to post this (y/n)")
        s = input()

    if s == "n" or s == "N":
        sys.exit()
    else:
        api.update_status(result)

    print('________________')


def print_top(array):
    print("0) Quit")
    for i in range(9):
        print(str(i + 1) + ") " + array[i]["name"])


def main():
    auth = tweepy.OAuthHandler(API_key, API_secret)
    auth.set_access_token(AT_token, AT_secret)
    auth.secure = True
    api = tweepy.API(auth)
    names = api.trends_place(id=23424977)[0]['trends']

    open('data.txt', 'w').close()
    print_top(names)

    num = input()

    while not is_int(num):
        print("\nWrong parameter--\n")
        print_top(names)
        num = input()

    if num == "0":
        sys.exit()

    request = names[int(num) - 1]['name']

    print("\n" + request)
    print('________________ \n')

    with open('data.txt', 'a', encoding="utf8") as file:
        open('data.txt', 'w').close()
        last_tweet = ""
        for tweet in tweepy.Cursor(api.search, q=request + " -filter:retweets", result_type="mixed", lang="en").items(2500):
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
            file.write(end_text + "\n")

    tweet_generator(api)

if __name__ == "__main__":
    main()
