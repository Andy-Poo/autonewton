#!/bin/bash

# sample slackbot token.
# use the token you assigned on Slack.
export SLACK_BOT_TOKEN=xoxb-12345678901-123456789012-xabcd01234ABCD0000000000

# get the Python virtualenv
. ./newton/bin/activate

export PYTHONPATH='.:newton/lib/python2.7/site-packages'

/usr/bin/python -u newton.py
