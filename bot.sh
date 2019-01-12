#!/bin/bash

# This script is usually run from a cron job and redirects all
# output to a log file. This is useful to capture diagnostics.
# The newton.py script can read this log file and return the
# results to the user via the "!bot log" command.
# The "!bot clear" command will truncate this log file.
# A suggested crontab entry could look like:
# * * * * * /home/andy/newton/bot.sh > /tmp/crontab.log 2>&1
# which will restart the bot at the top of every minute
# if it crashes.

# Change "andy" to the username of the account running this bot
/bin/ps -U andy -f | /bin/grep -q "[n]ewton.sh"
if [ $? -ne 0  ]; then
	cd ~/newton
        # put the log file where you want it
	#./newton.sh > /tmp/bot.log 2>&1 &
	./newton.sh >> /home/andy/log/bot.log 2>&1 &
fi
