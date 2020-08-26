#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
Script to to add sentiments:
(1) read each tweet for each topic line by line and add sentiment to json 
(2) output to file

input: directory of tweets to label
output: sentiment-labeled tweet files

'''

import sys
import json
import os
import textblob
from textblob import TextBlob

def sentiment(input_file, output_file):

	with open(input_file, 'r') as f:
		with open(output_file, 'w') as outfile:
			for line in f:
				line = line.strip()
				if line:
					tweet = json.loads(line)
					text = tweet['full_text']
					blob = TextBlob(text)
					sent = blob.sentiment
					tweet['sentiment'] = sent.polarity
					json.dump(tweet, outfile)
					outfile.write('\n')


def add_sentiment(input_dir, output_dir):

	for data_file in os.listdir(input_dir):
		if not data_file.startswith('.'):
			print('calculating sentiment: ' + data_file)
			sentiment(input_dir + data_file, output_dir + data_file)
			print('finished: ' + data_file)
			print()


if __name__ == "__main__":

	input_dir = sys.argv[1]
	sents_dir = sys.argv[2]

	if not os.path.exists(sents_dir):
		os.mkdir(sents_dir)

	add_sentiment(input_dir, sents_dir)

