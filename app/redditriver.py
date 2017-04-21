#!/usr/bin/env python2
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
from web import webapi, debugerror, application, net
import stories


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

webapi.internalerror = debugerror

# no escaping needs to be done as the data we get from reddit is already escaped
net.htmlquote = lambda x: x
render = render_cheetah(path.join(cwd, 'templates'))

################
# page handlers
################
class RedditRiver(object):
    def GET(self):
        st = stories.RiverStories()
        story_page = st.get()
        return render.stories_tpl(**story_page)

class RedditRiverPage(object):
    def GET(self, page):
        st = stories.RiverStoriesPage(page)
        story_page = st.get()
        return render.stories_tpl(**story_page)

class SubRedditRiver(object):
    def GET(self, subreddit):
        st = stories.SubRiverStories(subreddit)
        story_page = st.get()
        story_page['subreddit'] = subreddit
        return render.stories_tpl(**story_page)

class SubRedditRiverPage(object):
    def GET(self, subreddit, page):
        st = stories.SubRiverStoriesPage(subreddit, page)
        story_page = st.get()
        story_page['subreddit'] = subreddit
        return render.stories_tpl(**story_page)

class SubReddits(object):
    def GET(self):
        st = stories.SubRivers()
        subreddits = st.get()
        return render.subreddits_tpl(subreddits=subreddits)

class AboutRiver(object):
    def GET(self):
        return render.about_tpl()

class Stats(object):
    def GET(self):
        user_stats, story_stats = stories.UserStats(count=10).get()
        return render.stats_tpl(user_stats=user_stats, story_stats=story_stats)

class SubStats(object):
    def GET(self, subreddit):
        user_stats, story_stats = stories.UserStats(subreddit, count=10).get()
        return render.stats_tpl(user_stats=user_stats, story_stats=story_stats,
            subreddit=subreddit)


if __name__ == "__main__":
    app = application(urls, globals())
    app.run()
