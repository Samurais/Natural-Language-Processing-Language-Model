import argparse
import math
import os
import random
import sys
from collections import Counter
import matplotlib.pyplot as plt
import heapq

plt.style.use('ggplot')

#get command line arguments
parser = argparse.ArgumentParser(description='LM')
parser.add_argument('-c', help='Corpus Folder', required=True)
parser.add_argument('-g', help='Option to generate sentences', action='store_true', required=False, default=False)
parser.add_argument('-a', help='Option to use add one smoothing', action='store_true', required=False, default=False)
parser.add_argument('-p', help='Show Graph Plot of Probs', action='store_true', required=False, default=False)
parser.add_argument('-n', help='N-Gram to use', required=True)
parser.add_argument('-perp', help='Calculate Perplexity', action='store_true', required=False, default=False)

args = parser.parse_args()

#sets command lines arguments = to respective variable
corpusFolder = args.c
generateSentence = args.g
addOneSmoothing = args.a
ngram = int(args.n)
graph = args.p
perplexity = args.perp

#user must choose bigram or unigram
if(ngram > 2 or ngram < 1):
	print("-n flag must be either 1 or 2")
	sys.exit()

#gets all the text files from the folder
corpuses = []
for dirpath, dirnames, filenames in os.walk(corpusFolder):
	for filename in [f for f in filenames if f.endswith(".txt")]:
		corpus = open(os.path.join(dirpath, filename), "r", encoding='utf-8', errors='ignore')
		corpuses.append(corpus)

if(len(corpuses) == 0):
	print("Folder does not exist or contains no text files...")	
	print("Exiting...")
	sys.exit()

allWordsList = []

print("reading corpus...")

#appends every word to a list
for corpus in corpuses: # for reach text file in corpus
	for line in corpus: # for each line
		words = line.strip().split() #all words on line
		allWordsList.extend(words)

print("Using first 80 % of corpus to train and 20% of corpus to test")
#splits corpus into 80% training and 20% testing
train = allWordsList[: int(len(allWordsList) * .80)]
test = allWordsList[int(len(allWordsList) * .80):]
distinctWords = set(allWordsList) #distinct words
counts = Counter(train) #gets the counts of the words used for training
N = len(train) #total num of words for train and test words
V = len(set(train)) #total number of train and Test words

print("Calculating Counts...")
#makes room for bigram
for word in counts:
	count = counts[word]
	counts[word] = [count, {}]

#for bigram count
for word1, word2 in zip(train, train[1:]): #go through pairs
	
	if(counts[word1][1].get(word2) == None):
		counts[word1][1][word2] = 0
	counts[word1][1][word2] += 1

#close files
for corpus in corpuses:
	corpus.close()

#set probabilities
probs = {}

print("Calculating Probabilities...")

if(addOneSmoothing): print("Using add 1 smoothing")
else: print("Using MLE")

#sets known word probs
for word in counts:
	#print(word)
	#makes empty unigram prob and empty dict for bigram probs
	if(probs.get(word) == None):
		probs[word] = [-99, {}]

	if(addOneSmoothing):
		probs[word][0] = math.log((counts[word][0] + 1) / (N + V))

		for word2 in counts[word][1]:
			probs[word][1][word2] = math.log((counts[word][1][word2] + 1) / (counts[word][0] + V))
	else:
		probs[word][0] = math.log(counts[word][0] / N)
		for word2 in counts[word][1]:
			probs[word][1][word2] = math.log(counts[word][1][word2] / counts[word][0])

#performs weighted pick of dictionary key based on value
def weightedPick(d):
	r = random.uniform(0, sum(d.values()))
	s = 0.0
	for k, w in d.items():
		s += w
		if r < s: return k
	return k

#chooses a unigram by weight
def getWeightedUnigram():
	d = {}
	for word in probs:
		d[word] = math.exp(probs[word][0])
	return weightedPick(d)

#chooses a bigram from a given word by weight
def getWeightedBigram(prevWord):
	d = {}
	for word in probs[prevWord][1]:
		d[word] = math.exp(probs[prevWord][1].get(word))
	if(len(d) == 0): return None
	return weightedPick(d)

#generates sentence
if(generateSentence):

	for i in range(5):
		sentenceLength = 10
		print()


		if(ngram == 1): #if doing unigram model
			for i in range(sentenceLength):
				print(getWeightedUnigram(), end=" ")

		elif(ngram == 2): #if doing bigram model
			startWord = getWeightedUnigram()
			print(startWord, end=" ")

			for i in range(sentenceLength):
				next = getWeightedBigram(startWord)
				if(next == None):
					next = getWeightedUnigram()
				print(next, end=" ")
				startWord = next
		print()

#gets probability of a word
def getProbOfWord(word1, word2=None):
	if(word2 == None):
		if(probs.get(word1) == None):
			if(addOneSmoothing):
				return math.log(1 / (N + V))
			else:
				return -99
		else:
			return probs[word1][0]
	else:
		if(probs.get(word1) == None):
			if(addOneSmoothing):
				return math.log(1 / V)
			else:
				return -99
		if(probs[word1][1].get(word2) == None):
			if(addOneSmoothing):
				return math.log(1 / (counts[word1][0] + V))
			else:
				return -99
		return probs[word1][1][word2]

#calculates perplexity
if(perplexity):
	pp = 0

	if(ngram == 1):
		for word in test:
			prob = getProbOfWord(word)
			pp = pp + prob
	else:
		if(len(test) > 1): #if theres more than one word in the test words
			startWord = test[0]
			for word in test[1:]:
				probBi = getProbOfWord(startWord, word)
				probUni = getProbOfWord(word)

				#uses the bigram prob if it is good, otherwise just use unigram
				if(probBi > probUni):
					pp = pp + probBi
				else:
					pp = pp + probUni

				startWord = word
		else:
			pp = getProbOfWord(test[0])

	M = len(test)
	print("Perplexity = (exp(" + str(pp) + "))" + "^(-1/" + str(M) + ")")

#generates graphs
if(graph):
	print("Generating graphs using corpus folder of " + str(corpusFolder))


 	#unigrams
	unigramKeys = probs.keys()
	u = {}
	for word in unigramKeys: #converts to percentage
		u[word] = math.exp(getProbOfWord(word)) * 100

	#gets top 15 unigrams by prob
	unigramWords = heapq.nlargest(15, u, key=u.get)
	unigramValues = []
	for word in unigramWords:
		unigramValues.append(u[word])

	#bigrams
	b = {}
	for word1 in unigramKeys:
		for word2 in probs[word1][1].keys():
			b[word1 + " " + word2] = math.exp(getProbOfWord(word1) + getProbOfWord(word1, word2)) * 100

	bigramWords = heapq.nlargest(15, b, key=b.get)
	bigramValues = []
	for word in bigramWords:
		bigramValues.append(b[word])


	#plots everything
	fig, (uniplot, biplot) = plt.subplots(nrows=2)

	biplot.bar(range(len(bigramValues)), bigramValues)
	biplot.set_xlabel("Word")
	biplot.set_ylabel("Probability %")
	biplot.set_xticks(range(len(bigramWords)))
	biplot.set_xticklabels(bigramWords)

	uniplot.bar(range(len(unigramValues)), unigramValues)
	uniplot.set_xlabel("Word")
	uniplot.set_ylabel("Probability %")
	uniplot.set_xticks(range(len(unigramWords)))
	uniplot.set_xticklabels(unigramWords)

	plt.subplots_adjust(hspace = 10)
	plt.tight_layout()

	plt.suptitle("Top 15 Unigram and Bigram Probabilities")
	plt.show()
