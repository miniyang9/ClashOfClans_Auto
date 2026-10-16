"""A frame names one screen, or none when the buttons do not agree."""

import unittest

from clashofclans_auto.control_layout import CONTROL_BOXES, ControlBox
from clashofclans_auto.screen_match import match_screen
from clashofclans_auto.ui_flow import SCREENS

WIDTH = 651
HEIGHT = 404
YELLOW = bytes((0, 220, 230))
GREEN = bytes((40, 210, 30))
RED = bytes((30, 30, 220))


def _box(screen_id: str, control_id: str) -> ControlBox:
    for box in CONTROL_BOXES:
        if box.screen_id == screen_id and box.control_id == control_id:
            return box
    raise AssertionError(f"missing {screen_id}.{control_id}")


def _frame(paints: tuple[tuple[ControlBox, bytes, float], ...], width: int = WIDTH, height: int = HEIGHT):
    stride = (width * 3 + 3) & ~3
    data = bytearray(stride * height)
    for box, color, portion in paints:
        pixels = [
            (x, y)
            for y in range(height)
            for x in range(width)
            if box.contains(x, y, width, height)
        ]
        count = int(len(pixels) * portion)
        if count <= 0:
            raise AssertionError(f"{box.control_id} filled nothing")
        for x, y in pixels[:count]:
            index = y * stride + x * 3
            data[index : index + 3] = color
    return bytes(data), stride


class ScreenMatchTests(unittest.TestCase):
    def test_each_screen_is_recognized_from_its_buttons(self) -> None:
        samples = {
            "home": ((_box("home", "battle"), YELLOW, 1),),
            "attack_menu": (
                (_box("attack_menu", "search"), YELLOW, 1),
                (_box("attack_menu", "edit_army"), GREEN, 1),
            ),
            "army": (
                (_box("army", "attack"), GREEN, 1),
                (_box("army", "close"), RED, 1),
            ),
            "battle_prep": (
                (_box("battle_prep", "end_battle"), RED, 1),
                (_box("battle_prep", "next_opponent"), YELLOW, 1),
            ),
            "battle": ((_box("battle", "surrender"), RED, 1),),
            "results": ((_box("results", "return_home"), GREEN, 1),),
        }
        self.assertEqual(set(samples), set(SCREENS))
        for screen_id, paints in samples.items():
            data, stride = _frame(paints)
            self.assertEqual(match_screen(data, WIDTH, HEIGHT, stride), screen_id, screen_id)

    def test_home_button_uses_its_own_reference_size(self) -> None:
        width, height = 914, 568
        data, stride = _frame(((_box("home", "battle"), YELLOW, 1),), width, height)
        self.assertEqual(match_screen(data, width, height, stride), "home")

    def test_a_partly_covered_leave_button_is_still_the_fight(self) -> None:
        data, stride = _frame(((_box("battle", "surrender"), RED, 0.25),))
        self.assertEqual(match_screen(data, WIDTH, HEIGHT, stride), "battle")

    def test_a_weak_leave_button_is_unknown(self) -> None:
        data, stride = _frame(((_box("battle", "surrender"), RED, 0.05),))
        self.assertIsNone(match_screen(data, WIDTH, HEIGHT, stride))

    def test_two_screens_at_once_are_unknown(self) -> None:
        data, stride = _frame(
            (
                (_box("home", "battle"), YELLOW, 1),
                (_box("results", "return_home"), GREEN, 1),
            )
        )
        self.assertIsNone(match_screen(data, WIDTH, HEIGHT, stride))

    def test_attack_without_the_close_button_is_unknown(self) -> None:
        data, stride = _frame(((_box("army", "attack"), GREEN, 1),))
        self.assertIsNone(match_screen(data, WIDTH, HEIGHT, stride))

    def test_blank_and_broken_frames_are_unknown(self) -> None:
        data, stride = _frame(())
        self.assertIsNone(match_screen(data, WIDTH, HEIGHT, stride))
        self.assertIsNone(match_screen(data, 0, HEIGHT, stride))
        self.assertIsNone(match_screen(data[:10], WIDTH, HEIGHT, stride))


if __name__ == "__main__":
    unittest.main()
