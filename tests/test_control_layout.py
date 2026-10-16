"""Recorded clicks land on the control that was visible there."""

import unittest

from clashofclans_auto.control_layout import CONTROL_BOXES, control_at
from clashofclans_auto.ui_flow import SCREENS

WIDTH = 1303
HEIGHT = 808

# Left-button presses from session 20261016T000924.
PRESSES = (
    ("attack_menu", 249, 592, "search"),
    ("army", 1044, 667, "attack"),
    ("results", 711, 704, "return_home"),
)

# Deployment presses. Both battle screens share these bars and the battlefield.
DEPLOYED = (
    (269, 759, "troop_slot"),
    (324, 758, "troop_slot"),
    (426, 746, "spell_slot"),
    (438, 779, "spell_slot"),
    (546, 782, "spell_slot"),
    (1064, 365, "map"),
    (1072, 396, "map"),
    (1072, 410, "map"),
    (1068, 424, "map"),
    (1060, 444, "map"),
    (1047, 472, "map"),
    (1035, 488, "map"),
    (1025, 519, "map"),
    (1025, 519, "map"),
    (1051, 455, "map"),
    (1077, 408, "map"),
    (1076, 450, "map"),
    (949, 465, "map"),
    (943, 371, "map"),
    (860, 427, "map"),
    (855, 379, "map"),
    (833, 302, "map"),
    (776, 323, "map"),
    (830, 487, "map"),
    (779, 385, "map"),
    (820, 310, "map"),
)


class ControlLayoutTests(unittest.TestCase):
    def test_every_flow_control_has_a_box(self) -> None:
        placed = {(box.screen_id, box.control_id) for box in CONTROL_BOXES}
        for screen in SCREENS.values():
            for control in screen.controls:
                self.assertIn((screen.id, control.id), placed)

    def test_boxes_have_area(self) -> None:
        for box in CONTROL_BOXES:
            self.assertGreater(box.right, box.left)
            self.assertGreater(box.bottom, box.top)
            self.assertGreater(box.ref_width, 0)
            self.assertGreater(box.ref_height, 0)

    def test_recorded_presses_hit_the_visible_control(self) -> None:
        for screen_id, x, y, expected in PRESSES:
            self.assertEqual(
                control_at(screen_id, x, y, WIDTH, HEIGHT),
                expected,
                f"{screen_id} {x},{y}",
            )
        for screen_id in ("battle_prep", "battle"):
            for x, y, expected in DEPLOYED:
                self.assertEqual(
                    control_at(screen_id, x, y, WIDTH, HEIGHT),
                    expected,
                    f"{screen_id} {x},{y}",
                )

    def test_buttons_win_over_the_battlefield(self) -> None:
        self.assertEqual(control_at("battle_prep", 150, 650, WIDTH, HEIGHT), "end_battle")
        self.assertEqual(control_at("battle_prep", 1200, 600, WIDTH, HEIGHT), "next_opponent")
        self.assertEqual(control_at("battle", 150, 650, WIDTH, HEIGHT), "surrender")
        self.assertEqual(control_at("battle_prep", 1000, 600, WIDTH, HEIGHT), "map")

    def test_unpressed_buttons_still_have_a_place(self) -> None:
        self.assertEqual(control_at("attack_menu", 214, 781, WIDTH, HEIGHT), "edit_army")
        self.assertEqual(control_at("army", 1210, 174, WIDTH, HEIGHT), "close")

    def test_sidebar_and_gaps_are_not_controls(self) -> None:
        self.assertIsNone(control_at("battle", 20, 400, WIDTH, HEIGHT))
        self.assertIsNone(control_at("attack_menu", 249, 680, WIDTH, HEIGHT))
        self.assertIsNone(control_at("army", 1044, 400, WIDTH, HEIGHT))

    def test_home_battle_scales_from_its_own_capture(self) -> None:
        self.assertEqual(control_at("home", 186, 1040, 1828, 1136), "battle")
        self.assertIsNone(control_at("home", 1725, 1040, 1828, 1136))
        self.assertEqual(control_at("home", 133, 739, WIDTH, HEIGHT), "battle")
        self.assertIsNone(control_at("home", 249, 592, WIDTH, HEIGHT))


if __name__ == "__main__":
    unittest.main()
