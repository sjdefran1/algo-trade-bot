import sqlite3
import pandas as pd
import alpaca_trade_api as tradeapi
connection = sqlite3.connect('C:/Users/sjdef/Desktop/CODE/VADER/sql/data.db') 

cursor = connection.cursor()


def getData(timeFrame, limit):
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
    
    return universe

# ---------------------------------------------
# populate dataBase
# timeFrame =  minute, 1m, 5m, 15m, day
# limit = number of bars 0-1000


timeFrame = '15Min'
limit = 100
dataUni = getData(timeFrame, limit)


counter = 0
while counter <= len(dataUni) - 1:
    df = dataUni[counter].copy()
    stock = dataUni[counter].columns[1][0]
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


# ---------------
# gather day data
# ---------------
# timeFrame = 'day'
# limit = 1000
# dataUni = getData(timeFrame, limit)
# #dataUni = universe

# counter = 0
# while counter <= len(dataUni) - 1:
#     df = dataUni[counter].copy()
#     stock = dataUni[counter].columns[1][0]
#     df.columns = ['open', 'high', 'low', 'close', 'volume']
#     print(f'Uploading data for {stock}...')
#     for row in range(len(df)):
#         try:
#             idx = df.index[row]
#             insert = df.loc[idx]
#             cursor.execute(f"INSERT OR IGNORE into {stock}_{timeFrame} VALUES ('{df.index[row]}', {df.loc[idx][0]}, {df.loc[idx][1]}, {df.loc[idx][2]}, {df.loc[idx][3]}, {df.loc[idx][4]})")

#         #pd.DataFrame.to_sql(df, name=f'{stock}', con=connection, if_exists='append')
#         except Exception as e:
#             print(f"{stock} already has {df.index[row]}")
#             print(e)
    
#     print(f'Success uploading data for {stock}')
#     counter +=1
# connection.commit()   

# connection.close()

