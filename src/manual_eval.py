import sys
import json
import os
import pandas as pd

'''
Script to sample relevant tweets for manual eval:
(1) reads in relevant list as DataFrame
(2) randomly selects sample(s) of rows from DataFrame
	size of sample is passed in as sample_size
	number of samples is specified as num_samples
(3)	prints sample(s) as csv

input: directories for sentiment-labeled tweets
output: sample files

'''

sents_dir = sys.argv[1]
output_dir = sys.argv[2]

num_samples = int(sys.argv[3])
sample_size = int(sys.argv[4])

if not os.path.exists(output_dir):
	os.mkdir(output_dir)

for in_file in os.listdir(sents_dir):
	if not in_file.startswith('.'):
		print('sampling: ' + in_file)
		df = pd.read_json(sents_dir + in_file, lines=True)

		for i in range(num_samples):
			sample = df.sample(n = sample_size)
			sample.to_csv(output_dir + in_file + '_sample_' + str(i+1) + '.csv')

		print('finished: ' + in_file)
		print()
		
