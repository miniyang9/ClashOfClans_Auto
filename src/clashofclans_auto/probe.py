"""Capture the official client once and report whether the picture is real."""

from __future__ import annotations

import sys
from pathlib import Path

from clashofclans_auto.imageutil import encode_bmp_bgr24_topdown, is_blank_bgr24
from clashofclans_auto.win_capture import (
    capture_print_window,
    capture_visible_client,
    find_clash_windows,
    make_dpi_aware,
)


def main(argv: list[str] | None = None, output_dir: Path | None = None) -> int:
    del argv
    make_dpi_aware()
    windows = find_clash_windows()
    if not windows:
        print("没有找到部落冲突窗口。")
        print("请在 Google Play Games 里打开 Clash of Clans，让游戏窗口停在前台，不要最小化。")
        return 2
    destination = output_dir or Path("recordings") / "probe"
    destination.mkdir(parents=True, exist_ok=True)
    saw_content = False
    for index, window in enumerate(windows):
        print(
            f"窗口 {window.hwnd} 《{window.title}》"
            f" 客户区 {window.client_width}x{window.client_height}"
            f" 屏幕位置 {window.screen_x},{window.screen_y}"
        )
        for name, capture in (
            ("screen", capture_visible_client),
            ("printwindow", capture_print_window),
        ):
            frame = capture(window)
            blank = is_blank_bgr24(frame.pixels, frame.width, frame.height, frame.stride)
            path = destination / f"window-{index}-{name}.bmp"
            path.write_bytes(
                encode_bmp_bgr24_topdown(frame.pixels, frame.width, frame.height, frame.stride)
            )
            state = "几乎没有内容" if blank else "有画面内容"
            print(f"  {name}: {state} -> {path}")
            saw_content = saw_content or not blank
    if not saw_content:
        print("窗口找到了，但两种截法都没有拿到可见内容。")
        return 3
    return 0


if __name__ == "__main__":
    sys.exit(main())
