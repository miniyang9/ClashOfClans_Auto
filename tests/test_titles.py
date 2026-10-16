"""Window title matching."""

import unittest

from clashofclans_auto.titles import is_clash_window_title


class TitleTests(unittest.TestCase):
    def test_official_titles(self) -> None:
        self.assertTrue(is_clash_window_title("Clash of Clans"))
        self.assertTrue(is_clash_window_title("Clash of Clans - Google Play Games"))
        self.assertTrue(is_clash_window_title("部落冲突"))
        self.assertTrue(is_clash_window_title("部落冲突 (Clash of Clans) - player"))

    def test_repository_and_launcher_are_not_the_game(self) -> None:
        self.assertFalse(is_clash_window_title("ClashOfClans_Auto - Visual Studio Code"))
        self.assertFalse(is_clash_window_title("Google Play Games"))
        self.assertFalse(is_clash_window_title("规划部落冲突识图点击与基础任务 - grok"))
        self.assertFalse(is_clash_window_title("Capture the open Clash of Clans window - grok"))
        self.assertFalse(is_clash_window_title(""))


if __name__ == "__main__":
    unittest.main()
