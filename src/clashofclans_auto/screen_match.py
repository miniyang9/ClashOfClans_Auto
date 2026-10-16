"""Tell which screen a client frame shows.

Recognition uses the stable buttons in control_layout. The slot bar is ignored,
because reinforcements and heroes move those cards. A frame that matches none
of the screens, or more than one, is unknown and the caller stops.
"""

from __future__ import annotations

import math

from clashofclans_auto.control_layout import CONTROL_BOXES, ControlBox

# Measured on the recorded sessions. Real buttons stayed above these lines.
# The same regions on the other screens stayed under 0.05, apart from a
# pressed 放弃 button whose red coverage fell to about 0.28.
_YELLOW = 0.40
_GREEN = 0.18
_RED = 0.15


def _box(screen_id: str, control_id: str) -> ControlBox:
    for box in CONTROL_BOXES:
        if box.screen_id == screen_id and box.control_id == control_id:
            return box
    raise RuntimeError(f"missing box for {screen_id}.{control_id}")


_HOME_BATTLE = _box("home", "battle")
_SEARCH = _box("attack_menu", "search")
_EDIT_ARMY = _box("attack_menu", "edit_army")
_ATTACK = _box("army", "attack")
_CLOSE = _box("army", "close")
_LEAVE = _box("battle_prep", "end_battle")
_NEXT = _box("battle_prep", "next_opponent")
_RETURN = _box("results", "return_home")


def _yellow(rgb: tuple[int, int, int]) -> bool:
    red, green, blue = rgb
    return red > 190 and green > 150 and blue < 80 and (red + green) > blue * 4


def _green(rgb: tuple[int, int, int]) -> bool:
    red, green, blue = rgb
    return green > 150 and green > red + 40 and green > blue + 40 and red < 160


def _red(rgb: tuple[int, int, int]) -> bool:
    red, green, blue = rgb
    return red > 170 and red > green + 60 and red > blue + 60 and green < 110


def _ratio(
    box: ControlBox,
    data: bytes,
    width: int,
    height: int,
    stride: int,
    predicate,
) -> float:
    x0 = max(0, math.floor(box.left * width / box.ref_width))
    x1 = min(width, math.ceil(box.right * width / box.ref_width))
    y0 = max(0, math.floor(box.top * height / box.ref_height))
    y1 = min(height, math.ceil(box.bottom * height / box.ref_height))
    matched = 0
    total = 0
    for y in range(y0, y1):
        row = y * stride
        for x in range(x0, x1):
            if not box.contains(x, y, width, height):
                continue
            total += 1
            index = row + x * 3
            blue, green, red = data[index], data[index + 1], data[index + 2]
            if predicate((red, green, blue)):
                matched += 1
    if total == 0:
        return 0.0
    return matched / total


def match_screen(data: bytes, width: int, height: int, stride: int) -> str | None:
    """Return the screen id, or none when the frame is not one clear screen.

    Pixels are top-down BGR24, the same layout as a captured client frame.
    结束战斗 and 放弃 share one rectangle; 下一个 separates preparation from the fight.
    """
    if width <= 0 or height <= 0 or stride < width * 3:
        return None
    if len(data) < stride * height:
        return None

    matched: list[str] = []
    if _ratio(_HOME_BATTLE, data, width, height, stride, _yellow) >= _YELLOW:
        matched.append("home")
    if (
        _ratio(_SEARCH, data, width, height, stride, _yellow) >= _YELLOW
        and _ratio(_EDIT_ARMY, data, width, height, stride, _green) >= _GREEN
    ):
        matched.append("attack_menu")
    if (
        _ratio(_ATTACK, data, width, height, stride, _green) >= _GREEN
        and _ratio(_CLOSE, data, width, height, stride, _red) >= _RED
    ):
        matched.append("army")
    leave = _ratio(_LEAVE, data, width, height, stride, _red)
    nxt = _ratio(_NEXT, data, width, height, stride, _yellow)
    if leave >= _RED and nxt >= _YELLOW:
        matched.append("battle_prep")
    elif leave >= _RED:
        matched.append("battle")
    if _ratio(_RETURN, data, width, height, stride, _green) >= _GREEN:
        matched.append("results")
    if len(matched) != 1:
        return None
    return matched[0]
