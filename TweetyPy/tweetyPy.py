# -*- coding: utf-8 -*-
"""
TweetyPy

Machine learning app that can create own tweets and word clouds by learning from user statuses
or top trend tweets using Markov chain

@Author: Serhii Stets
"""

import re
import sys
import tweepy
import logging

from PIL import Image
from enum import Enum
from numpy import array
from random import randint
from os import path, getenv
from wordcloud import WordCloud
from io import BytesIO, BufferedReader
from markovify import Text as markov_generate


class CountryID(Enum):
    """Twitter id for given country."""
    UK = 23424975
    USA = 23424977
    CANADA = 23424775
    BRAZIL = 23424768
    GEMANY = 23424829
    MEXICO = 23424900


class TweetyPy:
    """TweetyPy implementation class."""

    def __init__(self, API_key: str, API_secret: str, AI_token: str, AI_secret: str) -> None:
        """Initialize TweetyPy object and check for authorization."""
        self.logger = self._create_logger()
        self.chosen_topic = ""
        self.tweets = []
        self.API_key = API_key
        self.API_secret = API_secret
        self.AI_token = AI_token
        self.AI_secret = AI_secret
        self.twitter_api: tweepy.API = self._twitter_authorization()

    def _create_logger(self) -> logging.Logger:
        logger = logging.getLogger('TweetyPy')
        logger.setLevel(level=logging.INFO)
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        return logger

    def _twitter_authorization(self) -> tweepy.API:
        """
        Trying to auth to twitter and get user @twitter from id to see if auth worked.
        Raise error if not.
        """
        try:
            twitter_auth = tweepy.OAuthHandler(self.API_key, self.API_secret)
            twitter_auth.set_access_token(self.AI_token, self.AI_secret)
            twitter_auth.secure = True
            twitter_api = tweepy.API(twitter_auth)
            twitter_api.get_user(user_id=783214)  # Checking auth with real Twitter request
            self.logger.info("Successfully Authenticated to Twitter API!")
            return twitter_api
        except tweepy.errors.Unauthorized:
            self.logger.critical("Incorrect API keys, authentication error.")
            raise tweepy.TweepyException("Incorrect API keys, authentication error.")

    def _get_trending_topics_by_country(self, country_id: CountryID) -> list[dict]:
        """Returns a list of top trending topics in twitter for given country."""
        return self.twitter_api.get_place_trends(id=country_id.value)[0]['trends']

    def _get_tweets_by_topic(self, topic_name: str) -> list[str]:
        """Return an array of tweets by given topic with removed url links in them."""
        tweets_iterator = tweepy.Cursor(self.twitter_api.search_tweets, q=f"{topic_name} -filter:retweets",
                                        result_type="mixed", lang="en").items(2500)
        return [re.sub(r'https\S+', '', tweet.text) for tweet in tweets_iterator]

    def generate_tweet(self, country_id: CountryID) -> str:
        """Generates tweet from random topic for given country."""
        trending_topics_list = self._get_trending_topics_by_country(country_id)
        self.chosen_topic = trending_topics_list[randint(0, 14)]['name']
        self.logger.info(f"The chosen topic is {self.chosen_topic}")
        self.tweets = self._get_tweets_by_topic(self.chosen_topic)
        self.logger.info(f"{len(self.tweets)} tweets were read")
        if not self.tweets:
            raise IndexError("Tweets list is empty, no tweets were given.")
        text_model = markov_generate(self.tweets)
        new_tweet = text_model.make_short_sentence(280)
        self.logger.info(f"Generated tweet - {new_tweet}")
        return new_tweet

    def generate_wordcloud(self) -> Image.Image:
        """Generating wordcloud with given topic and tweets."""
        if not self.tweets:
            raise IndexError("No tweets were parsed from Twitter.")
        str_tweets = ' '.join(self.tweets)
        current_directory = path.dirname(__file__)
        # Reads the mask image of twitter logo to numpy array
        twitter_mask = array(Image.open(path.join(current_directory, "twitter_logo.png")))
        new_word_cloud = WordCloud(background_color="white", mask=twitter_mask, contour_width=5,
                                   contour_color='steelblue')
        new_word_cloud.generate(str_tweets)
        logging.info("Generated wordcloud image.")
        return new_word_cloud.to_image()

    def send_tweet(self, tweet: str, image: Image.Image = None) -> None:
        """
        Post tweet depending on if image was given or not.
        Using BytesIO to save PIL.Image.Image object to memory
        and then sent it as a meadia file to twitter.
        """
        if image:
            bytes_obj = BytesIO()
            image.save(bytes_obj, "PNG")  # saves image to buffer
            # Change the stream position to the given byte offset
            # back to the beginning of the file after writing the initial in memory file
            bytes_obj.seek(0)
            fp = BufferedReader(bytes_obj)  # read obj from buffer
            self.twitter_api.update_status_with_media(tweet, filename="TweetyPy WordClouod", file=fp)
        else:
            self.twitter_api.update_status(tweet)
        self.logger.info("Tweet is now live!")


def run_tweetyPy():
    """Starting point for server and local runs of TweetyPy."""
    API_key = getenv("API_key", "optional-default")
    API_secret = getenv("API_secret", "optional-default")
    AI_token = getenv("AT_token", "optional-default")
    AI_secret = getenv("AT_secret", "optional-default")

    tweetyPy = TweetyPy(API_key, API_secret, AI_token, AI_secret)

    generated_tweet = tweetyPy.generate_tweet(CountryID.USA)

    if randint(0, 3) == 3:
        # For roughly every 4th tweet we want to generate wordcloud for it
        wordcloud_image = tweetyPy.generate_wordcloud()
        tweetyPy.send_tweet(f"Most popular words\n {tweetyPy.chosen_topic}", wordcloud_image)

    tweetyPy.send_tweet(generated_tweet)


if __name__ == "__main__":
    run_tweetyPy()
