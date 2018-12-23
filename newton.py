#!/usr/bin/env python

'''
autonewton - a smart bot that runs on the Slack platform
Copyright (C) 2018  Andy Poo

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License (LGPL) as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

See <http://www.gnu.org/licenses/> for a description of the LGPL.

Website: <http://autonewton.com/>
'''

import sys
reload(sys)  # Reload does the trick!
sys.setdefaultencoding('UTF8')

debug = False

import pprint
import os
import time
import re
import subprocess
import math

try:
    from slackclient.slackclient import SlackClient
except ImportError as e:
    print e

try:
    import wikipedia
except ImportError as e:
    print e

appName = os.path.basename(sys.argv[0])

from wikipedia import Wikipedia
from wiki2plain import Wiki2Plain

import eliza

import urllib2

time_format = '%a %Y/%m/%d %H:%M:%S'

rules = \
r"""
*(1)* Bullying and baiting people is not tolerated.
If you do this, you might get kicked from the chatroom by a moderator.
If you continue to cause trouble, we may revoke your account.

*(2)* Foul language *IS* tolerated. We cannot stop you from swearing, nor do we care if you swear.
Some words are considered offensive and if you use them, you will get a warning from Slackbot
that the word is considered offensive.

*(3)* We encourage people to welcome the newcomer to the room.
We want new people to come back and they may be in need of assistance, so please focus on them.
We consider the newcomer the most important person in the room.

*(4)* Talking behind people's back is discouraged.
Unlike Parachat, when you logout, you can see what was said in the room when you return, simply by scrolling back.
THE CHATROOM HISTORY IS NEVER DELETED.
If you said something negative about someone, don't be surprised if they become angry with you.

*(5)* Discussion about religion and politics often causes arguments.
We won't stop you from discussing it but if it regresses into an argument, don't be surprised if you get kicked.
We recommend you avoid these subjects.

*(6)* *BEING TRIGGERED*: `if you are being triggered LEAVE`.
We're not all going to change what we're talking about to satisfy YOU.

*(7)* We will not call the authorities on people who are in crisis, even if they say they are going to harm themselves.
This chat room is not a professional service.

*(8)* We believe we can all act as adults, so please use some manners and respect when speaking with other chatters.
We should be able to police ourselves.

This website is not affiliated with any religion.
We are not a Christian chat room. We do not care what you believe.
People with no beliefs are welcome too.
"""

bot_help = r"""
Hi! I'm your bot, Newton!

I can perform several functions for you.
These are my commands:

!help - Get this page.
!rules - Get a list of the chat room rules

!bot - This command.
    !bot ping - See if the bot is alive.
    !bot date - See what time it is where the bot is located.

!google, !g - Get the 3 top links for a subject.
!bing, !b - Get the 3 top links for a subject.
!g what is a bitcoin?

!wiki, !w - Get a Wikipedia article on a subject.
!w san francisco

!math, !calc - Perform a math calculation.

!units, !u - Do unit conversions.
    !u ounce gram
    !u tempC(-24.5) tempF

!distance, !dist -
    Distance in a straight line between two towns.
    !dist ottawa;melbourne
    !dist new york; los angeles

!hug, !hugs - Hug someone.
    !hug cher
    !hug @cher

!date - Get the date and time where you are located.
    !date @jommie - Get the date and time where Jommie lives.

!mobile - Information on getting Slack on mobile devices.
!apps - Information on getting Slack on desktop computers.
!beta - Information on getting the Beta releases of Slack.

!motd - Get the Message Of The Day.

!happy - Get Happy Message.

Commands must begin with an exclamation mark in the first column.
For tips about this chat program see:
http://autonewton.com/index.php/chat
"""

responses = {
'rules': rules,
'mobile': r"Slack has a great mobile app for iPhones and Androids. For iPhones, go the Apple App Store. For Androids, go to the Google Play Store. Both apps are free downloads. You can also get them here: https://slack.com/downloads/",
'apps': r"You can download the free Slack app for your computer at: https://slack.com/downloads/",
'beta': "These are the beta versions of Slack where you can try out the latest features.\nThis version may have bugs and if you find any please contact Slack support by typing, /feedback <your message> at the start of a new line.\n\nWindows: https://slack.com/beta/windows\n\nmacOS: https://slack.com/beta/osx\n\nAndroid: https://slack.com/beta/android\n\niOS (iPhones and iPads): https://slack.com/beta/ios\n\nLinux: https://slack.com/downloads/linux"
}

def google(query, youtube=False):
    from BingWebSearchv7 import Bing
    return Bing(query, youtube=youtube)


from xml.sax.saxutils import escape, unescape
# escape() and unescape() takes care of &, < and >.
html_escape_table = {
    '"': "&quot;",
    "'": "&apos;",
    " ": "%20"
}
html_unescape_table = {v:k for k, v in html_escape_table.items()}

def html_escape(text):
    return escape(text, html_escape_table)

def html_unescape(text):
    return unescape(text, html_unescape_table)


def wiki(query):
    #print 'wiki: query=', query
    result = None
    pageid = None

    #lang = 'simple'
    lang = 'en'
    wiki = Wikipedia(lang)

    try:
        content = wiki.article(query)
    except Exception as e:
        print >> sys.stderr, e
        content = None

    if content:
        #pp = pprint.PrettyPrinter(indent=4)
        #pp.pprint(content)

        try:
            d = eval(content)
            q = d['query']
            #print 'wiki: q=', q
            s = q['search']
            if s:
                s = s[0]
                #print '*'*40
                #print 'wiki: s=', s
                #print '*'*40
                pageid = s['pageid']
                #print 'wiki: pageid=', pageid
                #title = s['title']
                snippet = s['snippet']
                wiki2plain = Wiki2Plain(snippet)
                snippet = wiki2plain.text
                snippet = html_unescape(snippet)
                #pp = pprint.PrettyPrinter(indent=4)
                #pp.pprint(snippet)
                stripped = snippet.replace('\\\\', '\\')
                string = eval("u'" + stripped + "'")
                result = string
        except Exception as e:
                print 'wiki: Error:', e
                return (None, None)

    return (result, pageid)


def wikiurl(pageid):
    if debug: print 'wikiurl: pageid=', pageid

    url = 'https://en.wikipedia.org/w/api.php?action=query&prop=info&pageids=%d&inprop=url&format=json' % pageid
    #print 'wikiurl: url=', url
    #lang = 'simple'
    lang = 'en'
    wiki = Wikipedia(lang)

    try:
        result = wiki.fetch(url)
        content = result.read()
    except Exception as e:
        print >> sys.stderr, e
        content = None

    if content:
        #print 'wikiurl: content='
        #pp = pprint.PrettyPrinter(indent=4)
        #pp.pprint(content)

        try:
            d = eval(content)
            #print 'wikiurl: d=', d
            #count = 0
            #for c in d:
            #    print 'count=', count
            #    print 'c=', c
            #    count += 1
            #print 'count=', count
            q = d['query']
            #print 'wikiurl: q=', q
	    url = q['pages'][str(pageid)]['fullurl']
        except Exception as e:
                print 'wikiurl: Error:', e
                return None

    #print 'wikiurl: url=', url
    return url


def weather(query):
    if debug: print 'weather: query=', query
    url = html_escape('https://api.openweathermap.org/data/2.5/weather?q=%s' % query)
    url += '&appid=f9e3e8a64d9635fea2203b5e7bc373eb'
    #print 'weather: url=', url
    content = urllib2.urlopen(url).read()
    #print 'weather: content=', content
    lon = 0
    lat = 0
    description = ''
    temp = 0
    pressure = 0
    temp_min = 0
    temp_max = 0
    visibility = 0
    wind_speed = 0
    name = ''
    country = ''
    sunrise = 0
    sunset = 0
    try:
        values = eval(content)
        lon = values['coord']['lon']
        lat = values['coord']['lat']
        description = values['weather'][0]['description']
        temp = values['main']['temp']
        pressure = values['main']['pressure']
        temp_min = values['main']['temp_min']
        temp_max = values['main']['temp_max']
        visibility = values['visibility']
        wind_speed = values['wind']['speed']
        name = values['name']
        country = values['sys']['country']
        sunrise = values['sys']['sunrise']
        sunset = values['sys']['sunset']
    except Exception as e:
        print 'weather: Error:', e
        #return str(e)
    K = -273.15
    temp_c = temp + K
    temp_f = temp_c*9.0/5.0 + 32
    temp_min_c = temp_min + K
    temp_min_f = temp_min_c*9.0/5.0 + 32
    temp_max_c = temp_max + K
    temp_max_f = temp_max_c*9.0/5.0 + 32
    pressure_m = pressure/10.0
    pressure_i = pressure * 0.02953
    visibility_m = visibility/1000.0
    visibility_i = visibility_m * 0.621371
    wind_speed_m = wind_speed
    wind_speed_i = wind_speed_m * 0.621371
    #time_t = time.time()
    #diff = time.localtime(time.mktime(time_t)) - time.gmtime(time.mktime(time_t))
    #time_midnite = (t[0], t[1], t[2], 0, 0, 0, t[6], t[7], t[8],)
    #time_0 = (t[0], t[1], t[2], t[3], t[5], 0, t[6], t[7], t[8],)
    #diff = time.localtime(time_0) - time.localtime(time_midnite)
    #sunrise_t = time.localtime(sunrise)
    #sunrise = time.strftime('%H:%m', sunrise_t)
    result = 'Weather for %s, %s\n' % (name, country)
    result += '='*20 + '\n'
    result += 'Latitude=%.2f\n' % lat
    result += 'Longitude=%.2f\n' % lon
    result += 'Current Temperature: %.1fC/%.1fF\n' % (temp_c, temp_f)
    result += 'Minimum: %.1fC/%.1fF\n' % (temp_min_c, temp_min_f)
    result += 'Maximum: %.1fC/%.1fF\n' % (temp_max_c, temp_max_f)
    result += 'Pressure: %.1fkPa/%.1f inches\n' % (pressure_m, pressure_i)
    result += 'Visibility: %.1fkm/%.1f miles\n' % (visibility_m, visibility_i)
    result += 'Wind Speed: %.1fkm/%.1f miles\n' % (wind_speed_m, wind_speed_i)
    result += '%s\n' % description
    #result += 'Sunrise: %s\n' % sunrise
    return (result, lat, lon)


pat1 = re.compile(r"<@(.*)>")

# instantiate Slack client
slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))
# starterbot's user ID in Slack: value is assigned after the bot starts up
starterbot_id = None

# constants
RTM_READ_DELAY = 1 # 1 second delay between reading from RTM
MENTION_REGEX = "^<@(|[WU].+?)>(.*)"

def parse_bot_commands(slack_events):
    """
        Parses a list of events coming from the Slack RTM API to find bot commands.
        If a bot command is found, this function returns a tuple of command and channel.
        If its not found, then this function returns None, None.
    """
    for event in slack_events:
        if debug: print 'parse_bot_commands:'
        pp = pprint.PrettyPrinter(indent=4)
        if debug: pp.pprint(event)
        if event["type"] == "message" and not "subtype" in event:
            text = event["text"].encode('ascii', errors='ignore')
            if debug: print 'text=', text
            user = event["user"]
            if debug: print 'user=', user
            channel = event["channel"]
            if debug: print 'channel=', channel
            user_id, message = parse_direct_mention(text, user, users)
            pp = pprint.PrettyPrinter(indent=4)
            #print "message="
            #pp.pprint(message)
            if user_id == starterbot_id:
                message = eliza.analyze(message)
                print "eliza message='%s'" % message
                return message, channel
            else:
                try:
                    message = parse_command(text, user, users)
                except Exception as e:
                    print >> sys.stderr, e
                    message = None
                if message is not None:
                    return message, channel
    return None, None

def parse_direct_mention(message_text, user, users):
    """
        Finds a direct mention (a mention that is at the beginning) in message text
        and returns the user ID which was mentioned. If there is no direct mention, returns None
    """
    matches = re.search(MENTION_REGEX, message_text)
    if debug: print 'parse_direct_mention: matches=', matches
    # the first group contains the username, the second group contains the remaining message
    return (matches.group(1), matches.group(2).strip()) if matches else (None, None)

def parse_command(text, user, users):
    """
        Finds a bang command
    """
    if debug: print 'parse_command: text, user=', text, user
    result = None
    if re.search("^!", text):
        words = text.split()
        tokens = []
        for word in words:
            w = word.strip()
            if w:
                tokens.append(w)
        command = tokens[0][1:].lower()
        if command in responses:
            result = responses[command]
        elif command == 'help':
            result = bot_help
        elif command == 'bot':
            if len(tokens) < 2:
                result = bot_help
            else:
                bot_command = tokens[1]
                if bot_command == 'ping':
                    result = "I'm alive!"
                elif bot_command == 'quit':
                    sys.exit(0)
                elif bot_command == 'date':
                    result = time.strftime(time_format)
        elif command in ('bing', 'b', 'google', 'g', 'youtube', 'y'):
            query = ' '.join(tokens[1:])
            youtube = command in ('youtube', 'y')
            #urls = google(query, youtube=youtube)
            #result = ('\n' + '='*10 + '\n').join(urls)
            result = google(query, youtube=youtube)
        elif command in ('wiki', 'w'):
            query = ' '.join(tokens[1:])
            (result, pageid) = wiki(query)
            if result:
                url = wikiurl(pageid)
                if url:
                    result = url + '\n' + result
        elif command in ('hug', 'hugs'):
            token = tokens[1]
            m = pat1.search(token)
            if m:
                user_id = m.group(1)
                nick = find_nick(user_id, users)
            else:
                nick = token
            result = "((( " + nick + " )))"
        elif command == 'date':
            user_id = user
            if len(tokens) > 1:
                token = tokens[1]
                m = pat1.search(token)
                if m:
                    user_id = m.group(1)
            result = find_time(user_id, users)

        elif command in ('math', 'calc'):
            try:
                expression = ' '.join(tokens[1:])
                result = str(eval(expression))
            except Exception as e:
                print >> sys.stderr, e
                result = str(e)
        elif command in ('weather', 'we'):
            query = ' '.join(tokens[1:])
            (result, lat, lon)  = weather(query)
        elif command in ('distance', 'dist'):
            queryargs = ' '.join(tokens[1:])
            query = queryargs.split(';')
            query1 = query[0]
            query2 = query[1]
            if debug: print 'distance: query1=', query1
            if debug: print 'distance: query2=', query2
            (result, lat1, lon1)  = weather(query1)
            if debug: print 'distance: query1: result=', result
            if debug: print 'distance: query1: lat1', lat1
            if debug: print 'distance: query1: lon1', lon1
            (result, lat2, lon2)  = weather(query2)
            if debug: print 'distance: query2: result=', result
            if debug: print 'distance: query2: lat2', lat2
            if debug: print 'distance: query2: lon2', lon2
            #result = 'Latitude=%.2f, Longitude=%.2f' % (
                    #(lat2 - lat1), (lon2 - lon1))
            result = ''
            R = 6371e3      # metres
            phi1 = math.radians(lat1)
            phi2 = math.radians(lat2)
            delta_phi = math.radians(lat2 - lat1)
            delta_lambda = math.radians(lon2 - lon1)
            a = math.sin(delta_phi/2) * math.sin(delta_phi/2) + \
                math.cos(phi1) * math.cos(phi2) * \
                math.sin(delta_lambda/2) * math.sin(delta_lambda/2)
            c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
            dist = R * c
            result += '\ndistance = %.0f km (%.0f miles)' % (
                    dist/1000.0, dist/1.609344/1000.0)
        elif command in ('units', 'unit', 'u'):
            #query = ' '.join(tokens[1:])
            query = ''
            for token in tokens[1:]:
                query += '"' + token + '"' + ' '
            #print 'units: query=', query
            try:
               result = subprocess.check_output(
                   '/usr/bin/units -q %s' % query,
                   stderr=subprocess.STDOUT,
                   shell=True)
            except Exception as e:
                print 'units:', e
                result = 'units syntax error'
            #print 'units: result=', result

    return result

def find_nick(user_id, users):
    nick = "autonewton"
    ids = []
    for u in users:
        ids.append(u["id"])
    if user_id in ids:
        for u in users:
            if user_id == u["id"]:
                nick = u["profile"]["display_name"]
                break
    return nick

def find_time(user_id, users):
    result = ""
    ids = []
    for u in users:
        ids.append(u["id"])
    if user_id in ids:
        for u in users:
            if user_id == u["id"]:
                tz_offset = u["tz_offset"]
                time_t = time.time()
                time_gm = time.gmtime(time_t)
                time_local = time.localtime(time_t)
                localtime_t = time.mktime(time_local)
                user_t = int(time_t) + int(tz_offset)
                time_user = time.gmtime(user_t)
                tz_diff = int(user_t - time_t)
                tz_hours = tz_diff / (60*60)
                sign = ''
                if tz_diff >= 0:
                    sign = '+'
                zone = '(UTC%s%.1f)' % (sign, tz_hours) 
                result = time.strftime(time_format, time_user)
                result += ' ' + zone
                break
    return result

def handle_command(command, channel):
    """
        Executes bot command if the command is known
    """
    # Default response is help text for the user
    #default_response = "COMMAND UNKNOWN"

    response = command

    # Finds and executes the given command, filling in response
    #response = None
    # This is where you start to implement more commands!

    # Sends the response back to the channel
    slack_client.api_call(
        "chat.postMessage",
        channel=channel,
        text=response# or default_response
    )

def slack():
    global starterbot_id, users
    if slack_client.rtm_connect(with_team_state=False):
        print("Starter Bot connected and running!")
        # Read bot's user ID by calling Web API method `auth.test`
        starterbot_id = slack_client.api_call("auth.test")["user_id"]

        if debug: print 'slack: starterbot_id=', starterbot_id
        user_list = slack_client.api_call("users.list")
        pp = pprint.PrettyPrinter(indent=4)
        if debug: pp.pprint(user_list)
        users = []
        for u in user_list["members"]:
            users.append(u)
        if debug: pp.pprint(users)

        while True:
            if debug: print 'slack: parse bot commands'
            command, channel = parse_bot_commands(slack_client.rtm_read())
            if debug: print 'slack: command, channel=', command, channel
            if command:
                handle_command(command, channel)
            time.sleep(RTM_READ_DELAY)
    else:
        print("Connection failed. Exception traceback printed above.")

if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.ERROR)
    slack()
