#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
Scraping whisky auction websites for bottle data
using pandas instead of plotting
'''
import requests
from bs4 import BeautifulSoup
import re
import html
import sys
from datetime import datetime
import numpy as np
import pandas as pd
from progress.bar import Bar
import json

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

# Create pandas array to collect all data
giantPandadata = {
    'auctionhouse': pd.Series(dtype='str'), 
    'lotid': pd.Series(dtype='str'), 
    'bottlename': pd.Series(dtype='str'), 
    'saledate': pd.Series(dtype='datetime64[ns]'), 
    'hammerprice': pd.Series(dtype='float')}
giantPanda = pd.DataFrame(giantPandadata)

def pandaUpdate(giantPandaWH, giantPandaWA, giantPandaGW, giantPandaJW, giantPandaSWA):
    # use for creating final panda
    giantPandaFinal = pd.concat(
        [giantPandaWH, giantPandaWA, giantPandaGW, giantPandaJW, giantPandaSWA], ignore_index=True)
    #print('\n',giantPandaFinal[["auctionhouse", "bottlename"]].groupby("auctionhouse").count())
    bar.next()
    giantPandaFinal = giantPandaFinal.astype({'hammerprice': float})
    gp = giantPandaFinal.groupby(['bottlename'])
    print('\n',gp.agg(['count','mean']))
    #style.format({'mean':'£{:.2f}'}))
    print('\n', giantPandaFinal.groupby(['auctionhouse']).size().to_string())
    return


# Whisky Hammer search
whdata = {}
def wh():
    #whdata = {}
    whpandalist= []
    whsearchterm = searchterm.replace("+","-")
    wh_url = "https://www.whiskyhammer.com/auction/past/q-"+whsearchterm+"/?sortby=end-time&ps=1000"
    wh_htmlcode = requests_session.get(wh_url).content
    wh_data = BeautifulSoup(wh_htmlcode, 'html.parser')
    wh_auctionlist = wh_data.find('div', {'id':'browse'})
    wh_bottlelist = re.search("\\[\\{.+\\}\\]", str(wh_auctionlist))
    try:
        wh_bottlelisttrim = wh_bottlelist.group()[1:-1]
    except AttributeError:
        return giantPanda
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
        whpandalist.append({
        'auctionhouse':'wh', 
        'lotid': whiskyHammer[bottle]['id'],
        'bottlename': whiskyHammer[bottle]['name'],
        'saledate': str(datetime.strptime(whiskyHammer[bottle]['ends_human_friendly'],'%d\\/%m\\/%Y').date()),
        'hammerprice': whiskyHammer[bottle]['item_price']
        })
    bar.next()
    giantPandaWH = pd.DataFrame(whpandalist)
    #print('WH',type(giantPandaWH))
    return giantPandaWH

# Whisky Auctioneer search
wadata = {}
def wa():
    wadata = {}
    wapandalist=[]
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
            return giantPanda
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
            wapandalist.append({
            'auctionhouse':'wa', 
            'lotid': whiskyAuctioneer[bottle]['lot'],
            'bottlename': whiskyAuctioneer[bottle]['title'],
            'saledate': str(whiskyAuctioneer[bottle]['date']),
            'hammerprice': whiskyAuctioneer[bottle]['price']
            })
        except KeyError:
            continue
    bar.next()
    giantPandaWA = pd.DataFrame(wapandalist)
    #print('WA',type(giantPandaWA))
    return giantPandaWA

# Just Whisky search
jwdata = {}
def jw():
    jwpandalist=[] 
    jw_url_page = "https://www.just-whisky.co.uk/api/search_lots/?page=1&page_size=20&search="+searchterm+"&ordering=-lot_id&sold_lot=true&live_lot=false&filter_counters=false&strict_search=false"
    jw_htmlcode = requests_session.get(jw_url_page).content
    jw_parsed = json.loads(jw_htmlcode)
    # Find total number of pages  
    jw_lastpage = int(jw_parsed['data']['total_pages'])
    justWhisky={}
    bar.next()
    tempdict={'lot':'','title':'','price':'','date':''}
    for eachpage in range(jw_lastpage):
        jw_url = "https://www.just-whisky.co.uk/api/search_lots/?page="+str(eachpage+1)+"&page_size=20&search="+searchterm+"&ordering=-lot_id&sold_lot=true&live_lot=false&filter_counters=false&strict_search=false"
        jw_html_page_code = requests_session.get(jw_url).content
        jw_parsed_page = json.loads(jw_html_page_code)
        tempkey = ""
        # 'Results' entry has list of lots
        for lot_number in range(len(jw_parsed_page['data']['results'])): 
            tempdict={'lot':'','title':'','price':'','date':''}
            for lot in jw_parsed_page['data']['results'][lot_number].items():
                if lot[0] in 'reference_no':
                    tempdict['lot'] = str(lot[1])
                    tempkey = str(lot[1])
                if lot[0] in 'item': 
                    tempdict['title'] =  str(lot[1]['title'])    
                if lot[0] in 'hammer_price':
                    try: 
                        tempdict['price'] = str(lot[1].replace("," , ""))
                    except AttributeError:
                        tempdict['price'] = str("0")
                if lot[0] in 'created_at':
                    tempdict['date'] = datetime.strptime(str(lot[1].split('T',1)[0]), '%Y-%m-%d').date()
            newdict = {tempkey : tempdict}
            justWhisky.update(newdict)

    #jwdata = {}
    #print(len(justWhisky))
    for bottle in justWhisky:
        jwpandalist.append({
            'auctionhouse':'jw', 
            'lotid': justWhisky[bottle]['lot'],
            'bottlename': justWhisky[bottle]['title'],
            'saledate': str(justWhisky[bottle]['date']),
            'hammerprice': justWhisky[bottle]['price']
            })
    bar.next()
    giantPandaJW = pd.DataFrame(jwpandalist)
    return giantPandaJW


# Grand Whisky Auction search
gwdata = {}
def gw():
    gwpandalist=[]
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
            tempdict['title'] = str(name_data[0]).split(':', 1)[1].strip('",')

            tempkey = tempdict['lot']
            newdict = {tempkey : tempdict}
            grandWhisky.update(newdict)
        else:
            continue
        break

    gwdata = {}
    for bottle in grandWhisky:
        gwpandalist.append({
            'auctionhouse':'gw', 
            'lotid': grandWhisky[bottle]['lot'],
            'bottlename': grandWhisky[bottle]['title'],
            'saledate': str(grandWhisky[bottle]['date']),
            'hammerprice': grandWhisky[bottle]['price']
            })
    bar.next()
    giantPandaGW = pd.DataFrame(gwpandalist)
    #print('GW',type(giantPandaGW))
    return giantPandaGW

# Scotch Whisky Auctions search
swadata = {}
def swa():
    swapandalist=[]
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
    '133' : '10-JUL-2022', '134' : '14-AUG-2022', '135' : '11-SEP-2022', '136' : '09-OCT-2022', '137' : '13-NOV-2022', '138' : '11-DEC-2022', 
    '139' : '08-JAN-2023', '140' : '12-FEB-2023', '141' : '12-MAR-2023', '142' : '09-APR-2023'}
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
                tempdict['price']=float(entry.find('p', {'class':'sold'}).get_text().split(u"\xA3",1)[1].split(" ",1)[0].replace("," , ""))
            except AttributeError as e:
                #print('Error.', repr(e))
                continue
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
        swapandalist.append({
        'auctionhouse':'swa', 
        'lotid': scotchWhiskyAuctions[bottle]['lot'],
        'bottlename': scotchWhiskyAuctions[bottle]['title'],
        'saledate': str(scotchWhiskyAuctions[bottle]['date']),
        'hammerprice': scotchWhiskyAuctions[bottle]['price']
        })
    bar.next()
    giantPandaSWA = pd.DataFrame(swapandalist)
    #print('SWA',type(giantPandaSWA))
    return giantPandaSWA

def close():
    requests_session.close()

if __name__ == '__main__':
    pandaUpdate(wa(), wh(), gw(), jw(), swa())
    close() 
bar.finish()