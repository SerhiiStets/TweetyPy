# TweetyPy

<a href="https://twitter.com/_TweetyPy_" target="_blank">
<img alt="Twitter Follow" src="https://img.shields.io/twitter/follow/_TweetyPy_?style=social">
</a>

<br><br>
**Tweetypy** is a Machine learning app that can create own tweets by learning from user posts or top trend tweets using *Markov chain*. It can also create wordclouds based upon received twitter data. You can check him out at @_TweetyPy_ <br />

## What can it do?
### Create tweets with a certain topic from Twitter's trending page
<div>
  <img src="https://imgur.com/QAOnIhP.png" width="500"/>
</div>

### Create tweets based upon specific user's history
<div>
  <img src="https://imgur.com/GLZ9ajB.png" width="500"/>
</div>

### Create word clouds by tweets topic
<div>
  <img src="https://imgur.com/lF3TzWM.png" width="500"/>
</div>

## Installation

Clone this repo and install requirements.txt
```
$ git clone https://github.com/SerhiiStets/TweetyPy.git
$ pip install -r /path/to/requirements.txt
```
**NOTE: TweetyPy uses Twitter API to send and read tweets, the keys are stored on the server**<br><br>
To run the bot you need to specify your own keys. To get Twitter API tokens please check out - [How to get access to the Twitter API](https://developer.twitter.com/en/docs/twitter-api/getting-started/getting-access-to-the-twitter-api)
```python
auth = tweepy.OAuthHandler(os.getenv("API_key", "optional-default"), os.getenv("API_secret", "optional-default"))
auth.set_access_token(os.getenv("AT_token", "optional-default"), os.getenv("AT_secret", "optional-default"))
```
Right now TweetyPy uses [Heroku config vars](https://devcenter.heroku.com/articles/config-vars) to get and store these API tokens
## Usage
1. Change API variables with your Twitter API keys. Check out **Installation** step to see where you can get Twitter API tokens
```python
auth = tweepy.OAuthHandler(your_API_key, your_API_secret)  # Your API keys here
auth.set_access_token(your_AT_token, your_AT_secret)  # Your AI keys here
```
2. Run `tweetyPy.py` file in `TweetyPy` folder
```
$ cd TweetyPy
$ python tweetyPY.py
```
## Heroku
Bot is now running on Heroku. Using `clock.py` it reads and posts tweets every 4 hours

## Contributing

All bugs, feature requests, pull requests, feedback, etc., are welcome. [Create an issue](https://github.com/SerhiiStets/TweetyPy/issues/)


## License
[MIT License](https://choosealicense.com/licenses/mit/)
