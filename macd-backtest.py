# -*- coding: utf-8 -*-
"""
Created on Wed Dec 16 18:56:04 2020

@author: sjdef
"""
# imports for time
#import datetime as dt
#from datetime import datetime
import pytz

# imports for data
#import yfinance as yf # pricing data
#import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import sqlite3
# imports for trade
#import alpaca_trade_api as tradeapi
#import backtrader as bt

# ===========================
# Gathering data for backtest
# ===========================
connection = sqlite3.connect('C:/Users/sjdef/Desktop/CODE/VADER/sql/data.db') 
cursor = connection.cursor()
def getSqlData(timeFrame, Range=500):
    counter = 0
    # all 103 stocks below
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

# ============================
# Functions used during backtest()
# ============================

def directionTrend(DF):
    # universe = finalPort
    
    
    df = DF.copy()
    stock = df.columns[1][0]
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
        direction = 1
    elif isTrending == (True, -1):
        direction = -1
    else:
        direction = 0
    
    
    return direction

# find if last 5 our trending in our direction
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

# find results by win percentage from backtest and return dictionary
def whatsGood(results):
    backtest_results = results
    i = 0
    
    dominant_list = []
    sevenfive_list = []
    winners = []
    losers = []
    for i in range(len(backtest_results)):
        if backtest_results[i][3] == 100.0:
           add = backtest_results[i]
           dominant_list.append(add)
        elif backtest_results[i][3] > 75.0:
            add = backtest_results[i]
            sevenfive_list.append(add)
        elif backtest_results[i][3] > 50.0:
            add = backtest_results[i]
            winners.append(add)
        else:
            add = backtest_results[i]
            losers.append(add)
    results = [
       dominant_list,
       sevenfive_list,
       winners,
       losers
    ]
          
    return results
    


# ==============================
# Indicators used by backtest()
# ==============================
# ==================================================================================================
##def addSAR(universe, portfolio):
def addSAR(universe):
    
    
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
    
    finished_portfolio = []
    ##while counter <= len(portfolio) -1:
    while counter <= len(universe) - 1:    
        df  = universe[counter].copy()
        stock = universe[counter].columns[1][0]
        print(f'Calling {stock} psar values calculator....')
        df = calcSAR(df, stock)
        finished_portfolio.append(df)
        print(f'Recieved {stock} psar values')
        counter += 1
        
    return finished_portfolio

# find 2 percent of account size
# find how many shares we can buy with that
def positionSize(currentPrice, accountSize):
    # accountSize = 100000
    # currentPrice = 242.43
    money_to_risk = accountSize * .02
    shares = round(money_to_risk / currentPrice, 0)
    return shares

# used to get maxstop,target1r in backtesting
def quickPOS(lastClose, side):
    AvgGain = 1
    AvgLoss = .5
    if side == 'l':
        close = round(lastClose, 2)
        maxStop = round(close * ((100 - AvgLoss) / 100), 2)
        Target1R = round(close * ((100 + AvgGain) / 100), 2)
        # Target2R = round(close * ((100 + (2 * AvgGain)) / 100), 2)
        # Target3R = round(close * ((100 + (3 * AvgGain)) / 100), 2)
        # pos_rec = [maxStop, Target1R, Target2R, Target3R]
        pos_rec = [maxStop, Target1R]
        
        return pos_rec
    else:
        close = round(lastClose, 2)
        maxStop = round(close * ((100 + AvgLoss) / 100), 2)
        Target1R = round(close * ((100 - AvgGain) / 100), 2)
        # Target2R = round(close * ((100 - (2 * AvgGain)) / 100), 2)
        # Target3R = round(close * ((100 - (3 * AvgGain)) / 100), 2)
        # pos_rec = [maxStop, Target1R, Target2R, Target3R]
        pos_rec = [maxStop, Target1R]
        return pos_rec
    
    
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
        universe[counter] = MACD(DF, stock, 12, 26, 9) #12,26,9
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
           
    return universe
# ==============================================================================================

# =================================================
# Backtesting 
# =====================
# dataUni = getSqlData('15Min', 1070)
# dataUni = uni_MACD_CROSSOVER(dataUni, -1) # -5 is how many points we check backwards
# finalPort = addSAR(dataUni)

# ============================================================================================
def log(txt, option):
        if option  == 1:
           txtfile = open("C:/Users/sjdef/Desktop/CODE/VADER/logs/entries-exits.txt","a+")
           txtfile.write(txt)
           txtfile.close()
        elif option == 2:
           txtfile = open("C:/Users/sjdef/Desktop/CODE/VADER/logs/backtest-winpct.txt","w") 
           txtfile.write(txt)
           txtfile.close()
        elif option == 3:
           txtfile = open("C:/Users/sjdef/Desktop/CODE/VADER/logs/backtest-overview.txt","a+") 
           txtfile.write(txt)
           txtfile.close()
        elif option == 4:
           txtfile = open("C:/Users/sjdef/Desktop/CODE/VADER/logs/backtest-decisions.txt","a+") 
           txtfile.write(txt)
           txtfile.close()
        else:
           txtfile = open("C:/Users/sjdef/Desktop/CODE/VADER/logs/logErrors.txt","a+") 
           txtfile.write(txt)
           txtfile.close()
           
        txtfile.close()

#print filtered results
def summaryBT(results):
    #results = backtest_results
    txtfilefinal = open("C:/Users/sjdef/Desktop/CODE/VADER/logs/winners-losers.txt","w")
    # print dominant stocks / 100% winrate
    d=0
   
    print(f"Stocks with 100% win rate\n{'-'*15}\n")
    txtfilefinal.write(f"{'-'*15}\nStocks with 100% win rate\n{'-'*15}\n")  
    for d in range(len(results[0])):
        print(f"|{results[0][d][0]}| trades taken - {results[0][d][1]} | Profit made: ${results[0][d][4]}\n")
        txtfilefinal.write(f"|{results[0][d][0]}| trades taken - {results[0][d][1]} | Profit made: ${results[0][d][4]}\n")
    txtfilefinal.write(f"\n{'-'*30}\n")
    
    o = 0
    print(f"Stocks with 75%+ win rate\n{'-'*15}\n")
    txtfilefinal.write(f"Stocks with 75%+ win rate\n{'-'*15}\n")
    for o in range(len(results[1])):
        print(f"|{results[1][o][0]}| trades taken - {results[1][o][1]} | Win %: {results[1][o][3]} | Profit made: ${results[1][o][4]}\n")
        txtfilefinal.write(f"|{results[1][o][0]}| trades taken - {results[1][o][1]} | Win %: {results[1][o][3]} | Profit made: ${results[1][o][4]}\n")
    txtfilefinal.write(f"\n{'-'*30}\n")
    
    print(f"Stocks with 50-75% win rate\n{'-'*15}\n") 
    txtfilefinal.write(f"Stocks with 50-75% win rate\n{'-'*15}\n")
    for f in range(len(results[2])):
        print(f"|{results[2][f][0]}| trades taken - {results[2][f][1]} | Win %: {results[2][f][3]} | Profit made: ${results[2][f][4]}\n")
        txtfilefinal.write(f"|{results[2][f][0]}| trades taken - {results[2][f][1]} | Win %: {results[2][f][3]} | Profit made: ${results[2][f][4]}\n")
    txtfilefinal.write(f"\n{'-'*30}\n")
    
    print(f"Stocks with less than 50% win rate\n{'-'*15}\n") 
    txtfilefinal.write(f"Stocks with less than 50% win rate\n{'-'*15}\n")
    for l in range(len(results[3])):
        print(f"|{results[3][l][0]}| trades taken - {results[3][l][1]} | Win %: {results[3][l][3]} | Profit made: ${results[3][l][4]}\n")
        txtfilefinal.write(f"|{results[3][l][0]}| trades taken - {results[3][l][1]} | Win %: {results[3][l][3]} | Profit made: ${results[3][l][4]}\n")
    txtfilefinal.write(f"\n{'-'*30}\n")
    
    txtfilefinal.close()
        
def backtest(universe):
    txtfile = open("C:/Users/sjdef/Desktop/CODE/VADER/logs/entries-exits.txt","w")
    txtfile = open("C:/Users/sjdef/Desktop/CODE/VADER/logs/backtest-overview.txt","w") 
    txtfile = open("C:/Users/sjdef/Desktop/CODE/VADER/logs/logErrors.txt","w")
    txtfile = open("C:/Users/sjdef/Desktop/CODE/VADER/logs/backtest-decisions.txt","w")
     

     
    def getDecisions(universe):
        # universe = finalPort
        
        # open backtest.txt to write full results in
        # results = open("C:/Users/sjdef/Desktop/CODE/VADER/src/backtest.txt","w") 
        
        print('Starting to find stocks\n-------------------')
        
        # loop through universe to find all times we wouldve went long or short
        counter = 0
        while counter < len(universe):
            stock = universe[counter].columns[1][0]
            print(f'({counter}/{len(universe)})Finding decisions for {stock}')
            log(f'Finding decisions for {stock}\n', 4)
            
            # get current stocks dataframe
            # reindex the time so we grab only 9:00 - 16:00
            df = universe[counter].copy()
            nyc = pytz.timezone('America/New_York')
            df.index = pd.to_datetime(df.index, utc=True)
            df.index = df.index.tz_convert(nyc)
            df = df.between_time('9:00', '16:00', include_start=True, include_end=True, axis=0)
            i = 0
            #i = 206
            decision_list = []
            
            while i < len(df):
                # first 205 rows we don't make any decisions because we don't have
                # 200 day ma , 5 days for trend calc
                if i < 205 :
                    above_below = 0
                    decision_list.append('none')
                    i+=1
                # we now have 200 ma
                # decide if we need to long or short at anytime
                else:
                    above_below = findCTrend(df[:i+1], stock)
                    trend_dir = directionTrend(df[:i+1])
                    # if our macd crossed above our signal line and our last 5 points of our
                    # 200 day ma have been all trending upwards
                    if df[stock,'crossover'][:i+1][-1] == 1 and  above_below == 1 and trend_dir == 1:
                        decision_list.append('long')
                        log(f'\t{df.index[i]} - Found long postition for {stock}\n', 4)
                        print(f'\t{df.index[i]} - Found long postition for {stock}')
                    
                    # if our macd crossed below signal and last 5 points of trend are
                    # all trending downwords
                    elif df[stock, 'crossover'][:i+1][-1] == -1 and above_below == -1 and trend_dir == -1:
                        decision_list.append('short')
                        log(f'\t{df.index[i]} - Found short postition for {stock}\n', 4)
                        print(f'\t{df.index[i]} - Found short postition for {stock}')
                    else:
                        decision_list.append('none')
                    
                    i += 1
                    
            df[stock, 'decision'] = np.array(decision_list)
            universe[counter] = df.copy()
            print(f'({counter}/{len(universe)})Success Finding decisions for {stock}')
            log(f'Success Finding decisions for {stock}\n\n', 4)
            counter += 1
            
        print('-----------------------------\nHowbadisitlol') 
        # results.close()
        
        return universe
    
    def getPositionsBT(universe):
        counter = 0
        all_results = []
       
        inPosition = False
        while counter < len(universe):
            # universe = finalPort
            stock = universe[counter].columns[1][0]
            df = universe[counter].copy()
        
        
            
        
            nyc = pytz.timezone('America/New_York')
            df.index = pd.to_datetime(df.index, utc=True)
            df.index = df.index.tz_convert(nyc)
            df = df.between_time('9:00', '16:00', include_start=True, include_end=True, axis=0)
            
            
            positions = []
            lost = 0
            won = 0
            exited = []
            i = 0
            inPosition = False
            accountSize = 1000000
            log(f'Entering positions for {stock}\n----------------\n', 1)
            while i < len(df):
                # waiting for 200 day MA
                if i < 200:
                    i +=1
                # 200 day MA kicked in
                # now to see if we are in a pos or not
                else:
                    # no open position for this stock
                    if inPosition != True:
                        # long is in most recent row in decision
                        if df[(stock, 'decision')][i] == 'long':
                            shares = positionSize(df[(stock, 'close')][:i+1][-1], accountSize)
                            pos = ['L', df[(stock, 'close')][:i+1][-1], quickPOS(df[(stock, 'close')][:i+1][-1], 'l'), shares]
                            positions.append(pos)
                            inPosition = True
                            print(f"({len(positions)}) Long position entered at {df[(stock, 'close')][:i+1][-1]} for {shares} shares")
                            log(f" ({len(positions)}) {df.index[i]}-Long position entered at {df[(stock, 'close')][:i+1][-1]} for {shares} shares\n", 1)
                            
                        # short is in most recent row in decision
# =============================================================================
#                         elif df[(stock,'decision')][i] == 'short':
#                             shares = positionSize(df[(stock, 'close')][:i+1][-1], accountSize)
#                             pos = ['S', df[(stock, 'close')][:i+1][-1], quickPOS(df[(stock, 'close')][:i+1][-1], 's'), shares ]
#                             positions.append(pos)
#                             inPosition = True
#                             print(f"({len(positions)}) Short position entered at {df[(stock, 'close')][:i+1][-1]} for {shares} shares")
#                             log(f" ({len(positions)}) {df.index[i]}-Short position entered at {df[(stock, 'close')][:i+1][-1]} for {shares} shares\n", 1)
#                 
# =============================================================================
                        else:
                            inPosition = False
                        
                        i+=1
                    # we are in a trade on this stock
                    else:
                        #long position
                        if positions[-1][0] == 'L':
                            
# =============================================================================
#                             if df[stock,'crossover'][:i][-1] == -1:
#                                 add = [positions[-1][1], df[(stock, 'close')][:i][-1] ]
#                                 exited.append(add)
#                                 print(f"\t->Long Entry price ({positions[-1][1]}) crossed over in opposite dir\n\t->exited at {df[(stock, 'close')][:i][-1]}\n")
# 
#                                 inPosition = False
#                                 if df[(stock, 'close')][:i][-1] > positions[-1][1]:
#                                     won+=1
#                                 else:
#                                     lost +=1
# =============================================================================
                            # most recent close is below our most recent position stop loss
                            if df[(stock, 'close')][:i+1][-1] <= positions[-1][2][0]:
                                #adds to [exit_pos entry price, exit price]
                                add = [positions[-1][1], df[(stock, 'close')][:i+1][-1] ]
                                exited.append(add)
                                lost +=1
                                print(f'\t {df.index[i]} - Stopped out (W:{won}/L:{lost})\n')
                                log(f'\t{df.index[i]} - Stopped out\n\t->(W:{won}/L:{lost})\n', 1)
                                #position is over time to look for new trades
                                inPosition = False
                            
                            # if price is above profit target 1 
                            elif df[(stock, 'close')][:i+1][-1] >= positions[-1][2][1]:
                                # stop loss becomes 90 % of profit target 1
                                # positions[-1][2][0] = round(positions[-1][2][1] * .99, 2)
                                won +=1 
                                print(f"\t->Long Entry price ({positions[-1][1]}) reached profit target 1 = {positions[-1][2][1]} and exited at {df[(stock, 'close')][:i+1][-1]} (W:{won}/L:{lost})\n")
                                log(f"\t->{df.index[i]} - Long Entry price ({positions[-1][1]}) reached profit target 1 = {positions[-1][2][1]} and exited at {df[(stock, 'close')][:i+1][-1]}\n\t->(W:{won}/L:{lost})\n", 1)
                                add = [positions[-1][1], df[(stock, 'close')][:i+1][-1] ]
                                exited.append(add)
                                inPosition = False
                                
                            i+=1
                        #short position
# =============================================================================
#                         else:
#                             # MACD is now signaling the opposite
# # =============================================================================
# #                             if df[stock,'crossover'][:i][-1] == 1:
# #                                 add = [positions[-1][1], df[(stock, 'close')][:i][-1] ]
# #                                 exited.append(add)
# #                                 print(f"\t->Short Entry price ({positions[-1][1]}) crossed over in opposite dir\n\t->exited at {df[(stock, 'close')][:i][-1]}\n")
# #                                 if df[(stock, 'close')][:i][-1] < positions[-1][1]:
# #                                     won+=1
# #                                 else:
# #                                     lost +=1
# #                                     
# #                                 inPosition = False
# # =============================================================================
#                             # most recent close is below our most recent position stop loss
#                             if df[(stock, 'close')][:i+1][-1] >= positions[-1][2][0]:
#                                 #adds to [exit_pos entry price, exit price]
#                                 add = [positions[-1][1], df[(stock, 'close')][:i+1][-1] ]
#                                 exited.append(add)
#                                 inPosition = False
#                                 lost +=1
#                                 print(f'\t{df.index[i]} - Stopped out (W:{won}/L:{lost})\n')
#                                 log(f'\t{df.index[i]} - Stopped out\n\t->(W:{won}/L:{lost})\n', 1)
# 
#                             # check to see if above 1st target
#                             elif df[(stock, 'close')][:i+1][-1] <= positions[-1][2][1]:
#                                 # stop loss becomes 90 % of profit target 1
#                                 # positions[-1][2][0] = round(positions[-1][2][1] * .99, 2)
#                                 won +=1 
#                                 print(f"\t->{df.index[i]} - Short Entry price ({positions[-1][1]}) reached profit target 1 = {positions[-1][2][1]} and exited at {df[(stock, 'close')][:i+1][-1]}(W:{won}/L:{lost})\n")
#                                 log(f"\t->{df.index[i]} - Short Entry price ({positions[-1][1]}) reached profit target 1 = {positions[-1][2][1]} and exited at {df[(stock, 'close')][:i+1][-1]}\n\t->(W:{won}/L:{lost})\n",1)
#                                 add = [positions[-1][1], df[(stock, 'close')][:i+1][-1] ]
#                                 exited.append(add)
#                                 inPosition = False
# =============================================================================
                                
                            
                            i+=1
            if inPosition == True:
                if positions[-1][1] < df[stock, 'close'][-1]:
                    add = [positions[-1][1], df[(stock, 'close')][-1] ]
                    exited.append(add)
                    won +=1
                    log(f"\t-> Ran out of data exited at {df[stock, 'close'][-1]}\n\t->w/l({won}/{lost})", 1)

                else:
                    add = [positions[-1][1], df[(stock, 'close')][-1] ]
                    exited.append(add)
                    lost +=1
                    log(f"\t-> Ran out of data exited at {df[stock, 'close'][-1]}\n\t->w/l({won}/{lost})", 1)

            if len(positions) > 0:
                print(f'You took {won+lost}, won ->{won}, lost->{lost}, win percentage = %{round((won/(won+lost) *100), 2)}')              
                #positive for profit, negative for loss
                profit_loss = profit_or_loss(positions, exited)
                log(f'||{stock}||You took {won+lost} trades, won ->{won}, lost->{lost}, win percentage = %{round((won/(won+lost) *100), 2)}| P/L = ${round(profit_loss, 2)}\n\n', 3)

                # results = ticker, total trades, all positions, win percentage, p/L
                results = [stock, (won + lost), positions, round((won/(won+lost) *100), 2), round(profit_loss, 2)]
            else:
                results = [stock, (won + lost), positions, round((won/(won+lost) *100), 2), round(profit_loss,2)]

            all_results.append(results)
            counter += 1 
        
            
        
        return all_results
                
    # function of backtest
    # -----------------
    
    
    # run get decisions, then run positions
    # maybe have another function to calculate p/l of each trade 
    # print all to text document results
    
    
    
   
    universe = getDecisions(universe) 
    
    results = getPositionsBT(universe)
    txtfile.close()
    return results
    
# ==============================================================================================
# ================
# Running backtest
# ================

# get data we want
# find crossovers
# add psar and call it finalPort
dataUni = getSqlData('15Min', 1200)
dataUni = uni_MACD_CROSSOVER(dataUni, -1) # -5 is how many points we check backwards
finalPort = addSAR(dataUni)

# set our back test universe = to whatever we want out of final portfolio
backTestUni = finalPort


# =============================================================================
# finding stocks where most recent price is <50
# counter = 0
# temp = []
# while counter < len(backTestUni):
#     if backTestUni[counter].iloc[-1][3] < 50:
#         temp.append(backTestUni[counter])
#     counter +=1
# =============================================================================

# results [stock, # of trades, positions[], win percentage, p/l]
backtest_data = backtest(backTestUni)


# find win percentage of strategy overall
total = 0
for i in range(len(backtest_data)):
    # sum of all win/lose percentages
    total += backtest_data[i][3]

# average win rate for all backtests performed
averageWinRate = round(total/len(backtest_data), 2)
log(f'Win rate for {len(backtest_data)} different backtests is -> %{averageWinRate}', 2)
backtest_results = whatsGood(backtest_data)
summaryBT(backtest_results)

# ================
# Running backtest on only winners
# ================
# =============================================================================
# winners_data = []
# for i in range(len(backtest_results)):
#     
#     if i <= 2:
#         look_at = []
#         look_at = backtest_results[i]
#         #j=0
#         for j in range(len(look_at)):
#             ticker = look_at[j][0]
#             #z=0
#             for z in range(len(dataUni)):
#                 # if ticker in this dataframe equals ticker were looking for 
#                 # add it to our winners_data and break loop
#                 if dataUni[z].columns[0][0] == ticker:
#                     winners_data.append(dataUni[z])
#                     break
#                 else:
#                     pass
#                    
# winners_data = uni_MACD_CROSSOVER(winners_data, -1)
# winners_data = addSAR(winners_data)
# 
# winnersBT_results = backtest(winners_data)
# total = 0
# for i in range(len(winnersBT_results)):
#     # sum of all win/lose percentages
#     total += winnersBT_results[i][3]
# 
# # average win rate for all backtests performed
# averageWinRate = round(total/len(winnersBT_results), 2)
# log(f'Win rate for {len(winnersBT_results)} different backtests is -> %{averageWinRate}', 2)
# backtest_results = whatsGood(winnersBT_results)
# summaryBT(backtest_results)
# =============================================================================
