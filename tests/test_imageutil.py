"""Blank detection and BMP encoding."""

import unittest

from clashofclans_auto.imageutil import encode_bmp_bgr24_topdown, is_blank_bgr24


def _solid(width: int, height: int, color: tuple[int, int, int]) -> tuple[bytes, int]:
    blue, green, red = color
    stride = (width * 3 + 3) & ~3
    row = bytes((blue, green, red)) * width + b"\x00" * (stride - width * 3)
    return row * height, stride


class ImageUtilTests(unittest.TestCase):
    def test_flat_and_black_frames_are_blank(self) -> None:
        black, stride = _solid(80, 60, (0, 0, 0))
        gray, _ = _solid(80, 60, (4, 4, 4))
        self.assertTrue(is_blank_bgr24(black, 80, 60, stride))
        self.assertTrue(is_blank_bgr24(gray, 80, 60, stride))

    def test_colored_frame_is_not_blank(self) -> None:
        width, height = 80, 60
        stride = (width * 3 + 3) & ~3
        pixels = bytearray(_solid(width, height, (20, 40, 10))[0])
        pixels[0:3] = bytes((255, 220, 30))
        self.assertFalse(is_blank_bgr24(bytes(pixels), width, height, stride))

    def test_bmp_header_records_size(self) -> None:
        pixels, stride = _solid(3, 2, (10, 20, 30))
        encoded = encode_bmp_bgr24_topdown(pixels, 3, 2, stride)
        self.assertEqual(encoded[:2], b"BM")
        self.assertEqual(int.from_bytes(encoded[18:22], "little"), 3)
        self.assertEqual(int.from_bytes(encoded[22:26], "little"), 2)


if __name__ == "__main__":
    unittest.main()
