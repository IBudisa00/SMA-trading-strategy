import yfinance as yf
import pandas as pd
import numpy as np
import math as mt
import matplotlib.pyplot as plt
from backtesting import Backtest, Strategy
from backtesting.lib import crossover
from backtesting.test import SMA


#lmt - lockheed martin
#noc - northrop grumman
#gd - general dynamics
#rtx - rtx corporation

lmt = yf.Ticker("LMT")
lmt_data = lmt.history(start = "2021-10-30", end = "2024-10-30")
lmt_data["50days"] = lmt_data["Close"].rolling(window=50).mean()
lmt_data["200days"] = lmt_data["Close"].rolling(window=200).mean()

#adding signals
lmt_data["Signal"] = 0
signalColumn = lmt_data.columns.get_loc("Signal")
days50Column = lmt_data.columns.get_loc("50days")
days200Column = lmt_data.columns.get_loc("200days")
for row in range(49,len(lmt_data)):
    if lmt_data.iloc[row,days50Column] > lmt_data.iloc[row,days200Column]:
        lmt_data.iloc[row,signalColumn] = 1
    else:
        lmt_data.iloc[row,signalColumn] = 0
lmt_data["Difference"] = lmt_data["Signal"].diff()

startInvestment = 10000.0
lmt_data["Equity"] = startInvestment
equityColumn = lmt_data.columns.get_loc("Equity")
lmt_data["Quantity"] = 0
quantityColumn = lmt_data.columns.get_loc("Quantity")
openColumn = lmt_data.columns.get_loc("Open")
quantity = mt.floor(lmt_data.iloc[0,equityColumn]/lmt_data.iloc[0,openColumn])
remainder = startInvestment - quantity * lmt_data.iloc[0,openColumn]
lmt_data["Quantity"] = quantity
#lmt_data.iloc[0,EquityColumn] = 10000

for row in range(1,len(lmt_data)):
    lmt_data.iloc[row, equityColumn] = quantity * lmt_data.iloc[row, openColumn] + remainder 

#calculating equity curve, drawdown and sharpe ratio

dailyReturns = lmt_data["Close"].pct_change()
cumulativeReturns = (1 + dailyReturns).cumprod()
cumulativeMax = cumulativeReturns.cummax()
drawdown = (cumulativeReturns - cumulativeMax)/cumulativeMax

plt.figure(figsize=(14,10))
drawdown.plot(label="Drawdown")
plt.title("Drawdown of Lockheed Martin")
plt.xlabel("Date")
plt.ylabel("Drawdown (%)")
plt.legend()


riskFreeRateLMT = 0.04268
lmt_returns = np.log(lmt_data["Close"]).diff()
lmt_returns = lmt_returns.dropna()
lmt_meanReturns = np.mean(lmt_returns) * 252
lmt_volatility = np.std(lmt_returns) * np.sqrt(252)
sharpeRatio = (lmt_meanReturns - riskFreeRateLMT)/lmt_volatility
print("Sharpe ratio: ", sharpeRatio)

equityToday = remainder + lmt_data.iloc[len(lmt_data)-1,equityColumn]
print("Equity today = ", equityToday)
#visualising signals
plt.figure(figsize=(14,10))
plt.plot(lmt_data["Close"], label = "Lockheed Martin Closing Prices")
plt.plot(lmt_data["50days"], label = "50 days SMA", color="#892596")
plt.plot(lmt_data["200days"], label = "200 days SMA", color="#DB6531")
plt.plot(lmt_data[lmt_data["Difference"] == 1].index, lmt_data["50days"][lmt_data["Difference"] == 1], '^',markersize=10, color='g', label="Buy signal")
plt.plot(lmt_data[lmt_data['Difference'] == -1].index, lmt_data["50days"][lmt_data["Difference"] == -1], 'v', markersize=10, color='r', label="Sell signal")
plt.title("SMA crossover strategy for Lockheed Martin")
plt.xlabel("Date")
plt.ylabel("Price")
plt.legend()

#equity graph
plt.figure(figsize=(12,8))
plt.plot(lmt_data.index, lmt_data["Equity"], color='g')
plt.title("Equity change in time")

plt.show()

