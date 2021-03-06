import re
import os
import praw
import time
import MySQLdb
import OpenSSL
import tvdb_api
import tvdb_exceptions
import requests
import syslog

from configparser import ConfigParser

syslog.syslog(syslog.LOG_INFO, 'Process started')

tvshow = "seinfeld"

t = tvdb_api.Tvdb()

r = praw.Reddit("browser-based:TV Show Script:v1.0 (by /u/HeadlessChild)")

### LOGIN ###
config = ConfigParser()
config.read(os.getenv("HOME")+"/.reddit-episode-bot.conf")

tvshow = config.get("Reddit", "Tvshow")
username = config.get("Reddit", "Username")
password = config.get("Reddit", "Password")

r.login(username, password, disable_warning=True)
############

### DATABASE ###
db_username = config.get("MySQL", "Username")
db_password = config.get("MySQL", "Password")
db = MySQLdb.connect(host="localhost",
					 user=db_username,
					 passwd=db_password,
					 db="reddit_comments")
cur = db.cursor()

cur.execute('CREATE TABLE IF NOT EXISTS comments(ID TEXT)')
db.commit()
############

pattern1 = re.compile(r"""(?:(\ss)|season)(?:\s)(?P<s>\d+)(?:.*)(?:(\se)|x|episode|\n)(?:\s)(?P<ep>\d+)""", re.VERBOSE)
pattern2 = re.compile(r"""(?:(\ss)|season)(?P<s>\d+)(?:(\se)|(\sx)|episode|\n)(?:\s)(?P<ep>\d+)""", re.VERBOSE)
pattern3 = re.compile(r"""(?:(\ss)|season)(?:\s)(?P<s>\d+)(?:(\se)|(\sx)|episode|\n)(?P<ep>\d+)""", re.VERBOSE)
pattern4 = re.compile(r"""(?:(\ss)|season)(?P<s>\d+)(?:(\se)|(\sx)|episode|\n)(?P<ep>\d+)""", re.VERBOSE)
pattern5 = re.compile(r"""(?:(\ss)|season)(?P<s>\d+)(?:.*)(?:(\se)|(\sx)|episode|\n)(?P<ep>\d+)""", re.VERBOSE)
pattern6 = re.compile(r"""(?:(\ss)|season)(?:\s)(?P<s>\d+)(?:.*)(?:(\se)|(\sx)|episode|\n)(?P<ep>\d+)""", re.VERBOSE)
pattern7 = re.compile(r"""(?:s|season)(?P<s>\d+)(?:.*)(?:(\se)|(\sx)|episode|\n)(?:\s)(?P<ep>\d+)""", re.VERBOSE)
pattern8 = re.compile(r"""(?:s|season)(?P<s>\d+)(?:e|x|episode|\n)(?P<ep>\d+)""", re.VERBOSE)
pattern9 = re.compile(r"""(?:s|season)(?:\s)(?P<s>\d+)(?:e|x|episode|\n)(?:\s)(?P<ep>\d+)""", re.VERBOSE)
pattern10 = re.compile(r"""(?:s|season)(?P<s>\d+)(?:e|x|episode|\n)(?:\s)(?P<ep>\d+)""", re.VERBOSE)
pattern11 = re.compile(r"""(?:s|season)(?:\s)(?P<s>\d+)(?:e|x|episode|\n)(?P<ep>\d+)""", re.VERBOSE)

pattern12 = re.compile(r"""(?:(\se)|x|episode|\n)(?:\s)(?P<ep>\d+)(?:.*)(?:(\ss)|season)(?:\s)(?P<s>\d+)""", re.VERBOSE)
pattern13 = re.compile(r"""(?:(\se)|x|episode|\n)(?P<ep>\d+)(?:(\ss)|season)(?:\s)(?P<s>\d+)""", re.VERBOSE)
pattern14 = re.compile(r"""(?:(\se)|x|episode|\n)(?:\s)(?P<ep>\d+)(?:(\ss)|season)(?P<s>\d+)""", re.VERBOSE)
pattern15 = re.compile(r"""(?:(\se)|x|episode|\n)(?P<ep>\d+)(?:(\ss)|season)(?P<s>\d+)""", re.VERBOSE)
pattern16 = re.compile(r"""(?:(\se)|x|episode|\n)(?P<ep>\d+)(?:.*)(?:(\ss)|season)(?P<s>\d+)""", re.VERBOSE)
pattern17 = re.compile(r"""(?:(\se)|x|episode|\n)(?:\s)(?P<ep>\d+)(?:.*)(?:(\ss)|season)(?P<s>\d+)""", re.VERBOSE)
pattern18 = re.compile(r"""(?:(\se)|x|episode|\n)(?P<ep>\d+)(?:.*)(?:s|season)(?:\s)(?P<s>\d+)""", re.VERBOSE)
pattern19 = re.compile(r"""(?:e|x|episode|\n)(?P<ep>\d+)(?:s|season)(?P<s>\d+)""", re.VERBOSE)
pattern20 = re.compile(r"""(?:e|x|episode|\n)(?:\s)(?P<ep>\d+)(?:s|season)(?:\s)(?P<s>\d+)""", re.VERBOSE)
pattern21 = re.compile(r"""(?:e|x|episode|\n)(?P<ep>\d+)(?:s|season)(?:\s)(?P<s>\d+)""", re.VERBOSE)
pattern22 = re.compile(r"""(?:e|x|episode|\n)(?:\s)(?P<ep>\d+)(?:s|season)(?P<s>\d+)""", re.VERBOSE)

patterns = [pattern1, pattern2, pattern3, pattern4, pattern5, pattern6, pattern7, pattern8, pattern9, pattern10, pattern11, pattern12,
pattern13, pattern14, pattern15, pattern16, pattern17, pattern18, pattern19, pattern20, pattern21, pattern22 ]

def run_bot():
	subreddit = r.get_subreddit("seinfeld")
	comments = subreddit.get_comments(limit=512)
	for comment in comments:
		comment_text = comment.body.lower()
		for p in patterns:
			m = re.search(p, comment_text)
			ID = comment.id
			cur.execute('SELECT * FROM comments WHERE ID=(%s)', [ID])
			result = cur.fetchone()
			if m and not result and str(comment.author) != str(username):
				try:
					try:
						episode_info = t[tvshow][int(m.group('s'))][int(m.group('ep'))]
						comment.reply('**Seinfeld: Season '+m.group('s')+' Episode '+m.group('ep')+'**'+\
									  '\n___\n'\
									  '\n\n**Episode Name:** '+episode_info['episodename']+\
									  '\n\n**Overview:** '+episode_info['overview']+\
									  '\n\n**Director:** '+episode_info['director']+\
									  '\n\n**Writer(s):** '+episode_info['writer']+\
									  '\n\n**First Aired:** '+episode_info['firstaired']+\
									  '\n\n**Rating:** '+episode_info['rating']+\
									  '\n___\n'\
									  '^| ^Hi! ^I\'m ^a ^bot ^for ^the ^subreddit [^/r/seinfeld](https://www.reddit.com/r/seinfeld) '\
									  '^| [^Help ^me ^improve!](https://github.com/HeadlessChild/reddit-episode-bot) '\
									  '^| [^Report ^a ^bug](https://github.com/HeadlessChild/reddit-episode-bot/issues) '\
									  '^| [^Author](https://www.reddit.com/user/HeadlessChild/) '\
									  '^| ^Data ^from ^[TheTVDB](http://thetvdb.com/) ^|')
						cur.execute('INSERT INTO comments (ID) VALUES (%s)', [ID])
						db.commit()
						syslog.syslog(syslog.LOG_INFO, 'Replied to a comment (ID='+ID+')')
						print("Replied to a comment (ID="+ID+")")
					except (tvdb_exceptions.tvdb_seasonnotfound, tvdb_exceptions.tvdb_episodenotfound, praw.errors.InvalidComment):
						pass
				except praw.errors.RateLimitExceeded as error:
					print("Rate limit exceeded, must sleep for "
							"{} mins".format(float(error.sleep_time / 60)))
					time.sleep(error.sleep_time)
					episode_info = t[tvshow][int(m.group('s'))][int(m.group('ep'))]
					comment.reply('**Seinfeld: Season '+m.group('s')+' Episode '+m.group('ep')+'**'+\
								  '\n___\n'+\
								  '\n\n**Episode Name:** '+episode_info['episodename']+\
								  '\n\n**Overview:** '+episode_info['overview']+\
								  '\n\n**Director:** '+episode_info['director']+\
								  '\n\n**Writer(s):** '+episode_info['writer']+\
								  '\n\n**First Aired:** '+episode_info['firstaired']+\
								  '\n\n**Rating:** '+episode_info['rating']+\
								  '\n___\n'\
								  '^| ^Hi! ^I\'m ^a ^bot ^for ^the ^subreddit [^/r/seinfeld](https://www.reddit.com/r/seinfeld) '\
								  '^| [^Help ^me ^improve!](https://github.com/HeadlessChild/reddit-episode-bot) '\
								  '^| [^Report ^a ^bug](https://github.com/HeadlessChild/reddit-episode-bot/issues) '\
								  '^| [^Author](https://www.reddit.com/user/HeadlessChild/) '\
								  '^| ^Data ^from ^[TheTVDB](http://thetvdb.com/) ^|')
					cur.execute('INSERT INTO comments (ID) VALUES (%s)', [ID])
					db.commit()
					syslog.syslog(syslog.LOG_INFO, 'Replied to a comment (ID='+ID+')')
					print("Replied to a comment (ID="+ID+")")

while True:
	try:
		run_bot()
		time.sleep(25)
	except (praw.errors.HTTPException,
			OpenSSL.SSL.SysCallError,
			requests.exceptions.ReadTimeout,
			requests.exceptions.ConnectionError):
		time.sleep(30)
