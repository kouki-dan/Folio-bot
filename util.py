
from __future__ import annotations

import html
import json
import sys
import traceback
import time
from typing import List, Optional

import mechanicalsoup
import requests

import version


class Stock:
    def __init__(self, meigara: str, kabu_suu: str, unyo_kingaku: str, zenjitsu_hi_percent: str):
        self.meigara = meigara  # 銘柄
        self.kabu_suu = kabu_suu  # 数量
        self.unyo_kingaku = unyo_kingaku  # 運用金額
        self.zenjitsu_hi_percent = zenjitsu_hi_percent  # 前日比

    def __str__(self) -> str:
        return str(vars(self))

    def to_slack_msg(self) -> str:
        return f"<http://google.co.jp/search?q={self.meigara} ニュース|{self.meigara}>: {self.unyo_kingaku} ({self.zenjitsu_hi_percent})"

    @staticmethod
    def big_n(stocks, num):
        return sorted(stocks, key=lambda x: Stock.floatOr0(x.zenjitsu_hi_percent[:-1]), reverse=True)[0:num]

    @staticmethod
    def small_n(stocks, num):
        return sorted(stocks, key=lambda x: Stock.floatOr0(x.zenjitsu_hi_percent[:-1]), reverse=False)[0:num]

    @staticmethod
    def floatOr0(num):
        try:
            return float(num)
        except ValueError:
            return 0.0


class Portfolio:
    def __init__(self, stocks: List[Stock]):
        self.stocks = stocks  # 株

    def __str__(self) -> str:
        return str(vars(self)) + ", ".join(map(str, self.stocks))

    def max_stock(self) -> Stock:
        return max(self.stocks, key=lambda x: float(x.zenjitsu_hi_percent[:-1]))

    def min_stock(self) -> Stock:
        return min(self.stocks, key=lambda x: float(x.zenjitsu_hi_percent[:-1]))

    @staticmethod
    def parse_portfolio_from_dom(portfolio_box_dom):
        stocks_doms = portfolio_box_dom.select("tbody")[0].select("tr")
        stocks = []

        for i, stocks_dom in enumerate(stocks_doms):
            column = stocks_dom.select("td")
            meigara = column[0].text
            kabu_suu = column[1].text
            unyo_kingaku = column[2].text
            zenjitsu_hi = column[3].text
            stocks.append(Stock(meigara, kabu_suu, unyo_kingaku, zenjitsu_hi))

        return Portfolio(stocks)


class Theme:
    def __init__(self, name: str, url: str, oazukari_shisan: str, fukumi_soneki: str, fukumi_soneki_percent: str,
                 zenjitsu_hi: str, zenjitsu_hi_percent: str, portfolios: List[Portfolio]):
        self.name = name
        self.url = url
        self.oazukari_shisan = oazukari_shisan
        self.fukumi_soneki = fukumi_soneki
        self.fukumi_soneki_percent = fukumi_soneki_percent
        self.zenjitsu_hi = zenjitsu_hi
        self.zenjitsu_hi_percent = zenjitsu_hi_percent
        self.portfolios = portfolios

    def __str__(self) -> str:
        return str(vars(self)) + ", ".join(map(str, self.portfolios))

    def allStocks(self) -> List[Stock]:
        return [stock for portfolio in self.portfolios for stock in portfolio.stocks]

    def eiyuRanking(self, num) -> List[Stock]:
        return Stock.big_n(self.allStocks(), num)

    def senpanRanking(self, num) -> List[Stock]:
        return Stock.small_n(self.allStocks(), num)

    def to_slack_msg(self) -> str:
        return f"<{self.url}|{self.name}>: {self.oazukari_shisan}\n" \
               f"  含み損益:{self.fukumi_soneki}{self.fukumi_soneki_percent} 前日比:{self.zenjitsu_hi}{self.zenjitsu_hi_percent}"

    @staticmethod
    def parse_theme_url_from_dom(theme_card_dom):
        theme_link = theme_card_dom["href"]
        return "https://folio-sec.com" + theme_link

    @staticmethod
    def parse_theme_from_dom(theme_page_dom, url: str):
        titleDoms = theme_page_dom.select(".box__titleMain")
        ## 購入中の場合emptyになる。
        if len(titleDoms) == 0:
            return None
        name = titleDoms[0].text.rstrip("の資産")
        name = theme_page_dom.select(".box__titleMain")[0].text.rstrip("の資産")
        assets_num_doms = theme_page_dom.select(".assets__num")
        oazukari_shisan = assets_num_doms[0].text
        fukumi_soneki = assets_num_doms[1].text
        zenjitsu_hi = assets_num_doms[2].text

        percent_doms = theme_page_dom.select(".assets__percentage")
        fukumi_soneki_percent = percent_doms[0].text
        zenjitsu_hi_percent = percent_doms[1].text

        portfolio_box_doms = theme_page_dom.select(".portfolioBox")
        all_portfolios = []
        for i, portfolio_box_dom in enumerate(portfolio_box_doms):
            all_portfolios.append(Portfolio.parse_portfolio_from_dom(portfolio_box_dom))

        return Theme(
            name,
            url,
            oazukari_shisan,
            fukumi_soneki,
            fukumi_soneki_percent,
            zenjitsu_hi,
            zenjitsu_hi_percent,
            all_portfolios
        )


class UserAllTheme:
    def __init__(self, themes: List[Theme]):
        self.themes = themes

    def __str__(self) -> str:
        return str(vars(self)) + ", ".join(map(str, self.themes))

    def eiyuRankingForAllTheme(self, num) -> List[Stock]:
        return Stock.big_n([stock for theme in self.themes for stock in theme.allStocks()], num)

    def senpanRankingForAllTheme(self, num) -> List[Stock]:
        return Stock.small_n([stock for theme in self.themes for stock in theme.allStocks()], num)

    @staticmethod
    def parse_all_theme_card_doms(shisan_page_dom):
        return shisan_page_dom.select_one("section[class*=assetsCard]").select("a[class*=assetsCard]")


class Omakase:
    def __init__(self, plan: str, oazukari_shisan: str, fukumi_soneki: str, fukumi_soneki_percent: str,
                 zenjitsu_hi: str, zenjitsu_hi_percent: str):
        self.plan = plan
        self.oazukari_shisan = oazukari_shisan
        self.fukumi_soneki = fukumi_soneki
        self.fukumi_soneki_percent = fukumi_soneki_percent
        self.zenjitsu_hi = zenjitsu_hi
        self.zenjitsu_hi_percent = zenjitsu_hi_percent
        self.url = "https://folio-sec.com/mypage/assets/omakase"

    def __str__(self) -> str:
        return str(vars(self))

    def to_slack_msg(self) -> str:
        return f"<{self.url}|{self.plan}>: {self.oazukari_shisan}\n" \
               f"  含み損益:{self.fukumi_soneki}{self.fukumi_soneki_percent} 前日比:{self.zenjitsu_hi}{self.zenjitsu_hi_percent}"

    @staticmethod
    def parse_theme_from_dom(theme_page_dom) -> Optional[Omakase]:
        try:
            plan = theme_page_dom.select("[class^='MyPlan__name']")[0].text
        except IndexError:
            return None

        assets_num_doms = theme_page_dom.select(".assets__num")
        oazukari_shisan = assets_num_doms[0].text
        fukumi_soneki = assets_num_doms[1].text
        zenjitsu_hi = assets_num_doms[2].text

        percent_doms = theme_page_dom.select(".assets__percentage")
        fukumi_soneki_percent = percent_doms[0].text
        zenjitsu_hi_percent = percent_doms[1].text

        return Omakase(
            plan,
            oazukari_shisan,
            fukumi_soneki,
            fukumi_soneki_percent,
            zenjitsu_hi,
            zenjitsu_hi_percent,
        )


class UserShisan:
    shisan_url = "https://folio-sec.com/mypage/assets"

    def __init__(self, fukumi_soneki: str, fukumi_soneki_percent: str, zenjitsu_hi: str,
              zenjitsu_hi_percent: str, subete_no_shisan: str):
        self.fukumi_soneki = fukumi_soneki
        self.fukumi_soneki_percent = fukumi_soneki_percent
        self.zenjitsu_hi = zenjitsu_hi
        self.zenjitsu_hi_percent = zenjitsu_hi_percent
        self.subete_no_shisan = subete_no_shisan

    def __str__(self) -> str:
        return str(vars(self))

    @staticmethod
    def parse_user_shisan_page_dom(shisan_page_dom):
        asset_summary = shisan_page_dom.select(".mypageHeaderAssetSummary > div")
        subete_no_shisan = asset_summary[0].select(".mypageHeaderAssetSummary__col__value__price")[0].text

        fukumi_soneki = asset_summary[1].select(".mypageHeaderAssetSummary__col__value__price")[0].text
        zenjitsu_hi = asset_summary[2].select(".mypageHeaderAssetSummary__col__value__price")[0].text
        fukumi_soneki_percent = asset_summary[1].select(".mypageHeaderAssetSummary__col__label__ratio")[0].text[1:-1]
        zenjitsu_hi_percent = asset_summary[2].select(".mypageHeaderAssetSummary__col__label__ratio")[0].text[1:-1]
        return UserShisan(fukumi_soneki, fukumi_soneki_percent, zenjitsu_hi, zenjitsu_hi_percent, subete_no_shisan)


def login(mail: str, password: str) -> mechanicalsoup.StatefulBrowser:
    browser = mechanicalsoup.StatefulBrowser(
        soup_config={'features': 'html.parser'},
        raise_on_404=True,
        user_agent=user_agent(),
    )

    login_url = "https://folio-sec.com/login"
    login_page = browser.open(login_url)
    csrf_token_dict_str = login_page.soup.select("#meta")[0]["data-json"]
    token_dict = json.loads(html.unescape(csrf_token_dict_str))
    csrf_token = token_dict["csrf"]

    payload = {
        "username": mail,
        "password": password,
    }

    login_api_url = "https://folio-sec.com/api/v1/login"
    login_response = browser.post(login_api_url, data=payload, headers={
        "x-csrf-token": csrf_token,
    })
    login_response.raise_for_status() ## Please check mail/password or relogin via Web UI(https://folio-sec.com/login) when stopped at this line.
    return browser

def login_wealth_navi(mail: str, password: str) -> mechanicalsoup.StatefulBrowser:
    browser = mechanicalsoup.StatefulBrowser(
        soup_config={'features': 'html.parser'},
        raise_on_404=True,
        user_agent=user_agent(),
    )

    login_url = "https://invest.wealthnavi.com/"
    login_page = browser.open(login_url)

    login_page.soup.select("form")[0].select("#username")[0]["value"] = mail
    login_page.soup.select("form")[0].select("#password")[0]["value"] = password
    login_page.soup.select("form")[0]["action"] = "https://invest.wealthnavi.com/login"
    login_response = browser.submit(login_page.soup.select("form")[0])

    login_response.raise_for_status() ## Please check mail/password or relogin via Web UI(https://folio-sec.com/login) when stopped at this line.
    return browser

def fetch_folio_theme_shisan(browser, theme_card_dom) -> Optional[Theme]:
    theme_url = Theme.parse_theme_url_from_dom(theme_card_dom)
    theme_page = browser.open(theme_url)
    return Theme.parse_theme_from_dom(theme_page.soup, theme_url)


def fetch_folio_all_theme(browser, shisan_page_dom) -> UserAllTheme:
    all_theme_card_doms = UserAllTheme.parse_all_theme_card_doms(shisan_page_dom)

    all_theme_array = []
    for i, theme_card_dom in enumerate(all_theme_card_doms):
        themeOrNull = fetch_folio_theme_shisan(browser, theme_card_dom)
        if themeOrNull:
            all_theme_array.append(themeOrNull)
        time.sleep(1)
    return UserAllTheme(all_theme_array)


def fetch_folio_omakase(browser) -> Optional[Omakase]:
    omakase_page_dom = browser.open("https://folio-sec.com/mypage/assets/omakase")
    return Omakase.parse_theme_from_dom(omakase_page_dom.soup)


def fetch_folio_shisan(browser):
    shisan_page = browser.open(UserShisan.shisan_url)
    user_shisan = UserShisan.parse_user_shisan_page_dom(shisan_page.soup)
    all_theme = fetch_folio_all_theme(browser, shisan_page.soup)
    omakase = fetch_folio_omakase(browser)

    if len(all_theme.themes) > 0:
        all_theme_str = "\n".join(map(lambda t: t.to_slack_msg(), all_theme.themes))
    else:
        all_theme_str = None

    if omakase:
        omakase_str = omakase.to_slack_msg()
    else:
        omakase_str = None

    rankingNum = 1
    return {
        "all_shisan": user_shisan.subete_no_shisan,
        "all_theme": all_theme_str,
        "omakase": omakase_str,
        "fukumi_soneki_percent": user_shisan.fukumi_soneki_percent,
        "fukumi_soneki": user_shisan.fukumi_soneki,
        "comp_yesterday_percent": user_shisan.zenjitsu_hi_percent,
        "comp_yesterday": user_shisan.zenjitsu_hi,
        "today_eiyu": "\n".join([stock.to_slack_msg() for stock in all_theme.eiyuRankingForAllTheme(rankingNum)]),
        "today_senpan": "\n".join([stock.to_slack_msg() for stock in all_theme.senpanRankingForAllTheme(rankingNum)])
    }

def fetch_wealthnavi_shisan(browser):
    portfolio = browser.open("https://invest.wealthnavi.com/service/portfolio")
    hyokagaku = portfolio.soup.select(".currency-info")[0]

    all_shisan = hyokagaku.select(".evaluation")[0].text
    fukumi_soneki = hyokagaku.select(".difference")[0].text
    fukumi_soneki_percent = hyokagaku.select(".per")[0].text

    # TODO: calc yesterday info from hyokagaku
    # yesterday_hyokagaku = portfolio.soup.select(".graph .data-history")[0].select("tbody")[0].select("tr")[1]

    utiwake = ""
    for x in portfolio.soup.select("#assets-class-data")[0].select("tr")[1:]:
        splitted = x.text.split("\n")[1:]
        utiwake += " ".join(splitted[:2]) + " (" + splitted[2] + ")" + "\n"

    return {
        "all_shisan": all_shisan,
        "fukumi_soneki": fukumi_soneki,
        "fukumi_soneki_percent": fukumi_soneki_percent,
        # "comp_yesterday_percent": shisan["comp_yesterday_percent"],
        # "comp_yesterday": shisan["comp_yesterday"],
        "utiwake": utiwake,
    }

def post_error_to_slack(webhook_url, title):
    exc = sys.exc_info()
    exc_string = "\n".join(traceback.format_exception(exc[0], exc[1], exc[2])).encode("unicode_escape").decode(
        "utf-8").replace('"', r'\"')
    payload = f"""
    {{
        "attachments": [
            {{
                "fallback": "FOLIOの情報です(ERROR)",
                "color": "#ff0000",
                "title": "{title}(ERROR)",
                "title_link": "https://folio-sec.com/mypage/assets",
                "fields": [
                    {{
                        "title": "情報の取得に失敗しました",
                        "value": "<https://folio-sec.com/|FOLIO公式サイト>や<https://github.com/kouki-dan/Folio-bot|Botのバージョン>をご確認ください。\n<https://github.com/kouki-dan/folio-bot/issues|こちら>から問題の報告もお待ちしています。\n{exc_string}",
                        "short": false
                    }}
                ],
                "footer": "Folio Bot",
                "footer_icon": "https://slack-files2.s3-us-west-2.amazonaws.com/avatars/2018-08-08/413994431606_fe468300b6cccdefcd35_36.jpg",
                "ts": {int(time.time())}
            }}
        ]
    }}
    """
    requests.post(webhook_url, data={"payload": payload})

def create_payload(title, shisan):
    all_shisan = shisan["all_shisan"]
    all_theme = shisan["all_theme"]
    omakase = shisan["omakase"]
    fukumi_soneki_percent = shisan["fukumi_soneki_percent"]
    fukumi_soneki = shisan["fukumi_soneki"]
    comp_yesterday_percent = shisan["comp_yesterday_percent"]
    comp_yesterday = shisan["comp_yesterday"]
    today_eiyu = shisan["today_eiyu"]
    today_senpan = shisan["today_senpan"]

    utiwake = []

    if all_theme:
        utiwake.append({
            "title": "テーマ内訳",
            "value": all_theme,
            "short": False
        })

    if omakase:
        utiwake.append({
            "title": "おまかせ投資内訳",
            "value": omakase,
            "short": False
        })

    if all_theme:
        utiwake.append({
            "title": "本日の英雄 :sunny:",
            "value": today_eiyu,
            "short": True
        })

        utiwake.append({
            "title": "本日の戦犯 :umbrella_with_rain_drops:",
            "value": today_senpan,
            "short": True
        })

    payload = {
        "attachments": [
            {
                "fallback": "FOLIOの情報です",
                "color": "#f26161",
                "title": title,
                "title_link": "https://folio-sec.com/mypage/assets",
                "fields": [
                    {
                        "title": "現在の資産",
                        "value": all_shisan,
                        "short": False
                    },
                    {
                        "title": "含み損益 (%)",
                        "value": f"{fukumi_soneki}（{fukumi_soneki_percent}）",
                        "short": True
                    },
                    {
                        "title": "前日比 (%)",
                        "value": f"{comp_yesterday}（{comp_yesterday_percent}）",
                        "short": True
                    },
                ] + utiwake,
                "footer": "Folio Bot",
                "footer_icon": "https://slack-files2.s3-us-west-2.amazonaws.com/avatars/2018-08-08/413994431606_fe468300b6cccdefcd35_36.jpg",
                "ts": int(time.time())
            }
        ]
    }
    return json.dumps(payload)

def create_wealthnavi_payload(title, shisan):
    all_shisan = shisan["all_shisan"]
    fukumi_soneki_percent = shisan["fukumi_soneki_percent"]
    fukumi_soneki = shisan["fukumi_soneki"]
    utiwake = shisan["utiwake"]

    payload = {
        "attachments": [
            {
                "fallback": "FOLIOの情報です",
                "color": "#3584dc",
                "title": title,
                "title_link": "https://invest.wealthnavi.com/service/portfolio",
                "fields": [
                    {
                        "title": "現在の資産",
                        "value": all_shisan,
                        "short": False
                    },
                    {
                        "title": "含み損益 (%)",
                        "value": f"{fukumi_soneki}（{fukumi_soneki_percent}）",
                        "short": True
                    },
                    {
                        "title": "資産内訳",
                        "value": utiwake,
                        "short": False
                    },
                ],
                "footer": "Folio Bot",
                "footer_icon": "https://slack-files2.s3-us-west-2.amazonaws.com/avatars/2018-08-08/413994431606_fe468300b6cccdefcd35_36.jpg",
                "ts": int(time.time())
            }
        ]
    }
    return json.dumps(payload)

def post_shisan_to_slack(shisan, webhook_url, title):
    payload = create_payload(title, shisan)
    requests.post(webhook_url, data={"payload": payload})

def post_wealthnavi_shisan_to_slack(shisan, webhook_url, title):
    payload = create_wealthnavi_payload(title, shisan)
    requests.post(webhook_url, data={"payload": payload})

def is_weekday(target_datetime):
    if target_datetime.weekday() == 5 or target_datetime.weekday() == 6:
        return False
    return True

def user_agent() -> str:
    return f'Mozilla/5.0 (compatible; Edge; Foliobot/{version.version}; +http://github.com/kouki-dan/folio-bot)'
