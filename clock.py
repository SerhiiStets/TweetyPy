# -*- coding: utf-8 -*-
from apscheduler.schedulers.blocking import BlockingScheduler
from TweetyPy.tweetyPy import tweetyPy_run

scheduler = BlockingScheduler()


@scheduler.scheduled_job('interval', minutes=60 * 4)
def timed_job() -> None:
	"""Runs TweetyPy every 4 hours."""
	tweetyPy_run()


scheduler.start()