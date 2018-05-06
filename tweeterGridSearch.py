from tweeterAPI.tweeterBrowser import tweeterBrowser
import time

def main():
	gridFilename = 'GridFile.csv'
	sinceDate = '2018-03-01'
	untilDate = '2018-04-01'
	dictionaryFilename = 'concepts.csv'

	limit = 5

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
			tempLine = conceptLine.split(',')[:]
			crimeConcept = tempLine[0]
			crimeLine = tempLine
			relatedTermCrime[crimeConcept] = crimeLine

	#Set params
	maxtweets = 1000
	radius = '30km'
	enable = True

	if enable: 
		#Open output File
		outputFileName = 'TweetSearch'+sinceDate+'-'+untilDate+'_grid'+gridFilename.split('.')[0]+'.csv'

		with open('./Results/'+outputFileName, 'w') as outputFile:			
			checkDuplicates = []
			appendedResults = []
			print >> outputFile, "Username;DateTime;Retweets;Text;Hashtag;ID;Permanentlink;Concept;Latitud;Longitud;Radius"

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
						startingBrowser = tweeterBrowser(params)

						try:
							results = startingBrowser.getTweets()
						except Exception as error:
							continue
						for result in results:
		#						printResults = result+';'+crime+';'+concept+';'+geolocation[1][1:]+';'+geolocation[0]+';'+radius
							printResults = result+';'+geolocation[1][1:]+';'+geolocation[0]+';'+radius
							appendedResults.append(printResults)
							tweetId = printResults.split(';')[-7]
							if not(tweetId in checkDuplicates):
								checkDuplicates.append(tweetId)
								print >> outputFile, printResults

if __name__ == '__main__':
	main()