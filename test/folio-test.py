
import unittest
from unittest.mock import patch
import os

import folio


class MainTest(unittest.TestCase):

    @patch("util.is_weekday")
    @patch("util.post_shisan_to_slack")
    @patch("util.fetch_folio_shisan")
    @patch("util.login")
    def test_main_method_works(self, login_patch, fetch_folio_shisan_patch, post_shisan_to_slack_patch, is_weekday_patch):
        login_patch.return_value = None
        fetch_folio_shisan_patch.return_value = {
            "all_shisan": "すべての資産",
            "all_theme": "すべての資産",
            "fukumi_soneki_percent": "含み損益パーセント",
            "fukumi_soneki": "含み損益",
            "comp_yesterday_percent": "前日比パーセント",
            "comp_yesterday": "前日比",
            "today_eiyu": "英雄",
            "today_senpan": "戦犯",
        }
        post_shisan_to_slack_patch.return_value = None
        is_weekday_patch.return_value = True
        self.assertTrue(folio.main())

    @patch("util.is_weekday")
    @patch("util.post_shisan_to_slack")
    @patch("util.fetch_folio_shisan")
    @patch("util.login")
    def test_main_method_is_not_work_on_weekends(self, login_patch, fetch_folio_shisan_patch, post_shisan_to_slack_patch, is_weekday_patch):
        login_patch.return_value = None
        fetch_folio_shisan_patch.return_value = {
            "all_shisan": "すべての資産",
            "all_theme": "すべての資産",
            "fukumi_soneki_percent": "含み損益パーセント",
            "fukumi_soneki": "含み損益",
            "comp_yesterday_percent": "前日比パーセント",
            "comp_yesterday": "前日比",
            "today_eiyu": "英雄",
            "today_senpan": "戦犯",
        }
        post_shisan_to_slack_patch.return_value = None
        is_weekday_patch.return_value = False

        os.environ["SKIP_JP_HOLIDAY"] = "1"
        self.assertFalse(folio.main())

