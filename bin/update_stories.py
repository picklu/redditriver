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

""" This program updates the latest story list """

import os
import sys
import time
import fcntl
import redditstories
import autodiscovery
from sqlite3 import dbapi2 as sqlite

sys.path.append(sys.path[0] + '/../config')

import riverconfig as config

version = "3.0"

class Lock:
    """ File locking class """
    def __init__(self, file):
        self.file = file

    def lock(self):
        self.f = open(self.file, 'w')
        try:
            fcntl.lockf(self.f.fileno(), fcntl.LOCK_EX|fcntl.LOCK_NB)
            return True
        except IOError as e:
            return False

# Whether to do autodiscovery (when testing sometimes it's not needed)
# Can be set to false with --noautodisc command option
do_autodiscovery = True

# Wheter to print autodiscovery information
# Can be set to true with --autodescdebug command option
autodiscdebug = False

# This program keeps track of story positions accross config.story_pages reddit pages.
# If the story is no longer found in these pages, the information about its
# position on reddit is lost, and it is assigned an infinity position.
#
# How big is infinity? Suppose that there are 10000 new stories on reddit daily which
# hit the front page. If the infinity is a billion (1000000000), then it would take
# 1000000000 / 10000 = 100000 days or 273 years to overflow this number.
#
infinity_position = 1000000000

def main():
    conn = sqlite.connect(database=config.database, timeout=10)
    conn.row_factory = sqlite.Row
    conn.text_factory = str
    cur = conn.cursor()

    cur.execute("SELECT id, reddit_name FROM subreddits WHERE active = 1")
    subreddits = cur.fetchall()

    total_new = 0
    total_updated = 0
    for subreddit in subreddits:
        new_stories = 0
        updated_stories = 0
        print(f"Going after {subreddit['reddit_name']}'s subreddit stories! ")
        try:
            stories = redditstories.get_stories(subreddit=subreddit['reddit_name'], pages=config.story_pages)
        except redditstories.RedesignError as e:
            print(f"Could not get stories for {subreddit['reddit_name']} (reddit might have redesigned: {e})!")
            continue
        except redditstories.StoryError as e:
            print(f"Serious error while getting {subreddit['reddit_name']}: {e}!")
            continue

        for position, story in enumerate(stories, 1):
            story['position'] = position
            story['subreddit_id'] = subreddit['id']
            cur.execute("SELECT id, position FROM stories WHERE subreddit_id = ? AND title = ? AND url = ?",
                (subreddit['id'], story['title'], story['url']))
            existing_row = cur.fetchone()
            if existing_row:
                updated_stories += 1
                cur.execute("UPDATE stories SET comments = ? WHERE id = ?",
                    (story['comments'], existing_row['id']))
                if existing_row['position'] != story['position']:
                    # swap both positions to maintain consistency of positions
                    swap_id = cur.execute("SELECT id FROM stories WHERE subreddit_id = ? AND position = ?",
                        (subreddit['id'], position)).fetchone()[0]
                    cur.execute("UPDATE stories SET position = ? WHERE id = ?",
                        (story['position'], existing_row['id']))
                    cur.execute("UPDATE stories SET position = ? WHERE id = ?",
                        (existing_row['position'], swap_id))
                    conn.commit()
                continue

            story['url_mobile'] = ""
            if do_autodiscovery:
                try:
                    url = story['url']
                    url = url.decode("utf-8") if type(url) == bytes else url
                    if autodiscdebug:
                        print(f"Autodiscovering '{url}'")
                    autodisc = autodiscovery.AutoDiscovery()
                    story['url_mobile'] = autodisc.autodiscover(url)
                    if story['url_mobile']:
                        print(f"Autodiscovered '{story['url_mobile']}'")
                    else:
                        print("Did not autodiscover anything!")
                except (autodiscovery.AutoDiscoveryError, UnicodeEncodeError) as e:
                    if autodiscdebug:
                        print(f"Failed autodiscovering: {e}")
                    pass

            story['date_added'] = int(time.time())

            story_at_pos = cur.execute("SELECT id FROM stories WHERE subreddit_id = ? AND position = ?",
                (subreddit['id'], position)).fetchone()
            if story_at_pos:
                id = story_at_pos[0]
                cur.execute("UPDATE stories SET position = ? WHERE id = ?", (infinity_position, id))

            cur.execute("INSERT INTO stories (title, url, url_mobile, reddit_id, subreddit_id, "
                        "comments, user, position, date_reddit, date_added) "
                        "VALUES (:title, :url, :url_mobile, :id, :subreddit_id, "
                        ":comments, :user, :position, :unix_time, :date_added)",
                        story)
            new_stories += 1
            conn.commit()

        total_new += new_stories
        total_updated += updated_stories
        print(f"{new_stories} new and {updated_stories} updated ({new_stories+updated_stories} total)")

    print(f"Total: {total_new} new and {total_updated} updated ({total_new+total_updated} total)")

if __name__ == "__main__":
    lock = Lock(config.lock_dir + '/update_stories.lock')
    if not lock.lock():
        print("I might be already running!")
        sys.exit(1)

    argv = sys.argv[1:]
    if "--noautodisc" in argv:
        print("Setting autodiscovery to False")
        do_autodiscovery = False
    if "--autodiscdebug" in argv:
        print("Setting autodiscovery debug to True")
        autodiscdebug = True

    main()
