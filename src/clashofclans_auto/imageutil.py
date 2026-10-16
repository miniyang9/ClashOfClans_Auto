"""Pixel checks and BMP encoding for captured frames."""

from __future__ import annotations


def is_blank_bgr24(data: bytes, width: int, height: int, stride: int) -> bool:
    """Return true when sampled pixels are almost a single dark or flat color."""
    if width <= 0 or height <= 0 or stride < width * 3:
        return True
    if len(data) < stride * height:
        return True
    step_y = max(1, height // 40)
    step_x = max(1, width // 40)
    samples: list[int] = []
    for y in range(0, height, step_y):
        row = y * stride
        for x in range(0, width, step_x):
            index = row + x * 3
            blue, green, red = data[index], data[index + 1], data[index + 2]
            samples.append((red + green + blue) // 3)
    if not samples:
        return True
    return max(samples) - min(samples) <= 8


def encode_bmp_bgr24_topdown(data: bytes, width: int, height: int, stride: int) -> bytes:
    """Encode top-down BGR24 pixels as a 24-bit BMP."""
    if width <= 0 or height <= 0 or stride < width * 3:
        raise ValueError("invalid image size")
    if len(data) < stride * height:
        raise ValueError("pixel buffer is shorter than the image")
    row_stride = (width * 3 + 3) & ~3
    padding = b"\x00" * (row_stride - width * 3)
    rows = bytearray()
    for y in range(height - 1, -1, -1):
        start = y * stride
        rows += data[start : start + width * 3] + padding
    pixel_size = len(rows)
    header_size = 14 + 40
    file_size = header_size + pixel_size
    header = bytearray(header_size)
    header[0:2] = b"BM"
    header[2:6] = file_size.to_bytes(4, "little")
    header[10:14] = header_size.to_bytes(4, "little")
    header[14:18] = (40).to_bytes(4, "little")
    header[18:22] = width.to_bytes(4, "little", signed=True)
    header[22:26] = height.to_bytes(4, "little", signed=True)
    header[26:28] = (1).to_bytes(2, "little")
    header[28:30] = (24).to_bytes(2, "little")
    header[34:38] = pixel_size.to_bytes(4, "little")
    return bytes(header) + bytes(rows)
