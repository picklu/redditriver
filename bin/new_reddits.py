#!/usr/bin/env python2
# -*- coding: utf-8 -*-
import sys
import time
import wget
import json


def get_reddits(url, output = "new-reddits.json"):
    timestr = time.strftime("%Y%m%d-%H%M%S")
    return wget.download(url, "-".join([timestr,output]))

def read_reddits(jsonfile):
    with open(jsonfile, "r") as f:
        data = json.loads(f.read())

    if "data" not in data.keys():
        for key, value in data.items():
            print ""
            print "{}: {}".format(key, value)
        return
    
    data = loaded_data["data"]
    if "children" not in data.keys():
        for key, value in data.items():
            print ""
            print "{}: {}".format(key, value)
        return 
    
    reddits  = data["children"]
    
    if reddits:
        for reddit in reddits:
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
