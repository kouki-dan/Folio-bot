
import html
import json
import time
import os

import mechanicalsoup
import requests


def fetch_folio_shisan(mail, password):
    browser = mechanicalsoup.StatefulBrowser(
        soup_config={'features': 'html.parser'},
        raise_on_404=True,
        user_agent='FolioBot/0.1: github.com/kouki-dan/folio-bot',
    )

    login_url = "https://folio-sec.com/login"
    login_page = browser.open(login_url)
    csrf_token_dict_str = login_page.soup.select("#initial-data")[0].text
    token_dict = json.loads(html.unescape(csrf_token_dict_str))
    csrf_token = token_dict["csrf"]

    payload = {
        "username": mail,
        "password": password,
    }

    login_response = browser.post(login_url, data=payload, headers={
        "x-csrf-token": csrf_token,
    })

    shisan_url = "https://folio-sec.com/mypage/assets"
    shisan_page = browser.open(shisan_url)

    all_shisan = shisan_page.soup.select(".mypageCover__assetsAmount")[0].text
    fukumi_soneki_percent = shisan_page.soup.select(".assets__percentage")[0].text[1:-1]
    fukumi_soneki = shisan_page.soup.select(".assets__num")[1].text
    comp_yesterday_percent = shisan_page.soup.select(".assets__percentage")[1].text[1:-1]
    comp_yesterday = shisan_page.soup.select(".assets__num")[2].text
    return {
        "all_shisan": all_shisan,
        "fukumi_soneki_percent": fukumi_soneki_percent,
        "fukumi_soneki": fukumi_soneki,
        "comp_yesterday_percent": comp_yesterday_percent,
        "comp_yesterday": comp_yesterday,
    }

def post_error_to_slack(webhook_url, title):
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
                        "value": "<https://folio-sec.com/|FOLIO公式サイト>や<https://github.com/kouki-dan/Folio-bot|Botのバージョン>をご確認ください",
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
    fukumi_soneki_percent = shisan["fukumi_soneki_percent"]
    fukumi_soneki = shisan["fukumi_soneki"]
    comp_yesterday_percent = shisan["comp_yesterday_percent"]
    comp_yesterday = shisan["comp_yesterday"]

    payload = f"""
    {{
        "attachments": [
            {{
                "fallback": "FOLIOの情報です",
                "color": "#36a64f",
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


if __name__ == "__main__":
    mail = os.environ["USERNAME"]
    password = os.environ["PASSWORD"]
    webhook_url = os.environ["WEBHOOK_URL"]
    title = os.environ.get("TITLE", "今日のフォリオ")

    try:
        shisan = fetch_folio_shisan(mail, password)
    except:
        post_error_to_slack(webhook_url, title)
        exit(0)
    post_shisan_to_slack(shisan, webhook_url, title)

