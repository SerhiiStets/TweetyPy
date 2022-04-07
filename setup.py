# -*- coding: utf8 -*-
from setuptools import setup, find_packages

with open("README.md", 'r') as f:
    long_description = f.read()

setup(
   name='TweetyPy',
   version='1.0',
   description='Machine learning app that can create own tweets and word clouds by learning from user statuses '
               'or top trend tweets using Markov chain',
   license="MIT",
   long_description=long_description,
   author='Serhii Stets',
   author_email='stets.serhii@gmail.com',
   packages=['TweetyPy'],
)
