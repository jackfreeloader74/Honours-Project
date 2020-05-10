class Portfolio:

    assets = []
    cash = 0
    cash_str = ""
    exp_return = 0
    risk = 0
    BestRatio = True
    user_expected_return = 0
    algorithm = ""
    mar_value = 0
    total_dividend_earnings = 0

    dividend_fail = False


    def __init__(self, cash, algorithm, mar_value, user_expected_return):
        self.cash = cash
        self.algorithm = algorithm
        self.mar_value = mar_value
        self.user_expected_return = user_expected_return
        self.dividend_fail = False

    def getRatio(self):
        if self.risk == 0:
            return 0

        return round(float(self.exp_return)/float(self.risk),2)

    def getFutureCash(self):

        cash = self.cash
        profit = cash * self.exp_return
        future_cash = profit + cash
        future_cash = "{:,.2f}".format(future_cash)

        return future_cash


    def getExpectedReturnStr(self):
        return round(float(self.exp_return)*100,3)


    def getReturnAsPercentage(self):
        Return = round(float(self.exp_return)*100,3)

    def getPortfolioSize(self):

        size = len(self.assets)
        return size


    def getSharpeRatio(self):

        sharpe = self.exp_return / self.risk
        return sharpe
