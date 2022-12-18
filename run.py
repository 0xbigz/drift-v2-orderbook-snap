import requests
import os

x = requests.get('https://dlob.drift.trade/orders/json').json()

market_to_oracle_map = pd.DataFrame(x['oracles']).set_index('marketIndex').to_dict()['price']
market_to_oracle_map

import pandas as pd
df = pd.DataFrame([order['order'] for order in x['orders']])
user = pd.DataFrame([order['user'] for order in x['orders']], columns=['user'])
df = pd.concat([df, user],axis=1)
df['oraclePrice'] = df['marketIndex'].apply(lambda x: market_to_oracle_map[x])
df1 = df[(df.orderType=='limit')]
df1.loc[df1['price'].astype(int)==0, 'price'] = df1['oraclePrice'].astype(int) + df1['oraclePriceOffset'].astype(int)

for col in ['price', 'oraclePrice', 'oraclePriceOffset']:
    df1[col] = df1[col].astype(int)
    df1[col] /= 1e6
    
for col in ['quoteAssetAmountFilled']:
    df1[col] = df1[col].astype(int)
    df1[col] /= 1e6 

for col in ['baseAssetAmount', 'baseAssetAmountFilled']:
    df1[col] = df1[col].astype(int)
    df1[col] /= 1e9
    

market_types = sorted(df.marketType.unique())
market_indexes = sorted(df.marketIndex.unique())
for t in market_types:
    for i in market_indexes:
        mdf = df1[((df1.marketType==t) & (df1.marketIndex==i))]
        mdf = mdf[['price', 'baseAssetAmount', 'direction', 'user', 'status', 'orderType', 'marketType', 'slot', 'orderId', 'userOrderId',
       'marketIndex',  'baseAssetAmountFilled',
       'quoteAssetAmountFilled',  'reduceOnly', 'triggerPrice',
       'triggerCondition', 'existingPositionDirection', 'postOnly',
       'immediateOrCancel', 'oraclePriceOffset', 'auctionDuration',
       'auctionStartPrice', 'auctionEndPrice', 'maxTs', 'oraclePrice']]
        mdf = mdf.sort_values('price').reset_index(drop=True)
        out_ff = str(t)+str(i)+'/orderbook_slot_'+str(x['slot'])+'.csv'
        os.makedirs(str(t)+str(i), exist_ok=True)
        mdf.to_csv(out_ff, index=False)
