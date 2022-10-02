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
from matplotlib.ticker import AutoMinorLocator
#from dateutil import parser

# Convert list to dict{}
def Convert(lst):
    res_dct = {lst[i].strip('"'): lst[i + 1].strip('"') for i in range(0, len(lst), 2)}
    return res_dct
# Search input
searchterm = input("Search term: ");

# Whisky Hammer search
whdata = {}
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
	whdata = {};
	for bottle in whiskyHammer:
#		print (str(datetime.strptime(whiskyHammer[bottle]['ends_human_friendly'], '%d\/%m\/%Y').date())+":"+whiskyHammer[bottle]['item_price']+":"+whiskyHammer[bottle]['name'])
		whdata.update({str(datetime.strptime(whiskyHammer[bottle]['ends_human_friendly'],'%d\/%m\/%Y').date()) : whiskyHammer[bottle]['item_price']})
	#return results_plot(whdata, 'Whisky Hammer')
	return whdata

# Whisky Auctioneer search
wadata = {}
def wa():
	# Getting page by page data NOTE: page=1 is the second page
	# wa_url_page = "https://whiskyauctioneer.com/auction-search?items_per_page=500&sort=field_reference_field_end_date%20DESC&text=daftmill&page=1"
	wa_url_page = "https://whiskyauctioneer.com/auction-search?text="+searchterm+"&sort=field_reference_field_end_date+DESC&items_per_page=500&f%5B0%5D=cask_type%3A41"
	wa_htmlcode = requests.get(wa_url_page).content
	wa_data = BeautifulSoup(wa_htmlcode, 'html.parser')
	try:
		wa_lastpage = int(wa_data.find('li', {'class':'pager-last last'}).find('a').get('href')[-1])
	except IndexError:
		wa_lastpage = 0
	print ('Getting Whisky Auctioneer data from '+str(wa_lastpage+1)+' total page(s)...')
	# Loop through pages
	whiskyAuctioneer={}
	#tempdict={'lot':'','title':'','price':'','date':''}
	for eachpage in range(wa_lastpage+1):
		print (eachpage)
		#wa_url = "https://whiskyauctioneer.com/auction-search?items_per_page=500&sort=field_reference_field_end_date%20DESC&text="+searchterm+"&page="+str(eachpage)
		wa_url = "https://whiskyauctioneer.com/auction-search?text="+searchterm+"&sort=field_reference_field_end_date+DESC&items_per_page=500&f%5B0%5D=cask_type%3A41&page="+str(eachpage)
		#print (wa_url)
		#wa_url = "https://whiskyauctioneer.com/auction-search?text="+searchterm+"&sort=field_reference_field_end_date+DESC&items_per_page=500&f%5B0%5D=cask_type%3A41"
		#wa_url = "https://whiskyauctioneer.com/auction-search?text="+searchterm
		wa_htmlcode = requests.get(wa_url).content
		wa_data = BeautifulSoup(wa_htmlcode, 'html.parser')
		wa_auctionlist = wa_data.find('div', {'class':'view-content'})
		wa_lotlist = wa_auctionlist.find_all('span')
		#print (len(wa_lotlist))
		#whiskyAuctioneer={}
		#tempdict={'lot':'','title':'','price':'','date':''}
		# Function to split list into chunks of 7
		def chunker(seq, size):
		    return (seq[pos:pos + size] for pos in range(0, len(seq), size))
		for group in chunker (wa_lotlist, 7):
			#tempdict = {};
			for label in group:
				tempdict = {}
				if re.search('lotnumber', str(label)):
					tempdict['lot']=label.get_text(strip=True)[4:];
					tempkey = tempdict['lot'];
				elif re.search('protitle', str(label)):
					tempdict['title']=label.get_text(strip=True);
				elif re.search('Winning', str(label)):
					pass;
				elif re.search('£', str(label)):
					tempdict['price']=label.get_text().strip("£ ").replace(',' ,'')
				elif re.search('^\d\d\.\d\d', label.get_text(strip=True)):
					tempdict['date'] = datetime.strptime(label.get_text(), '%d.%m.%y').date();
				newdict = {tempkey : tempdict};
				whiskyAuctioneer.update(newdict);
	print (len(whiskyAuctioneer))
#	for k,v in whiskyAuctioneer.items(): 
#		for key in v:
#			print (key +":", v[key])
	print ("\n"+"Whisky Auctioneer:")
	wadata = {};
	for bottle in whiskyAuctioneer:
		print (whiskyAuctioneer[bottle][0])
		#print (str(whiskyAuctioneer[bottle]['date']))
		#print (str(whiskyAuctioneer[bottle]['date'])+":"+whiskyAuctioneer[bottle]['price']+":"+whiskyAuctioneer[bottle]['title'])
		try:
			wadata.update({str(whiskyAuctioneer[bottle]['date']) : whiskyAuctioneer[bottle]['price']})
		except KeyError:
			continue
	#return results_plot(wadata, 'Whisky Auctioneer')
	return print (len(wadata))

# Just Whisky search
jwdata = {}
def jw():
	# Find total number of pages
	jw_url_page = "https://www.just-whisky.co.uk/search?controller=search&orderby=reference&orderway=desc&category=171&search_query="+searchterm+"&submit_search.x=0&submit_search.y=0"
	jw_htmlcode = requests.get(jw_url_page).content
	jw_data = BeautifulSoup(jw_htmlcode, 'html.parser')
	jw_pagelist = jw_data.find('div', {'id':'pagination'}).find_all('a')
	try:
		jw_lastpage = int(jw_pagelist[-2].contents[0])
	except IndexError:
		jw_lastpage = 1
	print ('Getting Just-Whisky data from '+str(jw_lastpage)+' total page(s)...')
	justWhisky={}
	tempdict={'lot':'','title':'','price':'','date':''}
	for eachpage in range(jw_lastpage):
		print (eachpage+1)
		jw_url = "https://www.just-whisky.co.uk/search?controller=search&orderby=reference&orderway=desc&category=171&search_query="+searchterm+"&submit_search.x=0&submit_search.y=0&p="+str(eachpage+1)
		jw_htmlcode = requests.get(jw_url).content
		jw_data = BeautifulSoup(jw_htmlcode, 'html.parser')
		jw_auctionlist = jw_data.find_all('div', {'class':'auction_item'})
		for entry in jw_auctionlist:
			tempdict = {}
			tempdict['title']=entry.find('a', {'class':'product_img_link'}).get('title');
			tempdict['price']=float(entry.find('span', {'class':'price'}).get_text().split('£ ',1)[1].replace("," , ""))
			tempdict['lot']=entry.find('div', {'class':'lot'}).get_text().split(': ',1)[1]
			tempkey = tempdict['lot']
			try:
				tempdict['date'] = datetime.strptime("01-"+entry.find('a', {'class':'product_img_link'}).get('href').split('/',4)[3] , '%d-%B-%Y').date()
			except ValueError:
				tempdict['date'] = datetime.strptime("01-"+entry.find('a', {'class':'product_img_link'}).get('href').split('/',4)[3]+"-2020" , '%d-%B-%Y').date()
			newdict = {tempkey : tempdict}
			justWhisky.update(newdict)

	print ("\n"+"Just Whisky:")
	jwdata = {};
	for bottle in justWhisky:
#		print (str(datetime.strptime(whiskyHammer[bottle]['ends_human_friendly'], '%d\/%m\/%Y').date())+":"+whiskyHammer[bottle]['item_price']+":"+whiskyHammer[bottle]['name'])
		jwdata.update({str(justWhisky[bottle]['date']) : justWhisky[bottle]['price']})
	#return results_plot(jwdata, 'Just Whisky')
	return jwdata

def results_plot(bottlelist, auction):
#	Plot data
	plotstuff = {}
	for k,v in bottlelist.items():
		plotstuff[pltdates.datestr2num(k)] = float(v)
	data = list(plotstuff.items())
	fig, ax = plt.subplots(1,1,figsize=(10, 5))
	datemajor = pltdates.DateFormatter('%Y')
	dateminor = pltdates.DateFormatter('%m:%Y')
	dates = [x[0] for x in data]
	values = [x[1] for x in data]
	ax.plot(dates, values, 'o-')
	ax.xaxis.set_major_formatter(datemajor)
	ax.xaxis.set_minor_locator(AutoMinorLocator())
	ax.xaxis.set_minor_formatter(dateminor)
	ax.set_title(auction+" Bottles: "+searchterm)
	plt.xlabel('Date')
	plt.xticks(rotation=90)
	ax.tick_params(which='minor', length=6, rotation=90)
	plt.ylabel('Price (£)')
	plt.tight_layout()
	plt.show()

def multiplot(wadata, whdata, jwdata):
	# Plot all lines on one plot
	# WA data
	waplotstuff = {}
	for k,v in wadata.items():
		waplotstuff[pltdates.datestr2num(k)] = float(v)
	walist = list(waplotstuff.items())
	wadates = [x[0] for x in walist]
	wavalues = [x[1] for x in walist]
	# WH data
	whplotstuff = {}
	for k,v in whdata.items():
		whplotstuff[pltdates.datestr2num(k)] = float(v)
	whlist = list(whplotstuff.items())
	whdates = [x[0] for x in whlist]
	whvalues = [x[1] for x in whlist]
	# JW data
	jwplotstuff = {}
	for k,v in jwdata.items():
		jwplotstuff[pltdates.datestr2num(k)] = float(v)
	jwlist = list(jwplotstuff.items())
	jwdates = [x[0] for x in jwlist]
	jwvalues = [x[1] for x in jwlist]

	plt.figure(figsize=(10,5))
	plt.plot(wadates, wavalues, color = 'b', label = 'Whisky Auctioneer')
	plt.plot(whdates, whvalues, color = 'r', label = 'Whisky Hammer')
	plt.plot(jwdates, jwvalues, color = 'c', label = 'Just Whisky')
	ax = plt.gca()
	datemajor = pltdates.DateFormatter('%Y')
	dateminor = pltdates.DateFormatter('%m:%Y')
	ax.xaxis.set_major_formatter(datemajor)
	ax.xaxis.set_minor_locator(AutoMinorLocator())
	ax.xaxis.set_minor_formatter(dateminor)
	ax.set_title(" Bottles: "+searchterm)
	plt.xlabel('Date')
	plt.xticks(rotation=90)
	ax.tick_params(which='minor', length=6, rotation=90)
	ax.legend()
	plt.ylabel('Price (£)')
	plt.tight_layout()
	plt.show()


#results_plot()
#wh()
wa()
#jw()
#multiplot(wa(), wh(), jw())

