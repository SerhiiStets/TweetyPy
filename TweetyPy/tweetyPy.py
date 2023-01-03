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
        self.twitter_auth = tweepy.OAuthHandler(API_key, API_secret)
        self.twitter_auth.set_access_token(AI_token, AI_secret)
        self.twitter_auth.secure = True
        self.twitter_api = tweepy.API(self.twitter_auth)
        self._check_authentication_to_twitter()

    def _check_authentication_to_twitter(self) -> None:
        """Trying to get user @twitter from id to see if auth worked. Raise error if not."""
        try:
            self.twitter_api.get_user(user_id=783214)
        except tweepy.errors.Unauthorized:
            raise tweepy.TweepyException("Incorrect API keys, authentication error.")

    def get_trending_topics_by_country(self, country_id: CountryID) -> list[dict]:
        """Returns a list of top trending topics in twitter for given country."""
        return self.twitter_api.get_place_trends(id=country_id.value)[0]['trends']

    def get_tweets_by_topic(self, topic_name: str) -> list[str]:
        """Return an array of tweets by given topic with removed url links in them."""
        tweets_iterator = tweepy.Cursor(self.twitter_api.search_tweets, q=f"{topic_name} -filter:retweets",
                                        result_type="mixed", lang="en").items(2500)
        return [re.sub(r'https\S+', '', tweet.text) for tweet in tweets_iterator]

    @staticmethod
    def generate_tweet(tweets: list[str]) -> str:
        """Retuens newly create tweet from received list of tweets."""
        if not tweets:
            raise IndexError("Tweets list is empty, no tweets were given.")
        text_model = markov_generate(tweets)
        return text_model.make_short_sentence(280)

    @staticmethod
    def generate_wordcloud(tweets: str) -> Image.Image:
        """Generating wordcloud with given topic and tweets."""
        current_directory = path.dirname(__file__)
        # Reads the mask image of twitter logo to numpy array
        twitter_mask = array(Image.open(path.join(current_directory, "twitter_logo.png")))
        new_word_cloud = WordCloud(background_color="white", mask=twitter_mask, contour_width=5,
                                   contour_color='steelblue')
        new_word_cloud.generate(tweets)
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


def run_tweetyPy():
    """Starting point for server and local runs of TweetyPy."""
    logging.basicConfig(level=logging.INFO, stream=sys.stdout, format="%(asctime)s - %(levelname)s - %(message)s")
    try:
        API_key = getenv("API_key", "optional-default")
        API_secret = getenv("API_secret", "optional-default")
        AI_token = getenv("AT_token", "optional-default")
        AI_secret = getenv("AT_secret", "optional-default")

        tweetyPy = TweetyPy(API_key, API_secret, AI_token, AI_secret)
        logging.info("Successfully Authenticated to Twitter API!")

        trending_topics_list = tweetyPy.get_trending_topics_by_country(CountryID.USA)

        random_topic = trending_topics_list[randint(0, 14)]['name']
        logging.info(f"The chosen topic is {random_topic}")

        tweets = tweetyPy.get_tweets_by_topic(random_topic)
        logging.info(f"{len(tweets)} tweets were read")

        generated_tweet = tweetyPy.generate_tweet(tweets)
        logging.info(f"Generated tweet - {generated_tweet}")

        if randint(0, 3) == 3:
            # For roughly every 4th tweet we want to generate wordcloud for it
            wordcloud_image = tweetyPy.generate_wordcloud(' '.join(tweets))
            tweetyPy.send_tweet(f"Most popular words\n {random_topic}", wordcloud_image)
            logging.info("Generated wordcloud image.")

        tweetyPy.send_tweet(generated_tweet)
        logging.info("Tweet is now live!")
    except Exception as e:
        logging.critical(e)


if __name__ == "__main__":
    run_tweetyPy()
