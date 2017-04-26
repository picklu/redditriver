#!/usr/bin/env python2
#
# Refactoring Peteris Krumin's redditriver
# to make that working with current version of python (2.7.11),
# web.py (0.38) and Cheetah (2.4.4) template engine.
#
# The initial commit contains the full source code of http://redditriver.com website, which
# is available at http://catonmat.net/blog/designing-redditriver-dot-com-website
#
from os.path import dirname, abspath, join
cwdir = dirname(dirname(abspath(__file__)))


""" This module defines various config values of reddit river project """

# lock directory
#
lock_dir = join(cwdir, 'locks')

# path to sqlite database
#
database = join(cwdir, 'db/redditriver.db')

# path to mobile website autodiscovery config
#
autodisc_config = join(cwdir, 'config/autodisc.conf')

# number of subreddit pages to monitor for changes (used by update_subreddits.py)
#
subreddit_pages = 1

# number of story pages to monitor (used by update_stories.py)
#
story_pages = 2

# default subreddit (reddit_name) to display on the front page
#
default_subreddit = 'front_page'   # front_page is the 'reddit.com' front page

# stories per page to display on redditriver.com
#
stories_per_page = 25
