# This script will login to Reddit, return all liked stories for a given user
# parse all the electronicmusic subreddit likes and build and output for 
# a website listing.
#
import time
import urllib
import urllib2
import cookielib
import json
import ConfigParser
import logging
import tempfile
import os
import argparse

# Variables
hdr = {}
before_flag = False
link_value = '' 
liked_url =  'https://ssl.reddit.com/user/<username>/liked.json?limit=100&<direction>=<link_name>'
cj = cookielib.CookieJar()
cfg_file = 'rll.cfg'
final_file_location = ''
username = ''
password = ''
subreddit = ''
iCounter = 0
tmpfile = tempfile.TemporaryFile()
opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))

def get_config():
    config = ConfigParser.SafeConfigParser()
    config.optionxform(str())
    try:
        config.read(cfg_file)
        return config
    except Exception, e:
        logging.error(e)

# Retrieve values from config file
def load_config_values(config):
    try:
        global final_file_location
        global username
        global password
        global subreddit
        global hdr
        global before_flag
        global link_value
        final_file_location = config.get('PATHS','outputFile')
        subreddit = config.get('PATHS','subreddit')
        link_value = config.get('WAYPOINT','beforeLinkName')
        if link_value:
            before_flag = True
        username = config.get('CREDENTIALS','username')
        password = config.get('CREDENTIALS','password')
        hdr['User-Agent'] = config.get('CREDENTIALS','useragent')
        
    except Exception, e:
        logging.error(e)

# Write/Update config file
def write_config_values(before_link):
    try:
        configVal.set('WAYPOINT', 'beforeLinkName', before_link)
        f = open(cfg_file, 'w')
        configVal.write(f)
        f.close
    except Exception, e:
        logging.error(e)

# Reddit Login Function
def login(username, passwd):
    values = {'user': username,
              'api_type': 'json',
              'passwd': passwd}
 
    login_url = urllib2.Request('https://ssl.reddit.com/api/login/', headers=hdr)
    data = urllib.urlencode(values)
    try:
        response = opener.open(login_url, data).read()
    except Exception, e:
        logging.error(e)

def parse_data():
    global link_value
    global tmpfile
    global iCounter
    try:
        while (link_value is not None):
            time.sleep(3)
            liked_json = retrieve_liked(username)

            link_value = json.loads(liked_json.decode("utf-8"))["data"]["after"]
            liked_json = json.loads(liked_json.decode("utf-8"))["data"]["children"]
            for titles in liked_json:
                if not configVal.get('WAYPOINT', 'beforeLinkName'):
                    write_config_values(titles["data"]["name"])

                if(titles["data"]["subreddit"]==subreddit and titles["data"]["media"] is not None):
                    iCounter += 1
                    tmpfile.write('<a href=\''+ titles["data"]["url"] + '\'>' + titles["data"]["title"] + '</a><br/>\n' )
    except Exception, e:
        logging.error(e)

def write_output():
    global tmpfile
    try:
        if(iCounter>0):
            f2 = open(final_file_location, 'r')
            for line in f2:
                tmpfile.write(line)
            f2.close()
            tmpfile.seek(0)
            f = open(final_file_location, 'wb')
            for line in tmpfile:
                f.write(line)
            f.close()
        else:
            print 'empty'

        tmpfile.close()
    except Exception, e:
        logging.error(e)

# Fetch liked content for a user
def retrieve_liked(username):
    try:
        if(before_flag == True):
            direction = 'before'
        else:
            direction = 'after'
        repl = {'<username>':username, '<link_name>':link_value, '<direction>':direction}
        url = replace_all(liked_url, repl)
        print url
        url =  urllib2.Request(url, headers=hdr)
        response = opener.open(url).read()
        return response
    except Exception, e:
        logging.error(e)

def replace_all(text, dic):
    for i, j in dic.iteritems():
        text = text.replace(i, j)
    return text

###########################################################
# Main Processing
###########################################################
configVal = get_config()
load_config_values(configVal)

# Call login and retrieve liked content.  Each call must separated by at least 2 seconds.
login(username, password)
parse_data()
write_output()
