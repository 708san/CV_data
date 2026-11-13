"""機能別extrasを使った依存関係エラー案内を確認する。"""
from __future__ import annotations

import sys
import re
import tomllib
import unittest
from pathlib import Path
from unittest.mock import patch

from cvlesson.datasets import DatasetBundle, DatasetError


class PackagingMetadataTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        metadata_path = Path(__file__).resolve().parents[1] / "pyproject.toml"
        with metadata_path.open("rb") as file:
            cls.project = tomllib.load(file)["project"]

    @staticmethod
    def _requirement_names(requirements):
        names = set()
        for requirement in requirements:
            match = re.match(r"([A-Za-z0-9_.-]+)", requirement)
            if match:
                names.add(re.sub(r"[-_.]+", "-", match.group(1)).lower())
        return names

    def test_core_install_has_no_runtime_dependencies(self):
        self.assertEqual(self.project.get("dependencies", []), [])
        self.assertEqual(self.project["requires-python"], ">=3.11,<3.14")

    def test_features_are_declared_as_separate_extras(self):
        extras = self.project["optional-dependencies"]
        self.assertNotIn("all", extras)
        expected = {
            "test": {"pandas", "pillow"},
            "dataframe": {"pandas"},
            "display": {"numpy", "pillow", "matplotlib"},
            "torch": {"numpy", "pillow", "torch", "torchvision"},
            "ocr": {"paddleocr", "paddlex", "huggingface-hub"},
            "diffusion": {"pillow", "diffusers", "transformers", "huggingface-hub"},
        }
        for extra, packages in expected.items():
            with self.subTest(extra=extra):
                self.assertTrue(packages <= self._requirement_names(extras[extra]))
        ocr_requirements = extras["ocr"]
        self.assertTrue(any(req.startswith("paddlex[ocr]>=3.1.0,<3.2.0") for req in ocr_requirements))


class OptionalDependencyGuidanceTests(unittest.TestCase):
    def setUp(self):
        self.bundle = DatasetBundle(
            id="example",
            kind="classification",
            root=Path("."),
            manifest={},
            source_url="",
            version="1",
            rights_note="",
        )

    def test_dataframe_error_points_to_dataframe_extra(self):
        with patch.dict(sys.modules, {"pandas": None}):
            with self.assertRaisesRegex(DatasetError, r"cv-data-lesson\[dataframe\]"):
                self.bundle.to_df()

    def test_torch_dataset_error_points_to_torch_extra(self):
        with patch.dict(sys.modules, {"torch": None}):
            with self.assertRaisesRegex(DatasetError, r"cv-data-lesson\[torch\]"):
                self.bundle.to_torch_dataset()

    def test_display_error_points_to_both_required_extras(self):
        with patch.dict(sys.modules, {"matplotlib": None}):
            with self.assertRaisesRegex(
                DatasetError, r"cv-data-lesson\[display,dataframe\]"
            ):
                self.bundle.show_examples()


if __name__ == "__main__":
    unittest.main()
