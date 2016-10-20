TO RUN

REQUIRED FLAGS
-c is the flag for your corpus folder containing text files
-n is the flag for which ngram size you want to use. This can either be 1 or 2 for unigram or bigram respectively.


OPTIONAL FLAGS
-g Generates sentences
-a Uses add-1 smoothing
-perp Calculates Perplexity

-p Plots the probabilities of the unigrams and bigrams in a pretty bar chart. 
(This will only work if matplotlib is installed as a python module. You can uncomment code that has "UNCOMMENT IF MATPLOTLIB IS INSTALLED TO GET GRAPHS WORKING" if matplotlib is installed) Otherwise, leave the lines commented.


Example execution
python3 main.py -c brown -n 1 -g -a -perp -p
