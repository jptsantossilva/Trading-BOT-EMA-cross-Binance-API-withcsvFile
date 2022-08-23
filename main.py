from symtable import Symbol
from webbrowser import get
from binance import Client
import pandas as pd
import constants
import datetime as dt

# get binance api key and secret from constants.py file
api_key = constants.api_key
api_secret = constants.api_secret

client = Client(api_key, api_secret)

interval='1h'
posframe = pd.read_csv('/home/joaosilva/Documents/GitHub/Trading-BOT-EMA-cross-Binance-API-withcsvFile/position.csv')

def changepos(curr, buy=True):
    if buy:
        posframe.loc[posframe.Currency == curr, 'position'] = 1
    else:
        posframe.loc[posframe.Currency == curr, 'position'] = 0

    posframe.to_csv('position', index=False)

def gethourlydata(Symbol):
    frame = pd.DataFrame(client.get_historical_klines(Symbol,
                                                      interval,
                                                      '34 hours ago UTC'))
    
    frame = frame.iloc[:,:5] # use the first 5 columns
    frame.columns = ['Time','Open','High','Low','Close'] #rename columns
    frame[['Open','High','Low','Close']] = frame[['Open','High','Low','Close']].astype(float) #cast to float
    frame.Time = pd.to_datetime(frame.Time, unit='ms') #make human readable timestamp
    return frame

#df = gethourlydata('BTCUSDT')

def applytechnicals(df):
    # df['FastSMA'] = df.Close.rolling(8).mean()
    df['FastEMA'] = df.Close.ewm(span=10, adjust=False).mean()
    # df['SlowSMA'] = df.Close.rolling(34).mean()
    df['SlowEMA'] = df.Close.ewm(span=10, adjust=False).mean()

# applytechnicals(df)

def trader(curr):
    qty = posframe[posframe.Currency == curr].quantity.values[0]
    df = gethourlydata(curr)
    applytechnicals(df)

    lastrow = df.iloc[-1]
    # if not in position
    if not posframe[posframe.Currency == curr].position.values[0]:
        if lastrow.FastEMA > lastrow.SlowEMA:
            """ order = client.create_order(symbol=curr,
                                        side='BUY',
                                        type='MARKET',
                                        quantity = qty)
             """                            
            # print(order)
            print('BUY {curr}')
            changepos(curr, buy=True)
        else:
            print(f'Not is position {curr} but fast SMA below slow SMA')

    else: # in position
        print(f'Already in {curr} position')
        if lastrow.SlowEMA > lastrow.FastEMA:
            """ order = client.create_order(symbol=curr,
                                        side='SELL',
                                        type='MARKET',
                                        quantity = qty) """

            # print(order)
            print('SELL {curr}')
            changepos(curr, buy=False)

for coin in posframe.Currency:
    trader(coin)




