"""機能別extrasを使った依存関係エラー案内を確認する。"""
from __future__ import annotations

import sys
import re
import tomllib
import types
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from cvlesson.datasets import DatasetBundle, DatasetError, _enable_japanese_matplotlib


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

    def test_core_install_includes_lightweight_student_workflow_dependencies(self):
        dependencies = self._requirement_names(self.project.get("dependencies", []))
        self.assertTrue({"numpy", "pillow", "pandas", "matplotlib", "japanize-matplotlib"} <= dependencies)
        self.assertFalse({"torch", "torchvision", "paddleocr", "transformers", "diffusers"} & dependencies)
        self.assertEqual(self.project["requires-python"], ">=3.11,<3.14")

    def test_features_are_declared_as_separate_extras(self):
        extras = self.project["optional-dependencies"]
        self.assertNotIn("all", extras)
        expected = {
            "test": {"pandas", "pillow"},
            "dataframe": {"pandas"},
            "display": {"numpy", "pillow", "pandas", "matplotlib", "japanize-matplotlib"},
            "torch": {"numpy", "pillow", "torch", "torchvision"},
            "ocr": {"paddleocr", "paddlex", "pillow", "huggingface-hub"},
            "diffusion": {"pillow", "diffusers", "transformers", "huggingface-hub", "peft"},
        }
        for extra, packages in expected.items():
            with self.subTest(extra=extra):
                self.assertTrue(packages <= self._requirement_names(extras[extra]))
        ocr_requirements = extras["ocr"]
        self.assertTrue(any(req.startswith("paddlex[ocr]>=3.1.0,<3.2.0") for req in ocr_requirements))
        self.assertIn("langchain>=0.2,<1", ocr_requirements)
        self.assertIn("requests>=2.32.2,<2.33", ocr_requirements)
        self.assertIn("huggingface_hub>=0.23,<3", ocr_requirements)
        self.assertIn("huggingface_hub>=0.23,<3", extras["vision"])


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

    def test_dataframe_error_explains_basic_install(self):
        with patch.dict(sys.modules, {"pandas": None}):
            with self.assertRaisesRegex(DatasetError, r"pip install --pre cv-data-lesson"):
                self.bundle.to_df()

    def test_torch_dataset_error_points_to_torch_extra(self):
        with patch.dict(sys.modules, {"torch": None}):
            with self.assertRaisesRegex(DatasetError, r"cv-data-lesson\[torch\]"):
                self.bundle.to_torch_dataset()

    def test_display_error_explains_basic_install(self):
        with patch.dict(sys.modules, {"matplotlib": None}):
            with self.assertRaisesRegex(
                DatasetError, r"pip install --pre cv-data-lesson"
            ):
                self.bundle.show_examples()

    def test_japanese_matplotlib_is_configured_when_display_is_used(self):
        japanize = types.ModuleType("japanize_matplotlib")
        japanize.japanize = Mock()
        japanize.get_font_ttf_path = Mock(return_value="/fonts/ipaexg.ttf")
        font_manager = types.ModuleType("matplotlib.font_manager")

        class FakeFontProperties:
            def __init__(self, *, fname):
                self.fname = fname

            def get_name(self):
                return "IPAexGothic"

        font_manager.FontProperties = FakeFontProperties
        matplotlib = types.ModuleType("matplotlib")
        matplotlib.__path__ = []
        matplotlib.rcParams = {}
        with patch.dict(sys.modules, {
            "japanize_matplotlib": japanize,
            "matplotlib": matplotlib,
            "matplotlib.font_manager": font_manager,
        }), patch("cvlesson.datasets.Path.is_file", return_value=True):
            font = _enable_japanese_matplotlib()
        japanize.japanize.assert_called_once_with()
        self.assertEqual(font.fname, "/fonts/ipaexg.ttf")
        self.assertEqual(matplotlib.rcParams["font.family"], ["IPAexGothic"])

    def test_installed_japanese_font_file_is_available(self):
        try:
            import japanize_matplotlib
        except ImportError:
            self.skipTest("display extra is not installed")
        font_path = Path(japanize_matplotlib.get_font_ttf_path())
        self.assertTrue(font_path.is_file(), font_path)
        font = _enable_japanese_matplotlib()
        self.assertTrue(font.get_name())
        self.assertEqual(Path(font.get_file()), font_path)

    def test_missing_japanese_font_dependency_has_install_guidance(self):
        with patch.dict(sys.modules, {"japanize_matplotlib": None}):
            with self.assertRaisesRegex(DatasetError, r"pip install --pre cv-data-lesson"):
                _enable_japanese_matplotlib()


if __name__ == "__main__":
    unittest.main()
