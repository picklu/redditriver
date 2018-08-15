#!/usr/bin/env python3.6
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
from bs4 import BeautifulSoup
from socket import error as SocketError
from socket import setdefaulttimeout
from ssl import SSLError
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


version = "3.0"

reddit_url = 'https://www.reddit.com'
subreddits_url = 'https://www.reddit.com/reddits'

setdefaulttimeout(30)


class RedesignError(Exception):
    """ An exception class thrown when it seems that Reddit has redesigned """
    pass


class SubRedditError(Exception):
    """ An exception class thrown when something serious happened """
    pass


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
        entries = _extract_subreddits(content)
        for entry in entries:
            entry['position'] = position
            position += 1
        srs.extend(entries)
        url = _get_next_page(content)
        if not url:
            break

    return srs


def _extract_subreddits(content):
    """Given an HTML page, extracts all the subreddits and returns a list of dicts of them.

    See the 'html.examples/subreddit.entry.new.html' for an example how HTML of an entry looks like"""

    subreddits = []
    name = reddit_name = description = subscribers = ""
    soup = BeautifulSoup(content, features="html.parser")
    entries = soup.findAll('div', {'class': re.compile('entry *')})
    if not entries:
        raise RedesignError("<div> tag with a class 'entry' not found!")

    for entry in entries:
        title_row = entry.find('p', {'class': 'titlerow'})
        if not title_row:
            raise RedesignError("<p> tag with a class 'titlerow' not found!")

        reddit_entry = title_row.text
        if ":" not in reddit_entry:
            raise RedesignError("title was not found in the titlerow!")
        # found the name and the reddit name
        reddit_name, name = reddit_entry.split(":", 1)

        description_entry = entry.find('div', {'class': 'description'})
        if not description_entry:
            description = ""
        else:
            description = description_entry.text

        subscribers_entry = entry.find('span', {'class': 'score likes'})
        if not subscribers_entry:
            raise RedesignError(
                "<span> tag for subscribers info was not found!")

        subscribers_number = subscribers_entry.find('span',
                                                    {'class': 'number'})
        if not subscribers_number:
            raise RedesignError(
                "<span> tag for number of subscribers was not found!")
        # found subscribers    
        subscribers = subscribers_number.text

        subreddits.append({
            'name': name,
            'reddit_name': re.sub(('r/'), "", reddit_name),
            'description': description,
            'subscribers': subscribers
        })

    return subreddits


def _get_page(url):
    """ Gets and returns a web page at url """

    timestr = time.strftime("%Y%m%d-%H%M%S")
    uagent = f"picklus redditriver: 0.3-{timestr}"
    request = Request(url)
    request.add_header('User-Agent', uagent)

    try:
        response = urlopen(request)
        encoding = response.info().get_param('charset', 'utf8')
        content = response.read().decode(encoding)
    except (HTTPError, URLError, SocketError, SSLError) as e:
        raise SubRedditError(e)

    return content


def _get_next_page(content):
    soup = BeautifulSoup(content, features="html.parser")
    a = soup.find('a', {'rel': 'nofollow next'})
    if a:
        return str(a['href'])


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
        print('position     :       ', item['position'])
        print('name         :       ', item['name'])
        print('reddit_name  :       ', item['reddit_name'])
        print('description  :       ', item['description'])
        print('subscribers  :       ', item['subscribers'])
        print()

def print_subreddits_json(srs):
    """ Given a list of dictionaries of subreddits (srs), prints them out in
    json format."""

    import simplejson
    print(simplejson.dumps(srs, indent=4))


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
    parser.add_option(
        "-p",
        action="store",
        type="int",
        dest="pages",
        default=1,
        help="How many pages of subreddits to output. Default: 1.")
    parser.add_option(
        "-n",
        action="store_true",
        dest="new",
        help="Retrieve new subreddits. Default: nope.")
    options, args = parser.parse_args()

    output_printers = {
        'paragraph': print_subreddits_paragraph,
        'json': print_subreddits_json
    }

    if options.output not in output_printers:
        print("Valid -o parameter values are: paragraph or json!", file=sys.stderr)
        sys.exit(1)

    try:
        srs = get_subreddits(options.pages, options.new)
    except RedesignError as e:
        print(f"Reddit has redesigned! {e}!")
        sys.exit(1)
    except SubRedditError as e:
        print(f"Serious error: {e}!", file=sys.stderr)
        sys.exit(1)

    output_printers[options.output](srs)
    print("Success!!!")
