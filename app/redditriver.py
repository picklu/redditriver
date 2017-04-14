#!/usr/bin/env python
#
# Refactoring Peteris Krumin's redditriver
# to make that working with current version of python (2.7.11),
# web.py (0.38) and Cheetah (2.4.4) template engine. 
#
# The initial commit contains the full source code of http://redditriver.com website, which
# is available at http://catonmat.net/blog/designing-redditriver-dot-com-website
#
from os import sys, path, chdir
cwd = path.dirname(path.abspath(__file__))
chdir(cwd) # change the path to the directory of this file
from web.contrib.template import render_cheetah
import web
from datetime import datetime, timedelta
from time import mktime
from stories import RiverStories
from stories import RiverStoriesPage
from stories import SubRiverStories
from stories import SubRiverStoriesPage
from stories import UserStats
from stories import StoryStats
from stories import webdb


urls = (
    '/',                                 'RedditRiver',
    '/page/(\d+)/?',                     'RedditRiverPage',
    '/r/([a-zA-Z0-9_.-]+)/?',            'SubRedditRiver',
    '/r/([a-zA-Z0-9_.-]+)/page/(\d+)/?', 'SubRedditRiverPage',
    '/reddits/?',                        'SubReddits',
    '/stats/?',                          'Stats',
    '/stats/([a-zA-Z0-9_.-]+)/?',        'SubStats',
    '/about/?',                          'AboutRiver'
)

web.webapi.internalerror = web.debugerror

# no escaping needs to be done as the data we get from reddit is already escaped
web.net.htmlquote = lambda x: x
render = render_cheetah(path.join(cwd, 'templates'))

################
# page handlers
################
class RedditRiver(object):
    def GET(self):
        st = RiverStories()
        story_page = st.get()
        return render.stories_tpl(**story_page)

class RedditRiverPage(object):
    def GET(self, page):
        st = RiverStoriesPage(page)
        story_page = st.get()
        return render.stories_tpl(**story_page)

class SubRedditRiver(object):
    def GET(self, subreddit):
        st = SubRiverStories(subreddit)
        story_page = st.get()
        story_page['subreddit'] = subreddit
        return render.stories_tpl(**story_page)

class SubRedditRiverPage(object):
    def GET(self, subreddit, page):
        st = SubRiverStoriesPage(subreddit, page)
        story_page = st.get()
        story_page['subreddit'] = subreddit
        return render.stories_tpl(**story_page)

class SubReddits(object):
    def GET(self):
        subreddits = webdb.query("SELECT * FROM subreddits WHERE id > 0 and active = 1 ORDER by position")
        return render.subreddits_tpl(subreddits=subreddits)

class AboutRiver(object):
    def GET(self):
        return render.about_tpl()

class Stats(object):
    def GET(self):
        user_stats = UserStats(count=10).get()

        week_ago = datetime.now() - timedelta(days=7)
        unix_week = int(mktime(week_ago.timetuple()))
        story_stats = StoryStats(time_offset = unix_week, count=15).get()
        return render.stats_tpl(user_stats=user_stats, story_stats=story_stats)

class SubStats(object):
    def GET(self, subreddit):
        user_stats = UserStats(subreddit, count=10).get()

        week_ago = datetime.now() - timedelta(days=7)
        unix_week = int(mktime(week_ago.timetuple()))
        story_stats = StoryStats(time_offset = unix_week, subreddit=subreddit, count=15).get()
        return render.stats_tpl(user_stats=user_stats, story_stats=story_stats,
            subreddit=subreddit)


if __name__ == "__main__":
    app = web.application(urls, globals())
    app.run()