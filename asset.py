class Asset:

    ticker = ""
    weight = ""
    sector = ""
    share_volume = ""
    stock_name = ""
    dividend_earning = 0


    def __init__(self, ticker, sector, portfolio):
        self.ticker = ticker
        self.sector = sector
        self.portfolio = portfolio
        self.dividend_earning = 0


    def getDividendEarnings(self):

        if dividend_earning == 0:
            return "This stock does not return dividends."

        return self.dividend_earning
