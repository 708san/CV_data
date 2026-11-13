"""vision APIの入力検証と推論結果変換をモデル取得なしで確認する。"""
from __future__ import annotations

import unittest
import sys
from types import SimpleNamespace
from unittest.mock import patch

from cvlesson import vision


class _Tensor:
    def __init__(self, values):
        self.values = values

    def to(self, device):
        return self

    def cpu(self):
        return self

    def tolist(self):
        return self.values

    def __float__(self):
        return float(self.values)

    def __int__(self):
        return int(self.values)


class _Context:
    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False


class _Torch:
    @staticmethod
    def no_grad():
        return _Context()


class _CallableModel:
    config = SimpleNamespace(id2label={1: "bicycle"})

    def __call__(self, **kwargs):
        return "outputs"


class VisionTests(unittest.TestCase):
    def test_defaults_are_pinned_and_cpu(self):
        self.assertEqual(vision._DETECTOR_REVISION, "557a3b6fcdb1be415f074c22da2e16ab4f7e8265")
        self.assertEqual(vision._SEGMENTER_REVISION, "70c1a07f894ebb5b307fd9eaaee97b9dfc16068f")
        self.assertEqual(vision._load_kwargs(None, False), {"local_files_only": False})

    def test_custom_models_require_a_full_commit_revision(self):
        default = vision._resolve_model(None, None, "default/model", "a" * 40)
        self.assertEqual(default, ("default/model", "a" * 40))
        self.assertEqual(
            vision._resolve_model("custom/model", "B" * 40, "default/model", "a" * 40),
            ("custom/model", "b" * 40),
        )
        for model_id, revision in (("custom/model", None), ("custom/model", "main"), (None, "b" * 40)):
            with self.subTest(revision=revision), self.assertRaises(ValueError):
                vision._resolve_model(model_id, revision, "default/model", "a" * 40)

    def test_detector_load_passes_fixed_id_and_revision_to_both_components(self):
        calls = []

        class Loader:
            @classmethod
            def from_pretrained(cls, model_id, **kwargs):
                calls.append((cls.__name__, model_id, kwargs["revision"]))
                if cls.__name__ == "AutoModelForObjectDetection":
                    return SimpleNamespace(to=lambda device: None, eval=lambda: None)
                return object()

        processor_loader = type("AutoImageProcessor", (Loader,), {})
        model_loader = type("AutoModelForObjectDetection", (Loader,), {})
        fake_transformers = SimpleNamespace(
            AutoImageProcessor=processor_loader,
            AutoModelForObjectDetection=model_loader,
        )
        with patch("cvlesson.vision._check_device", return_value=_Torch):
            with patch.dict(sys.modules, {"transformers": fake_transformers}):
                vision.load_detector(local_files_only=True)
        self.assertEqual(
            calls,
            [
                ("AutoImageProcessor", vision._DETECTOR_ID, vision._DETECTOR_REVISION),
                ("AutoModelForObjectDetection", vision._DETECTOR_ID, vision._DETECTOR_REVISION),
            ],
        )

    def test_detection_converts_output_to_common_types(self):
        class Processor:
            def __call__(self, **kwargs):
                return {"pixel_values": "input"}

            def post_process_object_detection(self, outputs, **kwargs):
                self.kwargs = kwargs
                return [{
                    "boxes": [_Tensor([1.25, 2, 21, 30])],
                    "scores": [_Tensor(0.91)],
                    "labels": [_Tensor(1)],
                }]

        processor = Processor()
        detector = vision.ObjectDetector(processor, _CallableModel(), _Torch, "cpu")
        with patch("cvlesson.vision._open_image", return_value=SimpleNamespace(size=(40, 50))):
            predictions = detector.predict("ignored.jpg", threshold=0.4)
        self.assertEqual(predictions, [vision.Detection("bicycle", 0.91, (1.25, 2.0, 21.0, 30.0))])
        self.assertEqual(processor.kwargs, {"threshold": 0.4, "target_sizes": [(50, 40)]})

    def test_sam_selects_highest_scoring_mask_and_keeps_shape(self):
        class CandidateMask:
            def __init__(self, rows):
                self.rows = rows

            def numpy(self):
                return self

            def astype(self, dtype, copy=False):
                return [[bool(value) for value in row] for row in self.rows]

        class Processor:
            image_processor = SimpleNamespace(
                post_process_masks=lambda masks, original_sizes, reshaped_input_sizes: [[[
                    CandidateMask([[0, 1], [0, 0]]), CandidateMask([[1, 1], [1, 0]])
                ]]]
            )

            def __call__(self, **kwargs):
                return {
                    "original_sizes": SimpleNamespace(cpu=lambda: "original"),
                    "reshaped_input_sizes": SimpleNamespace(cpu=lambda: "resized"),
                }

        class Scores:
            def __getitem__(self, index):
                return self if index in (0, 1) else IndexError(index)

            def argmax(self):
                return SimpleNamespace(item=lambda: 1)

            def item(self):
                # SAMの品質ヘッドは0〜1に制限された確率とは限らない。
                return 1.2

        class Numpy:
            bool_ = bool

        processor = Processor()
        class Model:
            def __call__(self, **kwargs):
                return SimpleNamespace(pred_masks=SimpleNamespace(cpu=lambda: "masks"), iou_scores=Scores())

        model = Model()
        segmenter = vision.PromptSegmenter(processor, model, _Torch, Numpy, "cpu")
        with patch("cvlesson.vision._open_image", return_value=SimpleNamespace(size=(20, 20))):
            result = segmenter.predict("ignored.jpg", box=(1, 2, 10, 15))
        self.assertEqual(result.prompt_type, "box")
        self.assertEqual(result.score, 1.2)
        self.assertEqual(result.mask, [[True, True], [True, False]])

    def test_prompts_are_validated_before_model_call(self):
        segmenter = vision.PromptSegmenter(None, None, None, None, "cpu")
        with patch("cvlesson.vision._open_image", return_value=SimpleNamespace(size=(10, 8))):
            with self.assertRaisesRegex(ValueError, "どちらか一方"):
                segmenter.predict("ignored.jpg")
            with self.assertRaisesRegex(ValueError, "画像範囲内"):
                segmenter.predict("ignored.jpg", box=(5, 1, 3, 4))
            with self.assertRaisesRegex(ValueError, "画像範囲内"):
                segmenter.predict("ignored.jpg", point=(10, 2))

    def test_detection_score_threshold_is_validated(self):
        detector = vision.ObjectDetector(None, None, None, "cpu")
        with self.assertRaisesRegex(ValueError, "0から1"):
            detector.predict("missing.jpg", threshold=1.1)

    def test_unavailable_gpu_is_rejected_before_model_import(self):
        fake_torch = SimpleNamespace(
            cuda=SimpleNamespace(is_available=lambda: False, device_count=lambda: 0),
            backends=SimpleNamespace(mps=SimpleNamespace(is_available=lambda: False)),
        )
        with patch("cvlesson.vision._import_torch", return_value=fake_torch):
            with self.assertRaisesRegex(vision.VisionError, "利用できません"):
                vision._check_device("cuda:0")


if __name__ == "__main__":
    unittest.main()
