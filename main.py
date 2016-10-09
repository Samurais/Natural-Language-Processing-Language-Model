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
parser.add_argument('-c', help='Corpus Folder', required=True, nargs='+')
parser.add_argument('-g', help='Option to generate sentences', action='store_true', required=False, default=False)
parser.add_argument('-a', help='Option to use add one smoothing', action='store_true', required=False, default=False)
parser.add_argument('-d', help='For debugging', action='store_true', required=False, default=False)
parser.add_argument('-i', help='Option to use custom start word', required=False, default=None)
parser.add_argument('-p', help='Show Graph Plot of Probs', action='store_true', required=False, default=False)


args = parser.parse_args()

corpusFolders = args.c
generateSentence = args.g
addOneSmoothing = args.a
debugging = args.d
customStartWord = args.i
graph = args.p

corpuses = []

for folder in corpusFolders:
	for dirpath, dirnames, filenames in os.walk(folder):
		for filename in [f for f in filenames if f.endswith(".txt")]:
			corpus = open(os.path.join(dirpath, filename), "r", encoding='utf-8', errors='ignore')
			corpuses.append(corpus)

if(len(corpuses) == 0):
	print("Folder does not exist or contains no text files...")	
	print("Exiting...")
	sys.exit()


allWordsList = []

print("reading corpus...")
for corpus in corpuses: # for reach corpus
	for line in corpus: # for each line
		words = line.strip().split() #all words on line
		allWordsList.extend(words)

#unigram
counts = Counter(allWordsList)
N = sum(counts.values()) #total num of words

#makes room for bigram
for key in counts:
	value = counts[key]
	counts[key] = [value, {}]

#for bigram counts
for word1, word2 in zip(allWordsList, allWordsList[1:]): #go through pairs
	
	if(counts[word1][1].get(word2) == None):
		counts[word1][1][word2] = 0
	counts[word1][1][word2] += 1

#print(counts)

allWords = set(allWordsList)

if(customStartWord != None and customStartWord not in allWords):
	print("Start word '" + customStartWord + "' not in corpus. Choose a word in the corpus for your start word.")
	print("Exiting...")
	sys.exit()

#close files
for corpus in corpuses:
	corpus.close()

#set probabilities
probs = {}
V = len(allWords)

print("Calculating Probabilities...")
if(addOneSmoothing):
	print("using Add 1...")
else:
	print("Using MLE...")

for word in counts:

	#makes empty unigram prob and empty  dict for bigram probs
	if(probs.get(word) == None):
		probs[word] = [0, {}]

	if(counts[word][0] == 0):
		probs[word][0] = -9999 #basically 0 prob because you cant do log(0)
	else:
		probs[word][0] = math.log(counts[word][0] / N)
	for word2 in counts[word][1]:
		if(counts[word][1][word2] == 0):
			probs[word][1][word2] = -9999 #basically 0 prob because you cant do log(0)
		else:
			probs[word][1][word2] = math.log(counts[word][1][word2] / counts[word][0])

print(probs)

def weightedPick(d):
	values = [x * -1 for x in d.values()]
	r = random.uniform(0, sum(values))
	s = 0.0
	for key, weight, in d.items():
		weight = weight * -1
		s = s + weight 
		#if r >= s: print(key + " " + str(weight))
		if r > s: return key
	return key

def getWeightedUnigram():
	d = {}
	for key in probs:
		d[key] = probs[key][0]
	return weightedPick(d)

def getWeightedBigram(prevWord):
	d = {}
	for key in probs[prevWord][1]:
		d[key] = probs[prevWord][1].get(key)
	if(len(d) == 0): return None
	return weightedPick(d)

def getProbOfWord(word1, word2=None):
	if(word2 == None):
		return probs[word1][0]
	else:
		return probs[word1][1].get(word2, None)

if(generateSentence):

	output = []
	print("Generating sentence using corpus folder(s) of " + str(corpusFolders))
	print()
	if(customStartWord == None):
		startWord = getWeightedUnigram()
	else:
		startWord = customStartWord
	
	print(startWord, end=" ")

	count = []
	for x in range(100):
		next = getWeightedBigram(startWord)
		if(next != None):
			print(next,end=" ")
			#print(next)
			startWord = next
		else:
			startWord = getWeightedUnigram()
			print(startWord,end=" ")

	print()

if(graph):
	print("Generating graphs using corpus folder(s) of " + str(corpusFolders))
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


if(debugging and customStartWord):
	print(probs[customStartWord])

print()