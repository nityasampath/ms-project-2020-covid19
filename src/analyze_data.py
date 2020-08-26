#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
Script to extract data from output:
(1) count tweets and sentiments and store in DataFrame
(2) get case numbers, mobility data and Google Trends data
(3) smooth data
(4) calculate percents and ratios 
(5) calculate correlations
(6) output to csv file

input: directories for sentiment-labeled tweets, benchmark data files
output: data files of tweets/cases per day, data files of correlations

'''

import sys
import json
import pandas as pd
import os
import numpy as np
import datetime
from datetime import date, timedelta


def count(sent_file):

	counts = {}
	sentiments = {}

	with open(sent_file, 'r') as f:
		for line in f:
			line = line.strip()
			if line:
				tweet = json.loads(line)
				date = tweet['date']
				sentiment = tweet['sentiment']
				if sentiment > 0:
					positive = 1
					negative = 0
				elif sentiment < 0:
					positive = 0
					negative = 1
				else:
					positive = 0
					negative = 0
				if date not in counts:
					counts[date] = {'positive' : positive, 'negative' : negative, 'total' : 1}
				else:
					counts[date]['positive'] += positive
					counts[date]['negative'] += negative
					counts[date]['total'] += 1
				if date not in sentiments:
					sentiments[date] = [sentiment]
				else:
					sentiments[date].append(sentiment)

	return counts, sentiments


def calc_percents_ratios(df, smoothed): 

	if smoothed:
		df.insert(df.columns.get_loc("Smoothed Total") + 1 , 'Percentage Positive', np.where(df['Smoothed Total'] > 0, df['Smoothed Positive']/df['Smoothed Total'], 0))
		df.insert(df.columns.get_loc("Percentage Positive") + 1 , 'Percentage Negative', np.where(df['Smoothed Total'] > 0, df['Smoothed Negative']/df['Smoothed Total'], 0))
		df.insert(df.columns.get_loc("Smoothed New Cases") + 1, 'Cases Ratio', df['Smoothed New Cases'].rolling(2).apply(lambda x: (x.iloc[1]/x.iloc[0])))
	else:
		df.insert(df.columns.get_loc("Total") + 1, 'Percentage Positive', np.where(df['Total'] > 0, df['Positive']/df['Total'], 0))
		df.insert(df.columns.get_loc("Percentage Positive") + 1, 'Percentage Negative', np.where(df['Total'] > 0, df['Negative']/df['Total'], 0))
		df.insert(df.columns.get_loc("New Cases") + 1, 'Cases Ratio', df['New Cases'].rolling(2).apply(lambda x: (x.iloc[1]/x.iloc[0])))


def get_dataframe(counts, sentiments): 

	dates_counted = list(counts.keys())
	
	dates_counted.sort(key = lambda date: datetime.datetime.strptime(date, '%b %d %Y'))

	date1 = datetime.datetime.strptime(dates_counted[0], '%b %d %Y')
	date2 = datetime.datetime.strptime(dates_counted[-1], '%b %d %Y')

	dates = [date1 + timedelta(days=i) for i in range((date2-date1).days + 1)]

	dates = [date.strftime('%b %d %Y') for date in dates]

	positive_counts = []
	negative_counts = []
	total_counts = []
	average_sentiments = []

	for date in dates:
		if date in counts:
			positive_counts.append(counts[date]['positive'])
			negative_counts.append(counts[date]['negative'])
			total_counts.append(counts[date]['total'])
		else:
			positive_counts.append(0)
			negative_counts.append(0)
			total_counts.append(0)
		if date in sentiments:
			average_sentiments.append(sum(sentiments[date])/len(sentiments[date]))
		else:
			average_sentiments.append(0)

	df = {'Date': dates, 'Positive' : positive_counts, 'Negative' : negative_counts, 'Total' : total_counts, 'Average Sentiment' : average_sentiments} #'Percentage Positive' : positive_percentages, 'Percentage Negative' : negative_percentages, }

	df = pd.DataFrame.from_dict(df)

	return df


def get_case_numbers(cases_file, deaths_file, df):

	cases_data = pd.read_csv(cases_file)

	deaths_data = pd.read_csv(deaths_file)

	dates = list(df['Date'])

	case_numbers = []
	death_numbers = []
	new_cases = []
	new_deaths = []

	for date in dates:
		date_object = datetime.datetime.strptime(date, '%b %d %Y')
		prev_obj = date_object - datetime.timedelta(days=1)
		date_formatted = date_object.strftime('%m/%d/%y')
		prev_date = prev_obj.strftime('%m/%d/%y')
		date_formatted = date_formatted[1:]
		prev_date = prev_date[1:]
		mdy = date_formatted.split('/')
		prev_mdy = prev_date.split('/')
		
		if mdy[1][0] == '0':
			mdy[1] = mdy[1][1:]
		date_formatted = '/'.join(mdy)

		if prev_mdy[1][0] == '0':
			prev_mdy[1] = prev_mdy[1][1:]
		prev_date = '/'.join(prev_mdy) 
		
		case_value = cases_data[date_formatted].sum()
		case_numbers.append(case_value)

		prev_cases = cases_data[prev_date].sum()
		cases_delta = case_value-prev_cases
		new_cases.append(cases_delta)

		deaths_value = deaths_data[date_formatted].sum()
		death_numbers.append(deaths_value)

		prev_deaths = deaths_data[prev_date].sum()
		deaths_delta = deaths_value-prev_deaths
		new_deaths.append(deaths_delta)


	df['Cases'] = case_numbers
	df['New Cases'] = new_cases

	df['Deaths'] = death_numbers
	df['New Deaths'] = new_deaths


def smooth_data(df, window):

	copy_df = df.copy()
	copy_df.insert(copy_df.columns.get_loc("Positive"), 'Smoothed Positive', copy_df['Positive'].rolling(window, min_periods=1, center=True).mean())
	del copy_df['Positive']
	copy_df.insert(copy_df.columns.get_loc("Negative"), 'Smoothed Negative', copy_df['Negative'].rolling(window, min_periods=1, center=True).mean())
	del copy_df['Negative']
	copy_df.insert(copy_df.columns.get_loc("Total"), 'Smoothed Total', copy_df['Total'].rolling(window, min_periods=1, center=True).mean())
	del copy_df['Total']
	copy_df.insert(copy_df.columns.get_loc("Cases"), 'Smoothed Cases', copy_df['Cases'].rolling(window, min_periods=1, center=True).mean())
	del copy_df['Cases']
	copy_df.insert(copy_df.columns.get_loc("New Cases"), 'Smoothed New Cases', copy_df['New Cases'].rolling(window, min_periods=1, center=True).mean())
	del copy_df['New Cases']
	copy_df.insert(copy_df.columns.get_loc("Deaths"), 'Smoothed Deaths', copy_df['Deaths'].rolling(window, min_periods=1, center=True).mean())
	del copy_df['Deaths']
	copy_df.insert(copy_df.columns.get_loc("New Deaths"), 'Smoothed New Deaths', copy_df['New Deaths'].rolling(window, min_periods=1, center=True).mean())
	del copy_df['New Deaths']

	return copy_df

	
def get_mobility_data(mobility_file, df):

	mobility_data = pd.read_csv(mobility_file)

	dates = list(df['Date'])

	mobility_numbers = []
	death_numbers = []

	for date in dates:
		date_object = datetime.datetime.strptime(date, '%b %d %Y')
		date_formatted = date_object.strftime('%Y-%m-%d')
		
		mobility_value = mobility_data[date_formatted].mean()
		mobility_numbers.append(mobility_value)

	df['Mobility'] = mobility_numbers


def get_google_trends(trends_file, df):

	trends_data = pd.read_csv(trends_file, skiprows=2)

	dates = list(df['Date'])

	cols = list(trends_data.columns)

	trends_numbers = []

	for date in dates:
		date_object = datetime.datetime.strptime(date, '%b %d %Y')
		date_formatted = date_object.strftime('%Y-%m-%d')
	
		trends_value = trends_data.loc[trends_data[cols[0]] == date_formatted, cols[1]].item()
		if str(trends_value) == '<1':
			trends_value = 0
		trends_numbers.append(trends_value)


	df['Google Trends'] = trends_numbers


if __name__ == "__main__":

	sents_dir = sys.argv[1]
	csv_dir = sys.argv[2]
	cases_file = sys.argv[3]
	deaths_file = sys.argv[4]
	mobility_file = sys.argv[5]
	trends_dir = sys.argv[6]

	if not os.path.exists(csv_dir):
		os.mkdir(csv_dir)

	smoothing_window = int(sys.argv[7])

	topics = ['masks', 'social distancing', 'quarantine']

	for topic in topics:

		topic_counts, topic_sents = count(sents_dir + topic + '.json')
		topic_df = get_dataframe(topic_counts, topic_sents) 
		get_case_numbers(cases_file, deaths_file, topic_df)
		get_mobility_data(mobility_file, topic_df)
		if topic == 'masks':
			trends_file = 'masks.csv'
		elif topic == 'social distancing':
			trends_file = 'social distancing.csv'
		else:
			trends_file = 'quarantine.csv'
		get_google_trends(trends_dir + trends_file, topic_df)

		if topic_df['Google Trends'].dtypes == 'object':
			topic_df['Google Trends'] = pd.to_numeric(topic_df['Google Trends'])

		smoothed_df = smooth_data(topic_df, smoothing_window)

		calc_percents_ratios(topic_df, False)
		calc_percents_ratios(smoothed_df, True)

		print(topic_df.head(5))

		topic_corrs = topic_df.corr(method ='pearson')

		smoothed_corrs = smoothed_df.corr(method ='pearson')

		topic_df.to_csv(csv_dir + topic + '.csv')

		smoothed_df.to_csv(csv_dir + topic + '_smoothed.csv')

		topic_corrs.to_csv(csv_dir + topic + '_corrs.csv')

		smoothed_corrs.to_csv(csv_dir + topic + '_smoothed_corrs.csv')

