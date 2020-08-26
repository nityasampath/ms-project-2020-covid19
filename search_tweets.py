#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
Script to search data for relevant tweets:
(1) build lists of keywords/hastags for each topic
(2) search for tweets:
	tweets that have at least two keywords for a single topic are relevant to that topic
	tweets that have a hashtag for a topic are relevent to that topic
(3) print relevant lists to output file

input: directory of tweet files to search
output: relevant lists for each topic

'''

import sys
import json
import os


def search_tweets(input_dir, keywords, hashtags, output_dir):
	
	with open(output_dir + "masks.json", 'w') as masks_out, open(output_dir + "social distancing.json", 'w') as sd_out, open(output_dir + "quarantine.json", 'w') as quaran_out:

		for in_file in os.listdir(input_dir):
			if not in_file.startswith('.'):
				print('searching: ' + in_file)
				with open(input_dir + in_file, 'r') as f:
					for line in f:
						line = line.strip()
						if line:
							tweet = json.loads(line)
							mask_words = set(tweet['tokens']).intersection(set(keywords['masks']))
							sd_words = set(tweet['tokens']).intersection(set(keywords['social distancing']))
							quarantine_words = set(tweet['tokens']).intersection(set(keywords['quarantine']))

							mask_hashtags = set(tweet['tokens']).intersection(set(hashtags['masks']))
							sd_hashtags = set(tweet['tokens']).intersection(set(hashtags['social distancing']))
							q_hashtags = set(tweet['tokens']).intersection(set(hashtags['quarantine']))

							if mask_hashtags or len(mask_words) >= 2:
								json.dump(tweet, masks_out)
								masks_out.write('\n')
							if sd_hashtags or len(sd_words) >= 2:
								json.dump(tweet, sd_out)
								sd_out.write('\n')
							if q_hashtags or quarantine_words:
								json.dump(tweet, quaran_out)
								quaran_out.write('\n')

				print('finished: ' + in_file)
				print()


if __name__ == "__main__":

	input_dir = sys.argv[1]
	output_dir = sys.argv[2]

	if not os.path.exists(output_dir):
		os.mkdir(output_dir)

	masks = ['wear', 'wear', 'wearing', 'mask', 'masks', 'cover', 'face', 'facial', 'N95', 'respirator']
	masks_tags = ['mask', 'wearamask', 'facemask']
	soc_dist = ['distancing', 'social', 'distance']
	sd_tags = ['socialdistancing']
	quarantine = ['quarantine', 'quarantined', 'quarantining', 'self-isolate', 'self-isolating', 'isolating', 'isolate']#, 'work', 'home', 'stay']
	q_tags = ['quarantine', 'workfromhome', 'stayhomesavelives', 'selfisolation', 'stayathome', 'lockdown']

	keywords = {'masks' : masks, 'social distancing' : soc_dist, 'quarantine' : quarantine}
	hashtags = {'masks' : masks_tags, 'social distancing' : sd_tags, 'quarantine' : q_tags}

	search_tweets(input_dir, keywords, hashtags, output_dir)

