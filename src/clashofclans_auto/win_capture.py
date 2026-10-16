"""Find the game window and copy its visible client area."""

from __future__ import annotations

import ctypes
from ctypes import wintypes
from dataclasses import dataclass

from clashofclans_auto.titles import is_clash_window_title

user32 = ctypes.windll.user32
gdi32 = ctypes.windll.gdi32

SRCCOPY = 0x00CC0020
DIB_RGB_COLORS = 0
BI_RGB = 0
PW_RENDERFULLCONTENT = 2


def _configure_win32() -> None:
    """Use pointer-sized handles. The defaults truncate them on 64-bit Windows."""
    user32.EnumWindows.argtypes = [
        ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM),
        wintypes.LPARAM,
    ]
    user32.EnumWindows.restype = wintypes.BOOL
    user32.IsWindow.argtypes = [wintypes.HWND]
    user32.IsWindow.restype = wintypes.BOOL
    user32.IsWindowVisible.argtypes = [wintypes.HWND]
    user32.IsWindowVisible.restype = wintypes.BOOL
    user32.GetWindowTextLengthW.argtypes = [wintypes.HWND]
    user32.GetWindowTextLengthW.restype = ctypes.c_int
    user32.GetWindowTextW.argtypes = [wintypes.HWND, wintypes.LPWSTR, ctypes.c_int]
    user32.GetWindowTextW.restype = ctypes.c_int
    user32.GetClientRect.argtypes = [wintypes.HWND, ctypes.POINTER(RECT)]
    user32.GetClientRect.restype = wintypes.BOOL
    user32.ClientToScreen.argtypes = [wintypes.HWND, ctypes.POINTER(POINT)]
    user32.ClientToScreen.restype = wintypes.BOOL
    user32.GetDC.argtypes = [wintypes.HWND]
    user32.GetDC.restype = wintypes.HDC
    user32.GetWindowDC.argtypes = [wintypes.HWND]
    user32.GetWindowDC.restype = wintypes.HDC
    user32.ReleaseDC.argtypes = [wintypes.HWND, wintypes.HDC]
    user32.ReleaseDC.restype = ctypes.c_int
    user32.PrintWindow.argtypes = [wintypes.HWND, wintypes.HDC, wintypes.UINT]
    user32.PrintWindow.restype = wintypes.BOOL
    user32.SetProcessDPIAware.argtypes = []
    user32.SetProcessDPIAware.restype = wintypes.BOOL
    gdi32.CreateCompatibleDC.argtypes = [wintypes.HDC]
    gdi32.CreateCompatibleDC.restype = wintypes.HDC
    gdi32.CreateCompatibleBitmap.argtypes = [wintypes.HDC, ctypes.c_int, ctypes.c_int]
    gdi32.CreateCompatibleBitmap.restype = wintypes.HBITMAP
    gdi32.SelectObject.argtypes = [wintypes.HDC, wintypes.HGDIOBJ]
    gdi32.SelectObject.restype = wintypes.HGDIOBJ
    gdi32.DeleteObject.argtypes = [wintypes.HGDIOBJ]
    gdi32.DeleteObject.restype = wintypes.BOOL
    gdi32.DeleteDC.argtypes = [wintypes.HDC]
    gdi32.DeleteDC.restype = wintypes.BOOL
    gdi32.BitBlt.argtypes = [
        wintypes.HDC,
        ctypes.c_int,
        ctypes.c_int,
        ctypes.c_int,
        ctypes.c_int,
        wintypes.HDC,
        ctypes.c_int,
        ctypes.c_int,
        wintypes.DWORD,
    ]
    gdi32.BitBlt.restype = wintypes.BOOL
    gdi32.GetDIBits.argtypes = [
        wintypes.HDC,
        wintypes.HBITMAP,
        wintypes.UINT,
        wintypes.UINT,
        ctypes.c_void_p,
        ctypes.c_void_p,
        wintypes.UINT,
    ]
    gdi32.GetDIBits.restype = ctypes.c_int


class RECT(ctypes.Structure):
    _fields_ = (
        ("left", wintypes.LONG),
        ("top", wintypes.LONG),
        ("right", wintypes.LONG),
        ("bottom", wintypes.LONG),
    )


class POINT(ctypes.Structure):
    _fields_ = (("x", wintypes.LONG), ("y", wintypes.LONG))


class BITMAPINFOHEADER(ctypes.Structure):
    _fields_ = (
        ("biSize", wintypes.DWORD),
        ("biWidth", wintypes.LONG),
        ("biHeight", wintypes.LONG),
        ("biPlanes", wintypes.WORD),
        ("biBitCount", wintypes.WORD),
        ("biCompression", wintypes.DWORD),
        ("biSizeImage", wintypes.DWORD),
        ("biXPelsPerMeter", wintypes.LONG),
        ("biYPelsPerMeter", wintypes.LONG),
        ("biClrUsed", wintypes.DWORD),
        ("biClrImportant", wintypes.DWORD),
    )


_configure_win32()


@dataclass(frozen=True)
class GameWindow:
    hwnd: int
    title: str
    client_width: int
    client_height: int
    screen_x: int
    screen_y: int


@dataclass(frozen=True)
class CapturedFrame:
    width: int
    height: int
    stride: int
    pixels: bytes


def make_dpi_aware() -> None:
    """Use physical pixels so the client rectangle matches the capture."""
    try:
        shcore = ctypes.windll.shcore
        shcore.SetProcessDpiAwareness.argtypes = [ctypes.c_int]
        shcore.SetProcessDpiAwareness.restype = ctypes.HRESULT
        shcore.SetProcessDpiAwareness(2)
    except (AttributeError, OSError):
        user32.SetProcessDPIAware()


def _client_origin(hwnd: int) -> tuple[int, int, int, int]:
    rect = RECT()
    if not user32.GetClientRect(hwnd, ctypes.byref(rect)):
        raise OSError(f"GetClientRect failed for hwnd {hwnd}")
    origin = POINT(0, 0)
    if not user32.ClientToScreen(hwnd, ctypes.byref(origin)):
        raise OSError(f"ClientToScreen failed for hwnd {hwnd}")
    width = rect.right - rect.left
    height = rect.bottom - rect.top
    return origin.x, origin.y, width, height


def visible_window_titles() -> list[tuple[int, str]]:
    found: list[tuple[int, str]] = []

    @ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
    def visit(hwnd: int, _lparam: int) -> bool:
        if not user32.IsWindowVisible(hwnd):
            return True
        length = user32.GetWindowTextLengthW(hwnd)
        if length <= 0:
            return True
        buffer = ctypes.create_unicode_buffer(length + 1)
        user32.GetWindowTextW(hwnd, buffer, length + 1)
        found.append((int(hwnd), buffer.value))
        return True

    if not user32.EnumWindows(visit, 0):
        raise OSError("EnumWindows failed")
    return found


def find_clash_windows() -> list[GameWindow]:
    matches: list[GameWindow] = []
    for hwnd, title in visible_window_titles():
        if not is_clash_window_title(title):
            continue
        screen_x, screen_y, width, height = _client_origin(hwnd)
        if width < 200 or height < 200:
            continue
        matches.append(
            GameWindow(
                hwnd=hwnd,
                title=title,
                client_width=width,
                client_height=height,
                screen_x=screen_x,
                screen_y=screen_y,
            )
        )
    return matches


def refresh_game_window(window: GameWindow) -> GameWindow | None:
    """Return the window's current client area, or none when it is gone."""
    if not user32.IsWindow(window.hwnd) or not user32.IsWindowVisible(window.hwnd):
        return None
    try:
        screen_x, screen_y, width, height = _client_origin(window.hwnd)
    except OSError:
        return None
    if width < 200 or height < 200:
        return None
    return GameWindow(
        hwnd=window.hwnd,
        title=window.title,
        client_width=width,
        client_height=height,
        screen_x=screen_x,
        screen_y=screen_y,
    )


def _copy_dib(hdc_source: int, width: int, height: int, blit) -> CapturedFrame:
    memory_dc = gdi32.CreateCompatibleDC(hdc_source)
    if not memory_dc:
        raise OSError("CreateCompatibleDC failed")
    bitmap = gdi32.CreateCompatibleBitmap(hdc_source, width, height)
    if not bitmap:
        gdi32.DeleteDC(memory_dc)
        raise OSError("CreateCompatibleBitmap failed")
    previous = gdi32.SelectObject(memory_dc, bitmap)
    try:
        if not blit(memory_dc):
            raise OSError("copy into memory DC failed")
        stride = (width * 3 + 3) & ~3
        info = BITMAPINFOHEADER()
        info.biSize = ctypes.sizeof(BITMAPINFOHEADER)
        info.biWidth = width
        info.biHeight = -height
        info.biPlanes = 1
        info.biBitCount = 24
        info.biCompression = BI_RGB
        info.biSizeImage = stride * height
        buffer = ctypes.create_string_buffer(info.biSizeImage)
        rows = gdi32.GetDIBits(
            memory_dc,
            bitmap,
            0,
            height,
            buffer,
            ctypes.byref(info),
            DIB_RGB_COLORS,
        )
        if rows == 0:
            raise OSError("GetDIBits failed")
        return CapturedFrame(width=width, height=height, stride=stride, pixels=buffer.raw)
    finally:
        gdi32.SelectObject(memory_dc, previous)
        gdi32.DeleteObject(bitmap)
        gdi32.DeleteDC(memory_dc)


def capture_visible_client(window: GameWindow) -> CapturedFrame:
    """Copy the pixels currently shown on screen for the client area."""
    desktop = user32.GetDC(0)
    if not desktop:
        raise OSError("GetDC failed")
    try:
        def blit(memory_dc: int) -> bool:
            return bool(
                gdi32.BitBlt(
                    memory_dc,
                    0,
                    0,
                    window.client_width,
                    window.client_height,
                    desktop,
                    window.screen_x,
                    window.screen_y,
                    SRCCOPY,
                )
            )

        return _copy_dib(desktop, window.client_width, window.client_height, blit)
    finally:
        user32.ReleaseDC(0, desktop)


def capture_print_window(window: GameWindow) -> CapturedFrame:
    """Ask the window to paint itself, including some GPU-backed clients."""
    window_dc = user32.GetWindowDC(window.hwnd)
    if not window_dc:
        raise OSError("GetWindowDC failed")
    try:
        def blit(memory_dc: int) -> bool:
            return bool(user32.PrintWindow(window.hwnd, memory_dc, PW_RENDERFULLCONTENT))

        return _copy_dib(window_dc, window.client_width, window.client_height, blit)
    finally:
        user32.ReleaseDC(window.hwnd, window_dc)
