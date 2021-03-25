import sqlite3

connection = connection = sqlite3.connect('C:/Users/sjdef/Desktop/CODE/VADER/sql/data.db') 
cursor = connection.cursor()

tickers = ['AAL', 'AAPL', 'ADBE', 'ADI', 'ADP', 'ADSK', 'ALGN', 'ALXN', 'AMAT', 'AMGN', 'AMZN', 'ASML', 'ATVI', 'AVGO', 'BIDU', 'BIIB', 'BKNG', 'BMRN', 'CA', 'CDNS', 'CELG', 'CERN', 'CHKP', 'CHTR', 'CMCSA', 'COST', 'CSCO', 'CSX', 'CTAS', 'CTRP', 'CTSH', 'CTXS', 'DISH', 'DLTR', 'EA', 'EBAY', 'ESRX', 'EXPE', 'FAST', 'FB', 'FISV', 'FOX', 'FOXA', 'GILD', 'GOOG', 'GOOGL', 'HAS', 'HOLX', 'HSIC', 'IDXX', 'ILMN', 'INCY', 'INTC', 'INTU', 'ISRG', 'JBHT', 'JD', 'KHC', 'KLAC', 'LBTYA', 'LBTYK', 'LRCX', 'MAR', 'MCHP', 'MDLZ', 'MELI', 'MNST', 'MSFT', 'MU', 'MXIM', 'MYL', 'NFLX', 'NTES', 'NVDA', 'ORLY', 'PAYX', 'PCAR', 'PYPL', 'QCOM', 'QRTEA', 'REGN', 'ROST', 'SBUX', 'SHPG', 'SIRI', 'SNPS', 'STX', 'SWKS', 'SYMC', 'TMUS', 'TSLA', 'TTWO', 'TXN', 'ULTA', 'VOD', 'VRSK', 'VRTX', 'WBA', 'WDAY', 'WDC', 'WYNN', 'XLNX', 'XRAY']


timeFrame = '15Min'
counter = 0
while counter <= len(tickers) - 1:
    stock = tickers[counter]
    print(f'Creating table for {stock}')
    table = f"""CREATE TABLE {stock}_{timeFrame} (
                time TIMESTAMP UNIQUE,
                open INTEGER,
                high INTEGER,
                low	INTEGER,
                close INTEGER,
                volume INTEGER
                                )"""
    cursor.execute(table)
    print(f'Success creating table for {stock}')

    counter +=1

# ================
# create day table
# ================

# timeFrame = 'day'
# counter = 0
# while counter <= len(tickers) - 1:
#     stock = tickers[counter]
#     print(f'Creating table for {stock}')
#     table = f"""CREATE TABLE {stock}_{timeFrame} (
#                 time TIMESTAMP UNIQUE,
#                 open INTEGER,
#                 high INTEGER,
#                 low	INTEGER,
#                 close INTEGER,
#                 volume INTEGER
#                                 )"""
#     cursor.execute(table)
#     print(f'Success creating table for {stock}')

#     counter +=1