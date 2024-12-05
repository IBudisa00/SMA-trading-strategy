
from backtesting import Backtest, Strategy
from backtesting.lib import crossover
from backtesting.test import SMA
from main import lmt_data

class myStrategy(Strategy):
    def init(self):
        price = self.data.Close
        self.ma1 = self.I(SMA, price, 50)
        self.ma2 = self.I(SMA, price, 200)

    def next(self):
        if crossover(self.ma1, self.ma2):
            self.buy()
        elif crossover(self.ma2, self.ma1):
            self.sell()

backtest = Backtest(lmt_data, myStrategy,cash = 10000, commission = .002, exclusive_orders = True)
stats =  backtest.run()

print(stats)