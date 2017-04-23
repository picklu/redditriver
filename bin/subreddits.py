#!/usr/bin/env python2
#
# Peteris Krumins (peter@catonmat.net)
# http://www.catonmat.net  --  good coders code, great reuse
#
# Released under GNU GPL
#
# Developed as a part of redditriver.com project
# Read how it was designed:
# http://www.catonmat.net/blog/designing-redditriver-dot-com-website
#

import re
import sys
import time
import socket
import urllib2
from BeautifulSoup import BeautifulSoup as bs

version = "1.0"

reddit_url = 'https://www.reddit.com'
#subreddits_url = 'https://www.reddit.com/reddits'
subreddits_url = 'http://localhost:8080/subreddit.entry.new.html'

socket.setdefaulttimeout(30)

class RedesignError(Exception):
    """ An exception class thrown when it seems that Reddit has redesigned """
    pass

class SubRedditError(Exception):
    """ An exception class thrown when something serious happened """

def get_subreddits(pages=1, new=False):
    """ Goes to https://www.reddit.com/reddits, finds all subreddits
    accross 'pages' pages and returns a list of dictionaries of subreddits.

    If new is True, gets new subreddits at https://www.reddit.com/reddits/new

    Each dictionary contains the following key, value pairs:
     * position, position subreddit appears on subreddit page, for example, 12
     * name, name of the subreddit, for example, 'Pictures and Images'
     * reddit_name, short reddit name for the subreddit, for example, 'pics'
     * description, description of a subreddit, for example,
                     'Yeah reddit, you finally got it. Context appreciated.'
     * subscribers, number of subscribers, for example, 10682"""

    srs = []
    url = subreddits_url
    if new: url += '/new'
    position = 1
    for i in range(pages):
        content = _get_page(url)
        try:
            entries = _extract_subreddits(content)
        except:
            exit("There was something wrong!")
        
        for entry in entries:
            entry['position'] = position
            position += 1
        srs.extend(entries)
        url = _get_next_page(content)
        if not url:
            break

    return srs;

def _extract_subreddits(content):
    """Given an HTML page, extracts all the subreddits and returns a list of dicts of them.

    See the 'html.examples/subreddit.entry.txt' for an example how HTML of an entry looks like"""

    subreddits = []
    name = reddit_name = description = subscribers = ""
    soup = bs(content)
    entries = soup.findAll('div', {'class': re.compile('entry *')})
    if not entries:
        raise RedesignError, "'div' tag a class 'entry' not found!"
    
    for entry in entries:
        
        title_row = entry.find('p', {'class': 'titlerow'})
        if not title_row:
            raise RedesignError, "'p' tag with a class 'titlerow' not found!"
        
        print "Title Row => ", title_row
        reddit_entry = title_row.find('a')
        if not reddit_entry:
            raise RedesignError, "'a' tag was not found in the ttilerow!"
        
        print reddit_entry
        return
        reddit_name, name = reddit_entry.split(":")
        
        description_entry = entry.find('div', {'class': 'md'})
        if not description_entry:
            raise RedesignError, "'div' tag for description was not found!"
        
        description = description_entry.text
        
        subscribers_entry = entry.find('span', {'class': 'score likes'})
        if not subscribers_entry:
            raise RedesignError, "'span' tag for subscribers info was not found!"
        
        subscribers = subscribers_entry.find('span', {'class': 'number'})
        
        subreddits.append({
            'name': name.encode('utf8'),
            'reddit_name': reddit_name.encode('utf8'),
            'description': desc.encode('utf8'),
            'subscribers': subscs})

    return subreddits

def _get_page(url):
    """ Gets and returns a web page at url """

    timestr = time.strftime("%Y%m%d-%H%M%S")
    uagent = 'picklus redditriver: 0.1({})'.format(timestr)
    request = urllib2.Request(url)
    request.add_header('User-Agent', uagent)

    try:
        response = urllib2.urlopen(request)
        content = response.read()
    except (urllib2.HTTPError, urllib2.URLError, socket.error, socket.sslerror), e:
        raise SubRedditError, e

    return content

def _get_next_page(content):
    soup = BeautifulSoup(content)
    a = soup.find(lambda tag: tag.name == 'a' and tag.string == 'next')
    if a:
        return reddit_url + a['href']

def print_subreddits_paragraph(srs):
    """ Given a list of dictionaries of subreddits (srs), prints them out
    paragraph at a time:

     position: subreddit's position in subreddit's list (position)
     name: subreddit's name (name)
     reddit_name: subreddit's short name (reddit_name)
     description: subreddit's description (description)
     subscribers: number of subscribers (subscribers)

     ...
    """

    for item in srs:
        print 'position:', item['position']
        print 'name:', item['name']
        print 'reddit_name:', item['reddit_name']
        print 'description:', item['description']
        print 'subscribers:', item['subscribers']
        print

def print_subreddits_json(srs):
    """ Given a list of dictionaries of subreddits (srs), prints them out in
    json format."""

    import simplejson
    print simplejson.dumps(srs, indent=4)

if __name__ == '__main__':
    from optparse import OptionParser

    description = "A program by Peteris Krumins (http://www.catonmat.net)"
    usage = "%prog [options]"

    parser = OptionParser(description=description, usage=usage)
    parser.add_option("-o", action="store", dest="output", default="paragraph",
                      help="Output format: paragraph or json. Default: paragraph.")
    parser.add_option("-p", action="store", type="int", dest="pages",
                      default=1, help="How many pages of subreddits to output. Default: 1.")
    parser.add_option("-n", action="store_true", dest="new",
                      help="Retrieve new subreddits. Default: nope.")
    options, args = parser.parse_args()

    output_printers = { 'paragraph': print_subreddits_paragraph,
                        'json': print_subreddits_json }

    if options.output not in output_printers:
        print >>sys.stderr, "Valid -o parameter values are: paragraph or json!"
        sys.exit(1)

    try:
        srs = get_subreddits(options.pages, options.new)
    except RedesignError, e:
        print >>sys.stderr, "Reddit has redesigned! %s!" % e
        sys.exit(1)
    except StoryError, e:
        print >>sys.stderr, "Serious error: %s!" % e
        sys.exit(1)

    output_printers[options.output](srs)

