
import datetime
import unittest

from util import Stock, Portfolio, is_weekday

class StockTest(unittest.TestCase):
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

    def test_stock_to_slack_message(self):
        stock=Stock("meigara", "10", "kingaku", "+zenzitsuhi")
        self.assertEqual(stock.to_slack_msg(), "<http://google.co.jp/search?q=meigara ニュース|meigara>: kingaku (+zenzitsuhi)")

    def test_stock_big_n(self):
        big_3 = Stock.big_n(StockTest.stocks, 3)
        self.assertEqual(big_3[0].meigara, "日産自動車")
        self.assertEqual(big_3[1].meigara, "日本セラミック")
        self.assertEqual(big_3[2].meigara, "テクノスジャパン")

    def test_stock_small_n(self):
        small_3 = Stock.small_n(StockTest.stocks, 3)
        self.assertEqual(small_3[0].meigara, "ベリサーブ")
        self.assertEqual(small_3[1].meigara, "クラリオン")
        self.assertEqual(small_3[2].meigara, "ゼンリン")

class PotfolioTest(unittest.TestCase):

    def test_portfolio_should_get_max_stock(self):
        portfolio = Portfolio("バランス型", StockTest.stocks)
        self.assertEqual(portfolio.max_stock().meigara, "日産自動車")

    def test_portfolio_should_get_min_stock(self):
        portfolio = Portfolio("バランス型", StockTest.stocks)
        self.assertEqual(portfolio.min_stock().meigara, "ベリサーブ")

class WeekDayTest(unittest.TestCase):

    def test_is_weekday_works(self):
        monday = datetime.datetime(2018, 7, 9)
        tuesday = datetime.datetime(2018, 7, 10)
        wednesday = datetime.datetime(2018, 7, 11)
        thursday = datetime.datetime(2018, 7, 12)
        friday = datetime.datetime(2018, 7, 13)
        saturday = datetime.datetime(2018, 7, 14)
        sunday = datetime.datetime(2018, 7, 15)
        self.assertTrue(is_weekday(monday))
        self.assertTrue(is_weekday(tuesday))
        self.assertTrue(is_weekday(wednesday))
        self.assertTrue(is_weekday(thursday))
        self.assertTrue(is_weekday(friday))
        self.assertFalse(is_weekday(saturday))
        self.assertFalse(is_weekday(sunday))

