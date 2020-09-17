#!/usr/bin/env python3
'''
Summary stats for selected bottle
'''


import sys
import sqlite3
import time
import datetime
#import matplotlib.pyplot as plt
from dateutil import parser

conn = sqlite3.connect('./Documents/foemw/foemwSource')
c = conn.cursor()

#bottleSearch = str('%'+input('Enter bottle name: ')+'%')
#bottleId = 0

def summary_data():
    # Get Bottling Name
    c.execute ('SELECT bottlingid, bottlingname FROM bottlings')
    data = c.fetchall()
    bottleIdList=[]
    for i in data:
        bottleIdList.append(int(i[0]))
        print(i[0],i[1])
    #print(bottleIdList)
    bottleSearch = int(input('Enter bottle ID number: '))
    if bottleSearch in bottleIdList:
        bottleId = int(bottleSearch)
        #print('Bottle ID selected: '+str(bottleSearch))
    else:
        print('Wrong number')
        sys.exit()

    c.execute ('SELECT auctiondate, auctionlots.auctionhouseid, auctionhouses.auctionhousename, hammerprice/100, bottlings.bottlingname, bottlingid \
    FROM auctionlots \
    INNER JOIN auctionhouses ON auctionlots.auctionhouseid = auctionhouses.auctionhouseid \
    INNER JOIN bottlings ON auctionlots.bottlinglistid = bottlings.bottlingid \
    WHERE bottlingid == ? ORDER BY auctiondate DESC', (bottleId,))
    data = c.fetchall()
    #for e in data: print(e)
    print('\n')
    try:
        print('Bottle selected: '+str(data[0][4]))
    except IndexError:
        print('Nothing found')
        sys.exit()

    bottlename = data[0][2]
    values = []
    col_names = [i[0] for i in c.description]
    #for col in col_names: print(col)
    print(col_names[0], col_names[2], col_names[3])
    for row in data:
        print(row[0], row[2], '\t£',row[3])
        values.append(row[3])
    priceMean = sum(values) / len(values)
    print('Mean Hammer Price: £%.2f' % priceMean)
    print('Min Hammer Price: £%.2f' % min(values))
    print('Max Hammer Price: £%.2f' % max(values))



summary_data()

c.close()
conn.close()
