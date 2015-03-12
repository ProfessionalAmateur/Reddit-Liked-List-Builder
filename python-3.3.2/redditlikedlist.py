# This script will login to Reddit, return all liked stories for a given user
# parse all the subreddit likes and build and output for 
# a website listing.
#
import time
import datetime
import urllib.request, urllib.error, urllib.parse
import http.cookiejar
import json
import configparser
import logging
import tempfile
import os
import argparse

# Variables
hdr = {}
before_flag = False
link_value = '' 
liked_url =  'https://ssl.reddit.com/user/<username>/liked.json?limit=100&<direction>=<link_name>'
cj = http.cookiejar.CookieJar()
cfg_file = ''
final_file_location = ''
username = ''
password = ''
subreddit = ''
output_format = ''
iCounter = 0
tmpfile = tempfile.TemporaryFile()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

# Parse input
def parse_input_params():
    global cfg_file
    parser = argparse.ArgumentParser(description='Music list built from liked stories within a subreddit')
    parser.add_argument("config_file", help="Configuration file location")
    args = parser.parse_args()
    cfg_file = args.config_file

# Load config file
def get_config():
    config = configparser.SafeConfigParser()
    config.optionxform(str())
    try:
        config.read(cfg_file)
        return config
    except Exception as e:
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
        global output_format
        final_file_location = config.get('PATHS','outputFile')
        subreddit = config.get('PATHS','subreddit')
        link_value = config.get('WAYPOINT','beforeLinkName')
        if link_value:
            before_flag = True
        username = config.get('CREDENTIALS','username')
        password = config.get('CREDENTIALS','password')
        hdr['User-Agent'] = config.get('CREDENTIALS','useragent')
        output_format = config.get('OUTPUT','format')

    except Exception as e:
        logging.error(e)

# Reddit Login Function
def login(username, passwd):
    values = {'user': username,
              'api_type': 'json',
              'passwd': passwd}

    login_url = urllib.request.Request('https://ssl.reddit.com/api/login/', headers=hdr)
    data = urllib.parse.urlencode(values)
    data_bytes = data.encode('utf-8')
    try:
        response = opener.open(login_url, data_bytes).read()
    except Exception as e:
        logging.error(e)        
        
def process_reddit_data():
    global link_value
    global tmpfile
    global iCounter
    try:
        while (link_value is not None):
            time.sleep(3)
            liked_json = retrieve_liked(username)

            if (before_flag == False):
                link_value = json.loads(liked_json)["data"]["after"]
            else:
                link_value = json.loads(liked_json)["data"]["before"]

            liked_json = json.loads(liked_json)["data"]["children"]
            for titles in liked_json:
                iCounter += 1
                if (iCounter == 1):
                    write_config_values(titles["data"]["name"])

                if(titles["data"]["subreddit"]==subreddit and titles["data"]["media"] is not None):
                    if (output_format=="embeded"):
                        if ("www.youtube.com" in titles["data"]["url"]):
                           param = get_youtube_param(titles["data"]["url"])
                           param = (param.replace("['","")).replace("']","")
                           tmpfile.write(bytes('<div class=\'togglevid\'><img class=\'plus-img\' src=\'/images/trans.png\'>' + titles["data"]["title"] + '</div><div class=\'video\'><iframe width=\'420\' height=\'315\' data-src=\'//www.youtube.com/embed/'+ param +'\' frameborder=\'0\' allowfullscreen></iframe></div>\n', 'utf-8' ))
                        
                        elif ("soundcloud" in titles["data"]["url"]):
                            embed_html = get_soundcloud_html(titles["data"]["url"])
                            embed_html = embed_html.replace('src=','data-src=')
                            tmpfile.write(bytes('<div class=\'togglevid\'><img class=\'plus-img\' src=\'/images/trans.png\'>'+ titles["data"]["title"] + '</div><div class=\'video\'>'+ embed_html +'</div>\n', 'utf-8' ))
                        else:
                            tmpfile.write(bytes('<a href=\''+ titles["data"]["url"] + '\'>' + titles["data"]["title"] + '</a><br/>\n', 'utf-8' ))
                    else:
                        tmpfile.write(bytes('<a href=\''+ titles["data"]["url"] + '\'>' + titles["data"]["title"] + '</a><br/>\n', 'utf-8' ))

    except Exception as e:
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
        url =  urllib.request.Request(url, headers=hdr)
        r = opener.open(url).read()
        response = r.decode('utf-8')
        return response
    except Exception as e:
        logging.error(e)

# Write/Update config file
def write_config_values(before_link):
    try:
        configVal.set('WAYPOINT', 'beforeLinkName', before_link)
        f = open(cfg_file, 'w')
        configVal.write(f)
        f.close
    except Exception as e:
        logging.error(e)

def updated_timestamp():
    ts = time.time()
    st = datetime.datetime.fromtimestamp(ts).strftime('%m-%d-%Y %H:%M:%S')
    return("<p style='font-size: .8em;'>Last updated at: " + st + "</p>\n")
        
def write_output():
    global tmpfile
    try:
        if os.path.exists(final_file_location):
            #final output file aleady exists, we need to append new data.
            f2 = open(final_file_location, 'r')
            for i in range(1):
                next(f2)
            for line in f2:
                tmpfile.write(bytes(line, 'utf-8'))
            f2.close()

        tmpfile.seek(0)
        f = open(final_file_location, 'wb')
        f.write(bytes(updated_timestamp(), 'utf-8'))
        for line in tmpfile:
            f.write(bytes(line))
        f.close()

        tmpfile.close()
    except Exception as e:
        logging.error(e)

def get_youtube_param(url):
    parsed = urllib.parse.urlparse(url)
    param = str(urllib.parse.parse_qs(parsed.query)['v'])

    return param

# Get soundcloud embed html
def get_soundcloud_html(url):
    try:
        sndcld_url = 'http://soundcloud.com/oembed?format=json&url=' + url + '&iframe=true'
#        print(sndcld_url)
        url = urllib.request.Request(sndcld_url)
        r = opener.open(url).read()
        output = r.decode('utf-8')
        html = json.loads(output)["html"]
    except Exception as e:
        logging.error(e)

    return html

# generic replace text using dict function
def replace_all(text, dic):
    for i, j in dic.items():
        text = text.replace(i, j)
    return text


###########################################################
# Main Processing
###########################################################
parse_input_params()
configVal = get_config()
load_config_values(configVal)

# Call login and retrieve liked content.  Each call must separated by at least 2 seconds.
login(username, password)
process_reddit_data()
write_output()

