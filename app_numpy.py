#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
Scraping whisky auction websites for bottle data
using numpy instead of plotting
'''
import requests
from bs4 import BeautifulSoup
import re
import html
import sys
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib import dates as pltdates
from matplotlib.ticker import AutoMinorLocator
import statistics as stat
import numpy as np
from progress.bar import Bar
#from progress.spinner import Spinner

#bar = Spinner('Processing')
bar = Bar('>>', max=(11), suffix='Left %(eta_td)s')

# Single request session for speed
requests_session = requests.Session()

# Convert list to dict{}
def Convert(lst):
    res_dct = {lst[i].strip('"'): lst[i + 1].strip('"') for i in range(0, len(lst), 2)}
    return res_dct
# Search input from script argument or if missing, then from input
searchterm = ""
if len(sys.argv) == 2:
	searchterm = str(sys.argv[1]).replace(" ","+")
else:
	searchterm = input("Search term: ").replace(" ","+")


# Whisky Hammer search
whdata = {}
def wh():
	whdata = {}
	whsearchterm = searchterm.replace("+","-")
	wh_url = "https://www.whiskyhammer.com/auction/past/q-"+whsearchterm+"/?sortby=end-time&ps=1000"
	wh_htmlcode = requests_session.get(wh_url).content
	wh_data = BeautifulSoup(wh_htmlcode, 'html.parser')
	wh_auctionlist = wh_data.find('div', {'id':'browse'})
	wh_bottlelist = re.search("\\[\\{.+\\}\\]", str(wh_auctionlist))
	try:
		wh_bottlelisttrim = wh_bottlelist.group()[1:-1]
	except AttributeError:
		return whdata
	whiskyHammer={}
	bar.next()
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
	for bottle in whiskyHammer:
		whdata.update({whiskyHammer[bottle]['id'] : {str(datetime.strptime(whiskyHammer[bottle]['ends_human_friendly'],'%d\\/%m\\/%Y').date()) : whiskyHammer[bottle]['item_price']}})
	bar.next()
	return whdata


# Whisky Auctioneer search
wadata = {}
def wa():
	wadata = {}
	wasearchterm = str(searchterm.replace('+', '%20'))
	# Getting page by page data NOTE: page=1 is the second page
	headers = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36',}
	wa_url_page = "https://whiskyauctioneer.com/auction-search?text="+wasearchterm
	wa_htmlcode = requests_session.get(wa_url_page, headers = headers).content
	wa_data = BeautifulSoup(wa_htmlcode, 'html.parser')
	try:
		wa_lastpage = int(wa_data.find('li', {'class':'pager-last last'}).find('a').get('href').split('page=')[1])
	except (IndexError, AttributeError):
		wa_lastpage = 0
	# Loop through pages
	bar.next()
	whiskyAuctioneer={}
	for eachpage in range(wa_lastpage+1):
		wa_url = "https://whiskyauctioneer.com/auction-search?text="+wasearchterm+"&sort=field_reference_field_end_date+DESC&page="+str(eachpage)
		wa_htmlcode = requests_session.get(wa_url, headers = headers).content
		wa_data = BeautifulSoup(wa_htmlcode, 'html.parser')
		wa_auctionlist = wa_data.find('div', {'class':'view-content'})
		try:
			wa_lotlist = wa_auctionlist.find_all('span')
		except AttributeError:
			return wadata
		pagedict = {}
		# Function to split list into chunks of 7
		def chunker(seq, size):
			return (seq[pos:pos + size] for pos in range(0, len(seq), size))
		for group in chunker (wa_lotlist, 7):
			tempdict = {}
			for label in group:
				if re.search('Current Bid:', str(label)):
					break
				elif re.search('lotnumber', str(label)):
					tempdict['lot']=label.get_text(strip=True)[4:]
					tempkey = tempdict['lot']
				elif re.search('protitle', str(label)):
					tempdict['title']=label.get_text(strip=True)
				elif re.search(u"\xA3", str(label)):
					tempdict['price']= label.get_text().strip(u"\xA3").replace(',' , '')
				elif re.search('^\\d\\d\\.\\d\\d', label.get_text(strip=True)):
					tempdict['date'] = datetime.strptime(label.get_text(), '%d.%m.%y').date()
				newdict = {tempkey : tempdict}
				pagedict.update(newdict)
				whiskyAuctioneer.update(pagedict)
			else:
				continue
	wadata = {}
	for bottle in whiskyAuctioneer:
		try:
			wadata.update({whiskyAuctioneer[bottle]['lot'] : {str(whiskyAuctioneer[bottle]['date']) : whiskyAuctioneer[bottle]['price']}})
		except KeyError:
			continue
	bar.next()
	return wadata


# Just Whisky search
jwdata = {}
def jw():
	# Find total number of pages
	jw_url_page = "https://www.just-whisky.co.uk/search?controller=search&orderby=reference&orderway=desc&category=171&search_query="+searchterm+"&submit_search.x=0&submit_search.y=0"
	jw_htmlcode = requests_session.get(jw_url_page).content
	jw_data = BeautifulSoup(jw_htmlcode, 'html.parser')
	jw_pagelist = jw_data.find('div', {'id':'pagination'}).find_all('a')
	try:
		jw_lastpage = int(jw_pagelist[-2].contents[0])
	except IndexError:
		jw_lastpage = 1
	justWhisky={}
	bar.next()
	tempdict={'lot':'','title':'','price':'','date':''}
	for eachpage in range(jw_lastpage):
		jw_url = "https://www.just-whisky.co.uk/search?controller=search&orderby=reference&orderway=desc&category=171&search_query="+searchterm+"&submit_search.x=0&submit_search.y=0&p="+str(eachpage+1)
		jw_htmlcode = requests_session.get(jw_url).content
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

	jwdata = {}
	for bottle in justWhisky:
		jwdata.update({justWhisky[bottle]['lot'] : {str(justWhisky[bottle]['date']) : justWhisky[bottle]['price']}})
	bar.next()
	return jwdata

# Grand Whisky Auction search
gwdata = {}
def gw():
	# Change searchterm to include quotes and spaces
	gwsearchterm = str(searchterm.replace('+', '&'))
	grandWhisky = {}
	# Find total number of pages - cannot get this easily so just try 30 pages until fail
	for pageNumber in range(30):
		if pageNumber > 1:
			gw_url_page = "https://www.thegrandwhiskyauction.com/past-auctions/q-"+gwsearchterm+"/page-"+str(pageNumber+1)+"/72-per-page/end-time"
		else:
			gw_url_page = "https://www.thegrandwhiskyauction.com/past-auctions/q-"+gwsearchterm+"/72-per-page/end-time"
		gw_htmlcode = requests_session.get(gw_url_page).content
		gw_data = BeautifulSoup(gw_htmlcode, 'html.parser')
		try:
			gw_auctionlist = gw_data.find('div',{'class' : 'siteInnerWrapper'}).find_all('script')
		except AttributeError:
			break
		gw_string = str(gw_auctionlist[1])
		# Regex for data from script tag
		bar.next()
		for bottle in gw_string.split('}},'):
			tempdict = {}
			id_data=[]
			id_data = re.findall('\\"lot_id\\"\\:\\"\\d+\\"', bottle)
			try:
				tempdict['lot'] = str(id_data[0]).split(':',1)[1]
			except IndexError:
				break
			date_data =[]
			date_data = re.findall('\\"updated_at\\"\\:\\"\\d{4}-\\d{2}-\\d{2}\\s\\d{2}:\\d{2}:\\d{2}\\"', bottle)
			tempdict['date'] = datetime.strptime(str(date_data[-1]).split(':',1)[1].replace('"',''), '%Y-%m-%d %H:%M:%S').date()

			price_data =[]
			price_data = re.findall('\\"bid_value\\"\\:\\"\\d+\\.\\d{2}\\"', bottle)
			tempdict['price'] = str(price_data[0]).split(':',1)[1].replace('"','')

			name_data =[]
			name_data = re.findall('\\"name\\"\\:\\".*?\\"\\,', bottle)
			tempdict['title'] = str(name_data[0]).split(':',1)[1]

			tempkey = tempdict['lot']
			newdict = {tempkey : tempdict}
			grandWhisky.update(newdict)
		else:
			continue
		break

	gwdata = {}
	for bottle in grandWhisky:
		#print (str(datetime.strptime(whiskyHammer[bottle]['ends_human_friendly'], '%d\/%m\/%Y').date())+":"+whiskyHammer[bottle]['item_price']+":"+whiskyHammer[bottle]['name'])
		gwdata.update({grandWhisky[bottle]['lot'] : {str(grandWhisky[bottle]['date']) : grandWhisky[bottle]['price']}})
	bar.next()
	return gwdata

# Scotch Whisky Auctions search
swadata = {}
def swa():
	# Dict of date lookups for auction dates. Key '000' catches those not on this list
	swaAuctionDict={'000' : '01-JAN-2015',
	'201' : '18-NOV-2017', '045' : '01-JAN-2015', '046' : '01-FEB-2015', '047' : '01-MAR-2015', '048' : '01-APR-2015', 
	'049' : '01-MAY-2015', '050' : '01-JUN-2015', '051' : '01-JUL-2015', '052' : '02-AUG-2015', '053' : '01-SEP-2015', 
	'054' : '01-OCT-2015', '055' : '01-NOV-2015', '056' : '06-DEC-2015', '057' : '01-JAN-2016', '058' : '07-FEB-2016', 
	'059' : '01-MAR-2016', '060' : '01-APR-2016', '061' : '01-MAY-2016', 
	'062' : '05-JUN-2016','063' : '06-JUL-2016', '064' : '07-AUG-2016', '065' : '04-SEP-2016', '066' : '02-OCT-2016',
	'067' : '06-NOV-2016', '068' : '04-DEC-2016', '069' : '03-JAN-2017', '070' : '05-FEB-2017', '071' : '05-MAR-2017', '072' : '02-APR-2017', 
	'073' : '07-MAY-2017', '074' : '04-JUN-2017', '075' : '02-JUL-2017', '076' : '06-AUG-2017', '077' : '03-SEP-2017', '078' : '01-OCT-2017', 
	'079' : '05-NOV-2017', '080' : '03-DEC-2017', '081' : '07-JAN-2018', '082' : '04-FEB-2018', '083' : '04-MAR-2018', '084' : '01-APR-2018', 
	'085' : '06-MAY-2018', '086' : '03-JUN-2018', '087' : '01-JUL-2018', '088' : '05-AUG-2018', '089' : '02-SEP-2018', '090' : '07-OCT-2018', 
	'091' : '04-NOV-2018', '092' : '02-DEC-2018', '093' : '06-JAN-2019', '094' : '03-FEB-2019', '095' : '03-MAR-2019', '096' : '07-APR-2019', 
	'097' : '05-MAY-2019', '098' : '02-JUN-2019', '099' : '07-JUL-2019', '100' : '04-AUG-2019', '101' : '01-SEP-2019', '102' : '06-OCT-2019', 
	'103' : '03-NOV-2019', '104' : '01-DEC-2019', '105' : '05-JAN-2020', '106' : '02-FEB-2020', '107' : '01-MAR-2020', '108' : '07-JUN-2020', 
	'109' : '05-JUL-2020', '110' : '02-AUG-2020', '111' : '06-SEP-2020', '112' : '04-OCT-2020', '113' : '01-NOV-2020', '114' : '06-DEC-2020', 
	'115' : '05-JAN-2021', '116' : '07-FEB-2021', '117' : '07-MAR-2021', '118' : '04-APR-2021', '119' : '02-MAY-2021', '120' : '06-JUN-2021', 
	'121' : '04-JUL-2021', '122' : '01-AUG-2021', '123' : '05-SEP-2021', '124' : '03-OCT-2021', '125' : '07-NOV-2021', '126' : '05-DEC-2021', 
	'127' : '09-JAN-2022', '128' : '13-FEB-2022', '129' : '13-MAR-2022', '130' : '10-APR-2022', '131' : '08-MAY-2022', '132' : '12-JUN-2022', 
	'133' : '10-JUL-2022', '134' : '14-AUG-2022', '135' : '11-SEP-2022', '136' : '09-OCT-2022'}
	# Find total number of pages
	swa_url_page = "https://www.scotchwhiskyauctions.com/auctions/all/?q="+searchterm+"&search=a"
	swa_htmlcode = requests_session.get(swa_url_page).content
	swa_data = BeautifulSoup(swa_htmlcode, 'html.parser')
	swa_pagelist = swa_data.find('div', {'id':'lotswrap'}).find('h3').text
	swa_lastpage = int(int(swa_pagelist.split(' ',2)[1])/20)+1
	bar.next()
	scotchWhiskyAuctions={}
	tempdict={'lot':'','title':'','price':'','date':''}
	for eachpage in range(swa_lastpage):
		swa_url = "https://www.scotchwhiskyauctions.com/auctions/all/?q="+searchterm+"&search=a&page="+str(eachpage+1)
		swa_htmlcode = requests_session.get(swa_url).content
		swa_data = BeautifulSoup(swa_htmlcode, 'html.parser')
		try:
			swa_auctionlist = swa_data.find('div', {'id':'lots'}).find_all('a')
		except AttributeError:
			break
		for entry in swa_auctionlist:
			tempdict = {}
			tempdict['title']=entry.find('h4').text
			try:
				tempdict['price']=float(entry.find('p', {'class':'sold'}).get_text().split(u"\xA3",1)[1].replace("," , ""))
			except AttributeError:
				break
			tempdict['lot']=entry.find('h6').text.split(' ',2)[2]
			tempkey = tempdict['lot']
			#Date - comes from the lot id eg 127-01423 is the 127th auction so need a lookup dict of number:date
			auctionNumber = str(tempdict['lot'][0:3])
			try:
				tempdict['date'] = swaAuctionDict[auctionNumber]
			except KeyError:
				auctionNumber = str('000')
				tempdict['date'] = swaAuctionDict[auctionNumber]
			newdict = {tempkey : tempdict}
			scotchWhiskyAuctions.update(newdict)
		else:
			continue
		break
	swadata = {}
	for bottle in scotchWhiskyAuctions:
		swadata.update({scotchWhiskyAuctions[bottle]['lot'] : {str(scotchWhiskyAuctions[bottle]['date']) : scotchWhiskyAuctions[bottle]['price']}})
	bar.next()
	return swadata

def multiplot(wadata, whdata, jwdata, gwdata, swadata):
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
	# SWA data
	swaplotstuff = []
	for k,v in swadata.items():
		for key,value in v.items():
			swaplotstuff.append((pltdates.datestr2num(key) , float(value)))
	swadates = [x[0] for x in swaplotstuff]
	swavalues = [x[1] for x in swaplotstuff]
	bar.next()
	# All values for maths
	allValues = wavalues + whvalues + jwvalues + gwvalues + swavalues
    # numpy array for calculations
	npvalues = np.array(allValues)
	return print('\n','Array Size:',npvalues.size)
	'''
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
	swaLabel = "Scotch Whisky Auctions (n="+str(len(swavalues))+")"
	'''


def close():
    requests_session.close()

if __name__ == '__main__':
    multiplot(wa(), wh(), jw(), gw(), swa())
    close()
bar.finish()