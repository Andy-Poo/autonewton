#!/usr/bin/env python

"""
newton - a smart bot, like Siri, for Slack chat rooms.
Copyright (C) 2019  Andy Poo

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License (LGPL) as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

See <http://www.gnu.org/licenses/> for a description of the LGPL.
"""

debug = False
info = False

# date and time formats for strptime
formats = [
    '%H:%M',
    '%H:%M:%S',
    '%Y/%m/%d',
    '%y/%m/%d',
    '%m/%d',
    '%d/%m',
    '%Y/%m/%d %H:%M',
    '%Y/%m/%d %H:%M:%S',
    '%y/%m/%d %H:%M',
    '%y/%m/%d %H:%M:%S',
    '%H:%M %Y/%m/%d',
    '%H:%M:%S %Y/%m/%d',
    '%H:%M %y/%m/%d',
    '%H:%M:%S %y/%m/%d',
    '%m/%d',
    '%m/%d/%y',
    '%H:%M %m/%d',
    '%H:%M:%S %m/%d',
    '%H:%M %m/%d/%y',
    '%H:%M:%S %m/%d/%y',
    '%d/%m',
    '%d/%m/%y',
    '%d/%m/%Y',
    '%d/%m %H:%M',
    '%d/%m %H:%M:%S',
    '%d/%m/%y %H:%M',
    '%d/%m/%y %H:%M:%S',
    '%d/%m/%Y %H:%M',
    '%d/%m/%Y %H:%M:%S',
    '%a'
]

import time

def tokenize(text):
    if debug: print 'tokenize: text=', text
    tokens = []
    for token in text.split(' '):
        tokens.append(token.strip())
    return tokens


def parse(text, time_now):
    if debug: print 'parse: text=', text
    text = text.replace('midnight', '00:00')
    text = text.replace('midnite', '00:00')
    text = text.replace('noon', '12:00')
    found = False
    count = 0
    last = 0
    while not found:
        if debug: print 'parse: text1=', text
        tokens = tokenize(text)
        if debug: print 'parse: tokens=', tokens
        if len(tokens) > 0 and not tokens[0]:
            break
        #print 'len(tokens)=', len(tokens)
        #print 'count=', count
        last = len(tokens) - count
        #print 'last=', last
        text = ' '.join(tokens[:last+1])
        if debug: print 'parse: text2=', text
        count += 1
        time_x = None
        if text == 'now':
            tm = time.localtime(time_now)
            found = True
            """
            print 'text=', text
            tm = time.localtime(time_now)
            tm_year = tm.tm_year
            tm_mon = tm.tm_mon
            tm_mday = tm.tm_mday
            if text == 'noon':
                tm_hour = 12
            else:
                tm_hour = 0
            tm = (tm_year, tm_mon, tm_mday, tm_hour, 0, 0, tm.tm_wday, tm.tm_yday, tm.tm_isdst)
            found = True
            """
        else:
            for fmt in formats:
                #print 'dt: fmt=', fmt
                tm = 0
                try:
                    tm = time.strptime(text, fmt)
                    if debug: print 'parse: match with fmt=', fmt
                    if debug: print 'parse: tm=', time.asctime(tm)
                    found = True
                except Exception as e:
                    #print 'parse: tm:', e
                    tm = 0
                if tm and tm.tm_year == 1900 and tm.tm_mon == 1:
                    tm_now = time.localtime(time_now)
                    tm_year = tm_now.tm_year
                    tm_mon = tm_now.tm_mon
                    tm_mday = tm_now.tm_mday
                    tm = (tm_year, tm_mon, tm_mday, tm.tm_hour, tm.tm_min, tm.tm_sec, tm.tm_wday, tm.tm_yday, tm.tm_isdst)
                if found:
                    break
        #print 'tokens=', tokens
        text = ' '.join(tokens[:-1])
        if debug: print 'parse: text3=', text

    if debug: print 'parse: tm=', tm
    if debug: print 'parse: last=', last
    return (tm, last)


def dt(expression):
    if debug: print 'dt: expression=', expression
    if not expression:
        return 0

    time_now = time.time()
    time_1 = None
    time_2 = None

    result = parse(expression, time_now)
    if debug: print 'dt: result1=', result
    time_1 = result[0]
    if debug: print 'dt: time_1=', time_1
    last = result[1]
    if debug: print 'dt: last=', last

    if time_1 is not None:
        if debug: print 'dt: parsing second time'
        tokens = tokenize(expression)
        text = ' '.join(tokens[last+1:])
        if debug: print 'dt: text=', text
        if text:
            result = parse(text, time_now)
            if debug: print 'dt: result2=', result
            time_2 = result[0]
            #last = result[1]

    if debug: print 'dt: time_2=', time_2
    if not time_2:
        time_2 = time.localtime(time_now)
            
    if not time_1:
        return 0

    time_x = 0
    if time_1 is not None and time_2 is not None:
        #print 'time_1=', time_1
        #print 'time_2=', time_2
        if debug: print 'dt: time_1=', time.asctime(time_1)
        if debug: print 'dt: time_2=', time.asctime(time_2)
        try:
            time_t1 = time.mktime(time_1)
            time_t2 = time.mktime(time_2)
        except Exception as e:
            print 'dt: Error:', e
            return 0
        time_x = time_t2 - time_t1
        time_d = time_x / (60*60*24.)
        time_y = time_d / 365.25
        time_h = int(time_x / (60*60))
        if debug: print 'dt: time_x=', time_x
        if debug: print 'dt: hours=', time_h
        time_s = time_x % 60
        time_m = abs(int(time_x - time_h*60*60 - time_s)/60)
        if debug: print 'dt: time_m=', time_m
        if info: print 'dt: years=', time_y
        if info: print 'dt: days=', time_d
        if info: print 'dt: hours=%02d:%02d:%02d' % (time_h, time_m, time_s)
        if info: print 'dt: seconds=', time_x

    return time_x
    

if __name__ == '__main__':
    import sys
    print dt(' '.join(sys.argv[1:]))
