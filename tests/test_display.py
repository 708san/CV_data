"""共通画像表示の描画・保存をローカル合成画像で確認する。"""
from __future__ import annotations

import tempfile
import unittest
import sys
import types
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

try:
    import numpy as np
    from PIL import Image
except ImportError:  # pragma: no cover - optional display dependencies
    np = None
    Image = None

from cvlesson import display, ocr, vision


@unittest.skipIf(Image is None or np is None, "display extra is required")
class DisplayTests(unittest.TestCase):
    def setUp(self):
        self.image = Image.new("RGB", (40, 30), "white")

    def test_detection_draws_and_keeps_input_unchanged(self):
        before = self.image.copy()
        result = display.render(self.image, [vision.Detection("bottle", 0.9, (3, 4, 25, 24))])
        self.assertEqual(result.size, self.image.size)
        self.assertEqual(self.image.tobytes(), before.tobytes())
        self.assertNotEqual(result.tobytes(), before.tobytes())

    def test_detection_display_can_limit_to_top_five_and_defaults_to_all(self):
        detections = [
            vision.Detection(str(index), 1.0 - index / 10, (index, 2, index + 1, 10))
            for index in range(6)
        ]
        with patch.object(display, "_draw_detection", wraps=display._draw_detection) as draw_detection:
            display.render(self.image, detections, max_detections=5)
            self.assertEqual(draw_detection.call_count, 5)
            draw_detection.reset_mock()
            display.render(self.image, detections)
            self.assertEqual(draw_detection.call_count, 6)

    def test_max_detections_rejects_invalid_value(self):
        with self.assertRaises(ValueError):
            display.render(self.image, [], max_detections=-1)

    def test_ocr_display_can_limit_lines_without_changing_result(self):
        lines = tuple(
            ocr.OCRLine(str(index), 0.5 + index / 10, ((4, 4 + index * 4), (20, 4 + index * 4), (20, 10 + index * 4), (4, 10 + index * 4)))
            for index in range(3)
        )
        result = ocr.OCRResult(lines, "fixture")
        with patch.object(display, "_draw_ocr_line", wraps=display._draw_ocr_line) as draw_line:
            display.render(self.image, result, max_ocr_lines=2)
            self.assertEqual(draw_line.call_count, 2)
        self.assertEqual(len(result.lines), 3)

    def test_max_ocr_lines_rejects_invalid_value(self):
        with self.assertRaises(ValueError):
            display.render(self.image, [], max_ocr_lines=-1)

    def test_ocr_polygon_is_drawn(self):
        line = ocr.OCRLine("text", 0.92, ((4, 4), (24, 4), (24, 15), (4, 15)))
        result = display.render(self.image, ocr.OCRResult((line,), "fixture"))
        self.assertNotEqual(result.tobytes(), self.image.tobytes())

    def test_ocr_label_moves_below_polygon_at_top_edge(self):
        polygon_box = (4.0, 4.0, 24.0, 15.0)
        label_box = display._place_label(
            polygon_box,
            (48.0, 18.0),
            (100, 80),
            [polygon_box],
            [],
        )
        self.assertGreaterEqual(label_box[1], polygon_box[3])

    def test_ocr_label_avoids_other_polygons_and_existing_labels(self):
        first = (4.0, 4.0, 24.0, 15.0)
        second = (4.0, 22.0, 24.0, 33.0)
        occupied = [(30.0, 4.0, 39.0, 22.0)]
        label_box = display._place_label(
            first,
            (20.0, 12.0),
            (80, 60),
            [first, second],
            occupied,
        )
        def overlap_area(first, second):
            return max(0.0, min(first[2], second[2]) - max(first[0], second[0])) * max(
                0.0, min(first[3], second[3]) - max(first[1], second[1])
            )

        for obstacle in [first, second, *occupied]:
            self.assertEqual(overlap_area(label_box, obstacle), 0)

    def test_segmentation_mask_is_blended(self):
        mask = np.zeros((30, 40), dtype=np.bool_)
        mask[5:20, 6:22] = True
        result = display.render(self.image, vision.Segmentation(mask, 1.2, "point", (10, 10)))
        self.assertNotEqual(result.getpixel((10, 10)), self.image.getpixel((10, 10)))
        self.assertEqual(result.getpixel((35, 25)), self.image.getpixel((35, 25)))

    def test_detected_segment_draws_box_and_mask(self):
        mask = np.zeros((30, 40), dtype=np.bool_)
        mask[8:18, 9:20] = True
        detection = vision.Detection("bottle", 0.9, (3, 4, 25, 24))
        segmentation = vision.Segmentation(mask, 0.7, "box", detection.box)
        result = display.render(self.image, [vision.DetectedSegment(detection, segmentation)])
        self.assertNotEqual(result.tobytes(), self.image.tobytes())

    def test_mask_shape_must_match_image(self):
        with self.assertRaisesRegex(display.DisplayError, "マスク形状"):
            display.render(self.image, SimpleNamespace(
                mask=np.zeros((5, 5), dtype=np.bool_), prompt_type="point"
            ))

    def test_string_mask_is_rejected(self):
        mask = np.full((30, 40), "foreground", dtype="U10")
        with self.assertRaisesRegex(display.DisplayError, "boolまたは有限な数値"):
            display.render(self.image, SimpleNamespace(mask=mask, prompt_type="point"))

    def test_non_numeric_detection_box_is_display_error(self):
        with self.assertRaisesRegex(display.DisplayError, "検出boxは数値"):
            display.render(self.image, [vision.Detection("bottle", 0.9, ("x", 4, 25, 24))])

    def test_non_numeric_ocr_polygon_is_display_error(self):
        line = ocr.OCRLine("text", 0.92, (("x", 4), (24, 4), (24, 15), (4, 15)))
        with self.assertRaisesRegex(display.DisplayError, "OCR polygonは数値"):
            display.render(self.image, ocr.OCRResult((line,), "fixture"))

    def test_save_does_not_create_parent_when_render_fails(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            destination = Path(temp_dir) / "not-created" / "overlay.png"
            with self.assertRaises(display.DisplayError):
                display.save(self.image, destination, [vision.Detection("bottle", 0.9, ("x", 4, 25, 24))])
            self.assertFalse(destination.parent.exists())

    def test_save_does_not_create_parent_when_encoding_fails(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            destination = Path(temp_dir) / "not-created" / "overlay.invalidsuffix"
            with self.assertRaises(ValueError):
                display.save(self.image, destination)
            self.assertFalse(destination.parent.exists())

    def test_save_creates_parent_and_returns_path(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            destination = Path(temp_dir) / "nested" / "overlay.png"
            returned = display.save(self.image, destination)
            self.assertEqual(returned, destination)
            self.assertTrue(destination.is_file())
            with Image.open(destination) as saved:
                self.assertEqual(saved.size, self.image.size)

    def test_font_prefers_japanize_matplotlib_font(self):
        fake_japanize = types.ModuleType("japanize_matplotlib")
        fake_japanize.get_font_ttf_path = lambda: "/fonts/japanese.ttf"
        class FontModule:
            @staticmethod
            def truetype(path, size):
                if path == "/fonts/japanese.ttf":
                    return (path, size)
                raise OSError(path)
        with patch.dict(sys.modules, {"japanize_matplotlib": fake_japanize}):
            self.assertEqual(display._font(FontModule), ("/fonts/japanese.ttf", 14))


if __name__ == "__main__":
    unittest.main()
