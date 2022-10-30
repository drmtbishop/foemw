import pandas as pd
import numpy as np

giantpandadata = {
    'auctionhouse': pd.Series(dtype='str'),
    'lotid': pd.Series(dtype='str'),
    'bottlename': pd.Series(dtype='str'),
    'saledate': pd.Series(dtype='datetime64[ns]'),
    'hammerprice': pd.Series(dtype='float')
    }
giantPanda = pd.DataFrame(giantpandadata)

new_row = {
    'auctionhouse': 'wa',
    'lotid': 'abc123-4',
    'bottlename': 'Daftmill 15 Years',
    'saledate': '2022-06-20',
    'hammerprice': 160.00
    }

giantPanda = giantPanda.append(new_row, ignore_index=True)


print(giantPanda)