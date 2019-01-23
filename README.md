# autonewton
SYNOPSIS

A smart bot for chat rooms. Currently works on the Slack platform.


FEATURES

1. The autonewton bot lives on a channel in a Slack chat room of your choice.

2. autonewton listens for text entered into the channel by members.

3. autonewton is triggered by a line beginning with an exclamation mark, eg:

!help

We refer to these as "commands" and typically say, "Bang help".
"Bang" being the loud sound made by the old Teletype machines when
you hit that key.

4. autonewton can also talk English. You can talk to him,
by refering to him with the direct mention, eg:

@newton are you happy?

I have added a lot of funny responses to autonewton.
(I've tried to keep it PG LOL)

The file eliza.py implements it. It's a mess and I apologize for the crappy code.


All the commands and features are documented clearly inside newton.py,
so I won't waste time by repeating all the details here.


KEY FEATURES

!search : DuckDuckGo web search lookups.

!bing : Bing (Google) lookups (drops the top 3 matches into the chat window and cites them).

!wiki : Wikipedia lookups (drops the citation into the chat window).

!youtube : YouTube lookups (pastes into the chat window the top 3 videos).

!weather : Get the weather for any location in the world by city name.

!members, !member : Get the list of members or details for a specific member.

!date @member : Get the date and time of the time zone the given member is located.

!unit : Unit conversions. (Handy if you have Americans in the room).

!dt : Date and time difference calculator.

!distance : Calculate the straight line distance between any two towns on Earth.

!math : A simple math calculator that can also interpret Reverse-Polish notation (yeah I'm a geek).

!joke : Jokes. Get a Dad joke, one liner.

!lyric : Lyrics. Get the lyrics for any song by artist and song title

!cal : Calendar. Drop a UNIX-style "cal" calendar for any month of any year into the chat window.

And there are a few simple game-like features too.


INSTALLATION

1. In a terminal, execute:
git clone https://github.com/Andy-Poo/autonewton

2. Go into the extracted autonewton subdirectory and modify the file,
newton.sh and change the line:

export SLACK_BOT_TOKEN=xoxb-12345678901-123456789012-xabcd01234ABCD0000000000

To the token you assigned your bot in Slack in your room to your channel.

If you have any API keys you want to use for some of your own services,
please add them here.
The BING_SEARCH_KEY is used for Bing web searches.
The WEATHER_API_KEY is used by https://api.openweathermap.org/

If you intend to run this from a cron job, then you may also need to
modify, bot.sh


OFFICIAL AUTONEWTON WEBSITE

http://autonewton.com

This is a site that supports people who have mental illness or
know someone who does and is looking for help.

We also have a lot of laughs and the autonewton bot is one way
we have some fun.

If you think you have a mental illness or close to someone who does,
please come and join us.

The Slack chat room used by autonewton.com was used to develop
the autonewton bot and was tested by real members in a real chat room.

My thanks to my members of the autonewton.com site for their patience
in testing the bot and their suggestions for improvements and for
finding lots of bugs.

- Andy Poo

-------------------------------------------------------------------------------

RELEASE NOTES

3.2
- Add better exception handling and ensure bot can always terminate.
- Get Bing and Youtube lookups working again.
- Fixes to the Animal Game.

3.1
- Added the members command.

3.0
- Added background processing of web requests in a background thread
to prevent the bot from hanging if a web server does not respond.
- Added the Animal Game.

2.1
- Fixes to Eliza.

2.0
- First official release of autonewton.
- Changed code to object-oriented and added docstrings.
