#!/usr/bin/env python3
import sys
import sqlite3
import time
import datetime
import matplotlib.pyplot as plt
from dateutil import parser

conn = sqlite3.connect('./Documents/foemw/foemwSource')
c = conn.cursor()

bottleSearch = str('%'+input('Enter bottle name: ')+'%')
bottlename = ''

def graph_data():
    c.execute ('SELECT auctiondate, hammerprice/100, bottlingname \
    FROM auctionlots \
    INNER JOIN bottlings ON auctionlots.bottlinglistid = bottlings.bottlingid \
    WHERE bottlingname LIKE ? ORDER BY auctiondate', (bottleSearch,))
    data = c.fetchall()
    try:
        print('Bottle selected: '+data[0][2])
    except IndexError:
        print('Nothing found')
        sys.exit()
    bottlename = data[0][2]
    dates = []
    values = []

    for row in data:
        print(row)
        dates.append(parser.parse(row[0]))
        values.append(row[1])
    #Rolling mean values
    N = 3
    cumsum, moving_aves = [0], []
    for i, x in enumerate(values, 1):
        cumsum.append(cumsum[i-1] + x)
        if i >= N:
            moving_ave = (cumsum[i] - cumsum [i-N])/N
            moving_aves.append(moving_ave)
        else: moving_aves.append(cumsum[i]/i)

    plotFn(dates, values, moving_aves, bottlename)


def plotFn(dates, values, moving_aves, bottlename):
    plt.plot_date(dates, values, 'o')
    plt.plot_date(dates, moving_aves, '-')
    plt.ylabel('Auction Price (£)')
    plt.xticks(rotation=90)
    plt.subplots_adjust(bottom = 0.3)
    plt.title('Auction Price History with Rolling Average: ' + bottlename)
    plt.show()

graph_data()

c.close()
conn.close()
