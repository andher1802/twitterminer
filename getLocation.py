import oauth2 as oauth
import json
import io
import re

#Username;DateTime;Retweets;Text;Hashtag;ID;Permanentlink;Concept;Latitud;Longitud;Radius

def setAuth():
	consumer = oauth.Consumer(key=CONSUMER_KEY, secret=CONSUMER_SECRET)
	access_token = oauth.Token(key=ACCESS_TOKEN, secret=ACCESS_SECRET)
	client = oauth.Client(consumer, access_token)
	return client

def main():
	client = setAuth()
	filename = 'PlebicitoTweetSearch2016-09-30-2016-10-01_gridGridFile_Dictconcepts.csv.csv'
	filenameResults = 'locatedResults.csv'
	filenameSupportResults = 'complementaryResults.csv'
	encoding = 'utf-8'
	startPoint = 0

	with open ('./Results/'+filenameSupportResults, 'w') as supportOutputFile:
		with io.open ('./Results/'+filenameResults, 'w', encoding=encoding) as outputFile:
			# outputFile.write(unichr(9).join([
			# 	unicode('TweetID'), 
			# 	unicode('ID'),
			# 	unicode('Username'), 
			# 	unicode('DateTime'), 
			# 	unicode('Retweets'), 
			# 	unicode('Hashtag'),
			# 	unicode('Concept'),
			# 	unicode('Latitud'),
			# 	unicode('Longitud'),
			# 	unicode('Radius'),
			# 	unicode('TypeCoordinatesLocation'),
			# 	unicode('Real Latitud'),
			# 	unicode('Real Longitud'),
			# 	unicode('Reported location by User'),
			# 	unicode('created_at'),
			# 	unicode('text'), '\n'
			# 	]))

			supportOutputFile.write(unichr(9).join([unicode('TweetID'),unicode('Place')]))			

			with io.open ('./Results/'+filename, 'r', encoding=encoding) as inputFile:
				linesResults = inputFile.readlines()
				counterCoordinates = 0

				outputBuffer = []
				supportBuffer = []
				idCounter = startPoint

#				for line in linesResults[1+startPoint:startPoint+900]:
				for line in linesResults[1+startPoint:]:
					print line
					idCounter += 1
					lineList = line.rstrip().split(';')
					idString = lineList[-5]
					timeline_endpoint = "https://api.twitter.com/1.1/statuses/show/"+idString+".json"

					try:
						response, data = client.request(timeline_endpoint)
						tweets = json.loads(data)
					except:
						print "Twitter weird response. Try to see on browser: %s" % tweets
						sys.exit()
						return
	
					outputLine = []
					supportOutputLine = []

					outputLine.append(unicode(idCounter))
					supportOutputLine.append(unicode(idCounter))
					outputLine.append(unicode(lineList[-5]))
					outputLine.append(lineList[0])
					outputLine.append(lineList[1])
					outputLine.append(lineList[2])
					outputLine.append(lineList[-7])
					outputLine.append(lineList[-4])
					outputLine.append(lineList[-3])
					outputLine.append(lineList[-2])
					outputLine.append(lineList[-1])

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
					if 'place' in tweets.keys():
						supportOutputLine.append(unicode(tweets['place']))
					else:
						supportOutputLine.append(u'NA')
					if 'user' in tweets.keys():
						outputLine.append(unicode(tweets['user']['location']))
					else:
						outputLine.append(u'NA')
					if 'created_at' in tweets.keys():
						outputLine.append(unicode(tweets['created_at']))
					else:
						outputLine.append(u'NA')
					if 'text' in tweets.keys():
						tempText = ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", tweets['text']).split())
						tempText = tempText.replace('\n', ' ')
						tempText = tempText.replace('"', '')
						tempText = tempText.lower()
						outputLine.append(tempText)

					outputLine.append('\n')
					supportOutputLine.append('\n')

					outputFile.write(unichr(9).join(outputLine))
					supportOutputFile.write(unichr(9).join(supportOutputLine))

if __name__ == '__main__':
	main()