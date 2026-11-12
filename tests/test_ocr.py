"""OCR APIの標準ライブラリ範囲テスト。モデルや実行基盤は取得しない。"""
from __future__ import annotations

import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest.mock import patch

from cvlesson import ocr


class _FakePaddle:
    @staticmethod
    def is_compiled_with_cuda():
        return False

    class device:
        class cuda:
            @staticmethod
            def device_count():
                return 0


class OCRTests(unittest.TestCase):
    def test_parse_backend_result_to_common_lines(self):
        backend_result = types.SimpleNamespace(json={"res": {
            "rec_texts": ["  合計 1,200円 ", "", "部活動費"],
            "rec_scores": [0.97, 0.8, 1.2],
            "rec_polys": [
                [[1, 2], [11, 2], [11, 8], [1, 8]],
                [[0, 0], [1, 0], [1, 1], [0, 1]],
                [[2, 3], [12, 3], [12, 9], [2, 9]],
            ],
        }})
        lines = ocr._parse_result(backend_result)
        self.assertEqual([line.text for line in lines], ["合計 1,200円", "部活動費"])
        self.assertEqual(lines[0].confidence, 0.97)
        self.assertEqual(lines[1].confidence, 1.0)
        self.assertEqual(lines[0].polygon[0], (1.0, 2.0))

    def test_predict_uses_local_image_and_returns_joined_text(self):
        class Pipeline:
            def predict(self, *, input):
                self.image_path = input
                return [{"res": {
                    "rec_texts": ["行1", "行2"],
                    "rec_scores": [0.9, 0.8],
                    "rec_polys": [],
                }}]

        with tempfile.TemporaryDirectory() as temp_dir:
            image = Path(temp_dir) / "sample.jpg"
            image.write_bytes(b"placeholder")
            pipeline = Pipeline()
            result = ocr.OCR(pipeline, device="cpu", language="japan").predict(image)
        self.assertEqual(result.text, "行1\n行2")
        self.assertEqual(pipeline.image_path, str(image))
        self.assertEqual(len(result.lines[0].polygon), 0)
        self.assertEqual(result.to_dict()["lines"][1]["text"], "行2")

    def test_predict_rejects_missing_image(self):
        reader = ocr.OCR(object(), device="cpu", language="japan")
        with self.assertRaises(FileNotFoundError):
            reader.predict("does-not-exist.png")

    def test_load_uses_fixed_revisions_and_cpu_by_default(self):
        calls = []

        class FakePipeline:
            def __init__(self, **kwargs):
                self.kwargs = kwargs
                calls.append(kwargs)

        def snapshot_download(**kwargs):
            calls.append(kwargs)
            return "/cached/model"

        paddleocr_module = types.ModuleType("paddleocr")
        paddleocr_module.PaddleOCR = FakePipeline
        hub_module = types.ModuleType("huggingface_hub")
        hub_module.snapshot_download = snapshot_download
        with patch.object(ocr, "_import_paddle", return_value=_FakePaddle), patch.dict(
            sys.modules,
            {"paddleocr": paddleocr_module, "huggingface_hub": hub_module},
        ):
            reader = ocr.load()

        self.assertEqual(reader.device, "cpu")
        self.assertEqual(calls[0]["repo_id"], ocr._DETECTION_REPO)
        self.assertEqual(calls[0]["revision"], ocr._DETECTION_REVISION)
        self.assertEqual(calls[1]["repo_id"], ocr._RECOGNITION_REPO)
        self.assertEqual(calls[1]["revision"], ocr._RECOGNITION_REVISION)
        self.assertEqual(calls[2]["ocr_version"], "PP-OCRv5")
        self.assertEqual(calls[2]["lang"], "japan")
        self.assertEqual(calls[2]["device"], "cpu")
        self.assertEqual(calls[2]["text_detection_model_dir"], "/cached/model")

    def test_load_refuses_gpu_before_model_download_when_unavailable(self):
        with patch.object(ocr, "_import_paddle", return_value=_FakePaddle):
            with self.assertRaisesRegex(ocr.OCRError, "利用できません"):
                ocr.load(device="gpu:0")

    def test_custom_models_must_be_local_and_provided_as_a_pair(self):
        with self.assertRaisesRegex(ValueError, "両方"):
            ocr.load(detection_model_dir="./detector")


if __name__ == "__main__":
    unittest.main()
