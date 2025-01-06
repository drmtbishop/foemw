
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
searchterm = "rosebank 31"

# Single request session for speed
requests_session = requests.Session()

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
        #print(str(jw_url))
        tempkey = ""
        # 'Results' entry has list of lots
        for lot_number in range(len(jw_parsed_page['data']['results'])): 
            tempdict={'lot':'','title':'','price':'','date':''}
            #tempkey = ""
            for lot in jw_parsed_page['data']['results'][lot_number].items():
                #print(lot)
                #print("PAGE NUMBER:  "+str(eachpage+1))
                if lot[0] in 'reference_no':
                    #print ('Lot: ' + str(lot[1]))
                    tempdict['lot'] = str(lot[1])
                    #print("TEMPDICT -lotID"+str(tempdict['lot']))
                    tempkey = str(lot[1])
                if lot[0] in 'item':
                    #print ('Title: ' + str(lot[1]['title']))  
                    tempdict['title'] =  str(lot[1]['title'])    
                if lot[0] in 'hammer_price':
                    try: 
                        #print ('Price: ' + str(lot[1].replace("," , "")))
                        tempdict['price'] = str(lot[1].replace("," , ""))
                    except AttributeError:
                        #print ('Price: ' + str("0"))
                        tempdict['price'] = str("0")
                if lot[0] in 'created_at':
                    #print ('Date: ' , datetime.strptime(str(lot[1].split('T',1)[0]), '%Y-%m-%d').date())
                    tempdict['date'] = datetime.strptime(str(lot[1].split('T',1)[0]), '%Y-%m-%d').date()
            newdict = {tempkey : tempdict}
            #print("Length NEWDICT: "+str(len(newdict)))
            justWhisky.update(newdict)

    #jwdata = {}
    print(len(justWhisky))
    for bottle in justWhisky:
        #print(bottle)
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
    print('\n', giantPandaJW)
    return giantPandaJW


jw()

'''
# Just Whisky search
jwdata = {}
def jw1():
    jwpandalist=[]
	# Find total number of pages    
    #jw_url_page = "https://www.just-whisky.co.uk/search?controller=search&orderby=reference&orderway=desc&category=171&search_query="+searchterm+"&submit_search.x=0&submit_search.y=0"
    jw_url_page = "https://www.just-whisky.co.uk/api/search_lots/?page=1&page_size=20&search="+searchterm+"&ordering=-lot_id&sold_lot=true&live_lot=false&filter_counters=false&strict_search=false"
    jw_htmlcode = requests_session.get(jw_url_page).content
    print(jw_htmlcode)
    jw_data = BeautifulSoup(jw_htmlcode, 'html.parser')
    #print(jw_data)
    print(searchterm)
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
        #jw_url = "https://www.just-whisky.co.uk/search?controller=search&orderby=reference&orderway=desc&category=171&search_query=%22rosebank+21%22&submit_search.x=0&submit_search.y=0"+str(eachpage+1)
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
    print('JW',type(giantPandaJW))
    print(giantPandaJW)
    return giantPandaJW


'''