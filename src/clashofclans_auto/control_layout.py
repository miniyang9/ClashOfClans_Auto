"""Where each clickable control sits in the client area.

Boxes were measured on the 1303 by 808 session 20261016T000924, except
home.battle, which was measured on a 1828 by 1136 home-village capture.
Coordinates scale with the client size. The smallest box that contains a
point wins, so a button stays ahead of the battlefield behind it.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ControlBox:
    screen_id: str
    control_id: str
    left: int
    top: int
    right: int
    bottom: int
    ref_width: int = 1303
    ref_height: int = 808

    def contains(self, x: int, y: int, width: int, height: int) -> bool:
        x0 = self.left * width / self.ref_width
        x1 = self.right * width / self.ref_width
        y0 = self.top * height / self.ref_height
        y1 = self.bottom * height / self.ref_height
        return x0 <= x < x1 and y0 <= y < y1

    def area(self) -> int:
        return (self.right - self.left) * (self.bottom - self.top)


def _box(
    screen_id: str,
    control_id: str,
    left: int,
    top: int,
    right: int,
    bottom: int,
    ref_width: int = 1303,
    ref_height: int = 808,
) -> ControlBox:
    return ControlBox(screen_id, control_id, left, top, right, bottom, ref_width, ref_height)


_TROOP_SLOTS = ((213, 694, 299, 807), (299, 694, 385, 807))
_SPELL_SLOTS = ((394, 694, 482, 807), (482, 694, 568, 807))
_MAP = (80, 36, 1295, 689)
_LEAVE = (90, 624, 233, 677)


def _slots(screen_id: str, control_id: str, slots: tuple[tuple[int, int, int, int], ...]) -> tuple[ControlBox, ...]:
    return tuple(_box(screen_id, control_id, *slot) for slot in slots)


CONTROL_BOXES: tuple[ControlBox, ...] = (
    _box("home", "battle", 105, 963, 268, 1117, 1828, 1136),
    _box("attack_menu", "search", 150, 550, 401, 623),
    _box("attack_menu", "edit_army", 124, 750, 305, 808),
    _box("army", "attack", 1008, 646, 1231, 703),
    _box("army", "close", 1184, 150, 1237, 199),
    _box("battle_prep", "end_battle", *_LEAVE),
    _box("battle_prep", "next_opponent", 1112, 582, 1303, 639),
    *_slots("battle_prep", "troop_slot", _TROOP_SLOTS),
    *_slots("battle_prep", "spell_slot", _SPELL_SLOTS),
    _box("battle_prep", "map", *_MAP),
    _box("battle", "surrender", *_LEAVE),
    *_slots("battle", "troop_slot", _TROOP_SLOTS),
    *_slots("battle", "spell_slot", _SPELL_SLOTS),
    _box("battle", "map", *_MAP),
    _box("results", "return_home", 606, 684, 783, 749),
)


def control_at(screen_id: str, x: int, y: int, width: int, height: int) -> str | None:
    """Return the control under a client point, or none when it misses them all."""
    if width <= 0 or height <= 0:
        return None
    found: ControlBox | None = None
    for box in CONTROL_BOXES:
        if box.screen_id != screen_id or not box.contains(x, y, width, height):
            continue
        if found is None or box.area() < found.area():
            found = box
    if found is None:
        return None
    return found.control_id
