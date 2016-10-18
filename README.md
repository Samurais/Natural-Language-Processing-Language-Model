TO RUN

Required Flags
-c is the flag for your corpus folder containing text files
-n is the flag for which ngram size you want to use. This can either be 1 or 2 for unigram or bigram respectively.

Optional Flags
-p Plots the probabilities of the unigrams and bigrams
-g Generates sentences
-a Uses add-1 smoothing
-perp Calculates Perplexity

Example execution
python3 main.py -c brown -n 1 -p -g -a -perp
