"""ResNet APIの入力検証と任意依存の案内を確認する。"""
from __future__ import annotations

import importlib.util
import math
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from cvlesson import models


class ResNetEstimatorTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.image = Path(self.temp.name) / "sample.jpg"
        self.image.write_bytes(b"placeholder")

    def test_constructor_does_not_import_or_download_model(self):
        estimator = models.ResNetClassifier()
        self.assertEqual(estimator.device, "cpu")
        self.assertEqual(estimator.epochs, 5)
        self.assertFalse(estimator.is_fitted_)

    def test_invalid_training_inputs_fail_before_loading_torch(self):
        classifier = models.ResNetClassifier()
        with self.assertRaisesRegex(ValueError, "2種類以上"):
            classifier.fit([self.image], ["healthy"])
        with self.assertRaisesRegex(ValueError, "画像数とy"):
            classifier.fit([self.image, self.image], ["healthy"])

        regressor = models.ResNetRegressor()
        with self.assertRaisesRegex(ValueError, "有限の数値"):
            regressor.fit([self.image], [float("nan")])

    def test_predict_before_fit_has_actionable_message(self):
        with self.assertRaisesRegex(models.ModelError, "先にfit"):
            models.ResNetClassifier().predict([self.image])

    def test_predict_proba_converts_logits_to_tensor_and_normalizes_rows(self):
        class FakeTensor:
            def __init__(self, values):
                self.values = values

            def numpy(self):
                return self.values

        class FakeTorch:
            def as_tensor(self, values):
                self.input = values
                return FakeTensor(values)

            def softmax(self, tensor, dim):
                if not isinstance(tensor, FakeTensor):
                    raise TypeError("softmax input must be a Tensor")
                if dim != 1:
                    raise AssertionError("softmaxはクラス軸(dim=1)へ適用してください")
                probabilities = []
                for row in tensor.values:
                    peak = max(row)
                    exponentials = [math.exp(value - peak) for value in row]
                    total = sum(exponentials)
                    probabilities.append([value / total for value in exponentials])
                return FakeTensor(probabilities)

        estimator = models.ResNetClassifier()
        estimator._torch = FakeTorch()
        logits = [[-1.0, 1.0], [2.0, 0.0]]
        with patch.object(estimator, "_predict_values", return_value=logits):
            probabilities = estimator.predict_proba([self.image, self.image])

        self.assertIs(estimator._torch.input, logits)
        self.assertEqual(len(probabilities), 2)
        for row in probabilities:
            self.assertAlmostEqual(sum(row), 1.0)

    def test_pillow_image_inputs_are_copied_and_regression_pairs_are_supported(self):
        try:
            from PIL import Image
        except ImportError:
            self.skipTest("Pillowが必要です")
        image = Image.new("RGB", (8, 6), "red")
        rows = models._image_rows([image], allow_pairs=False)
        self.assertIsNot(rows[0], image)
        self.assertEqual(rows[0].size, image.size)
        pairs = models._image_rows([(self.image, image)], allow_pairs=True)
        self.assertEqual(pairs[0][0], self.image)
        self.assertIsNot(pairs[0][1], image)
        rgb = models._load_rgb_image(rows[0])
        self.assertEqual(rgb.mode, "RGB")
        self.assertEqual(image.mode, "RGB")

    @unittest.skipIf(importlib.util.find_spec("torch"), "PyTorch導入環境では重み取得を避ける")
    def test_missing_torch_message(self):
        with self.assertRaisesRegex(models.ModelError, r"cv-data-lesson\[torch\]"):
            models.available_devices()


if __name__ == "__main__":
    unittest.main()
