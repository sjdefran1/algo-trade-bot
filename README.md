# algo-trade-bot
Python and sql project that trades on Alpacas paper trading platform

DISCLAIMER

********
You should not engage in trading unless you fully understand the nature of the transactions you are entering into and the extent of your exposure to loss. If you do not fully understand these risks you must seek independent advice from your financial advisor. All trading strategies are used at your own risk.
********

*******
Do Not use this code to make your own investment decisions
*******


Files
******
MACD-Crossover -> script that accesses sql db, evaluates the data and creates positions based on that data

Macd-backtest -> Script that uses past data from sql db to determine how the macd strategy performs

populate-db -> gathers info from yfinance and populates sql db

create-db -> creates sql database with schema for yfinance info
