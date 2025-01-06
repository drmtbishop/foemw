#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
Scraping DRAMFACE website for bottle review scores
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

bar = Bar('>>', max=(11), suffix='Left %(eta_td)s')

# Single request session for speed
requests_session = requests.Session()

# Convert list to dict{}
def Convert(lst):
    res_dct = {lst[i].strip('"'): lst[i + 1].strip('"') for i in range(0, len(lst), 2)}
    return res_dct
'''
# Search input from script argument or if missing, then from input
searchterm = ""
if len(sys.argv) == 2:
	searchterm = str(sys.argv[1]).replace(" ","%20")
else:
	searchterm = input("Search term: ").replace(" ","%20")
'''
df_url = "https://www.dramface.com/all-reviews"
#df_htmlcode = requests_session.get(df_url).content
#df_data = BeautifulSoup(df_htmlcode, 'html.parser')
#df_articlelist = df_data.find_all('h1', {'class': 'blog-title'})
#for review in df_articlelist: print(review.find('a').get('href'))
#print(df_articlelist)
#df_olderlink = df_data.find('div', {'class': 'older'}).find('a').get('href')
#print(df_olderlink)

# Aim:
# Get list of URLs and link to second page from first page
# Amend URLs to global list
# Got to next URL and repeat
bigArticleList = []

def getArticles(url):
    df_htmlcode = requests_session.get(url).content
    df_data = BeautifulSoup(df_htmlcode, 'html.parser')
    df_articlelist = df_data.find_all('h1', {'class': 'blog-title'})
    for review in df_articlelist:
        bigArticleList.append(review.find('a').get('href'))
    # print(df_articlelist)
    df_olderlink = df_data.find('div', {'class': 'older'}).find('a').get('href')
    nextpageURL = "https://www.dramface.com"+df_olderlink
    print(nextpageURL)
    return nextpageURL

getArticles(df_url)
print(bigArticleList)

'''
# Create pandas array to collect all data
giantPandadata = {
    'reviewer': pd.Series(dtype='str'), 
    'tldr': pd.Series(dtype='str'), 
    'bottlename': pd.Series(dtype='str'), 
    'subheading': pd.Series(dtype='str'),
    'reviewdate': pd.Series(dtype='datetime64[ns]'), 
    'abv': pd.Series(dtype='float')}
giantPanda = pd.DataFrame(giantPandadata)

def pandaUpdate(giantPandaDF):
    # use for creating final panda
    giantPandaFinal = giantPandaDF
    #print('\n',giantPandaFinal[["auctionhouse", "bottlename"]].groupby("auctionhouse").count())
    bar.next()
    giantPandaFinal = giantPandaFinal.astype({'abv': float})
    #gp = giantPandaFinal.groupby(['bottlename'])
    #print('\n',gp.agg(['count','mean']))
    #style.format({'mean':'£{:.2f}'}))
    print('\n', giantPandaFinal.groupby(['bottlename']).size())
    return

'''
# Whisky Hammer search
dfdata = {}
def df():
    #whdata = {}
    dfpandalist= []
    dfsearchterm = searchterm.replace("+","-")
    df_url = "https://www.dramface.com/all-reviews#eapps-search-621828cd-e493-462f-9142-266dcd6702b4-" + \
        dfsearchterm
    df_htmlcode = requests_session.get(df_url).content
    df_data = BeautifulSoup(df_htmlcode, 'html.parser')
    df_articlelist = df_data.find('div', {'class': 'blog-title preFlex flexIn'})
    
    '''
    df_bottlelist = re.search("\\[\\{.+\\}\\]", str(df_auctionlist))
    try:
        df_bottlelisttrim = df_bottlelist.group()[1:-1]
    except AttributeError:
        return giantPanda
    dramFace={}
    bar.next()
    for item in df_bottlelisttrim.split("}"):
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
            dramFace.update(newdict)
    for bottle in dramFace:
        dfpandalist.append({
        'auctionhouse':'wh', 
        'lotid': dramFace[bottle]['id'],
        'bottlename': dramFace[bottle]['name'],
        'saledate': str(datetime.strptime(whiskyHammer[bottle]['ends_human_friendly'],'%d\\/%m\\/%Y').date()),
        'hammerprice': dramFace[bottle]['item_price']
        })
    '''
    bar.next()
    giantPandaDF = pd.DataFrame(dfpandalist)
    #print('WH',type(giantPandaWH))
    return giantPandaDF
'''
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
                tempdict['date'] = datetime.strptime("01-January-2023", '%d-%B-%Y').date()
                #tempdict['date'] = datetime.strptime("01-"+entry.find('a', {'class':'product_img_link'}).get('href').split('/',4)[3].split(
                #    '-')[0]+"-"+entry.find('a', {'class':'product_img_link'}).get('href').split('/',4)[3].split('-')[1], '%d-%B-%Y').date()
            newdict = {tempkey : tempdict}
            justWhisky.update(newdict)

    jwdata = {}
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
    #print('JW',type(giantPandaJW))
    return giantPandaJW
'''


def close():
    requests_session.close()

if __name__ == '__main__':
    #pandaUpdate(df())
    #df()
    close() 
bar.finish()