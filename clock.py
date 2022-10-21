# -*- coding: utf-8 -*-
from TweetyPy.tweetyPy import run_tweetyPy
from apscheduler.schedulers.blocking import BlockingScheduler

scheduler = BlockingScheduler()


@scheduler.scheduled_job('interval', minutes=60 * 8)
def timed_job() -> None:
    """Runs TweetyPy every 8 hours."""
    run_tweetyPy()


scheduler.start()
