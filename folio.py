
import datetime
import os

import util

def main():
    JST = datetime.timezone(datetime.timedelta(hours=+9), "JST")
    # TODO: Implement skipping Japanese holiday.
    if os.environ.get("SKIP_JP_HOLIDAY", False) and not util.is_weekday(datetime.datetime.now(JST)):
        print("Today is holiday. Skipped.")
        return False

    mail = os.environ["USERNAME"]
    password = os.environ["PASSWORD"]
    webhook_url = os.environ["WEBHOOK_URL"]
    title = os.environ.get("TITLE", "今日のフォリオ")
    wealthnavi_mode = os.environ.get("WEALTHNAVI_MODE", False)
    if wealthnavi_mode:
        try:
            browser = util.login_wealth_navi(mail, password)
            shisan = util.fetch_wealthnavi_shisan(browser)
        except:
            util.post_error_to_slack(webhook_url, title)
            return False
        util.post_wealthnavi_shisan_to_slack(shisan, webhook_url, title)
        return True

    try:
        browser = util.login(mail, password)
        shisan = util.fetch_folio_shisan(browser)
    except:
        util.post_error_to_slack(webhook_url, title)
        return False
    util.post_shisan_to_slack(shisan, webhook_url, title)
    return True


if __name__ == "__main__":
    if os.environ.get("CLOUDRUN", False):
        import flask
        app = flask.Flask(__name__)
        port = os.environ.get("PORT", 5000)
        port = int(port)

        @app.route("/run", methods=["POST"])
        def run():
            main()
            return ""
        app.run(port=port)
    else:
        main()
    exit(0)
