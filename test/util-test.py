
import datetime
import unittest
import json

from util import Stock, Portfolio, is_weekday, create_payload

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

    def test_stock_big_n_with_no_zenjitsu_hi(self):
        big_3 = Stock.big_n(StockTest.stocks + [
            Stock("前日比なし", "2株", "¥--円", "--%"),
        ], 3)
        self.assertEqual(big_3[0].meigara, "日産自動車")
        self.assertEqual(big_3[1].meigara, "日本セラミック")
        self.assertEqual(big_3[2].meigara, "テクノスジャパン")

class PotfolioTest(unittest.TestCase):

    def test_portfolio_should_get_max_stock(self):
        portfolio = Portfolio(StockTest.stocks)
        self.assertEqual(portfolio.max_stock().meigara, "日産自動車")

    def test_portfolio_should_get_min_stock(self):
        portfolio = Portfolio(StockTest.stocks)
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

class CreatePayloadTest(unittest.TestCase):

    def test_create_payload_theme_only(self):
        shisan = {
            "all_shisan": "shisan",
            "all_theme": "all_theme",
            "omakase": None,
            "fukumi_soneki_percent": "fukumi_soneki%",
            "fukumi_soneki": "fukumi_soneki",
            "comp_yesterday_percent": "comp_yesterday%",
            "comp_yesterday": "comp_yesterday",
            "today_eiyu": "eiyu",
            "today_senpan": "senpan",
        }

        payload_str = create_payload("title", shisan)
        payload = json.loads(payload_str)
        attachment = payload["attachments"][0]
        self.assertEqual(attachment["title"], "title")

        fields = attachment["fields"]
        self.assertEqual(fields[0]["title"], "現在の資産")
        self.assertEqual(fields[0]["value"], "shisan")

        self.assertEqual(fields[1]["title"], "含み損益 (%)")
        self.assertEqual(fields[1]["value"], "fukumi_soneki（fukumi_soneki%）")

        self.assertEqual(fields[2]["title"], "前日比 (%)")
        self.assertEqual(fields[2]["value"], "comp_yesterday（comp_yesterday%）")

        self.assertEqual(fields[3]["title"], "テーマ内訳")
        self.assertEqual(fields[3]["value"], "all_theme")

        self.assertEqual(fields[4]["title"], "本日の英雄 :sunny:")
        self.assertEqual(fields[4]["value"], "eiyu")

        self.assertEqual(fields[5]["title"], "本日の戦犯 :umbrella_with_rain_drops:")
        self.assertEqual(fields[5]["value"], "senpan")

    def test_create_payload_omakase_only(self):
        shisan = {
            "all_shisan": "shisan",
            "all_theme": None,
            "omakase": "omakase",
            "fukumi_soneki_percent": "fukumi_soneki%",
            "fukumi_soneki": "fukumi_soneki",
            "comp_yesterday_percent": "comp_yesterday%",
            "comp_yesterday": "comp_yesterday",
            "today_eiyu": "eiyu",
            "today_senpan": "senpan",
        }

        payload_str = create_payload("title", shisan)
        payload = json.loads(payload_str)
        attachment = payload["attachments"][0]
        self.assertEqual(attachment["title"], "title")

        fields = attachment["fields"]
        self.assertEqual(fields[0]["title"], "現在の資産")
        self.assertEqual(fields[0]["value"], "shisan")

        self.assertEqual(fields[1]["title"], "含み損益 (%)")
        self.assertEqual(fields[1]["value"], "fukumi_soneki（fukumi_soneki%）")

        self.assertEqual(fields[2]["title"], "前日比 (%)")
        self.assertEqual(fields[2]["value"], "comp_yesterday（comp_yesterday%）")

        self.assertEqual(fields[3]["title"], "おまかせ投資内訳")
        self.assertEqual(fields[3]["value"], "omakase")

        self.assertEqual(len(fields), 4)

    def test_create_payload_theme_and_omakase(self):
        shisan = {
            "all_shisan": "shisan",
            "all_theme": "theme",
            "omakase": "omakase",
            "fukumi_soneki_percent": "fukumi_soneki%",
            "fukumi_soneki": "fukumi_soneki",
            "comp_yesterday_percent": "comp_yesterday%",
            "comp_yesterday": "comp_yesterday",
            "today_eiyu": "eiyu",
            "today_senpan": "senpan",
        }

        payload_str = create_payload("title", shisan)
        payload = json.loads(payload_str)
        attachment = payload["attachments"][0]
        self.assertEqual(attachment["title"], "title")

        fields = attachment["fields"]
        self.assertEqual(fields[0]["title"], "現在の資産")
        self.assertEqual(fields[0]["value"], "shisan")

        self.assertEqual(fields[1]["title"], "含み損益 (%)")
        self.assertEqual(fields[1]["value"], "fukumi_soneki（fukumi_soneki%）")

        self.assertEqual(fields[2]["title"], "前日比 (%)")
        self.assertEqual(fields[2]["value"], "comp_yesterday（comp_yesterday%）")

        self.assertEqual(fields[3]["title"], "テーマ内訳")
        self.assertEqual(fields[3]["value"], "theme")

        self.assertEqual(fields[4]["title"], "おまかせ投資内訳")
        self.assertEqual(fields[4]["value"], "omakase")

        self.assertEqual(fields[5]["title"], "本日の英雄 :sunny:")
        self.assertEqual(fields[5]["value"], "eiyu")

        self.assertEqual(fields[6]["title"], "本日の戦犯 :umbrella_with_rain_drops:")
        self.assertEqual(fields[6]["value"], "senpan")

