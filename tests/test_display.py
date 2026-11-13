"""共通画像表示の描画・保存をローカル合成画像で確認する。"""
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

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

    def test_ocr_polygon_is_drawn(self):
        line = ocr.OCRLine("text", 0.92, ((4, 4), (24, 4), (24, 15), (4, 15)))
        result = display.render(self.image, ocr.OCRResult((line,), "fixture"))
        self.assertNotEqual(result.tobytes(), self.image.tobytes())

    def test_ocr_can_draw_boxes_without_overlapping_text_labels(self):
        line = ocr.OCRLine("text", 0.92, ((4, 4), (24, 4), (24, 15), (4, 15)))
        with_boxes = display.render(self.image, ocr.OCRResult((line,), "fixture"), show_labels=False)
        self.assertNotEqual(with_boxes.tobytes(), self.image.tobytes())
        with self.assertRaisesRegex(ValueError, "show_labels"):
            display.render(self.image, None, show_labels=1)

    def test_ocr_report_shows_readable_text_confidence_and_collapsed_crop(self):
        line = ocr.OCRLine("<script>alert(1)</script>", 0.925, ((4, 4), (24, 4), (24, 15), (4, 15)))
        result = ocr.OCRResult((line,), "fixture")
        original = result.to_dict()
        report = display.render_ocr_report(self.image, result)
        self.assertIn("&lt;script&gt;alert(1)&lt;/script&gt;", report)
        self.assertNotIn("<script>alert(1)</script>", report)
        self.assertIn("信頼度の目安: 92.5%", report)
        self.assertIn("<details><summary>画像の該当部分を見る</summary>", report)
        self.assertIn("data:image/png;base64,", report)
        self.assertEqual(result.to_dict(), original)

    def test_ocr_report_handles_empty_result_and_invalid_polygon(self):
        empty = display.render_ocr_report(self.image, ocr.OCRResult((), "fixture"))
        self.assertIn("文字を検出できませんでした。", empty)
        line = ocr.OCRLine("位置なし", 0.4, ())
        report = display.render_ocr_report(self.image, ocr.OCRResult((line,), "fixture"))
        self.assertIn("位置情報はありません", report)
        self.assertNotIn("data:image/png;base64,", report)

    def test_ocr_report_rejects_invalid_crop_padding(self):
        result = ocr.OCRResult((), "fixture")
        for padding in (-1, True, 1.5):
            with self.subTest(padding=padding), self.assertRaisesRegex(ValueError, "crop_padding"):
                display.render_ocr_report(self.image, result, crop_padding=padding)
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

    def test_save_creates_parent_and_returns_path(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            destination = Path(temp_dir) / "nested" / "overlay.png"
            returned = display.save(self.image, destination)
            self.assertEqual(returned, destination)
            self.assertTrue(destination.is_file())
            with Image.open(destination) as saved:
                self.assertEqual(saved.size, self.image.size)


if __name__ == "__main__":
    unittest.main()
