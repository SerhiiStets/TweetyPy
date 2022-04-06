# -*- coding: utf8 -*-
"""
TweetyPy

Machine learning app that can create own tweets and word clouds by learning from user statuses
or top trend tweets using Markov chain

@Author: Serhii Stets
"""

import re
import tweepy
import markovify

import numpy as np
from os import path
from PIL import Image
from random import randint
from wordcloud import WordCloud

from api import API_key, API_secret, AT_token, AT_secret


class SendTweet:
    """Send tweets via tweepy."""

    def __init__(self, twitter_api: tweepy.api, tweet: str, image_path: str = ""):
        """Initialise SendTweet.

        Parameters
        ----------
        twitter_api : twitter_api
        tweet : str
        image_path : str
        """
        self.twitter_api = twitter_api
        self.tweet = tweet
        self.image_path = image_path  # Future wordcloud implementation

    def send_text_tweet(self):
        self.twitter_api.update_status(self.tweet)

    def send_text_image_tweet(self):
        self.twitter_api.update_with_media(self.image_path, self.tweet)


class TweetGenerator:
    """Tweet and wordcloud generator."""

    def __init__(self, topic_name: str, tweets: list[str]) -> None:
        """Initialise TweetGenerator.

        Parameters
        ----------
        topic_name : str
            Twitter trends topic's name
        tweets : list[str]
            List of 3000 tweets from topic_name
        """
        self.topic_name = topic_name
        self.tweets = tweets

    def topic_tweet_generator(self) -> str:
        """Generating tweet about trends topic using Markov's chain.

        Returns
        -------
        str
            Final version of the tweet, ready to publish
        """
        text_model = markovify.Text(self.tweets)
        result = text_model.make_short_sentence(len(self.topic_name) - 281)
        return f"{self.topic_name} {result}"

    def wordcloud_generator(self):
        """Generating wordcloud with given topic and tweets."""
        d = path.dirname(__file__)
        twitter_mask = np.array(Image.open(path.join(d, "twitter_logo.png")))  # read the mask image
        wc = WordCloud(background_color="white", mask=twitter_mask, contour_width=3, contour_color='steelblue')
        wc.generate(self.tweets)  # generate word cloud
        wc.to_file(path.join(d, "cloud.png"))
        status = f"Most popular words\n {self.topic_name}"
        raise NotImplementedError


def create_tweet_by_topic(twitter_api: tweepy.api, topics: list, num: int) -> None:
    """Gathering and publishing tweets by chosen topic.

    Parameters
    ----------
    twitter_api
    topics
    num

    Returns
    -------

    """
    topic_name = topics[num]['name']

    print("\n" + topic_name)
    tweets = []
    for tweet in tweepy.Cursor(twitter_api.search_tweets, q=topic_name + " -filter:retweets", result_type="mixed",
                               lang="en").items(3000):
        tweets.append(re.sub(r'https\S+', '', tweet.text))

    generated_text = TweetGenerator(topic_name, tweets)
    new_tweet = SendTweet(twitter_api, generated_text.topic_tweet_generator())
    new_tweet.send_text_tweet()


if __name__ == "__main__":
    auth = tweepy.OAuthHandler(API_key, API_secret)
    auth.set_access_token(AT_token, AT_secret)
    auth.secure = True
    api = tweepy.API(auth)
    topic_names = api.get_place_trends(id=23424977)[0]['trends']  # Getting US based top twitter trends
    print(type(topic_names[0]))
    create_tweet_by_topic(api, topic_names, randint(0, 14))
