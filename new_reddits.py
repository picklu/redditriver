#!/usr/bin/env python3.6
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
    headers = {"User-agent": f"picklu-bot-0.3-{timestr}"}
    
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
        print()
        for key, value in data.items():
            print(f"{key}: {value}")
        return
    
    data = data["data"]
    if "children" not in data.keys():
        print()
        for key, value in data.items():
            print(f"{key}: {value}")
        return 
    
    reddits  = data["children"]
    
    if reddits:
        for reddit in reddits:
            if "data" not in reddit.keys():
                print()
                for key, value in reddit.items():
                    print(f"{key}: {value}")
                return
        
            edata = reddit["data"]
            print("*******************************************")
            print(f"title: {edata['title']}")
            print(f"subreddit: {edata['subreddit']}")
            print(f"url: {edata['url']}")
            print(f"permalink: {edata['permalink']}")
            print(f"selftext_html: {edata['selftext_html']}")
            print("*******************************************")
    else:
        print("Something went wrong!")


if __name__ == "__main__":
    url = "https://www.reddit.com/new.json"
    read_reddits(get_reddits(url))
