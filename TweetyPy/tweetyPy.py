#!/usr/bin/env python
# -*- coding: utf8 -*-
"""
TweetyPy

Machine learning app that can create own tweets and word clouds by learning from user statuses
or top trend tweets using Markov chain

@Author: Serhii Stets
"""

import re
import sys
import tweepy
import markovify
import socket
import logging

from api import *
import numpy as np
from os import path
from PIL import Image
from tweepy import TweepError
from wordcloud import WordCloud


def internet_connection(host: str="8.8.8.8", port: int=53, timeout: int=3) -> bool:
    """
    Checking internet connection

    Host: 8.8.8.8 (google-public-dns-a.google.com)
    OpenPort: 53/tcp
    Service: domain (DNS/TCP)

    Parameters
    ----------
    host : str
    port : int
    timeout : int

    Returns
    -------

    """
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except Exception as e:
        logging.exception(e)
        return False


# Menu check for y or n
def y_or_n(s):
    if s == "y" or s == "n" or s == "Y" or s == "N":
        return True
    else:
        return False


# Check if input isn't number
def is_int(s):
    try:
        int(s)
        return True
    except ValueError:
        return False


# Print main menu
def print_top(array):
    print("q ) Quit")
    print("0 ) Acc average tweet")
    for i in range(15):
        print(str(i + 1) + " ) " + array[i]["name"]) if i <= 8 else print(str(i + 1) + ") " + array[i]["name"])


# Creating word cloud
def word_cloud_generator(api, request):
    d = path.dirname(__file__)
    text = open(path.join(d, 'data.txt'), encoding="utf8").read()

    # load image
    imagePath = "cloud.png"

    # read the mask image
    twitter_mask = np.array(Image.open(path.join(d, "twitter_logo.png")))

    wc = WordCloud(background_color="white", mask=twitter_mask, contour_width=3,
                   contour_color='steelblue')

    # generate word cloud
    wc.generate(text)

    # store to file
    wc.to_file(path.join(d, "cloud.png"))

    # Text for tweet
    status = "Most popular words\n" + request

    # Send the tweet with image
    api.update_with_media(imagePath, status)


#  Creating and posting tweet
def tweet_generator(api, request, key):
    # Post settings
    def settings_acc(tweet, header, text_model):
        print("\n" + header + tweet)
        print("\nDo you want to post this? (y/n)")

        s = input()

        # Check input parameter
        while not y_or_n(s):
            print("\nWrong parameter--\n")
            print(header + tweet)
            print("\nDo you want to post this? (y/n)")
            s = input()

        if s == "y" or s == "Y":
            # Post tweet
            api.update_status(header + tweet)
            print("\nDONE\n")
            tweetyPy()
        else:
            print("\nDo you want to create new sentence? (y/n)")
            s = input()
            # Check input parameter
            while not y_or_n(s):
                print("\nWrong parameter--\n")
                print(header + tweet)
                print("\nDo you want to create new sentence? (y/n)")
                s = input()

            if s == "y" or s == "Y":
                tweet = text_model.make_short_sentence(280 - len(header))
                settings_acc(tweet, header, text_model)
        tweetyPy()

    # Post settings
    def settings_topic(tweet):
        print('________________\n')

        print("\nDo you want to add #? (y/n)")
        print(tweet)

        s = input()
        # Check input parameter
        while not y_or_n(s):
            print("\nWrong parameter--\n")
            print(tweet)
            print("\nDo you want to add #? (y/n)")
            s = input()

        if s == "y" or s == "Y":
            # Post tweet
            print("Write your #")
            htag = input()
            tweet = tweet + " " + htag

        print(tweet)

        # TODO edit tags if wrong

        print("\nDo you want to post this? (y/n)")

        s = input()

        # Check input parameter
        while not y_or_n(s):
            print("\nWrong parameter--\n")
            print(tweet)
            print("\nDo you want to post this? (y/n)")
            s = input()

        if s == "y" or s == "Y":
            # Post tweet
            api.update_status(tweet)

        else:
            print("\nDo you want to create new sentence? (y/n)")
            s = input()
            # Check input parameter
            while not y_or_n(s):
                print("\nWrong parameter--\n")
                print(tweet)
                print("\nDo you want to create new sentence? (y/n)")
                s = input()

            if s == "y" or s == "Y":
                tweet = text_model.make_short_sentence(280)
                settings_topic(tweet)

        print("\nGenerate word cloud? (y/n)")

        s = input()

        # Check input parameter
        while not y_or_n(s):
            print("\nWrong parameter--\n")
            print(tweet)
            print("\nGenerate word cloud? (y/n)")
            s = input()

        if s == "n" or s == "N":
            tweetyPy()
        else:
            # Generate word cloud
            word_cloud_generator(api, request)

        print('________________')
        tweetyPy()

    # Get raw text as string.
    with open("data.txt", encoding="utf8") as f:
        text = f.read()

    # Build the model
    text_model = markovify.Text(text)

    if key == "acc":
        # Tweet info header
        header_text = "Average @" + request + " tweet:\n\n"
        # Print randomly-generated sentence of no more than 280 characters for tweet
        result = text_model.make_short_sentence(280 - len(header_text))
        settings_acc(result, header_text, text_model)
    else:
        # Print randomly-generated sentence of no more than 280 characters for tweet
        result = text_model.make_short_sentence(280)
        settings_topic(result)


def acc_tweet(api):
    # Check if username exists
    def check_acc(account):
        try:
            # q1q0q1q1q3 - Example of non-existent username
            # Check if exist
            api.get_user(account)
            return account

        except TweepError:
            print("\nWrong username------\n")
            print(account)
            print("Want to try again? (y/n)")
            s = input()

            # Check input parameter
            while not y_or_n(s):
                print("\nWrong parameter--")
                print("\nWant to try again? (y/n)")
                s = input()

            if s == "n" or s == "N":
                tweetyPy()
            else:
                print("\nPrint username:")
                account = input()
                check_acc(account)

    # Create tweet with username
    def create_tweet(user):
        with open('data.txt', 'a', encoding="utf8") as file:
            # Clear file
            open('data.txt', 'w').close()
            for status in tweepy.Cursor(api.user_timeline, id=user).items():
                # Checking for retweets, replies and other
                if (not status.retweeted) and ('RT @' not in status.text) and (not status.text.startswith("@")):
                    result = status.text

                    # Can't work without it, not a joke
                    result = result.encode('utf8')
                    result = result.decode('utf8')

                    end_text = str(result)

                    # Deleting all urls in tweet
                    end_text = re.sub(r'http\S+', '', end_text, flags=re.MULTILINE)
                    print(end_text)
                    print('\n')
                    # Write tweet to the file
                    file.write(end_text + "\n")
        tweet_generator(api, user, "acc")

    # Ask for user name
    print("Print username:")
    user = input()

    # Go to create tweet, check_acc is checking if username exists
    create_tweet(check_acc(user))


def topic_tweet(api, names, num):
    # Check what # do you choose
    while not is_int(num) or int(num) > 15:
        print("\nWrong parameter--\n")
        print_top(names)
        num = input()

    request = names[int(num) - 1]['name']

    print("\n" + request)
    print('________________ \n')

    # Open file for record
    with open('data.txt', 'a', encoding="utf8") as file:
        # Clear file
        open('data.txt', 'w').close()
        last_tweet = ""
        for tweet in tweepy.Cursor(api.search, q=request + " -filter:retweets", result_type="mixed", lang="en").items(
                2500):
            print(tweet.text)

            text = tweet.text

            # Check for repeated tweets
            if text == last_tweet:
                continue
            else:
                last_tweet = text

            # Can't work without it, not a joke
            text = text.encode('utf8')
            text = text.decode('utf8')

            end_text = str(text)

            # Deleting all urls in tweet
            end_text = re.sub(r'http\S+', '', end_text, flags=re.MULTILINE)

            print('\n')

            # Write tweet to the file
            file.write(end_text + "\n")

    # Create tweet
    tweet_generator(api, request, "topic")


def tweetyPy() -> None:
    auth = tweepy.OAuthHandler(API_key, API_secret)
    auth.set_access_token(AT_token, AT_secret)
    auth.secure = True
    api = tweepy.API(auth)
    names = api.trends_place(id=23424977)[0]['trends']

    # Clear file
    open('data.txt', 'w').close()

    # Print top trends
    print_top(names)

    num = input()

    # Quit
    if num == "q":
        sys.exit()
    # Create average account tweet
    elif num == "0":
        acc_tweet(api)
    else:
        topic_tweet(api, names, num)


if __name__ == "__main__":
    # Checking for internet connection
    if internet_connection():
        tweetyPy()
    else:
        print("No internet connection")
