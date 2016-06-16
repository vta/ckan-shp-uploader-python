#!/usr/local/bin/python
# -*- coding: utf-8 -*-

import urllib2
from urlparse import urlparse

try:
    input = raw_input
except NameError:
    pass



HEADER = '\033[95m'
OKBLUE = '\033[94m'
OKGREEN = '\033[92m'
WARNING = '\033[93m'
FAIL = '\033[91m'
ENDC = '\033[0m'
BOLD = '\033[1m'
UNDERLINE = '\033[4m'

def waiter():
    spinner = ['-','\\','|','/','-','\\','|','/']
    spinner_i = 0
    progress = 0
    for i in range(0,100):
        sys.stdout.write("Download progress: %s   \r" % spinner[spinner_i] )
        time.sleep(0.1)
        spinner_i = (spinner_i + 1) % len(spinner)
        sys.stdout.flush()
    print 'Done!                           '


def url_exists(url):
    parsed_url = urlparse(url)
    if not bool(parsed_url.scheme):
        return False
    try:
        urllib2.urlopen(url)
        return True         # URL Exist
    except ValueError, ex:
        return False        # URL not well formatted
    except urllib2.URLError, ex:
        return False        # URL don't seem to be alive


def prompt(message, errormessage, isvalid):
    """Prompt for input given a message and return that value after verifying the input.

    Args:
        message (str): the message to display when asking the user for the value
        errormessage (str): the message to display when the value fails validation
        isvalid (func): a function that returns True if the value given by the user is valid
    
    Returns:
        str. the value provided by the user

    """
    res = None
    while res is None:
        res = input(HEADER+str(message)+': ' +ENDC)
        if not isvalid(res):
            print  WARNING +str(errormessage)+ENDC
            res = None
    return res
