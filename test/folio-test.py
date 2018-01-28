
import unittest

from folio import Stock, Portfolio

class StockTest(unittest.TestCase):
    def test_stock_to_slack_message(self):
        stock=Stock("meigara", "10", "kingaku", "+zenzitsuhi")
        self.assertEqual(stock.to_slack_msg(), "meigara: kingaku+zenzitsuhi")


class PotfolioTest(unittest.TestCase):
    stocks = [
        Stock("ＳＵＢＡＲＵ", "6株", "22,086円", "+0.00%"),
        Stock("日本セラミック","6株", "18,480円", "+0.82%"),
        Stock("デンソー", "2株", "14,076円", "-0.31%"),
        Stock("テクノスジャパン", "12株", "11,364円", "+0.53%"),
        Stock("トヨタ自動車", "1株", "7,608円", "+0.18%"),
        Stock("日産自動車", "5株", "5,910円", "+1.11%"),
        Stock("ゼンリン", "1株", "4,180円", "-1.18%"),
        Stock("ベリサーブ", "1株", "3,800円", "-2.56%"),
        Stock("クラリオン", "9株", "3,591円", "-1.48%"),
        Stock("ディー・エヌ・エー", "1株", "2,426円", "-0.12%"),
    ]

    def test_portfolio_should_get_max_stock(self):
        portfolio = Portfolio("バランス型", PotfolioTest.stocks)
        self.assertEqual(portfolio.max_stock().meigara, "日産自動車")

    def test_portfolio_should_get_min_stock(self):
        portfolio = Portfolio("バランス型", PotfolioTest.stocks)
        self.assertEqual(portfolio.min_stock().meigara, "ベリサーブ")

