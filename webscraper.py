#!/usr/bin/env python3
'''
Scraping auction websites for bottle data
'''

#from urllib.request import urlopen
import requests
from bs4 import BeautifulSoup
import re
import html
#import sys
#import time
#import datetime
#import matplotlib.pyplot as plt
#from dateutil import parser

# Convert list to dict{}
def Convert(lst):
    res_dct = {lst[i].strip('"'): lst[i + 1].strip('"') for i in range(0, len(lst), 2)}
    return res_dct

searchterm = input("Search term:")
wh_url = "https://www.whiskyhammer.com/auction/past/q-"+searchterm+"/"
wh_htmlcode = requests.get(wh_url).content
wh_data = BeautifulSoup(wh_htmlcode, 'html.parser')
wh_auctionlist = wh_data.find('div', {'id':'browse'})
wh_bottlelist = re.search("\[\{.+\}\]", str(wh_auctionlist))
wh_bottlelisttrim = wh_bottlelist.group()[1:-1]

whiskyHammer={}
for item in wh_bottlelisttrim.split("}"):
	tempdict = {}
	for each in item.split(","):
		part = html.unescape(each.strip('"{"'))
		keyvalue = part.strip('{"').split(':',1)
		try:
			tempdict[keyvalue[0].strip('"')] = keyvalue[1]
		except IndexError:
			continue
		tempkey = tempdict['id']
		newdict = {tempkey : tempdict}
		whiskyHammer.update(newdict)
print ("Whisky Hammer:")
for bottle in whiskyHammer: print (whiskyHammer[bottle]['item_price'])


'''

#Data array setup
for item in bottlelisttrim.split(","):
	if 'name' in item and 'status_name' not in item:
		print (item.split(":")[1])
'''
'''
def summary_data():
    # Get Bottling Name
summary_data()
'''

