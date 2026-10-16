"""Session files written by the read-only recorder."""

import json
import tempfile
import unittest
from pathlib import Path

from clashofclans_auto.session import SessionLog, SessionRecorder


class SessionTests(unittest.TestCase):
    def test_press_drag_and_release_use_client_coordinates(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            log = SessionLog(
                root,
                started_at="2026-10-15T23:40:00-07:00",
                window_title="部落冲突 (Clash of Clans)",
                client_width=200,
                client_height=100,
            )
            frames: list[bytes] = []
            clock = {"now": 0}

            def capture() -> bytes:
                frames.append(b"bmp")
                return b"bmp-bytes"

            recorder = SessionRecorder(
                log,
                origin_x=40,
                origin_y=20,
                width=200,
                height=100,
                capture=capture,
                clock=lambda: clock["now"],
            )
            recorder.handle("move", "", 50, 30)
            recorder.handle("down", "left", 55, 40)
            clock["now"] = 10
            recorder.handle("move", "", 70, 48)
            clock["now"] = 20
            recorder.handle("move", "", 71, 48)
            clock["now"] = 80
            recorder.handle("up", "left", 90, 60)
            recorder.handle("down", "left", 10, 10)

            meta = json.loads((root / "meta.json").read_text(encoding="utf-8"))
            self.assertEqual(meta["source"], "human")
            self.assertEqual(meta["window_title"], "部落冲突 (Clash of Clans)")
            self.assertEqual(meta["client_width"], 200)
            self.assertEqual(meta["client_height"], 100)
            events = [
                json.loads(line)
                for line in (root / "events.jsonl").read_text(encoding="utf-8").splitlines()
            ]
            self.assertEqual([event["type"] for event in events], ["down", "move", "up"])
            self.assertEqual(events[0]["x"], 15)
            self.assertEqual(events[0]["y"], 20)
            self.assertEqual(events[0]["button"], "left")
            self.assertEqual(events[0]["frame"], "frames/0001.bmp")
            self.assertEqual((root / "frames" / "0001.bmp").read_bytes(), b"bmp-bytes")
            self.assertNotIn("frame", events[1])
            self.assertEqual(events[1]["buttons"], ["left"])
            self.assertNotIn("button", events[1])
            self.assertEqual(events[2]["type"], "up")
            self.assertEqual(len(frames), 1)
            self.assertTrue(all(event["type"] != "key" for event in events))

    def test_resize_is_its_own_event(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            log = SessionLog(
                root,
                started_at="2026-10-15T23:40:00-07:00",
                window_title="Clash of Clans",
                client_width=200,
                client_height=100,
            )
            recorder = SessionRecorder(
                log,
                origin_x=0,
                origin_y=0,
                width=200,
                height=100,
                capture=lambda: b"frame",
                clock=lambda: 5,
            )
            recorder.set_geometry(8, 9, 320, 180)
            recorder.handle("down", "left", 18, 19)
            events = [
                json.loads(line)
                for line in (root / "events.jsonl").read_text(encoding="utf-8").splitlines()
            ]
            self.assertEqual(events[0], {"t_ms": 5, "type": "resize", "width": 320, "height": 180})
            self.assertEqual(events[1]["x"], 10)
            self.assertEqual(events[1]["y"], 10)

    def test_failed_capture_still_records_the_press(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            log = SessionLog(
                root,
                started_at="2026-10-15T23:40:00-07:00",
                window_title="Clash of Clans",
                client_width=50,
                client_height=40,
            )

            def capture() -> bytes:
                raise OSError("capture failed")

            recorder = SessionRecorder(
                log,
                origin_x=0,
                origin_y=0,
                width=50,
                height=40,
                capture=capture,
                clock=lambda: 1,
            )
            recorder.handle("down", "left", 3, 4)
            event = json.loads((root / "events.jsonl").read_text(encoding="utf-8"))
            self.assertEqual(event["type"], "down")
            self.assertNotIn("frame", event)
            self.assertEqual(list((root / "frames").iterdir()), [])


if __name__ == "__main__":
    unittest.main()
