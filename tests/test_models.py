"""ResNet APIの入力検証と任意依存の案内を確認する。"""
from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path

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

    @unittest.skipIf(importlib.util.find_spec("torch"), "PyTorch導入環境では重み取得を避ける")
    def test_missing_torch_message(self):
        with self.assertRaisesRegex(models.ModelError, r"cv-data-lesson\[torch\]"):
            models.available_devices()


if __name__ == "__main__":
    unittest.main()
