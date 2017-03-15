import nltk
import string
import sys
import json
import unicodedata
from collections import Counter
from nltk.corpus import brown
from nltk.corpus import gutenberg
from nltk.corpus import twitter_samples
N = 2
OUT_FILE = "ngrams.json"
RemovePunctTable = {ord(c): None for c in string.punctuation+string.whitespace}

#common_urls.txt gathered from http://s3.amazonaws.com/alexa-static/top-1m.csv.zip

if len(sys.argv) >= 2:
	N = int(sys.argv[1])

if len(sys.argv) >= 3:
	OUT_FILE = sys.argv[2]

def cleanString(strng):
	strng = str(unicodedata.normalize('NFKD', strng).encode('ascii','ignore'))
	return strng.translate(RemovePunctTable).lower()

def getNGrams(source, n):
	return [source[i:i+n] for i in range(len(source)-n)]

def counterToFreq(counter):
	freqHistogram = dict(counter)
	count = sum(freqHistogram.values())
	for elem in freqHistogram:
		freqHistogram[elem] = freqHistogram[elem] / count
	return freqHistogram

print("Analyzing brown corpus")
nltk.download('brown')
brownCnt = Counter(
	getNGrams(
		cleanString("".join(brown.words())),
		N
	)
)

print("Analyzing gutenberg sample")
nltk.download('gutenberg')
gutenCnt = Counter(
	getNGrams(
		cleanString("".join(gutenberg.words())),
		N
	)
)

print("Analyzing twitter sample")
nltk.download('twitter_samples')
twitterCnt = Counter(
	getNGrams(
		cleanString("".join(twitter_samples.strings())),
		N
	)
)

print("Analyzing alexa 1 million urls")
#we handle urls a bit differently to prevent m_ from biasing the results
urlCnt = Counter({})
loader = 0
with open('common_urls_www.txt') as urls:
	for url in urls:
		cnt = Counter(
			getNGrams(
				cleanString(url),
				N
			)
		)
		urlCnt += cnt
		loader += 1
		if loader % 1000 == 0:
			sys.stdout.write(".")
			sys.stdout.flush()
		

nFreq = counterToFreq(brownCnt + gutenCnt + twitterCnt + urlCnt)
nFreq["ngram_size"] = N

with open(OUT_FILE, 'w') as out:
	json.dump(nFreq, out)
