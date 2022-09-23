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
#import sqlite3
#import time
#import datetime
#import matplotlib.pyplot as plt
#from dateutil import parser

def Convert(lst):
    res_dct = {lst[i].strip('"'): lst[i + 1].strip('"') for i in range(0, len(lst), 2)}
    return res_dct


searchterm = input("Search term:")
url = "https://www.whiskyhammer.com/auction/past/q-"+searchterm+"/"
htmlcode = requests.get(url).content
data = BeautifulSoup(htmlcode, 'html.parser')
auctionlist = data.find('div', {'id':'browse'})

bottlelist = re.search("\[\{.+\}\]", str(auctionlist))
bottlelisttrim = bottlelist.group()[1:-1]

# Try splitting on "," then making dicts with {} groups
resultdict={}
for item in bottlelisttrim.split("}"):
	#print (item)
	tempdict = {}
	for each in item.split(","):
		#print (each)
		#tempdict = {}
		part = html.unescape(each.strip('"{"'))
		#print (part)
		#for key in part:
		#	print (key.strip('"'))
		#for part in html.unescape(each.strip('{')):
		#	print (part.split(':',1))
		keyvalue = part.strip('{"').split(':',1)
		#print ('key: '+keyvalue[0].strip('"'))
		tempdict[keyvalue[0].strip('"')] = keyvalue[1]
		#print (tempdict.keys())
		#print (tempdict.values())
		# Create dict of dicts with ID as name of each nested dict
		#print (tempdict['id'])
		tempkey = tempdict['id']
		newdict = {tempkey : tempdict}
		resultdict.update(newdict)
	#break
print (resultdict)
'''
#Screen output
for item in bottlelisttrim.split(","):
	if 'id' in item:
		print (item)
	elif 'name' in item and 'status_name' not in item:
		print (item[8:-1])
	elif 'item_price' in  item and 'item_price_ex_vat' not in item:
		print (item[13:])
	elif 'ends_human_friendly' in item and 'ends_human_friendly_alt' not in item:
		print (item[23:-1])

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

