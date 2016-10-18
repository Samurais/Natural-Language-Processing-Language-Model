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

#sets command lines arguments equal to respective variable
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
		corpus = open(os.path.join(dirpath, filename), "r")
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

print("Using first 80 % of corpus to train and last 20% of corpus to test")
#splits corpus into 80% training and 20% testing
split = int(len(allWordsList) * .80)
train = allWordsList[: split]
test = allWordsList[split:]
counts = Counter(train) #gets the counts of the words used for training
N = len(train) #total num of words for train 
V = len(set(allWordsList)) # num of unique words

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

print("Calculating Probabilities...")

if(addOneSmoothing): print("Using add 1 smoothing...")
else: print("Using MLE...")

def getProbOfBigram(word1, word2):

	if word1 not in counts:
		if(addOneSmoothing):
			return math.log(1 / V)
		else:
			return -99

	if(word2 not in counts[word1][1]):
		if(addOneSmoothing):
			return math.log(1 / (counts[word1][0] + V))
		else:
			return -99

	if(addOneSmoothing):
		return math.log(counts[word1][1][word2] / (counts[word1][0] + V))
	else:
		return math.log(counts[word1][1][word2] / counts[word1][0])

def getProbOfUnigram(word1):
	if word1 in counts:
		if(addOneSmoothing):
			return math.log(counts[word1][0] / (N + V))
		else:
			return math.log(counts[word1][0] / N)
	else:
		if(addOneSmoothing):
			return math.log(1 / (N + V))
		else:
			return -99

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
	for word in set(allWordsList):
		d[word] = math.exp(getProbOfUnigram(word))
	return weightedPick(d)

#chooses a bigram from a given word by weight
def getWeightedBigram(prevWord):
	d = {}
	for word in set(allWordsList):
		d[word] = math.exp(getProbOfWord(prevWord, word))
	return weightedPick(d)

#generates sentence
if(generateSentence):

	for i in range(5):
		sentenceLength = 20
		print()

		if(ngram == 1): #if doing unigram model
			for i in range(sentenceLength):
				print(getWeightedUnigram(), end=" ")

		elif(ngram == 2): #if doing bigram model
			startWord = getWeightedUnigram()
			print(startWord, end=" ")

			#feeds the output as the previous word to use as input for bigram prediction
			for i in range(sentenceLength):
				next = getWeightedBigram(startWord)
				if(next == None):
					#if the previous word has no word after it, pick a unigram
					next = getWeightedUnigram()
				print(next, end=" ")
				startWord = next
		print()
	print()
#calculates perplexity
if(perplexity):
	pp = 0

	if(ngram == 1):
		for word in test:
			prob = getProbOfUnigram(word)
			pp = pp + prob
	else:
		if(len(test) > 1): #if theres more than one word in the test words
			startWord = test[0]
			for word in test[1:]:
				probBi = getProbOfBigram(startWord, word)
				probUni = getProbOfUnigram(word)

				#uses the bigram prob if it is good, otherwise just use unigram
				if(probBi > probUni):
					pp = pp + probBi
				else:
					pp = pp + probUni

				startWord = word
		else:
			pp = getProbOfUnigram(test[0])

	M = len(test)
	print("Perplexity = (exp(" + str(pp) + "))" + "^(-1/" + str(M) + ")")

#generates graphs
if(graph):
	print("Generating graphs using corpus folder of " + str(corpusFolder))

 	#unigrams
	unigramKeys = counts.keys()
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
		for word2 in counts[word1][1].keys():
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
