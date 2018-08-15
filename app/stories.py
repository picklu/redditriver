#!/usr/bin/env python3.6
import sys
import re
import web
from urllib.parse import urlparse
from config import riverconfig as config
from datetime import datetime, timedelta
from time import mktime

webdb = web.database(dbn='sqlite', db=config.database)

def get_nice_host(url):
    """ Given a URL, extracts a 'nice' version of host, for example:
        >>> get_nice_host('http://www.reddit.com')
        'reddit.com'
        >>> get_nice_host('http://ww2.nba.com')
        'nba.com'
        >>> get_nice_host('http://foo.bar.baz/a.html')
        'foo.bar.baz' """

    parsed_url = urlparse(url)
    host = parsed_url[1]    # 1 is 'host'
    host = host.decode('utf-8') if type(host) == bytes else host
    host = re.sub(r'www?\d*\.', '', host)
    return host

class Stories:
    def __init__(self, subreddit, page):
        self.subreddit = subreddit
        self.page = int(page)
        if self.page == 0: self.page = 1
        if self.page > sys.maxsize: self.page = 1

    def _story_query(self):
        story_query = ("SELECT st.title title, st.url url, st.url_mobile url_mobile, "
                       "st.comments comments, st.user user, "
                       "st.date_reddit date_reddit "
                       "FROM stories st "
                       "LEFT JOIN subreddits su "
                       "ON st.subreddit_id = su.id "
                       "WHERE su.reddit_name = '%s' "
                       "ORDER BY st.position, st.date_added DESC "
                       "LIMIT %d "
                       "OFFSET %d")

        offset = (self.page - 1) * config.stories_per_page

        # We do a trick here of making a webdb.query for + 1 story to see if we
        # should display the next page link. If we get +1 story, then
        # the next page exists.
        #
        query = (story_query % (self.subreddit, config.stories_per_page + 1, offset))
        return query

    def get(self):
        query = self._story_query()
        tmp_stories = webdb.query(query)

        stories = []
        next_page = prev_page = False
        for idx, s in enumerate(tmp_stories):
            if idx >= config.stories_per_page:
                next_page = True
                break
            s.host = get_nice_host(s['url'])
            s.niceago = web.datestr(datetime.fromtimestamp(s['date_reddit']), datetime.now())
            stories.append(s)

        if self.page != 1:
            prev_page = True

        next_page_link = prev_page_link = None
        if next_page:
            next_page_link = self.next_page(self.subreddit, self.page)
        if prev_page:
            prev_page_link = self.prev_page(self.subreddit, self.page)

        return {'stories': stories,
                'next_page': next_page,
                'prev_page': prev_page,
                'next_page_link': next_page_link,
                'prev_page_link': prev_page_link}


class RiverStories(Stories):
    def __init__(self, page=1):
        super().__init__(config.default_subreddit, page)

    def next_page(self, subreddit, page):
        return "/page/" + str(page + 1)

class RiverStoriesPage(RiverStories):
    def __init__(self, page):
        super().__init__(page)

    def prev_page(self, subreddit, page):
        if page == 2: return "/"
        return "/page/" + str(page - 1)

class SubRiverStories(Stories):
    def __init__(self, subreddit, page=1):
        super().__init__(subreddit, page)

    def next_page(self, subreddit, page):
        return "/r/" + subreddit + "/page/" + str(page + 1)

class SubRiverStoriesPage(SubRiverStories):
    def __init__(self, subreddit, page):
        super().__init__(subreddit, page)

    def prev_page(self, subreddit, page):
        if page == 2:
            return "/r/" + subreddit
        return "/r/" + subreddit + "/page/" + str(page - 1)

class Rivers:
    def __init__(self, page):
        self.page = int(page)
        if self.page == 0: self.page = 1
        if self.page > sys.maxsize: self.page = 1
    
    def _river_query(self):
        river_query = ("SELECT * FROM subreddits WHERE id > 0 and active = 1 "
                       "ORDER by position "
                       "LIMIT %d "
                       "OFFSET %d")

        offset = (self.page - 1) * config.subreddits_per_page

        # We do a trick here of making a webdb.query for + 1 story to see if we
        # should display the next page link. If we get +1 story, then
        # the next page exists.
        #
        query = (river_query % (config.subreddits_per_page + 1, offset))
        return query
        
    def get(self):
        query = self._river_query()
        tmp_rivers = webdb.query(query)

        rivers = []
        next_page = prev_page = False
        for idx, s in enumerate(tmp_rivers):
            if idx >= config.subreddits_per_page:
                next_page = True
                break
            rivers.append(s)

        if self.page != 1:
            prev_page = True

        next_page_link = prev_page_link = None
        if next_page:
            next_page_link = self.next_page(self.page)
        if prev_page:
            prev_page_link = self.prev_page(self.page)

        return {'subreddits': rivers,
                'next_page': next_page,
                'prev_page': prev_page,
                'next_page_link': next_page_link,
                'prev_page_link': prev_page_link}

class SubRivers(Rivers):
    def __init__(self, page=1):
        super().__init__(page)

    def next_page(self, page):
        return "/reddits/page/" + str(page + 1)

class SubRiversPage(SubRivers):
    def __init__(self, page):
        super().__init__(page)

    def prev_page(self, page):
        if page == 2: return "/reddits/"
        return "reddits/page/" + str(page - 1)

class StoryStats:
    def __init__(self, time_offset, subreddit=config.default_subreddit, count=10):
        self.subreddit = subreddit
        self.count = count
        self.time_offset = time_offset

    def _story_query(self):
        stats_query = ("SELECT st.title title, st.url url, st.url_mobile url_mobile, "
                       "st.comments comments, st.user user, "
                       "st.date_reddit date_reddit "
                       "FROM stories st "
                       "LEFT JOIN subreddits su "
                       "ON st.subreddit_id = su.id "
                       "WHERE su.reddit_name = '%s' AND st.date_reddit >= %d "
                       "ORDER BY st.date_reddit DESC "
                       "LIMIT %d ")

        query = stats_query % (self.subreddit, self.time_offset, self.count)
        return query

    def get(self):
        query = self._story_query()
        tmp_stories = webdb.query(query)
        stories = []
        for s in tmp_stories:
            s.host = get_nice_host(s['url'])
            s.niceago = web.datestr(datetime.fromtimestamp(s['date_reddit']), datetime.now())
            stories.append(s)
        return stories

class UserStats:
    def __init__(self, subreddit=config.default_subreddit, count=10):
        self.subreddit = subreddit
        self.count = count

    def _user_query(self):
        stats_query = ("SELECT COUNT(st.user) stories, st.user user "
                       "FROM stories st "
                       "LEFT JOIN subreddits su "
                       "ON st.subreddit_id = su.id "
                       "WHERE su.reddit_name = '%s' "
                       "GROUP BY user "
                       "ORDER BY stories DESC "
                       "LIMIT %d ")

        query = stats_query % (self.subreddit, self.count)
        return query

    def get(self):
        week_ago = datetime.now() - timedelta(days=7)
        unix_week = int(mktime(week_ago.timetuple()))
        story_stats = StoryStats(time_offset = unix_week, subreddit=self.subreddit, count=15).get()
        query = self._user_query()
        user_stats = webdb.query(query)
        return (user_stats, story_stats)
