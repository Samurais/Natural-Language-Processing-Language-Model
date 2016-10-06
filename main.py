import argparse
import math
import os


#get command line arguments
parser = argparse.ArgumentParser(description='LM')
parser.add_argument('-c', help='Corpus Folder', required=True, nargs='+')
parser.add_argument('-g', help='Option to generate sentences', required=False, default=False)
args = parser.parse_args()

corpusFolders = args.c
generateSentence = args.g

corpuses = []

for folder in corpusFolders:
	for dirpath, dirnames, filenames in os.walk(folder):
		for filename in [f for f in filenames if f.endswith(".txt")]:
			corpus = open(os.path.join(dirpath, filename), "r")
			corpuses.append(corpus)


N = 0

counts = {}

for corpus in corpuses: # for reach corpus
	for line in corpus: # for each line
		words = line.strip().split() #all words on line

		#for unigram counts
		for word in words:
			N = N + 1 #increases total number of words
			if(counts.get(word) == None):
				counts[word] = [0 , {}]
			counts[word][0] += 1

		#for bigram counts
		for word1, word2 in zip(words, words[1:]): #go through pairs
			
			if(counts[word1][1].get(word2) == None):
				counts[word1][1][word2] = 0
			counts[word1][1][word2] += 1


#close files
for corpus in corpuses:
	corpus.close()

probs = {}

for word in counts:
	if(probs.get(word) == None):
		probs[word] = [0, {}]
	probs[word][0] = math.log(counts[word][0] / N)

	for word2 in counts[word][1]:
		probs[word][1][word2] = math.log(counts[word][1][word2] / counts[word][0])

def getProb(word1, word2 = None):
	if(word2 == None):
		return probs[word1][0]
	else:
		return probs[word1][1][word2]

def getCount(word1, word2 = None):
	if(word2 == None):
		return counts[word1][0]
	else:
		return counts[word1][1][word2]

def getHighestProbWordFromPrevWord(prevWord):
	wordlist = probs[prevWord][1]
	return max(wordlist, key=wordlist.get)

def printPossibleWordsFromPrevWord(prevWord):
	print(probs[prevWord][1])

printPossibleWordsFromPrevWord("Alex")
print(getHighestProbWordFromPrevWord("Alex"))
