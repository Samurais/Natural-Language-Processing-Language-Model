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

args = parser.parse_args()

corpusFolder = args.c
generateSentence = args.g
addOneSmoothing = args.a
ngram = int(args.n)
graph = args.p

if(ngram > 2 or ngram < 1):
	print("-n flag must be either 1 or 2")
	sys.exit()

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
for corpus in corpuses: # for reach text file in corpus
	for line in corpus: # for each line
		words = line.strip().split() #all words on line
		allWordsList.extend(words)

print("Using first 85 % of corpus to train and 15% of corpus to test")
train = allWordsList[: int(len(allWordsList) * .85)]
test = allWordsList[int(len(allWordsList) * .15):]
distinctWords = set(allWordsList)
counts = Counter(train)
N = sum(counts.values()) #total num of words for training

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
V = len(set(train))

print("Calculating Probabilities...")

if(addOneSmoothing): print("Using add 1 smoothing")
else: print("Using MLE")

#sets known word probs
for word in train:

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


for word in distinctWords:

	if word in test and word not in train:
		probs[word] = [-99, {}]

		if(addOneSmoothing):
			probs[word][0] = math.log(1 / (N + V))
			for word2 in distinctWords:
				probs[word][1][word2] = math.log(1 / V)
		else:
			probs[word][0] = -99
			for word2 in distinctWords:
				probs[word][1][word2] = -99

	for word2 in distinctWords:
		if(probs[word][1].get(word2) == None):
			if(addOneSmoothing):
				probs[word][1][word2] = math.log(1 / V)
			else:
				probs[word][1][word2] = -99

print(probs)

def weightedPick(d):
	r = random.uniform(0, sum(d.values()))
	s = 0.0
	for k, w in d.items():
		s += w
		if r < s: return k
	return k

def getWeightedUnigram():
	d = {}
	for word in probs:
		d[word] = math.exp(probs[word][0])
	return weightedPick(d)

def getWeightedBigram(prevWord):
	d = {}
	for word in probs[prevWord][1]:
		d[word] = probs[prevWord][1].get(word)
	if(len(d) == 0): return None
	return weightedPick(d)
	
if(generateSentence):

	if(ngram == 1):
		for i in range(10):
			print(getWeightedUnigram(), end=" ")

	elif(ngram == 2):
		startWord = getWeightedUnigram()
		print(startWord, end=" ")

		for i in range(10):
			next = getWeightedBigram(startWord)
			if(next == None):
				next = getWeightedUnigram()
			print(next, end=" ")
			startWord = next

def getProbOfWord(word1, word2=None):
	if(word2 == None):
		return probs[word1][0]
	else:
		return probs[word1][1].get(word2, None)

if(graph):
	print("Generating graphs using corpus folder of " + str(corpusFolder))
	#for unigrams
	unigramKeys = probs.keys()
	u = {}
	for word in unigramKeys:
		u[word] = math.exp(getProbOfWord(word)) * 100

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

print()