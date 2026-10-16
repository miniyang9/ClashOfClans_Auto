"""Pointer coordinate conversion and gesture filtering."""

import unittest

from clashofclans_auto.pointer import PointerState, inside_client, note_down, note_move, note_up, to_client


class PointerTests(unittest.TestCase):
    def test_screen_point_becomes_client_point(self) -> None:
        self.assertEqual(to_client(150, 80, 40, 20), (110, 60))

    def test_edges_belong_inside_until_the_far_side(self) -> None:
        self.assertTrue(inside_client(0, 0, 100, 50))
        self.assertFalse(inside_client(100, 0, 100, 50))
        self.assertFalse(inside_client(-1, 10, 100, 50))

    def test_move_without_a_press_is_ignored(self) -> None:
        state = PointerState()
        self.assertFalse(note_move(state, 10, 10, 0))

    def test_press_outside_does_not_start_a_gesture(self) -> None:
        state = PointerState()
        self.assertFalse(note_down(state, "left", 120, 10, 100, 50))
        self.assertFalse(note_move(state, 130, 10, 20))
        self.assertFalse(note_up(state, "left"))

    def test_drag_samples_by_time_or_distance(self) -> None:
        state = PointerState()
        self.assertTrue(note_down(state, "left", 10, 10, 100, 50))
        self.assertTrue(note_move(state, 12, 10, 10))
        self.assertFalse(note_move(state, 13, 10, 20))
        self.assertTrue(note_move(state, 30, 10, 30))
        self.assertTrue(note_move(state, 30, 10, 90))
        self.assertTrue(note_up(state, "left"))
        self.assertFalse(note_move(state, 40, 10, 100))


if __name__ == "__main__":
    unittest.main()
