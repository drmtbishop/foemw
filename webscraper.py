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
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib import dates as pltdates
#from dateutil import parser

# Convert list to dict{}
def Convert(lst):
    res_dct = {lst[i].strip('"'): lst[i + 1].strip('"') for i in range(0, len(lst), 2)}
    return res_dct
# Search input
searchterm = input("Search term:");

# Whisky Hammer search
def wh():
	wh_url = "https://www.whiskyhammer.com/auction/past/q-"+searchterm+"/?sortby=end-time&ps=1000"
	#wh_url = "https://www.whiskyhammer.com/auction/past/q-"+searchterm+"/"
	wh_htmlcode = requests.get(wh_url).content
	wh_data = BeautifulSoup(wh_htmlcode, 'html.parser')
	wh_auctionlist = wh_data.find('div', {'id':'browse'})
	wh_bottlelist = re.search("\[\{.+\}\]", str(wh_auctionlist))
	wh_bottlelisttrim = wh_bottlelist.group()[1:-1]

	whiskyHammer={}
	for item in wh_bottlelisttrim.split("}"):
		tempdict = {}
		for each in item.split(","):
			part = html.unescape(each.strip('"{'))
			keyvalue = part.strip('{"').split(':',1)
			try:
				tempdict[keyvalue[0].strip('"')] = keyvalue[1].strip('"')
			except IndexError:
				continue
			tempkey = tempdict['id']
			newdict = {tempkey : tempdict}
			whiskyHammer.update(newdict)
	print ("\n"+"Whisky Hammer:")
	#print (whiskyHammer)
	bottlelist = {};
	for bottle in whiskyHammer:
#		print (str(datetime.strptime(whiskyHammer[bottle]['ends_human_friendly'], '%d\/%m\/%Y').date())+":"+whiskyHammer[bottle]['item_price']+":"+whiskyHammer[bottle]['name'])
		bottlelist.update({str(datetime.strptime(whiskyHammer[bottle]['ends_human_friendly'],'%d\/%m\/%Y').date()) : whiskyHammer[bottle]['item_price']})

#	Plot data
	plotstuff = {}
	for k,v in bottlelist.items():
		plotstuff[pltdates.datestr2num(k)] = float(v)
	data = list(plotstuff.items())
	fig, ax = plt.subplots(1,1,figsize=(10, 5))
	hfmt = pltdates.DateFormatter('%d:%m:%Y')
	dates = [x[0] for x in data]
	values = [x[1] for x in data]
	ax.plot(dates, values, 'o-')
	ax.xaxis.set_major_formatter(hfmt)
	ax.set_title("WH Bottles: "+searchterm)
	fig.autofmt_xdate()
	plt.show()


# Whisky Auctioneer search
def wa():
	wa_url = "https://whiskyauctioneer.com/auction-search?text="+searchterm+"&sort=field_reference_field_end_date+DESC&items_per_page=500&f%5B0%5D=cask_type%3A41"
	#wa_url = "https://whiskyauctioneer.com/auction-search?text="+searchterm
	wa_htmlcode = requests.get(wa_url).content
	wa_data = BeautifulSoup(wa_htmlcode, 'html.parser')
	wa_auctionlist = wa_data.find('div', {'class':'view-content'})
	wa_lotlist = wa_auctionlist.find_all('span')
	whiskyAuctioneer={}
	tempdict={'lot':'','title':'','price':'','date':''}
	# Function to plit list into chunks of 7
	def chunker(seq, size):
	    return (seq[pos:pos + size] for pos in range(0, len(seq), size))
	for group in chunker (wa_lotlist, 7):
		tempdict = {};
		for label in group:
			if re.search('lotnumber', str(label)):
				tempdict['lot']=label.get_text(strip=True)[4:];
				tempkey = tempdict['lot'];
			elif re.search('protitle', str(label)):
				tempdict['title']=label.get_text(strip=True);
			elif re.search('Winning', str(label)):
				pass;
			elif re.search('£', str(label)):
				tempdict['price']=label.get_text().strip('£');
			elif re.search('^\d\d\.\d\d', label.get_text(strip=True)):
				tempdict['date'] = datetime.strptime(label.get_text(), '%d.%m.%y').date();
			newdict = {tempkey : tempdict};
			whiskyAuctioneer.update(newdict);
	print ("\n"+"Whisky Auctioneer:")
	for bottle in whiskyAuctioneer: print (str(whiskyAuctioneer[bottle]['date'])+":"+whiskyAuctioneer[bottle]['price']+":"+whiskyAuctioneer[bottle]['title'])

wh()
#wa()


