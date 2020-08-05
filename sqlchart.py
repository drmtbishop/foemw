#!/usr/bin/env python3

import sqlite3
import time
import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from dateutil import parser
from matplotlib import style
#style.use('fivethirtyeight')


conn = sqlite3.connect('foemwSource')
c = conn.cursor()

bottleSearch = '%Inaugural%'

def read_from_db():
    c.execute ('SELECT auctiondate, hammerprice, bottlingname \
    FROM auctionlots \
    INNER JOIN bottlings ON auctionlots.bottlinglistid = bottlings.bottlingid \
    WHERE bottlingname LIKE ? ORDER BY auctiondate', (bottleSearch,))
    data = c.fetchall()
    #print(data)
    for row in data:
        print(row)

def graph_data():
    c.execute ('SELECT auctiondate, hammerprice, bottlingname \
    FROM auctionlots \
    INNER JOIN bottlings ON auctionlots.bottlinglistid = bottlings.bottlingid \
    WHERE bottlingname LIKE ? ORDER BY auctiondate', (bottleSearch,))
    data = c.fetchall()

    dates = []
    values = []

    for row in data:
        dates.append(parser.parse(row[0]))
        values.append(row[1]/100)

    plotFn(dates, values, bottleSearch)
    #plt.plot_date(dates, values, '+')
    #plt.ylabel('Auction Price (£)')
    #plt.xticks(rotation=90)
    #plt.subplots_adjust(bottom = 0.3)
    #plt.title('Auction Price History for Search: ' + bottleSearch)
    #plt.show()

def multi_graph_plot():
    c.execute ('SELECT auctiondate, hammerprice, bottlingname \
    FROM auctionlots \
    INNER JOIN bottlings ON auctionlots.bottlinglistid = bottlings.bottlingid \
    WHERE bottlingname LIKE ? ORDER BY auctiondate', (bottleSearch,))
    data = c.fetchall()

    dates = []
    values = []
    bottles = []

    for row in data:
        if row[2] not in bottles: bottles.append(row[2])
    for bottle in sorted(bottles):
        dates = []
        values = []
        for row in data:
            if row[2] == bottle:
                values.append(row[1]/100)
                dates.append(parser.parse(row[0]))
        plotFn(dates, values, bottle)

def plotFn(dates, values, bottle):
    plt.plot_date(dates, values, '+')
    plt.ylabel('Auction Price (£)')
    plt.xticks(rotation=90)
    plt.subplots_adjust(bottom = 0.3)
    plt.title('Auction Price History for Search: ' + bottle)
    plt.show()



read_from_db()
graph_data()
#multi_graph_plot()
c.close()
conn.close()
