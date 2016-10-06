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

allWords = set(allWordsList)

if(customStartWord != None and customStartWord not in allWords):
	print("Start word '" + customStartWord + "' not in corpus. Choose a word in the corpus for your start word.")
	print("Exiting...")
	sys.exit()

# #add 0 probs for all words where needed. NEED TO FIX
# print("Adding default probs for all words not in bigrams.. (This may take a while)")
# for key in counts:
# 	for word in allWords:
# 		if(counts[key][1].get(word) == None):
# 			counts[key][1][word] = 0

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

#really inefficient algorithim to find highest prob
def getHighestProbWordFromPrevWord(prevWord):
	wordlist = probs[prevWord][1]

	if(len(wordlist) == 0):
		return None

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
	if(customStartWord == None):
		startWord = getHighestProbUnigram()
	else:
		startWord = customStartWord
	
	print(startWord, end=" ")
	for x in range(100):
		next = getHighestProbWordFromPrevWord(startWord)
		if(next != None):
			print(next,end=" ")
			startWord = next
		else:
			break
	print()

if(graph):
	#for unigrams
	keys = probs.keys()
	values = [probs[x][0] for x in keys]
	#print(values)
	u10 = dict(zip(keys, values))
	#print(u10)
	words = heapq.nlargest(20, u10, key=u10.get)
	values = []
	for word in words:
		values.append(math.exp(probs[word][0]) * 100)
	print(values[0])

	plt.title("Unigrams Probability")
	plt.xlabel('Word')
	plt.ylabel('Prob %')
	plt.bar(range(len(values)), values)
	plt.xticks(range(len(words)), words)
	plt.show()

if(debugging and customStartWord):
	print(probs[customStartWord])
