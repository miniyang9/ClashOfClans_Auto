"""Record mouse presses inside the official client. This does not click."""

from __future__ import annotations

import ctypes
import sys
from collections import deque
from ctypes import wintypes
from datetime import datetime
from pathlib import Path

from clashofclans_auto.imageutil import encode_bmp_bgr24_topdown
from clashofclans_auto.session import SessionLog, SessionRecorder
from clashofclans_auto.win_capture import (
    POINT,
    capture_visible_client,
    find_clash_windows,
    make_dpi_aware,
    refresh_game_window,
    user32,
)

WH_MOUSE_LL = 14
HC_ACTION = 0
WM_MOUSEMOVE = 0x0200
WM_BUTTON_DOWN = {0x0201: "left", 0x0204: "right", 0x0207: "middle"}
WM_BUTTON_UP = {0x0202: "left", 0x0205: "right", 0x0208: "middle"}

HOOKPROC = ctypes.WINFUNCTYPE(ctypes.c_ssize_t, ctypes.c_int, wintypes.WPARAM, wintypes.LPARAM)
HANDLER = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.DWORD)


class MSLLHOOKSTRUCT(ctypes.Structure):
    _fields_ = (
        ("pt", POINT),
        ("mouseData", wintypes.DWORD),
        ("flags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ctypes.c_size_t),
    )


class MSG(ctypes.Structure):
    _fields_ = (
        ("hwnd", wintypes.HWND),
        ("message", wintypes.UINT),
        ("wParam", wintypes.WPARAM),
        ("lParam", wintypes.LPARAM),
        ("time", wintypes.DWORD),
        ("pt", POINT),
    )


def _configure_hook() -> None:
    user32.SetWindowsHookExW.argtypes = [ctypes.c_int, HOOKPROC, wintypes.HINSTANCE, wintypes.DWORD]
    user32.SetWindowsHookExW.restype = wintypes.HHOOK
    user32.CallNextHookEx.argtypes = [wintypes.HHOOK, ctypes.c_int, wintypes.WPARAM, wintypes.LPARAM]
    user32.CallNextHookEx.restype = ctypes.c_ssize_t
    user32.UnhookWindowsHookEx.argtypes = [wintypes.HHOOK]
    user32.UnhookWindowsHookEx.restype = wintypes.BOOL
    user32.GetMessageW.argtypes = [ctypes.POINTER(MSG), wintypes.HWND, wintypes.UINT, wintypes.UINT]
    user32.GetMessageW.restype = ctypes.c_int
    user32.TranslateMessage.argtypes = [ctypes.POINTER(MSG)]
    user32.TranslateMessage.restype = wintypes.BOOL
    user32.DispatchMessageW.argtypes = [ctypes.POINTER(MSG)]
    user32.DispatchMessageW.restype = ctypes.c_ssize_t
    user32.PostQuitMessage.argtypes = [ctypes.c_int]
    user32.SetTimer.argtypes = [wintypes.HWND, ctypes.c_size_t, wintypes.UINT, ctypes.c_void_p]
    user32.SetTimer.restype = ctypes.c_size_t


_configure_hook()


def _missing_window() -> int:
    print("没有找到部落冲突窗口。")
    print("请在 Google Play Games 里打开 Clash of Clans，让游戏窗口停在前台，不要最小化。")
    return 2


def main(argv: list[str] | None = None, output_dir: Path | None = None) -> int:
    del argv
    make_dpi_aware()
    windows = find_clash_windows()
    if not windows:
        return _missing_window()
    window = windows[0]
    if len(windows) > 1:
        print(f"找到 {len(windows)} 个游戏窗口，记录第一个。")
    started = datetime.now().astimezone()
    destination = output_dir or Path("recordings") / started.strftime("%Y%m%dT%H%M%S")
    log = SessionLog(
        destination,
        started_at=started.isoformat(timespec="seconds"),
        window_title=window.title,
        client_width=window.client_width,
        client_height=window.client_height,
    )
    start = started.timestamp()

    def clock() -> int:
        return int((datetime.now().astimezone().timestamp() - start) * 1000)

    def capture() -> bytes:
        current = refresh_game_window(window)
        target = current or window
        frame = capture_visible_client(target)
        return encode_bmp_bgr24_topdown(frame.pixels, frame.width, frame.height, frame.stride)

    recorder = SessionRecorder(
        log,
        origin_x=window.screen_x,
        origin_y=window.screen_y,
        width=window.client_width,
        height=window.client_height,
        capture=capture,
        clock=clock,
    )
    pending: deque[tuple[str, str, int, int]] = deque()
    hook_state: dict[str, object] = {"hook": None, "alive": True}

    def enqueue(kind: str, button: str, screen_x: int, screen_y: int) -> None:
        pending.append((kind, button, screen_x, screen_y))

    def on_pointer(n_code: int, w_param: int, l_param: int) -> int:
        if n_code == HC_ACTION and hook_state["alive"]:
            try:
                info = ctypes.cast(l_param, ctypes.POINTER(MSLLHOOKSTRUCT)).contents
                message = int(w_param)
                if message == WM_MOUSEMOVE:
                    enqueue("move", "", info.pt.x, info.pt.y)
                elif message in WM_BUTTON_DOWN:
                    enqueue("down", WM_BUTTON_DOWN[message], info.pt.x, info.pt.y)
                elif message in WM_BUTTON_UP:
                    enqueue("up", WM_BUTTON_UP[message], info.pt.x, info.pt.y)
            except Exception as exc:
                print(f"记录中断: {exc}", file=sys.stderr)
                hook_state["alive"] = False
                user32.PostQuitMessage(1)
        return int(user32.CallNextHookEx(hook_state["hook"], n_code, w_param, l_param))

    callback = HOOKPROC(on_pointer)
    hook_state["callback"] = callback

    def on_console_ctrl(_ctrl_type: int) -> bool:
        user32.PostQuitMessage(0)
        return True

    ctrl_handler = HANDLER(on_console_ctrl)
    kernel32 = ctypes.windll.kernel32
    kernel32.SetConsoleCtrlHandler.argtypes = [HANDLER, wintypes.BOOL]
    kernel32.SetConsoleCtrlHandler.restype = wintypes.BOOL
    kernel32.SetConsoleCtrlHandler(ctrl_handler, True)

    hook = user32.SetWindowsHookExW(WH_MOUSE_LL, callback, None, 0)
    if not hook:
        print("无法安装鼠标监听。")
        return 1
    hook_state["hook"] = hook
    stop_flag = destination / "STOP"
    print(f"正在记录《{window.title}》。只观察，不点击。")
    print("在游戏里操作。结束时按 Ctrl+C，或创建这个文件：")
    print(stop_flag)
    user32.SetTimer(None, 1, 200, None)
    message = MSG()
    try:
        while hook_state["alive"]:
            result = user32.GetMessageW(ctypes.byref(message), None, 0, 0)
            if result == 0 or result == -1:
                break
            if stop_flag.exists():
                break
            current = refresh_game_window(window)
            if current is None:
                print("游戏窗口已关闭。")
                break
            recorder.set_geometry(
                current.screen_x,
                current.screen_y,
                current.client_width,
                current.client_height,
            )
            while pending:
                kind, button, screen_x, screen_y = pending.popleft()
                recorder.handle(kind, button, screen_x, screen_y)
            user32.TranslateMessage(ctypes.byref(message))
            user32.DispatchMessageW(ctypes.byref(message))
    finally:
        user32.UnhookWindowsHookEx(hook)
    print(f"记录结束，共 {log.event_count} 条。目录：{destination}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
