#!/usr/bin/env python2
# -*- coding: utf-8 -*-
import wget
import json


def get_reddits(url, output = "./new_reddits.json"):
    return wget.download(url, out = output)

def read_reddits(jsonfile):
    with open(jsonfile, "r") as f:
        data = json.loads(f.read())

    reddits = data["data"]["children"]
    for reddit in reddits:
        edata = reddit["data"]
        print "title: %s" % (edata["title"])
        print "subreddit: %s" % (edata["subreddit"])
        print "url: %s" % (edata["url"])
        print "permalink: %s" % (edata["permalink"])
        print "selftext_html: %s" % (edata["selftext_html"])


if __name__ == "__main__":
    url = "https://www.reddit.com/new.json"
    read_reddits(get_reddits(url))
