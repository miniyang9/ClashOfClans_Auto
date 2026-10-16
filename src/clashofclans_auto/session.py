"""Write one human session as meta, events, and press screenshots."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Callable

from clashofclans_auto.pointer import (
    PointerState,
    held_buttons,
    note_down,
    note_move,
    note_up,
    to_client,
)


class SessionLog:
    def __init__(
        self,
        root: Path,
        *,
        started_at: str,
        window_title: str,
        client_width: int,
        client_height: int,
    ) -> None:
        self.root = root
        self.frames = root / "frames"
        self.events_path = root / "events.jsonl"
        self.frames.mkdir(parents=True, exist_ok=True)
        self._frame_index = 0
        self.event_count = 0
        meta = {
            "source": "human",
            "started_at": started_at,
            "window_title": window_title,
            "client_width": client_width,
            "client_height": client_height,
        }
        (root / "meta.json").write_text(
            json.dumps(meta, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    def add_frame(self, payload: bytes) -> str:
        self._frame_index += 1
        name = f"{self._frame_index:04d}.bmp"
        (self.frames / name).write_bytes(payload)
        return f"frames/{name}"

    def add_event(self, event: dict) -> None:
        line = json.dumps(event, ensure_ascii=False, separators=(",", ":"))
        with self.events_path.open("a", encoding="utf-8") as handle:
            handle.write(line + "\n")
            handle.flush()
        self.event_count += 1


def pointer_event(
    t_ms: int,
    kind: str,
    x: int,
    y: int,
    *,
    button: str | None = None,
    buttons: list[str] | None = None,
    frame: str | None = None,
) -> dict:
    event: dict = {"t_ms": t_ms, "type": kind, "x": x, "y": y}
    if button is not None:
        event["button"] = button
    if buttons is not None:
        event["buttons"] = buttons
    if frame is not None:
        event["frame"] = frame
    return event


def resize_event(t_ms: int, width: int, height: int) -> dict:
    return {"t_ms": t_ms, "type": "resize", "width": width, "height": height}


class SessionRecorder:
    """Record pointer gestures. It never sends input."""

    def __init__(
        self,
        log: SessionLog,
        *,
        origin_x: int,
        origin_y: int,
        width: int,
        height: int,
        capture: Callable[[], bytes],
        clock: Callable[[], int],
    ) -> None:
        self.log = log
        self.origin_x = origin_x
        self.origin_y = origin_y
        self.width = width
        self.height = height
        self.capture = capture
        self.clock = clock
        self.pointer = PointerState()

    def set_geometry(self, origin_x: int, origin_y: int, width: int, height: int) -> None:
        if (width, height) != (self.width, self.height):
            self.log.add_event(resize_event(self.clock(), width, height))
            self.width = width
            self.height = height
        self.origin_x = origin_x
        self.origin_y = origin_y

    def handle(self, kind: str, button: str, screen_x: int, screen_y: int) -> None:
        x, y = to_client(screen_x, screen_y, self.origin_x, self.origin_y)
        t_ms = self.clock()
        if kind == "down":
            if not note_down(self.pointer, button, x, y, self.width, self.height):
                return
            frame = self._capture_frame()
            self.log.add_event(pointer_event(t_ms, "down", x, y, button=button, frame=frame))
            return
        if kind == "move":
            if not note_move(self.pointer, x, y, t_ms):
                return
            self.log.add_event(
                pointer_event(t_ms, "move", x, y, buttons=held_buttons(self.pointer))
            )
            return
        if kind == "up" and note_up(self.pointer, button):
            self.log.add_event(pointer_event(t_ms, "up", x, y, button=button))

    def _capture_frame(self) -> str | None:
        try:
            return self.log.add_frame(self.capture())
        except OSError:
            return None
