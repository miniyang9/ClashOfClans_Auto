"""Turn screen points into client coordinates and decide which ones to keep."""

from __future__ import annotations

from dataclasses import dataclass, field


def to_client(screen_x: int, screen_y: int, origin_x: int, origin_y: int) -> tuple[int, int]:
    """Convert a screen point to coordinates inside the window client area."""
    return screen_x - origin_x, screen_y - origin_y


def inside_client(x: int, y: int, width: int, height: int) -> bool:
    return 0 <= x < width and 0 <= y < height


def should_sample_move(
    last_ms: int | None,
    now_ms: int,
    last_xy: tuple[int, int] | None,
    xy: tuple[int, int],
    *,
    min_ms: int = 50,
    min_px: int = 8,
) -> bool:
    """Sample a drag often enough to see its shape, and skip the points in between."""
    if last_ms is None or last_xy is None:
        return True
    if now_ms - last_ms >= min_ms:
        return True
    dx = xy[0] - last_xy[0]
    dy = xy[1] - last_xy[1]
    return dx * dx + dy * dy >= min_px * min_px


@dataclass
class PointerState:
    held: dict[str, bool] = field(default_factory=dict)
    last_move_ms: int | None = None
    last_xy: tuple[int, int] | None = None


def note_down(state: PointerState, button: str, x: int, y: int, width: int, height: int) -> bool:
    """Start a gesture when the press lands inside the client area."""
    inside = inside_client(x, y, width, height)
    state.held[button] = inside
    return inside


def note_move(state: PointerState, x: int, y: int, now_ms: int) -> bool:
    """Keep a drag sample only while a recorded press is still down."""
    if not any(state.held.values()):
        return False
    xy = (x, y)
    if not should_sample_move(state.last_move_ms, now_ms, state.last_xy, xy):
        return False
    state.last_move_ms = now_ms
    state.last_xy = xy
    return True


def note_up(state: PointerState, button: str) -> bool:
    """Finish a gesture that began inside the client area."""
    recording = state.held.pop(button, False)
    if not any(state.held.values()):
        state.last_move_ms = None
        state.last_xy = None
    return recording


def held_buttons(state: PointerState) -> list[str]:
    return sorted(name for name, down in state.held.items() if down)
