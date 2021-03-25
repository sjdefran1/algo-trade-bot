# -*- coding: utf-8 -*-
"""
Created on Tue Dec  8 01:26:31 2020

@author: sjdef
"""

# imports for time
import time
from datetime import datetime
import pytz

# imports for data
#import yfinance as yf # pricing data
#import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import sqlite3
# imports for trade
import alpaca_trade_api as tradeapi
#import backtrader as bt

# ticker = 'TSLA'
# ohlcv = yf.download(ticker,dt.date(2020, 6, 2)-dt.timedelta(1825),dt.date(2020, 6, 2))
connection = sqlite3.connect('C:/Users/sjdef/Desktop/CODE/VADER/sql/data.db') 
cursor = connection.cursor()

# global var for max orders this bot can have at once
MAX_ORDERS = 5

# connect to alpaca
api = tradeapi.REST(
    base_url= 'https://paper-api.alpaca.markets',
    key_id='PK8IOBAM1R0SRJWSRWLN',
    secret_key='IKauGAZE66TMRMll2s1jcbP2anIPx6xOehuBwRiu'
)

# =============================================================================
# api.submit_order(
#     symbol='TSLA',
#     qty=15,
#     side='buy',
#     type='market',
#     time_in_force='gtc'
# )
# =============================================================================

def populate_db(timeFrame, limit):
    #connect to alpaca
    NY = 'America/New_York'
    api = tradeapi.REST(
        base_url= 'wss://data.alpaca.markets/stream',
        key_id='PK8IOBAM1R0SRJWSRWLN',
        secret_key='IKauGAZE66TMRMll2s1jcbP2anIPx6xOehuBwRiu'
    )
    
    
    tickers = ['AAL', 'AAPL', 'ADBE', 'ADI', 'ADP', 'ADSK', 'ALGN', 'ALXN', 'AMAT', 'AMGN', 'AMZN', 'ASML', 'ATVI', 'AVGO', 'BIDU', 'BIIB', 'BKNG', 'BMRN', 'CA', 'CDNS', 'CELG', 'CERN', 'CHKP', 'CHTR', 'CMCSA', 'COST', 'CSCO', 'CSX', 'CTAS', 'CTRP', 'CTSH', 'CTXS', 'DISH', 'DLTR', 'EA', 'EBAY', 'ESRX', 'EXPE', 'FAST', 'FB', 'FISV', 'FOX', 'FOXA', 'GILD', 'GOOG', 'GOOGL', 'HAS', 'HOLX', 'HSIC', 'IDXX', 'ILMN', 'INCY', 'INTC', 'INTU', 'ISRG', 'JBHT', 'JD', 'KHC', 'KLAC', 'LBTYA', 'LBTYK', 'LRCX', 'MAR', 'MCHP', 'MDLZ', 'MELI', 'MNST', 'MSFT', 'MU', 'MXIM', 'MYL', 'NFLX', 'NTES', 'NVDA', 'ORLY', 'PAYX', 'PCAR', 'PYPL', 'QCOM', 'QRTEA', 'REGN', 'ROST', 'SBUX', 'SHPG', 'SIRI', 'SNPS', 'STX', 'SWKS', 'SYMC', 'TMUS', 'TSLA', 'TTWO', 'TXN', 'ULTA', 'VOD', 'VRSK', 'VRTX', 'WBA', 'WDAY', 'WDC', 'WYNN', 'XLNX', 'XRAY']
    universe = []
    now = pd.Timestamp.now(tz=NY)
    
    
    end = pd.Timestamp.now(tz=NY) - pd.Timedelta('1 days')
    # timeFrame = 'day'
    # limit = 1000
    for ticker in tickers:
        print(f'Gathering data for {ticker}')
        
    
        current = api.get_barset(
                ticker,
                timeFrame,
                limit = limit,
                start=now,
                end=end
            )
        universe.append(current.df)
        print(f'Success gathering data for {ticker}')
   

    #store our last day we gathered data for
    lastDate = now.strftime("%m-%d-%Y, 18:30:00-05:00")
    fileTest = open("C:/Users/sjdef/Desktop/CODE/VADER/src/lastday.txt","w") 
    fileTest.write(str(lastDate))
    fileTest.close()
    
    

# ---------------------------------------------
# populate dataBase
# timeFrame =  minute, 1m, 5m, 15m, day
# limit = number of bars 0-1000

    #timeFrame = '15Min'
    #limit = 400
    
    print('\nEntering stocks into database\n')
    
    counter = 0
    while counter <= len(universe) - 1:
        df = universe[counter].copy()
        stock = universe[counter].columns[1][0]
        df.columns = ['open', 'high', 'low', 'close', 'volume']
        print(f'Uploading data for {stock}...')
        for row in range(len(df)):
            try:
                idx = df.index[row]
                insert = df.loc[idx]
                cursor.execute(f"INSERT OR IGNORE into {stock}_{timeFrame} VALUES ('{df.index[row]}', {df.loc[idx][0]}, {df.loc[idx][1]}, {df.loc[idx][2]}, {df.loc[idx][3]}, {df.loc[idx][4]})")
    
            #pd.DataFrame.to_sql(df, name=f'{stock}', con=connection, if_exists='append')
            except Exception as e:
                print(f"{stock} already has {df.index[row]}")
                print(e)
        
        print(f'Success uploading data for {stock}')
        counter +=1
    connection.commit()
    return

def getSqlData(timeFrame, Range=500):
    counter = 0
    # all stocks we have data for
    # tickers = ['AAL', 'AAPL', 'ADBE', 'ADI', 'ADP', 'ADSK', 'ALGN', 'ALXN', 'AMAT', 'AMGN', 'AMZN', 'ASML', 'ATVI', 'AVGO', 'BIDU', 'BIIB', 'BKNG', 'BMRN', 'CA', 'CDNS', 'CELG', 'CERN', 'CHKP', 'CHTR', 'CMCSA', 'COST', 'CSCO', 'CSX', 'CTAS', 'CTRP', 'CTSH', 'CTXS', 'DISH', 'DLTR', 'EA', 'EBAY', 'ESRX', 'EXPE', 'FAST', 'FB', 'FISV', 'FOX', 'FOXA', 'GILD', 'GOOG', 'GOOGL', 'HAS', 'HOLX', 'HSIC', 'IDXX', 'ILMN', 'INCY', 'INTC', 'INTU', 'ISRG', 'JBHT', 'JD', 'KHC', 'KLAC', 'LBTYA', 'LBTYK', 'LRCX', 'MAR', 'MCHP', 'MDLZ', 'MELI', 'MNST', 'MSFT', 'MU', 'MXIM', 'MYL', 'NFLX', 'NTES', 'NVDA', 'ORLY', 'PAYX', 'PCAR', 'PYPL', 'QCOM', 'QRTEA', 'REGN', 'ROST', 'SBUX', 'SHPG', 'SIRI', 'SNPS', 'STX', 'SWKS', 'SYMC', 'TMUS', 'TSLA', 'TTWO', 'TXN', 'ULTA', 'VOD', 'VRSK', 'VRTX', 'WBA', 'WDAY', 'WDC', 'WYNN', 'XLNX', 'XRAY']
    # winning stocks below
    tickers = ['AAL', 'AMAT', 'CMCSA', 'CSCO', 'DISH', 'KHC', 'MNST', 'MU', 'SBUX', 'STX', 'ADI', 'ADP', 'ALGN', 'ASML', 'AVGO', 'BIDU', 'CA', 'CDNS', 'CELG', 'CERN', 'CHTR', 'CSX', 'CTSH', 'FAST', 'FISV', 'INTU', 'KLAC', 'LBTYA', 'LRCX', 'MCHP', 'PAYX', 'QCOM', 'ROST', 'TMUS', 'TSLA', 'TTWO', 'VOD', 'WDC']
    
    universe = []
    #Range = 200
    while counter < len(tickers):
        stock = tickers[counter]
        #read in table from sql
        df = pd.read_sql_query(f"select * from {stock}_{timeFrame} order by time desc limit {Range};", connection)
        #format df to work with rest of code
        nyc = pytz.timezone('America/New_York')
        df.index = pd.to_datetime(df.index, utc=True)
        df.index = df.index.tz_convert(nyc)
        df = df.set_index('time')
        df = df.iloc[::-1]
        columns = [(stock,'open'),(stock,'high'), (stock, 'low'), (stock, 'close'), (stock, 'volume')]
        df.columns=pd.MultiIndex.from_tuples(columns)
        universe.append(df)
        #cursor.execute(f'SELECT * from {stock}')
        #df = cursor.fetchall()
        connection.commit()
        counter += 1

    return universe

# find profit/loss of backtests
def profit_or_loss(positions, exited):
    profit_loss = 0
    counter = 0
    while counter <= len(positions)-1:
        #position = 0
        # long pos
        shares = positions[counter][3]
        entry = positions[counter][1]
        Exit = exited[counter][1]
        amount = 0
        
        if positions[counter][0] == 'L':
           #loss
           if entry > Exit:
               amount = entry - Exit
               profit_loss = profit_loss - (amount * shares)
               print(f'Entry: {entry} | Exit: {Exit} | Shares: {shares} | Loss/Share: {round(amount,2)} | Running p/L: ${round(profit_loss,2)} |\n\n')
           elif Exit > entry:
               amount = Exit - entry
               profit_loss = profit_loss + (amount * shares)
               print(f'Entry: {entry} | Exit: {Exit} | Profit/Share: {round(amount,2)} | Running p/L: ${round(profit_loss,2)} |\n\n')
           else:
               print('weird')
           
        # short pos
        else:
              #loss
           if entry > Exit:
               amount = entry - Exit
               profit_loss = profit_loss + (amount * shares)
               print(f'Entry: {entry} | Exit: {Exit} | Shares: {shares} | Profit/Share: {round(amount,2)} | Running p/L: ${round(profit_loss,2)} |\n\n' )
           elif Exit > entry:
               amount = Exit - entry
               profit_loss = profit_loss - (amount * shares)
               print(f'Entry: {entry} | Exit: {Exit} | Shares: {shares} | Loss/Share: {round(amount,2)} | Running p/L: ${round(profit_loss,2)} |\n\n')
           else:
               print('weird')
        counter +=1    
        
    return profit_loss
        

# find 2 percent of account size
# find how many shares we can buy with that
def positionSize(currentPrice, accountSize):
    # accountSize = 100000
    # currentPrice = 242.43
    money_to_risk = accountSize * .02
    shares = round(money_to_risk / currentPrice, 0)
    return shares

# used to get maxstop,target1r in backtesting
def quickPOS(universe):
    # universe = finalPort
    counter = 0
    positions = []
    while counter <= len(universe) -1:
        position_rec = []
        stock = universe[counter].columns[1][0]
        df = universe[counter].copy()
        close = round(df[stock, 'close'][-1], 2)
        AvgGain = 3
        AvgLoss = 2
        side = df[stock, 'crossover'][-1]
        # long pos
        if side == 1:
            maxStop = round(close * ((100 - AvgLoss) / 100), 2)
            Target1R = round(close * ((100 + AvgGain) / 100), 2)
            
            # pos_rec = [shares, stop loss, target profit]
            pos_rec = [positionSize(close, accountSize=100000), maxStop, Target1R]
            positions.append(pos_rec)
        
        # short pos
        else:
            maxStop = round(close * ((100 + AvgLoss) / 100), 2)
            Target1R = round(close * ((100 - AvgGain) / 100), 2)

            # pos_rec = [shares, stop loss, target profit]
            pos_rec = [positionSize(close, accountSize=100000), maxStop, Target1R]
            positions.append(pos_rec)
        
        counter +=1
    return positions


##def addSAR(universe, portfolio):
def addSAR(universe, trending_in_portfolio):
    
    
    def calcSAR(df, stock):
        df.columns = ['open', 'high', 'low', 'close', 'volume', 'crossover']
        df['AF'] =0.02
        df['PSAR'] = df['low']
        df['EP'] = df['high']
        df['PSARdir'] = "bull"
    
        for a in range(1, len(df)):
            # if trending upwards  
            # Current SAR = Prior SAR + Prior AF(Prior EP - Prior SAR)
            if df.loc[df.index[a-1], 'PSARdir'] == 'bull':
    
                df.loc[df.index[a], 'PSAR'] = df.loc[df.index[a-1], 'PSAR'] + (df.loc[df.index[a-1], 'AF']*(df.loc[df.index[a-1], 'EP']-df.loc[df.index[a-1], 'PSAR']))          
    
                df.loc[df.index[a], 'PSARdir'] = "bull"
                
                # if our low is less than our previos psar, trend has changed into bearish
                # change our ['EP'] to the new low
                # psar becomes our last extreme-point
                if df.loc[df.index[a], 'low'] < df.loc[df.index[a-1], 'PSAR']:
                    df.loc[df.index[a], 'PSARdir'] = "bear"
                    df.loc[df.index[a], 'PSAR'] = df.loc[df.index[a-1], 'EP']
                    df.loc[df.index[a], 'EP'] = df.loc[df.index[a-1], 'low']
                    df.loc[df.index[a], 'AF'] = .02
                
                # trend is still bullish
                else:
                    # see if we are at a new high
                    # set our new high to current row, in column ['EP']
                    if df.loc[df.index[a], 'high'] > df.loc[df.index[a-1], 'EP']:
                        df.loc[df.index[a], 'EP'] = df.loc[df.index[a], 'high']
                        
                        # check to see if were at max accelearation
                        if df.loc[df.index[a-1], 'AF'] <= 0.18:
                            df.loc[df.index[a], 'AF'] =df.loc[df.index[a-1], 'AF'] + 0.02
                        # if we are keep it at .2
                        else:
                            df.loc[df.index[a], 'AF'] = df.loc[df.index[a-1], 'AF']
                    
                    # our extreme point hasn't changed so AF and EP are set to previous day values
                    elif df.loc[df.index[a], 'high'] <= df.loc[df.index[a-1], 'EP']:
                        df.loc[df.index[a], 'AF'] = df.loc[df.index[a-1], 'AF']
                        df.loc[df.index[a], 'EP'] = df.loc[df.index[a-1], 'EP']               
    
    
            # if trending downwards 
            # Current SAR = Prior SAR - Prior AF(Prior EP - Prior SAR)
            elif df.loc[df.index[a-1], 'PSARdir'] == 'bear':
                
                df.loc[df.index[a], 'PSAR'] = df.loc[df.index[a-1], 'PSAR'] - (df.loc[df.index[a-1], 'AF']*(df.loc[df.index[a-1], 'PSAR']-df.loc[df.index[a-1], 'EP']))
    
                df.loc[df.index[a], 'PSARdir'] = "bear"
                # trend changed
                if df.loc[df.index[a], 'high'] > df.loc[df.index[a-1], 'PSAR']:
                    df.loc[df.index[a], 'PSARdir'] = "bull"
                    df.loc[df.index[a], 'PSAR'] = df.loc[df.index[a-1], 'EP']
                    df.loc[df.index[a], 'EP'] = df.loc[df.index[a-1], 'high']
                    df.loc[df.index[a], 'AF'] = .02
                # still bearish, check for new extreme low, if there is adjust AF
                else:
                    if df.loc[df.index[a], 'low'] < df.loc[df.index[a-1], 'EP']:
                        df.loc[df.index[a], 'EP'] = df.loc[df.index[a], 'low']
                        if df.loc[df.index[a-1], 'AF'] <= 0.18:
                            df.loc[df.index[a], 'AF'] = df.loc[df.index[a-1], 'AF'] + 0.02
                        else:
                            df.loc[df.index[a], 'AF'] = df.loc[df.index[a-1], 'AF']
    
                    elif df.loc[df.index[a], 'low'] >= df.loc[df.index[a-1], 'EP']:
                        df.loc[df.index[a], 'AF'] = df.loc[df.index[a-1], 'AF']
                        df.loc[df.index[a], 'EP'] = df.loc[df.index[a-1], 'EP']           
        
                        
        #get rid of rest of values and store psar
        df = df.drop(['PSARdir', 'EP', 'AF'], axis = 1)
        columns = [(stock,'open'),(stock,'high'), (stock, 'low'), (stock, 'close'), (stock, 'volume'), (stock, 'crossover'), (stock, 'PSAR')]
        df.columns=pd.MultiIndex.from_tuples(columns)

        return df
    
    
    counter = 0
    portfolio = trending_in_portfolio
    finished_portfolio = []
    while counter <= len(portfolio) -1:
    ##while counter <= len(universe) - 1:    
        loc = portfolio[counter][0]
        df = universe[loc].copy()
        ##df  = universe[counter].copy()
        stock = universe[loc].columns[1][0]
        ##stock = universe[counter].columns[1][0]
        print(f'Calling {stock} psar values calculator....')
        df = calcSAR(df, stock)
        finished_portfolio.append(df)
        print(f'Recieved {stock} psar values')
        counter += 1
        
    return finished_portfolio

def directionTrend(universe):
    # universe = finalPort
    counter = 0
    trending_portfolio = []
    while counter < len(universe):
        df = universe[counter].copy()
        stock = universe[counter].columns[1][0]
        df[stock, "trendMA"] = df[stock, "close"].ewm(span = 200, min_periods = 200).mean()
        df = df.dropna()
        length = len(df[stock, "trendMA"])
        # decide what direction the trend is 
        i = 0
        trend = []
        for i in range(length):
            # if current point trend is greater than last point we are trending up, 1
            # else trending down, -1
            if df[stock, "trendMA"][i] > df[stock, 'trendMA'][i-1]:
                trend.append(1) # 1 meaning trading above average
            else:
               # print(f"on {df['trendMA']}")
                trend.append(-1)
        
        #check if last 5 values are all the same, if they are then the stock is considered
        #trending and added to list
        lastx_direction = trend[-5:]
        check = lastx_direction[0]
        crossoverDir = df[stock, 'crossover'][-1]
        isTrending = (True, 0)
        if check == 1:
            for item in lastx_direction: 
                if check != item or check != crossoverDir: 
                    isTrending = (False, 0)
                    break;
                else:
                    isTrending = (True, 1)
        else:
            for item in lastx_direction: 
                if check != item or check != crossoverDir: 
                    isTrending = (False, 0)
                    break;
                else:
                    isTrending = (True, -1)  
                
        df[stock, 'Direction'] = np.array(trend)
        #df = df.drop([stock, 'trendMA'], axis=1)
        
        
        if isTrending == (True, 1):
            trending_portfolio.append(df)
            print(f'Adding {stock} to finalPortV2 for a long pos')
        elif isTrending == (True, -1):
            trending_portfolio.append(df)
            print(f'Adding {stock} to finalPortV2 for a short pos')
        else:
            pass
        counter +=1
    return trending_portfolio
    
# finds if stock is trading above or below the 200 day ma
def findCTrend(DF, stock):
    df = DF.copy()
    df[stock, "trendMA"] = df[stock, "close"].ewm(span = 200, min_periods = 200).mean()
    df = df.dropna()
    length = len(df[stock, "trendMA"])
    # decide what direction the trend is 
    i = 0
    trend = []
    for i in range(length):
        if df[stock, "trendMA"][i] < df[stock, 'close'][i]:
            trend.append(1) # 1 meaning trading above average
        else:
           # print(f"on {df['trendMA']}")
            trend.append(-1)
    #check if last 5 values are all the same, if they are then the stock is considered
    #trending and added to list
    
    lastx_direction = trend[-5:]
    check = lastx_direction[0]
    isTrending = (True, 0)
    if check == 1:
        for item in lastx_direction: 
            if check != item: 
                isTrending = (False, 0)
                break;
            else:
                isTrending = (True, 1)
    else:
        for item in lastx_direction: 
            if check != item: 
                isTrending = (False, 0)
                break;
            else:
                isTrending = (True, -1)  
                
    df[stock, 'Direction'] = np.array(trend)
    #df = df.drop([stock, 'trendMA'], axis=1)
    
    
    if isTrending == (True, 1):
        trendDir = 1
    elif isTrending == (True, -1):
        trendDir = -1
    else:
        trendDir = 0
        
    # returns 1 if trending up
    # -1 if down
    # 0 if no trend
    return trendDir


# calculate moving average x to find the trend, x is usually 200
def getTrending(universe, portfolio, x):
    #universe = dataUni
    #portfolio = currentPortfolio
    #x = 200
    
    
    counter = 0
    trending_list = []
    print(f"Finding Trending Stocks\n{'-'*15}")
    while counter <= len(portfolio) - 1:
        loc = portfolio[counter][0]
        df = universe[loc].copy()
        stock = universe[loc].columns[1][0]
        
        df[stock, "trendMA"] = df[stock, "close"].ewm(span = x, min_periods = x).mean()
        #df["trendMA"] = df["Adj Close"].ewm(span = x, min_periods = x).mean()
        df = df.dropna()
        length = len(df[stock, "trendMA"])
        # decide what direction the trend is 
        i = 0
        trend = []
        for i in range(length):
            if df[stock, "trendMA"][i] < df[stock, 'close'][i]:
                trend.append(1) # 1 meaning trading above average
            else:
               # print(f"on {df['trendMA']}")
                trend.append(-1)
        
        #check if last 5 values are all the same, if they are then the stock is considered
        #trending and added to list
        lastx_direction = trend[-5:]
        check = lastx_direction[0]
        isTrending = True
        
        for item in lastx_direction: 
            if check != item: 
                isTrending = False
                break;
        df[stock, 'Direction'] = np.array(trend)
        #df = df.drop([stock, 'trendMA'], axis=1)
        
        
        if isTrending == True:
            trending_list.append([loc, portfolio[counter][1]])
            print(f"Adding {stock} to trending list..")
        
        counter += 1
    
    print(f'Success finding trending stocks, NO in list {len(trending_list)}')
    return trending_list


# calcating time and market hours
def getMarketHours():
    # get our current time
    nyc = pytz.timezone('America/New_York')
    
    currentTimeInIA = datetime.now()
    currentTimeInNY = datetime.now().astimezone(nyc)
    today = datetime.today().astimezone(nyc)
    today_str = datetime.today().astimezone(nyc).strftime('%Y-%m-%d')
    
    # get market open close from alpaca
    calendar = api.get_calendar(start=today_str, end=today_str)[0]
    
    # set market open and close by replacing with current info from calender
    market_open = today.replace(
        hour=calendar.open.hour,
        minute=calendar.open.minute,
        second=0
    )
    market_open = market_open.astimezone(nyc)
    
    market_close = today.replace(
        hour=calendar.close.hour,
        minute=calendar.close.minute,
        second=0
    )
    market_close = market_close.astimezone(nyc)
    
    print(f"Market hours are open {market_open.strftime('%I:%M %p')} - {market_close.strftime('%I:%M %p')} NY time")
    print(f"\t->It is currently {currentTimeInIA.strftime('%I:%M %p')} in Iowa" \
          f"\n\t\t->Iowa->NY: {currentTimeInNY.strftime('%I:%M %p')}")
   
    currentTimeInNY = datetime.today().astimezone(nyc)
    since_market_open = currentTimeInNY - market_open
    since_market_close = currentTimeInNY - market_close
    # datetime.timedelta(days=-1, seconds=75267, microseconds=786704)
    # if its been a day since market closed 
  
    print(f"It has been {((since_market_open.seconds / 60) / 60):.0f} hours and {(since_market_open.seconds / 60) % 60:.0f}" \
          f" minutes since the market opened\n\t->({((since_market_open.seconds / 60) / 60):.0f}:{(since_market_open.seconds / 60) % 60:.0f})")
    print(f"Time since market closed -> { currentTimeInNY - market_close }")
    
    # yesno is False if market is closed,True if market is open
    if since_market_close.seconds > 0:
        yesno = False
    else: 
        yesno = True
    
    return since_market_open, currentTimeInNY, yesno


# refined macd and crossover functions for alpaca data
def MACD(DF, stock, a, b, c):
    # df = universe[6]
    # stock = 'FB'
    # a = 12
    # b = 26
    # c = 9
    
    df = DF.copy() #create copy of yf dataframe
    
    df[stock, "MA_Fast"] = df[stock, "close"].ewm(span = a, min_periods = a).mean() # get a period ma (12 usually)
    df[stock, "MA_Slow"] = df[stock, "close"].ewm(span = b, min_periods = b).mean() # get b period ma (26 usually)
    df[stock, "MACD"] = df[stock, "MA_Fast"] - df[stock, "MA_Slow"] # calc MACD Line and store within dataframe
    df[stock, "Signal"] = df[stock, "MACD"].ewm(span = c, min_periods = c).mean() # find signal line using macd and value C (9 usually)
    
    # fix formatting to drop ma_fast and ma_slow data
    # remove multi index so we can drop rows, then re add it
    # drop nan values
    df.columns = df.columns.droplevel()
    df = df.drop( "MA_Fast", axis = 1)
    df = df.drop('MA_Slow', axis = 1)
    columns = [(stock,'open'),(stock,'high'), (stock, 'low'), (stock, 'close'), (stock, 'volume'), (stock, 'MACD'), (stock, 'Signal')]
    df.columns=pd.MultiIndex.from_tuples(columns)
    df.dropna(inplace = True) # get rid of nan values
    
    
    return df


# find when signal and macd crossover
# question to answer, when returning should we drop macd and signal?
def crossover(DF, stock): 
    df = DF.copy()
    
    length = len(df[stock,'MACD'])
    cross_list = []
    
    for i in range(length):
            if(df[stock,'MACD'].tolist()[i-1] < df[stock,'Signal'].tolist()[i-1] and df[stock,'MACD'].tolist()[i] > df[stock,'Signal'].tolist()[i]):
                cross_list.append(1) # time to buy for long
            elif(df[stock, 'MACD'].tolist()[i-1] > df[stock, 'Signal'].tolist()[i-1] and df[stock, 'MACD'].tolist()[i] < df[stock, 'Signal'].tolist()[i]):
                cross_list.append(-1) # time to sell for short
            else:
                cross_list.append(0) # no crossovers
    df[stock,'crossover'] = np.array(cross_list)
 
   
    # fix formatting to drop ma_fast and ma_slow data
    # remove multi index so we can drop rows, then re add it
    # drop nan values
    df.columns = df.columns.droplevel()
    df = df.drop( "MACD", axis = 1)
    df = df.drop('Signal', axis = 1)
    columns = [(stock,'open'),(stock,'high'), (stock, 'low'), (stock, 'close'), (stock, 'volume'), (stock, 'crossover')]
    df.columns=pd.MultiIndex.from_tuples(columns)
   
    return df


# calculating macd and signal line for each stock,
# then finding their crossovers for each stock
# returns portfolio of [corresponding index in universe, stock names]
def uni_MACD_CROSSOVER(universe, checkBack):
    counter = 0
    while counter <= len(universe) -1:
        # set a temp DF to pass to macd <- could also just send dataUni[counter]
        DF = universe[counter].copy()
        stock = universe[counter].columns[1][0]
        
        print(f'Macd called for {universe[counter].columns[1][0]}')
        universe[counter] = MACD(DF, stock, 12, 26, 9)
        print(f'MACD RECIEVED FOR {universe[counter].columns[1][0]}')
        
        print(f'Crossover called for {universe[counter].columns[1][0]}')
        universe[counter] = crossover(universe[counter], stock)
        print(f'Crossover recieved for {universe[counter].columns[1][0]}')
        counter += 1
    
    # finding all stocks that had a crossover in the latest datapoint
    counter = 0
    latestCross = []
    print(f"{'-'*20}\nLatest Crossovers\n{'-'*20}")
    while counter <= len(universe) - 1:
        stock = universe[counter].columns[1][0]
        
        # puts last 15 values of crossover in a list, then reverses it so newest values are closer to 0index
        lastCheckBackVal = universe[counter].iloc[checkBack:, 5].to_numpy().tolist()
        lastCheckBackVal.reverse()
        
        
        # iterates through list to see if there were any crossovers
        # if there were we add it to latestCross list, 
        i = 0
        for i in range(len(lastCheckBackVal)):
            if(lastCheckBackVal[i] == -1):
                print(f'{universe[counter].columns[1][0]}')
                # append [location in index for corresponding dataframe, stock name]
                latestCross.append([counter, universe[counter].columns[1][0]])
                break
            elif(lastCheckBackVal[i] == 1):
                print(f'{universe[counter].columns[1][0]}')
                # append [location in index for corresponding dataframe, stock name]
                latestCross.append([counter, universe[counter].columns[1][0]])
                break
            else:
                pass
                # print('wtf')
        
        counter += 1
        
        # stocks that have crossedover within lastcheckback are added to our portfolio for now
        portfolio = []
        for cross in range(len(latestCross)):
            portfolio.append(latestCross[cross])
        
    # print(portfolio)
           
    #return universe
    return portfolio
# --------------------
# orders
# ---------

def get_orders():
   portfolio = api.list_positions()
   api.list_orders()
   return portfolio

def place_order(df, position):
    
    if len(get_orders()) >= MAX_ORDERS:
            print('Max orders\nReturning..')
            return
        
    stock = df.columns[0][0]
    print(f'\n-Submiting order for {stock}-')
    
    stopLoss = position[1]
    takeProfit = position[2]
    if df.iloc[-1][5] == 1:
        side = 'buy'
        limit_price = round(stopLoss * .99, 2)
    else:
        side = 'sell'
        limit_price = round(stopLoss * 1.01, 2)
        
    print(f'Side: {side}\nStop loss: {stopLoss}\nTake Profit: {takeProfit}\nLimit Price: {limit_price}')
    
    
    api.submit_order(
        symbol=stock,
        qty=position[0],
        side= side,
        type= 'market',
        time_in_force='gtc',
        order_class='bracket',
        stop_loss={'stop_price': stopLoss,
                   'limit_price': limit_price},
        take_profit={'limit_price': takeProfit}
    )
    time.sleep(2)
    info = api.get_position(stock)
    avg_entry = info.avg_entry_price
    current_order = [stock, side, stopLoss, avg_entry, takeProfit]
   
    
    time_ordered = datetime.now()
    order = [stock, side, stopLoss, avg_entry, takeProfit]
    print(f'\n-Order submitted at: {time_ordered}-\n')
    return order
    

def place_orders(finalPort, positions):
    counter = 0
    orders_list = []
    while counter < len(positions):
        # if we have more than 5 orders this loop terminates and we return to main
        if len(get_orders()) > MAX_ORDERS:
            print('Max orders\nReturning..')
            return
        
        
        stock = finalPort[counter].columns[0][0]
        print(f'\n-Submiting order for {stock}-')
        
        stopLoss = positions[counter][1]
        takeProfit = positions[counter][2]
        if finalPort[counter].iloc[-1][5] == 1:
            side = 'buy'
            limit_price = round(stopLoss * .99, 2)
        else:
            side = 'sell'
            limit_price = round(stopLoss * 1.01, 2)
            
        print(f'Side: {side}\nStop loss: {stopLoss}\nTake Profit: {takeProfit}\nLimit Price: {limit_price}')
        
        
        api.submit_order(
            symbol=stock,
            qty=positions[counter][0],
            side= side,
            type= 'market',
            time_in_force='gtc',
            order_class='bracket',
            stop_loss={'stop_price': stopLoss,
                       'limit_price': limit_price},
            take_profit={'limit_price': takeProfit}
        )
        time.sleep(2)
        info = api.get_position(stock)
        avg_entry = info.avg_entry_price
        current_order = [stock, side, stopLoss, avg_entry, takeProfit]
        orders_list.append(current_order)
        
        time_ordered = datetime.now()
        print(f'\n-Order submitted at: {time_ordered}-\n')
        
        counter+=1
    return orders_list

def print_orders(orders):
    info = api.list_positions()
    counter = 0
    while counter < len(info):
        avg_entry = info.avg_entry_price
        
        
        counter += 1
# ----------------------------------------------
# main function
# ----------------------------------------------
def main():
    res = getMarketHours()
    mostRecent = 0
    posCount = 0
    orders = 0
    
    
    # if were within market hours
    while res[2] == False:
        
        #   check to see if we have most recent data is the same as the last run through
        #   if true, pass, if false try to find new positions
        # gets the most recent bar and uploads it to sql
        populate_db('15Min', 1)
        
        # grabs last 500 points from db
        dataUni = getSqlData('15Min') # defaults to last 500 data points in data base
        
        # if we have already looked at the most recent data point we pass and try 
        # again to get the new point
        # or if we are already in 5 plus positions we pass as well
        res = getMarketHours()
        if dataUni[0].index[-1] == mostRecent:
            print(f'\nNo new data to work with most recent still {mostRecent}\nSleeping until next minute\n')
            time.sleep(50)
            pass
        # have more than 5 orders
        elif len(get_orders()) >= MAX_ORDERS:
            print(f'\n-{dataUni[0].index[-1]} - Max order count of {MAX_ORDERS} has been reached-\n')

            time.sleep(50)
            pass
        #check for current positions
        
        else:
            # get our current pos from alpaca
            current_positions = get_orders()
            
           
            # creates portfolio
            # finds latest crossovers, finds trending crossovers
            # adds psar, will proabably be taken out
            # finds positions for trending crossovers
            currentPortfolio = uni_MACD_CROSSOVER(dataUni, -1) # -5 is how many points we check backwards
            trending_in_portfolio = getTrending(dataUni, currentPortfolio, 200)
            finalPort = addSAR(dataUni, trending_in_portfolio)
            finalPortV2 = directionTrend(finalPort)
            positions = quickPOS(finalPortV2)
            if len(positions) > 0:
                #ticker = 0
                for ticker in range(len(positions)):
                    stock = finalPortV2[ticker].columns[0][0]
                    df = finalPortV2[ticker]
                    position = positions[ticker]
                    #checks to see if we already have position for this stock
                    try:
                        api.get_position(stock)
                        print(f'Already have position for {stock}')
                    except Exception:
                        print(f'No current position for {stock}\nCalling api..\n')
                        place_order(df, position)
                #
                #orders = place_orders(finalPort, positions)
            else:
                print(f'\n-{dataUni[0].index[-1]}-!No new positions found!\n')
            mostRecent = dataUni[0].index[-1]
            res = getMarketHours()
            # place trades
            posCount +=1
            print(f'\nCalculated pos for {mostRecent} Sleeping for 60 Seconds\n')
            time.sleep(60)
                        
    # market is closed
    print('\nMarket is closed')

        
        
    #getAccount() <- get current positions, equity blah blah

#Calls main to begin bot run
main()
