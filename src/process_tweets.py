#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
Script to preprocess tweet data
(1) remove urls, punctuation and emojis from tweet text, tokenize
(2) reformat dates
(3) print output to new json file -> to be used in search

input: unprocessed data directory
output: stripped tweet files

'''

import sys
import json
import os
import re
import nltk
from nltk.corpus import stopwords
import string


def clean_tweets(tweet, stop_words):

	new_tweet = tweet
	new_tweet['tokens'] = re.sub(r"http\S+", "", new_tweet['full_text']).lower().strip()
	new_tweet['tokens'] = re.sub(r"@\S+", "", new_tweet['tokens']).strip()
	new_tweet['tokens'] = re.sub(r'[^\s\w\d]', "", new_tweet['tokens'])
	new_tweet['tokens'] = nltk.word_tokenize(new_tweet['tokens'])
	new_tweet['tokens'] = [t for t in new_tweet['tokens'] if t not in stop_words and t not in string.punctuation]
	date = new_tweet['created_at']
	date_tokens = date.split(' ')
	new_date = ' '.join((date_tokens[1], date_tokens[2], date_tokens[-1]))
	new_tweet['date'] = new_date
	del new_tweet['created_at']
	return new_tweet

def process_tweets(data_file, output_file):

	stop_words = stopwords.words('english')
	with open(data_file, 'r', encoding="ISO-8859-1") as f:
		with open(output_file, 'w') as outfile:
			for line in f:
				line = line.strip()
				if line:
					tweet = json.loads(line)
					cleaned = clean_tweets(tweet, stop_words)
					json.dump(cleaned, outfile)
					outfile.write('\n')


if __name__ == "__main__":

	data_dir = sys.argv[1] 
	output_dir = sys.argv[2]

	if not os.path.exists(output_dir):
		os.mkdir(output_dir)

	for data_file in os.listdir(data_dir):
		if not data_file.startswith('.'):
			print('processing: ' + data_file)
			process_tweets(data_dir + data_file, output_dir + data_file)
			print('finished: ' + data_file)
			print()

