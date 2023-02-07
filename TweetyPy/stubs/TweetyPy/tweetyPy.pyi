from PIL import Image
from _typeshed import Incomplete
from enum import Enum
from typing import Optional

class CountryID(Enum):
    UK: int
    USA: int
    CANADA: int
    BRAZIL: int
    GEMANY: int
    MEXICO: int

class TweetyPy:
    logger: Incomplete
    chosen_topic: str
    tweets: Incomplete
    API_key: Incomplete
    API_secret: Incomplete
    AI_token: Incomplete
    AI_secret: Incomplete
    twitter_api: Incomplete
    def __init__(self, API_key: str, API_secret: str, AI_token: str, AI_secret: str) -> None: ...
    def generate_tweet(self, country_id: CountryID) -> str: ...
    def generate_wordcloud(self) -> Image.Image: ...
    def send_tweet(self, tweet: str, image: Optional[Image.Image] = ...) -> None: ...

def run_tweetyPy() -> None: ...
