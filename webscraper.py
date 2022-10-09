#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
Scraping auction websites for bottle data
'''


#from urllib.request import urlopen
import requests
from bs4 import BeautifulSoup
import re
import html
import sys
#import time
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib import dates as pltdates
from matplotlib.ticker import AutoMinorLocator
#from dateutil import parser
import statistics as stat

# Convert list to dict{}
def Convert(lst):
    res_dct = {lst[i].strip('"'): lst[i + 1].strip('"') for i in range(0, len(lst), 2)}
    return res_dct
# Search input
searchterm = input("Search term: ").replace(" ","+");

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
		whdata.update({whiskyHammer[bottle]['id'] : {str(datetime.strptime(whiskyHammer[bottle]['ends_human_friendly'],'%d\/%m\/%Y').date()) : whiskyHammer[bottle]['item_price']}})
	print ("WH Records: "+str(len(whdata)))
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
	except (IndexError, AttributeError):
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
		wa_htmlcode = requests.get(wa_url).content
		wa_data = BeautifulSoup(wa_htmlcode, 'html.parser')
		wa_auctionlist = wa_data.find('div', {'class':'view-content'})
		try:
			wa_lotlist = wa_auctionlist.find_all('span')
		except AttributeError:
			print ("No such bottle - please try again")
			sys.exit()
		#print (len(wa_lotlist))
		pagedict = {}
		# Function to split list into chunks of 7
		def chunker(seq, size):
		    return (seq[pos:pos + size] for pos in range(0, len(seq), size))
		for group in chunker (wa_lotlist, 7):
			tempdict = {};
			for label in group:
				#print (label)
				#tempdict = {}
				if re.search('Current Bid:', str(label)):
					break;
				elif re.search('lotnumber', str(label)):
					tempdict['lot']=label.get_text(strip=True)[4:];
					tempkey = tempdict['lot'];
				elif re.search('protitle', str(label)):
					tempdict['title']=label.get_text(strip=True);
				elif re.search(u"\xA3", str(label)):
					tempdict['price']= label.get_text().strip(u"\xA3").replace(',' , '');
				elif re.search('^\d\d\.\d\d', label.get_text(strip=True)):
					tempdict['date'] = datetime.strptime(label.get_text(), '%d.%m.%y').date();
				newdict = {tempkey : tempdict};
				pagedict.update(newdict);
				whiskyAuctioneer.update(pagedict);
			else:
				continue
			#break
	#print (len(whiskyAuctioneer))

	wadata = {};
	for bottle in whiskyAuctioneer:
		try:
			wadata.update({whiskyAuctioneer[bottle]['lot'] : {str(whiskyAuctioneer[bottle]['date']) : whiskyAuctioneer[bottle]['price']}})
		except KeyError:
			continue

	#return results_plot(wadata, 'Whisky Auctioneer')
	print ("WA Records: "+str(len(wadata)))
	return wadata


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
			tempdict['price']=float(entry.find('span', {'class':'price'}).get_text().split(u"\xA3",1)[1].replace("," , ""))
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
		jwdata.update({justWhisky[bottle]['lot'] : {str(justWhisky[bottle]['date']) : justWhisky[bottle]['price']}})
	#return results_plot(jwdata, 'Just Whisky')
	print ("JW Records: "+str(len(jwdata)))
	return jwdata

# Grand Whisky Auction search
gwdata = {}
def gw():

	grandWhisky = {}
	print ('\n'+'Getting Grand Whisky Auction data from page...')
	# Find total number of pages - cannot get this easily so just try 30 pages until fail
	for pageNumber in range(30):
		print(pageNumber+1)
		gw_url_page = "https://www.thegrandwhiskyauction.com/past-auctions/q-"+searchterm+"/page-"+str(pageNumber+1)+"/end-time"
		gw_htmlcode = requests.get(gw_url_page).content
		gw_data = BeautifulSoup(gw_htmlcode, 'html.parser')
		gw_auctionlist = gw_data.find('div',{'class' : 'siteInnerWrapper'}).find_all('script')

		gw_string = str(gw_auctionlist[1])
		#print(gw_string[0:50])


		# Regex for data from script tag
		for bottle in gw_string.split('}},'):
			tempdict = {}
			#print(len(bottle))
			#print(bottle)
			id_data=[]
			id_data = re.findall('\\"lot_id\\"\\:\\"\\d+\\"', bottle)
			#print(str(id_data[0]))
			#print(str(id_data[0]).split(':',1)[1])
			try:
				tempdict['lot'] = str(id_data[0]).split(':',1)[1]
			except IndexError:
				break
			date_data =[]
			date_data = re.findall('\\"updated_at\\"\\:\\"\\d{4}-\\d{2}-\\d{2}\\s\\d{2}:\\d{2}:\\d{2}\\"', bottle)
			#print(str(date_data[-1]))
			#print(datetime.strptime(str(date_data[-1]).split(':',1)[1].replace('"',''), '%Y-%m-%d %H:%M:%S').date())
			tempdict['date'] = datetime.strptime(str(date_data[-1]).split(':',1)[1].replace('"',''), '%Y-%m-%d %H:%M:%S').date()

			price_data =[]
			price_data = re.findall('\\"bid_value\\"\\:\\"\\d+\\.\\d{2}\\"', bottle)
			#print(str(price_data[0]))
			#print(str(price_data[0]).split(':',1)[1])
			tempdict['price'] = str(price_data[0]).split(':',1)[1].replace('"','')

			name_data =[]
			name_data = re.findall('\\"name\\"\\:\\".*?\\"\\,', bottle)
			#print(str(name_data[0]))
			#print(str(name_data[0]).split(':',1)[1])
			tempdict['title'] = str(name_data[0]).split(':',1)[1]

			tempkey = tempdict['lot']
			newdict = {tempkey : tempdict}
			grandWhisky.update(newdict)
		else:
			continue
		break
	#return print(len(grandWhisky))

	print ("\n"+"Grand Whisky Auction:")
	gwdata = {};
	for bottle in grandWhisky:
		#print (str(datetime.strptime(whiskyHammer[bottle]['ends_human_friendly'], '%d\/%m\/%Y').date())+":"+whiskyHammer[bottle]['item_price']+":"+whiskyHammer[bottle]['name'])
		gwdata.update({grandWhisky[bottle]['lot'] : {str(grandWhisky[bottle]['date']) : grandWhisky[bottle]['price']}})
	#return results_plot(gwdata, 'Grand Whisky')
	#print ("GW Records: "+str(len(gwdata)))
	return gwdata


def results_plot(bottlelist, auction):
#	Plot data
	plotstuff = []
	for k,v in bottlelist.items():
		for key,value in v.items():
			plotstuff.append((pltdates.datestr2num(key) , float(value)))
	data = plotstuff
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


def multiplot(wadata, whdata, jwdata, gwdata):
	# Plot all lines on one plot
	# WA data
	waplotstuff = []
	for k,v in wadata.items():
		for key,value in v.items():
			waplotstuff.append((pltdates.datestr2num(key) , float(value)))
	wadates = [x[0] for x in waplotstuff]
	wavalues = [x[1] for x in waplotstuff]
	# WH data
	whplotstuff = []
	for k,v in whdata.items():
		for key,value in v.items():
			whplotstuff.append((pltdates.datestr2num(key) , float(value)))
	whdates = [x[0] for x in whplotstuff]
	whvalues = [x[1] for x in whplotstuff]
	# JW data
	jwplotstuff = []
	for k,v in jwdata.items():
		for key,value in v.items():
			jwplotstuff.append((pltdates.datestr2num(key) , float(value)))
	jwdates = [x[0] for x in jwplotstuff]
	jwvalues = [x[1] for x in jwplotstuff]
	# GW data
	gwplotstuff = []
	for k,v in gwdata.items():
		for key,value in v.items():
			gwplotstuff.append((pltdates.datestr2num(key) , float(value)))
	gwdates = [x[0] for x in gwplotstuff]
	gwvalues = [x[1] for x in gwplotstuff]

	# All values for maths
	allValues = wavalues + whvalues + jwvalues + gwvalues
	meanValue = str("{:.2f}".format(float(stat.mean(allValues))))
	maxValue = str(max(allValues))
	minValue = str(min(allValues))
	sdValue = str("{:.2f}".format(float(stat.stdev(allValues))))
	nValue = str(len(allValues))
	valuesString = "Mean: "+meanValue+"   sd: "+sdValue+"   Min: "+minValue+"   Max: "+maxValue
	waLabel = "Whisky Auctioneer (n="+str(len(wavalues))+")"
	whLabel = "Whisky Hammer (n="+str(len(whvalues))+")"
	jwLabel = "Just Whisky (n="+str(len(jwvalues))+")"
	gwLabel = "Grand Whisky Auction (n="+str(len(gwvalues))+")"
	plt.figure(figsize=(10,5))
	plt.plot(wadates, wavalues, marker = 'x', color = 'b', label = waLabel)
	plt.plot(whdates, whvalues, marker = '*', color = 'r', label = whLabel)
	plt.plot(jwdates, jwvalues, marker = 'o', color = 'c', label = jwLabel)
	plt.plot(gwdates, gwvalues, marker = '+', color = 'g', label = gwLabel)
	ax = plt.gca()
	datemajor = pltdates.DateFormatter('%Y')
	dateminor = pltdates.DateFormatter('%m:%Y')
	ax.xaxis.set_major_formatter(datemajor)
	ax.xaxis.set_minor_locator(AutoMinorLocator())
	ax.xaxis.set_minor_formatter(dateminor)
	ax.set_title(" Bottles (n="+nValue+"): "+searchterm+"\n"+valuesString)
	plt.xlabel('Date')
	plt.xticks(rotation=90)
	ax.tick_params(which='minor', length=6, rotation=90)
	ax.legend()
	plt.ylabel('Price (£)')
	plt.tight_layout()
	plt.show()


#results_plot()
#wh()
#wa()
#jw()
#gw()
multiplot(wa(), wh(), jw(), gw())

