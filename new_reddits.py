#!/usr/bin/env python2
# -*- coding: utf-8 -*-
import sys
import time
import json
import requests


def get_reddits(url, output = "new-reddits.json"):
    """ Accepts an url to download a json file
    returns full path of the downloaded file
    """
    timestr = time.strftime("%Y%m%d-%H%M%S")
    headers = {'User-agent': 'mincklu-bot: {}'.format(timestr)}
    
    # get data from url
    r = requests.get(url, headers = headers)
    
    # return text file if the response is ok; none otherwise
    return r.text if r.ok else None

def read_reddits(jsonfile):
    """ Reads reddits from the jsonfile
    """
    if jsonfile:
        data = json.loads(jsonfile)
    else:
        sys.exit("Failed load reddits!")

    if "data" not in data.keys():
        print ""
        for key, value in data.items():
            print "{}: {}".format(key, value)
        return
    
    data = data["data"]
    if "children" not in data.keys():
        print ""
        for key, value in data.items():
            print "{}: {}".format(key, value)
        return 
    
    reddits  = data["children"]
    
    if reddits:
        for reddit in reddits:
            if "data" not in reddit.keys():
                print ""
                for key, value in reddit.items():
                    print "{}: {}".format(key, value)
                return
        
            edata = reddit["data"]
            print "*******************************************"
            print "*******************************************"
            print "title: %s" % edata["title"]
            print "subreddit: %s" % edata["subreddit"]
            print "url: %s" % edata["url"]
            print "permalink: %s" % edata["permalink"]
            print "selftext_html: %s" % edata["selftext_html"]
            print "*******************************************"
            print "*******************************************"
    else:
        print "Something went wrong!"


if __name__ == "__main__":
    url = "https://www.reddit.com/new.json"
    read_reddits(get_reddits(url))
