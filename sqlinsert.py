#!/usr/bin/env python3
'''
Script to insert new auction lot record
'''

import sys
import sqlite3
import time
import datetime

conn = sqlite3.connect('./Documents/foemw/foemwSource')
c = conn.cursor()

def get_lot_data_from_input():

    # Bottling Name
    c.execute ('SELECT bottlingid, bottlingname FROM bottlings')
    data = c.fetchall()
    for i in data:
        print(i[0],i[1])

    bottleSearch = int(input('Enter bottle ID number: '))
    if bottleSearch < len(data):
        auctionBottle = bottleSearch
        #print('Bottle ID selected: '+str(bottleSearch))
    else:
        print('Wrong number')
        sys.exit()

    # Auction House
    c.execute ('SELECT auctionhouseid, auctionhousename FROM auctionhouses')
    data = c.fetchall()
    for i in data:
        print(i[0],i[1])

    auctionhouseSearch = int(input('Enter Auction House ID number: '))
    if auctionhouseSearch <= len(data):
        #print('Auction House ID selected: '+str(auctionhouseSearch))
        auctionHouse = auctionhouseSearch
    else:
        print('Wrong number')
        sys.exit()

    # Auction Date
    auctiondateInput = str(input('Enter auction date (YYYY-MM-DD): '))
    try:
        datetime.datetime.strptime(auctiondateInput, '%Y-%m-%d')
        auctionDate = auctiondateInput
        #print('Auction date input: '+auctiondateInput)
    except ValueError:
        print('Incorrect date format, should be YYYY-MM-DD')
        sys.exit()

    # Auction Comment
    auctioncommentInput = str(input('Enter lot comment: '))
    #print('Auction comment input: '+auctioncommentInput)
    auctionComment = auctioncommentInput

    # Lot ID
    auctionlotidInput = str(input('Enter lot ID: '))
    #print('Auction ID input: '+auctionlotidInput)
    auctionLotID = auctionlotidInput

    # Lot Price
    auctionpriceInput = str(input('Enter hammer price (pence): '))
    #print('Auction hammer price input: '+auctionpriceInput)
    auctionPrice = int(auctionpriceInput)

    # Confirmation
    print('OK to insert data into database?')
    if str(input('y/n?')) == 'y':
        insertFn(auctionHouse, auctionDate, auctionComment, auctionBottle, auctionPrice, auctionLotID)
    else: sys.exit()

def insertFn(auctionHouse, auctionDate, auctionComment, auctionBottle, auctionPrice, auctionLotID):
    c.execute('INSERT INTO auctionlots(auctiondate, lotreference, hammerprice, lotcomment, auctionhouseid, bottlinglistid)\
    VALUES(?,?,?,?,?,?)', (auctionDate, auctionLotID, auctionPrice, auctionComment, auctionHouse, auctionBottle,))
    conn.commit()
    print('The database entry you made was:')
    c.execute('SELECT * FROM auctionlots ORDER BY lotid DESC LIMIT 1')
    data = c.fetchall()
    print(data)

get_lot_data_from_input()

c.close()
conn.close()
