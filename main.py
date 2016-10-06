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
				counts[word1][1][word2] = 1
			else:
				counts[word1][1][word2] += 1

print(counts["apple"])

#close files
for corpus in corpuses:
	corpus.close()