#!/usr/bin/env python

# current program version:
VERSION = '3.4'

import glob
import os
import time

def version():
    list_of_files = glob.glob('*.py') # * means all if need specific format then *.csv
    latest_file = max(list_of_files, key=os.path.getctime)
    #print latest_file
    time_t = os.path.getctime(latest_file)
    return VERSION + '\n' + time.asctime(time.localtime(time_t))

if __name__ == '__main__':
    print version()
