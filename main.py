import argparse
import math


#get command line arguments
parser = argparse.ArgumentParser(description='LM')
parser.add_argument('-c','--c', help='Corpus Files', required=True, nargs='+')
args = parser.parse_args()

corpusFilesPath = args.c

corpuses = []

#opens all the corpuses
for path in  corpusFilesPath:
	corpus = open(path, 'r')
	corpuses.append(corpus)

#generates unigrams
unigramsMap = {}
bigramsMap = {}

N = 0

for corpus in corpuses: # for reach corpus
	for line in corpus: # for each line
		words = line.strip().split() #all words on line
		for word in words:
			N = N + 1 #increases total number of words
			

			
		for word1, word2 in zip(words, words[1:]): #go through pairs
			print(word1 + " " + word2)

# print(unigramsMap)

# for MLE
