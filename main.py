import argparse
import math
import os
import random
import sys


#get command line arguments
parser = argparse.ArgumentParser(description='LM')
parser.add_argument('-c', help='Corpus Folder', required=True, nargs='+')
parser.add_argument('-g', help='Option to generate sentences', action='store_true', required=False, default=False)
parser.add_argument('-a', help='Option to use add one smoothing', action='store_true', required=False, default=False)
parser.add_argument('-d', help='For debugging', action='store_true', required=False, default=False)
parser.add_argument('-i', help='Option to use custom start word', required=False, default=None)



args = parser.parse_args()

corpusFolders = args.c
generateSentence = args.g
addOneSmoothing = args.a
debugging = args.d
startWord = args.i

corpuses = []

for folder in corpusFolders:
	for dirpath, dirnames, filenames in os.walk(folder):
		for filename in [f for f in filenames if f.endswith(".txt")]:
			corpus = open(os.path.join(dirpath, filename), "r")
			corpuses.append(corpus)

N = 0

counts = {}
allWordsList = []

print("reading corpus...")
for corpus in corpuses: # for reach corpus
	for line in corpus: # for each line
		words = line.strip().split() #all words on line

		#for unigram counts
		for word in words:
			N = N + 1 #increases total number of words
			allWordsList.append(word)
			if(counts.get(word) == None):
				counts[word] = [0 , {}]
			counts[word][0] += 1

		#for bigram counts
		for word1, word2 in zip(words, words[1:]): #go through pairs
			
			if(counts[word1][1].get(word2) == None):
				counts[word1][1][word2] = 0
			counts[word1][1][word2] += 1

allWords = set(allWordsList)

if(startWord != None and startWord not in allWords):
	print("Start word '" + startWord + "' not in corpus. Choose a word in the corpus for your start word.")
	print("Exiting...")
	sys.exit()

#add 0 probs for all words where needed. NEED TO FIX
print("Adding default probs for all words not in bigrams.. (This may take a while)")
for key in counts:
	for word in allWords:
		if(counts[key][1].get(word) == None):
			counts[key][1][word] = 0

#close files
for corpus in corpuses:
	corpus.close()


#set probabilities
probs = {}
V = len(set(allWords))

print("Calculating Probabilities...")
if(addOneSmoothing):
	print("using Add 1...")
else:
	print("Using MLE...")

for word in counts:

	#makes empty unigram prob and empty  dict for bigram probs
	if(probs.get(word) == None):
		probs[word] = [0, {}]

	if(addOneSmoothing):
		probs[word][0] = math.log((counts[word][0] + 1) / (N + V))
		for word2 in counts[word][1]:
			probs[word][1][word2] = math.log((counts[word][1][word2] + 1) / (counts[word][0] + V))

	else:
		if(counts[word][0] == 0):
			probs[word][0] = -9999 #basically 0 prob because you cant do log(0)
		else:
			probs[word][0] = math.log(counts[word][0] / N)
		for word2 in counts[word][1]:
			if(counts[word][1][word2] == 0):
				probs[word][1][word2] = -9999 #basically 0 prob because you cant do log(0)
			else:
				probs[word][1][word2] = math.log(counts[word][1][word2] / counts[word][0])


#helping functions for testing
# def getProb(word1, word2 = None):
# 	if(word2 == None):
# 		return probs[word1][0]
# 	else:
# 		return probs[word1][1][word2]

# def getCount(word1, word2 = None):
# 	if(word2 == None):
# 		return counts[word1][0]
# 	else:
# 		return counts[word1][1][word2]

#really inefficient algorithim to find highest prob
def getHighestProbWordFromPrevWord(prevWord):
	wordlist = probs[prevWord][1]
	maxList = []
	max = -9999
	for word in wordlist:
		if(wordlist[word] > max):
			max = wordlist[word]

	#gets the ties for max and adds them to list
	for word in wordlist:
		if(wordlist[word] == max):
			maxList.append(word)

	#return random one
	return random.choice(maxList)

# def printPossibleWordsFromPrevWord(prevWord):
# 	print(probs[prevWord][1])

#really inefficient to find highest prob
def getHighestProbUnigram():
	#returns the unigram with the highest probability
	maxList = []
	max = -9999
	for word in probs:
		if(probs[word][0] > max):
			max = probs[word][0]

	for word in probs:
		if(probs[word][0] == max):
			maxList.append(word)

	return random.choice(maxList)


if(generateSentence):

	print("Generating sentence using corpus folder(s) of " + str(corpusFolders))
	if(startWord == None):
		startWord = getHighestProbUnigram()
	
	print(startWord, end=" ")
	for x in range(100):
		next = getHighestProbWordFromPrevWord(startWord)
		if(next):
			print(next,end=" ")
			startWord = next
		else:
			break
	print()

if(debugging):
	print(probs)
