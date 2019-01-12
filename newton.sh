#!/bin/bash

# this is the token you will get from Slack to authenticate with the bot on your channel
# edit it and change it to your installation
export SLACK_BOT_TOKEN="xoxb-12345678901-123456789012-xabcd01234ABCD0000000000"

# these are the API keys specific to your installation
export WEATHER_API_KEY="somehexadecimalstring"

# get the Python virtualenv
. ./newton/bin/activate

export PYTHONPATH='.:newton/lib/python2.7/site-packages'

/usr/bin/python -u newton.py
