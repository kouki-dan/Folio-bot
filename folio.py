
import html
import json
import time
import os
import re
import sys
import traceback
import time

import mechanicalsoup
import requests

def login(mail, password):
    browser = mechanicalsoup.StatefulBrowser(
        soup_config={'features': 'html.parser'},
        raise_on_404=True,
        user_agent='FolioBot/0.1: github.com/kouki-dan/folio-bot',
    )

    login_url = "https://folio-sec.com/login"
    login_page = browser.open(login_url)
    csrf_token_dict_str = login_page.soup.select("#initial-data")[0]["data-json"]
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
    return browser

def fetch_folio_theme_shisan(browser, theme_card_dom):
    theme_link = theme_card_dom["href"]
    theme_name = theme_card_dom.select(".assetsCard__name")[0].text
    theme_url = "https://folio-sec.com" + theme_link
    theme_page = browser.open(theme_url)

    assets_num_doms = theme_page.soup.select(".assets__num")
    amount = assets_num_doms[0].text
    gain_yen = assets_num_doms[1].text
    profit_yen = assets_num_doms[2].text

    percent_doms = theme_page.soup.select(".assets__percentage")
    gain_percent = percent_doms[0].text
    profit_percent = percent_doms[1].text

    return f"<{theme_url}|{theme_name}>: {amount}\n  含み損益:{gain_yen}{gain_percent} 前日比:{profit_yen}{profit_percent}"


def fetch_folio_shisan(browser):
    shisan_url = "https://folio-sec.com/mypage/assets"
    shisan_page = browser.open(shisan_url)

    all_shisan = shisan_page.soup.select(".mypageCover__assetsAmount")[0].text
    fukumi_soneki_percent = shisan_page.soup.select(".assets__percentage")[0].text[1:-1]
    fukumi_soneki = shisan_page.soup.select(".assets__num")[1].text
    comp_yesterday_percent = shisan_page.soup.select(".assets__percentage")[1].text[1:-1]
    comp_yesterday = shisan_page.soup.select(".assets__num")[2].text

    all_theme_card_doms = shisan_page.soup.select(".assetsCard__card")
    all_theme_array = []
    for i, theme_card_dom in enumerate(all_theme_card_doms):
      all_theme_array.append(
        fetch_folio_theme_shisan(browser, theme_card_dom)
      )
      time.sleep(1)
    all_theme = "\n".join(all_theme_array)

    return {
        "all_shisan": all_shisan,
        "all_theme": all_theme,
        "fukumi_soneki_percent": fukumi_soneki_percent,
        "fukumi_soneki": fukumi_soneki,
        "comp_yesterday_percent": comp_yesterday_percent,
        "comp_yesterday": comp_yesterday,
    }

def post_error_to_slack(webhook_url, title):
    exc = sys.exc_info()
    exc_string = "\n".join(traceback.format_exception(exc[0], exc[1], exc[2])).encode("unicode_escape").decode("utf-8").replace('"', r'\"')
    payload = f"""
    {{
        "attachments": [
            {{
                "fallback": "FOLIOの情報です(ERROR)",
                "color": "#ef1c3b",
                "title": "{title}(ERROR)",
                "title_link": "https://folio-sec.com/mypage/assets",
                "fields": [
                    {{
                        "title": "情報の取得に失敗しました",
                        "value": "<https://folio-sec.com/|FOLIO公式サイト>や<https://github.com/kouki-dan/Folio-bot|Botのバージョン>をご確認ください。{exc_string}",
                        "short": false
                    }}
                ],
                "thumb_url": "https://emoji.slack-edge.com/T5KKCPE2C/folio/c73ae303fcd0a1da.png",
                "footer": "Folio Bot",
                "footer_icon": "https://emoji.slack-edge.com/T5KKCPE2C/folio/c73ae303fcd0a1da.png",
                "ts": {int(time.time())}
            }}
        ]
    }}
    """
    requests.post(webhook_url, data={"payload": payload})

def post_shisan_to_slack(shisan, webhook_url, title):
    all_shisan = shisan["all_shisan"]
    all_theme = shisan["all_theme"]
    fukumi_soneki_percent = shisan["fukumi_soneki_percent"]
    fukumi_soneki = shisan["fukumi_soneki"]
    comp_yesterday_percent = shisan["comp_yesterday_percent"]
    comp_yesterday = shisan["comp_yesterday"]

    payload = f"""
    {{
        "attachments": [
            {{
                "fallback": "FOLIOの情報です",
                "color": "#189ac5",
                "title": "{title}",
                "title_link": "https://folio-sec.com/mypage/assets",
                "fields": [
                    {{
                        "title": "現在の資産",
                        "value": "{all_shisan}",
                        "short": false
                    }},
                    {{
                        "title": "含み損益 (%)",
                        "value": "{fukumi_soneki} ({fukumi_soneki_percent})",
                        "short": true
                    }},
                    {{
                        "title": "前日比 (%)",
                        "value": "{comp_yesterday} ({comp_yesterday_percent})",
                        "short": true
                    }},
                    {{
                        "title": "内訳",
                        "value": "{all_theme}",
                        "short": false
                    }}
                ],
                "footer": "Folio Bot",
                "footer_icon": "https://emoji.slack-edge.com/T5KKCPE2C/folio/c73ae303fcd0a1da.png",
                "ts": {int(time.time())}
            }}
        ]
    }}
    """

    requests.post(webhook_url, data={"payload": payload})


if __name__ == "__main__":
    mail = os.environ["USERNAME"]
    password = os.environ["PASSWORD"]
    webhook_url = os.environ["WEBHOOK_URL"]
    title = os.environ.get("TITLE", "今日のフォリオ")

    try:
        browser = login(mail, password)
        shisan = fetch_folio_shisan(browser)
    except:
        post_error_to_slack(webhook_url, title)
        exit(1)
    post_shisan_to_slack(shisan, webhook_url, title)
    exit(0)

