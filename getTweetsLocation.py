from tweeterAPI.tweeterBrowser import tweeterBrowser
import io
import oauth2 as oauth
import json
import re
import sys

import time
from datetime import datetime

def setAuth():
	ACCESS_TOKEN = '570259739-4u7BUZr6jEkwOPNnh46b3yOupCditBI6fVaT34aR'
	ACCESS_SECRET = 'YFpqCtdEVglZs4W7PbeL10Mq8zHYPdExvVZ8u7I3GPp65'
	CONSUMER_KEY = 'GsaV4E0nUX8ns4nNMmZihEXUD'
	CONSUMER_SECRET = 'zED1r57gysR7aL9dguhWHZxgSknf60juzGCRzFSzFaebsczR3O'
	consumer = oauth.Consumer(key=CONSUMER_KEY, secret=CONSUMER_SECRET)
	access_token = oauth.Token(key=ACCESS_TOKEN, secret=ACCESS_SECRET)
	client = oauth.Client(consumer, access_token)
	return client

def main():
	gridFilename = 'GridFile.csv'
	dictionaryFilename = 'concepts.csv'
	sinceDate = '2018-02-01'
	untilDate = '2018-04-30'

	#Reading grid file
	with open('./sources/'+gridFilename, 'r') as GridFile:
		gridFileBuffer = GridFile.readlines()
		coordinatesBuffer = []

		for element in gridFileBuffer[:]:
			stringCoordinates = element[1:-2] # lon, lat
			coordinatesBuffer.append(stringCoordinates.split(','))

	#Open dict file here
	relatedTermCrime = {}
	with open ('./sources/'+dictionaryFilename, 'r') as dictFile:
		dictBuffer = dictFile.readlines()
		for conceptLine in dictBuffer:
			tempLine = conceptLine.strip().split(',')[:]
			crimeConcept = tempLine[0]
			crimeLine = tempLine
			relatedTermCrime[crimeConcept] = crimeLine

	#Set params
	maxtweets = 10000
	radius = '40km'
	outputFileName = 'ColombianElections_'+sinceDate+'-'+untilDate+'_grid'+gridFilename.split('.')[0]+'.csv'
	encoding = 'utf-8'
	checkduplicates = []

	with io.open('./Results/'+outputFileName, 'w', encoding=encoding) as outputFile:		
		for crime, relatedConcepts in relatedTermCrime.iteritems():
			for concept in relatedConcepts:
				for geolocation in coordinatesBuffer:
					params = {
					'query':concept,
					'geocode': geolocation[1][1:]+','+geolocation[0]+','+radius,
					'since':sinceDate,
					'until':untilDate,
					'maxTweets':maxtweets,
					}

					print params
					startingBrowser = tweeterBrowser(params)
					try:
						results = startingBrowser.getTweets()
					except(Exception):
						print Exception
						sys.exit()

					client = setAuth()

					errorCounter = 0 
					for result in results:
						idTweet = result.split(';')[-2]
						if idTweet in checkduplicates:
							continue
						timeline_endpoint = "https://api.twitter.com/1.1/statuses/show/"+idTweet+".json"
						try:
							response, data = client.request(timeline_endpoint)
							tweets = json.loads(data)
						except:
							print "Twitter weird response. Try to see on browser: %s" % tweets
							continue

						if 'x-rate-limit-remaining' in response.keys(): 
							print response['x-rate-limit-remaining']
							if int(response['x-rate-limit-remaining']) <= 1:
								timeReset = int(response['x-rate-limit-reset'])
								systemTime = int(time.time())
								print timeReset - systemTime
								time.sleep(timeReset - systemTime)
						else:
							errorCounter += 1
							if errorCounter < 20:
								print "error found at:"
								continue
							else:
								print "restart location search"
								continue

						outputLine = []
						outputLine.append(result.split(';')[-2])
						if 'user' in tweets.keys():
							outputLine.append(unicode(tweets['user']['name']))
							outputLine.append(unicode(tweets['user']['screen_name']))
#							outputLine.append(unicode(tweets['user']['location']))
						else:
							outputLine.append(u'NA')
						if 'created_at' in tweets.keys():
							outputLine.append(unicode(tweets['created_at']))
						else:
							outputLine.append(u'NA')
						if 'coordinates' in tweets.keys():
							if tweets['coordinates']:
								outputLine.append(unicode(tweets['coordinates']['type']))
								outputLine.append(unicode(tweets['coordinates']['coordinates'][1]))
								outputLine.append(unicode(tweets['coordinates']['coordinates'][0]))
							else:
								outputLine.append(u'NA')
								outputLine.append(u'NA')
								outputLine.append(u'NA')
						else:
							outputLine.append(u'NA')
							outputLine.append(u'NA')
							outputLine.append(u'NA')
						if 'text' in tweets.keys():
							tempText = ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", tweets['text']).split())
							tempText = tempText.replace('\n', ' ')
							tempText = tempText.replace('"', '')
							tempText = tempText.lower()
							outputLine.append(tempText)
						outputLine.append('\n')
						outputFile.write(unichr(9).join(outputLine))
						checkduplicates.append(idTweet)

if __name__ == '__main__':
	main()