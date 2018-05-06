import urllib,urllib2,json,re,datetime,sys,cookielib

from unidecode import unidecode
from pyquery import PyQuery

import time

class Tweet:
	def __init__(self):
		pass

class tweeterBrowser:
	params = {}

	def __init__(self, params=None):
		if params:
			self.setParams(params)

	def setParams(self, params):
		self.params = dict(params)

	def getTweets(self):
		searchParams = dict(self.params)
		
		if 'maxTweets' in self.params.keys():
			maxTweets = self.params['maxTweets']
		else:
			maxTweets = 10

		refreshCursor = ''
		active = True
		result = []
		bufferLength = 15000

		if searchParams:
			while active:
				try:
					currentJson = tweeterBrowser.getJson(searchParams, refreshCursor)
				except Exception as error:
					print error
					raise Exception(searchParams)
					continue
				refreshCursor = currentJson['min_position']

				if len(currentJson['items_html'].strip()) == 0:
					break

				tweets = PyQuery(currentJson['items_html'])('div.js-stream-tweet')

				if len(tweets) == 0:
					break

				for tweetHTML in tweets:
					tweetPQ = PyQuery(tweetHTML)
					tweet = Tweet()
					usernameTweet = tweetPQ("span:first.username.u-dir b").text();
					txt = re.sub(r"\s+", " ", tweetPQ("p.js-tweet-text").text().replace('# ', '#').replace('@ ', '@'));
					retweets = int(tweetPQ("span.ProfileTweet-action--retweet span.ProfileTweet-actionCount").attr("data-tweet-stat-count").replace(",", ""));
					favorites = int(tweetPQ("span.ProfileTweet-action--favorite span.ProfileTweet-actionCount").attr("data-tweet-stat-count").replace(",", ""));
					dateSec = int(tweetPQ("small.time span.js-short-timestamp").attr("data-time"));
					id = tweetPQ.attr("data-tweet-id");
					permalink = tweetPQ.attr("data-permalink-path");

					tweet.id = id
					tweet.permalink = 'https://twitter.com' + permalink
					tweet.username = usernameTweet
					tweet.text = txt
					tweet.date = datetime.datetime.fromtimestamp(dateSec)
					tweet.retweets = retweets
					tweet.favorites = favorites
					tweet.mentions = " ".join(re.compile('(@\\w*)').findall(tweet.text))
					tweet.hashtags = " ".join(re.compile('(#\\w*)').findall(tweet.text))

					result.append(tweet)
					time.sleep(5)
			
					if maxTweets > 0 and len(result) >= maxTweets:
						active = False
						break

			returnResults = []

			for t in result:
				returnResults.append('%s;%s;%d;%s;%s;%s;%s' % (t.username, t.date.strftime("%Y-%m-%d %H:%M"), t.retweets, unidecode(t.text), t.hashtags, t.id, t.permalink))
			return returnResults

		else:
			print 'no params to search'
			return False

	@staticmethod
	def getJson(searchParams, refreshCursor):
		cookieJar = cookielib.CookieJar()
		queryStructure = ''
		url = "https://twitter.com/i/search/timeline?f=tweets&q=%s&src=typd&max_position=%s"
#		url = "https://twitter.com/i/search/timeline?f=tweets&q=%s&src=typd"

		queryStructureOrdered = ['','','','','']

		for param in searchParams.keys():
			if param == 'username':
				queryStructureOrdered[0] = ' from:' + searchParams[param]
			if param == 'query':
				queryStructureOrdered[1] = ' ' + searchParams[param]
			if param == 'geocode':
				queryStructureOrdered[2] = ' geocode:' + searchParams[param]
			if param == 'since':
				queryStructureOrdered[3] = ' since:' + searchParams[param]
			if param == 'until':
				queryStructureOrdered[4] = ' until:' + searchParams[param]
		
		queryStructure = ''.join(queryStructureOrdered)
#		print urllib.quote(queryStructure)

		headers = [
			('Host', "twitter.com"),
			('User-Agent', "Mozilla/5.0 (Windows NT 6.1; Win64; x64)"),
			('Accept', "application/json, text/javascript, */*; q=0.01"),
			('Accept-Language', "de,en-US;q=0.7,en;q=0.3"),
			('X-Requested-With', "XMLHttpRequest"),
			('Referer', url),
			('Connection', "keep-alive")
		]

		url = url % (urllib.quote(queryStructure), refreshCursor)
		opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookieJar))
		opener.addheaders = headers

		try:
			response = opener.open(url)
			jsonResponse = response.read()
			print url
		except:
			print 'error'
			raise Exception('Exception')

		dataJson = json.loads(jsonResponse)
		return dataJson