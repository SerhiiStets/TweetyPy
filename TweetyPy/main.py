#!/usr/bin/env python
# -*- coding: utf8 -*-

import re
import sys
import tweepy
import markovify
import socket
import logging

from api import *
from os import path
from tweepy import TweepError
from wordcloud import WordCloud
import matplotlib.pyplot as plt


def internet_connection(host="8.8.8.8", port=53, timeout=3):
    """
    Host: 8.8.8.8 (google-public-dns-a.google.com)
    OpenPort: 53/tcp
    Service: domain (DNS/TCP)
    """
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except Exception as e:
        logging.exception(e)
        return False


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


def word_cloud_generator(api, request):
    d = path.dirname(__file__)
    text = open(path.join(d, 'data.txt'), encoding="utf8").read()
    wc = WordCloud(width=1920, height=1080, background_color="white", collocations=False).generate(text)

    plt.figure(figsize=(20, 10))  # specify the size of the figure

    plt.imshow(wc, interpolation="nearest", aspect="auto")
    plt.axis("off")
    plt.tight_layout(pad=0)
    plt.savefig('cloud.png', facecolor='white', bbox_inches='tight')

    # load image
    imagePath = "cloud.png"
    status = "Most popular words\n" + request

    # Send the tweet
    api.update_with_media(imagePath, status)


def tweet_generator(api, request):
    # Post settings
    def settings(tweet):
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
                settings(tweet)

        print("\nGenerate word cloud? (y/n)")

        s = input()

        # Check input parameter
        while not y_or_n(s):
            print("\nWrong parameter--\n")
            print(tweet)
            print("\nGenerate word cloud? (y/n)")
            s = input()

        if s == "n" or s == "N":
            main()
        else:
            # Generate word cloud
            word_cloud_generator(api, request)

        print('________________')
        main()

    # Get raw text as string.
    with open("data.txt", encoding="utf8") as f:
        text = f.read()

    # Build the model
    text_model = markovify.Text(text)

    # Print randomly-generated sentence of no more than 280 characters for tweet
    result = text_model.make_short_sentence(280)
    settings(result)


def acc_tweet(api):
    # Post settings
    def settings(tweet, header, text_model):
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
                settings(tweet, header, text_model)
        main()

    # Check if username exists
    def check_acc(account):
        try:
            # q1q0q1q1q3 - Example of non-existent username
            # Check if exist
            api.get_user(account)
            # Go to create tweet
            create_tweet(account)
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
                main()
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

        with open("data.txt", encoding="utf8") as f:
            text = f.read()

        # Build the model
        text_model = markovify.Text(text)

        # Tweet info header
        header_text = "Average @" + user + " tweet:\n\n"
        # Print randomly-generated sentence of no more than 280 characters for tweet
        result = text_model.make_short_sentence(280 - len(header_text))
        settings(result, header_text, text_model)

    print("Print username:")
    user = input()
    check_acc(user)


def print_top(array):
    print("q ) Quit")
    print("0 ) Acc average tweet")
    for i in range(15):
        print(str(i + 1) + " ) " + array[i]["name"]) if i <= 8 else print(str(i + 1) + ") " + array[i]["name"])


def main():
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
    tweet_generator(api, request)


if __name__ == "__main__":
    if internet_connection():
        main()
    else:
        print("No internet connection")
