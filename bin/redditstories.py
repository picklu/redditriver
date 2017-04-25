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
import datetime
import dateutil.parser as dtp
from BeautifulSoup import BeautifulSoup

version = "2.0"

reddit_url = 'https://www.reddit.com'
subreddit_url = 'https://www.reddit.com/r'

socket.setdefaulttimeout(30)

class RedesignError(Exception):
    """ An exception class thrown when it seems that Reddit has redesigned """
    pass

class StoryError(Exception):
    """ An exception class thrown when something serious happened """
    pass

def get_stories(subreddit="front_page", pages=1, new=False):
    """ If subreddit front_page, goes to https://www.reddit.com, otherwise goes to
    https://www.reddit.com/r/subreddit. Finds all stories accross 'pages' pages
    and returns a list of dictionaries of stories.

    If new is True, gets new stories at https:www.//reddit.com/new or
    https://www.reddit.com/r/subreddit/new"""

    stories = []
    if subreddit == "front_page":
        url = reddit_url
    else:
        url = subreddit_url + '/' + subreddit
    if new: url += '/new'
    position = 1
    for i in range(pages):
        content = _get_page(url)
        new_stories = _extract_stories(content)
        for story in new_stories:
            story['url'] = story['url'].replace('&amp;', '&')
            story['position'] = position
            story['subreddit'] = subreddit
            position += 1
        stories.extend(new_stories)
        url = _get_next_page(content)
        if not url:
            break

    return stories;

def _extract_stories(content):
    """Given an HTML page, extracts all the stories and returns a list of dicts of them.

    See the 'html.examples/story.entry.html' for an example how HTML of an entry looks like"""

    stories = []
    soup = BeautifulSoup(content)
    entries = soup.findAll('div', {'class': re.compile('entry *')})
    for entry in entries:
        p_title = entry.find('p', {'class': re.compile('title *')});
        if not p_title:
            raise RedesignError("title <p> tag was not found")

        a_title = p_title.find('a', {'class': re.compile('title *')})
        if not a_title:
            raise RedesignError("title <a> tag was not found")

        title = a_title.text
        url = a_title['href']
        if url.startswith('/'): # link to reddit itself
            url = reddit_url + url
            
        div_reportform = entry.find('div', {'class': re.compile('reportform report-t3_*')})
        if not div_reportform:
            raise RedesignError("reportform <div> tag was not found")
        
        m = re.search(r'reportform report-t3_(.+)', div_reportform['class'])
        if not m:
            raise RedesignError("a reddit id was not found")
        
        id = m.group(1)

        # there is no score span in the reddit story page
        score = 0
        
        p_tagline = entry.find('p', {'class': 'tagline'});
        if not p_tagline:
            raise RedesignError("tagline <p> tag was not found")

        a_author = p_tagline.find('a', {'class': re.compile('author *')})
        if not a_author:
            raise RedesignError("user 'a' tag was not found")
        
        user = a_author.text
        
        time_posted = p_tagline.find('time', {'class': 'live-timestamp'})
        if not time_posted:
            raise RedesignError("posted ago <time> tag was not found")

        posted_at = time_posted["datetime"]
        if not posted_at:
            raise RedesignError("unable to extract story date")
        
        try:
            unix_time, human_time = _to_unix(posted_at)
        except Exception as e:
            raise RedesignError("Not a valid date-time. %s" %e)

        a_comment = entry.find('a', {'class': re.compile('bylink comments *')})
        if not a_comment:
            raise RedesignError("no comment 'a' tag was found")

        if a_comment.text == "comment":
            comments = 0
        else:
            m = re.search(r'(\d+) comment', a_comment.text)
            if not m:
                raise RedesignError("comment could could not be extracted")
            comments = int(m.group(1))

        stories.append({
            'id': id.encode('utf8'),
            'title': title.encode('utf8'),
            'url': url.encode('utf8'),
            'score': score,
            'comments': comments,
            'user': user.encode('utf8'),
            'unix_time': unix_time,
            'human_time': human_time.encode('utf8')})

    return stories

def _to_unix(postedat):
    dt = dtp.parse(postedat)
    unix_time = int(time.mktime(dt.timetuple()))
    human_time = time.ctime(unix_time)
    return (unix_time, human_time)

def _get_page(url):
    """ Gets and returns a web page at url """

    timestr = time.strftime("%Y%m%d-%H%M%S")
    uagent = 'picklus redditriver: 0.1({})'.format(timestr)
    request = urllib2.Request(url)
    request.add_header('User-Agent', uagent)

    try:
        response = urllib2.urlopen(request)
        content = response.read()
    except (urllib2.HTTPError, urllib2.URLError, socket.error,
            socket.sslerror) as e:
        raise StoryError(e)

    return content

def _get_next_page(content):
    soup = BeautifulSoup(content)
    a = soup.find('a', {'rel': 'nofollow next'})
    if a:
        return str(a['href'])

def print_stories_paragraph(stories):
    """ Given a list of dictionaries of stories, prints them out paragraph at a time. """

    for story in stories:
        print 'position:', story['position']
        print 'subreddit:', story['subreddit']
        print 'id:', story['id']
        print 'title:', story['title']
        print 'url:', story['url']
        print 'score:', story['score']
        print 'comments:', story['comments']
        print 'user:', story['user']
        print 'unix_time:', story['unix_time']
        print 'human_time:', story['human_time']
        print

def print_stories_json(stories):
    """ Given a list of dictionaries of stories, prints them out in json format."""

    import simplejson
    print simplejson.dumps(stories, indent=4)

if __name__ == '__main__':
    from optparse import OptionParser

    description = """A program by Peteris Krumins (http://www.catonmat.net)
    - upgraded by Subrata Sarker <subrata_sarker@yahoo.com>"""
    usage = "%prog [options]"

    parser = OptionParser(description=description, usage=usage)
    parser.add_option(
        "-o", 
        action="store", 
        dest="output", 
        default="paragraph",
        help="Output format: paragraph or json. Default: paragraph.")
    parser.add_option("-p", 
        action="store", 
        type="int", 
        dest="pages",
        default=1, 
        help="How many pages of stories to output. Default: 1.")
    parser.add_option("-s", 
        action="store", 
        dest="subreddit", 
        default="front_page",
        help="Subreddit to retrieve stories from. Default: front_page.")
    parser.add_option("-n", 
        action="store_true", 
        dest="new",
        help="Retrieve new stories. Default: nope.")
    options, args = parser.parse_args()

    output_printers = { 'paragraph': print_stories_paragraph,
                        'json': print_stories_json }

    if options.output not in output_printers:
        print >>sys.stderr, "Valid -o parameter values are: paragraph or json!"
        sys.exit(1)

    try:
        stories = get_stories(options.subreddit, options.pages, options.new)
    except RedesignError, e:
        print >>sys.stderr, "Reddit has redesigned! %s!" % e
        sys.exit(1)
    except StoryError, e:
        print >>sys.stderr, "Serious error: %s!" % e
        sys.exit(1)

    output_printers[options.output](stories)
