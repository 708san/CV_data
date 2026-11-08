"""学習済みLoRA重みカタログのネットワーク不要テスト。"""
from __future__ import annotations

import hashlib
import io
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path
from unittest.mock import patch

from cvlesson import weights


class LoraWeightTests(unittest.TestCase):
    def test_catalog_and_info_do_not_use_network(self):
        with patch("cvlesson.weights.urllib.request.urlopen") as urlopen:
            catalog = weights.list_available()
            info = weights.info("tcd_sd15")
        urlopen.assert_not_called()
        self.assertEqual([item["id"] for item in catalog], ["tcd_sd15"])
        self.assertEqual(info["version"], "449a99f6bbded2bdbbc66386b2a4fbf8db8d3807")
        self.assertEqual(info["license"]["name"], "MIT（LoRA重み）")
        self.assertIn("Open RAIL-M", info["base_model_license"]["name"])

    def test_get_downloads_only_on_explicit_call_and_verifies_sha256(self):
        content = b"fixed LoRA test payload"
        test_item = replace(
            weights._WEIGHTS["tcd_sd15"],
            size_bytes=len(content),
            sha256=hashlib.sha256(content).hexdigest(),
            url="https://example.invalid/fixed-test-weight",
        )
        temp_root = str(Path(tempfile.gettempdir()).resolve())
        with tempfile.TemporaryDirectory(dir=temp_root) as temp_dir:
            with patch.dict(weights._WEIGHTS, {"test_weight": test_item}):
                with patch("cvlesson.weights.urllib.request.urlopen", return_value=io.BytesIO(content)) as urlopen:
                    path = weights.get("test_weight", cache_dir=temp_dir)
                urlopen.assert_called_once()
                self.assertEqual(path.read_bytes(), content)
                with patch("cvlesson.weights.urllib.request.urlopen") as no_download:
                    cached = weights.get("test_weight", cache_dir=temp_dir)
                no_download.assert_not_called()
                self.assertEqual(cached, path)

    def test_bad_hash_does_not_leave_a_weight_file(self):
        content = b"wrong test payload"
        test_item = replace(
            weights._WEIGHTS["tcd_sd15"],
            size_bytes=len(content),
            sha256="0" * 64,
            url="https://example.invalid/fixed-test-weight",
        )
        temp_root = str(Path(tempfile.gettempdir()).resolve())
        with tempfile.TemporaryDirectory(dir=temp_root) as temp_dir:
            with patch.dict(weights._WEIGHTS, {"bad_weight": test_item}):
                with patch("cvlesson.weights.urllib.request.urlopen", return_value=io.BytesIO(content)):
                    with self.assertRaisesRegex(weights.WeightError, "SHA-256"):
                        weights.get("bad_weight", cache_dir=temp_dir)
            files = [path for path in Path(temp_dir).rglob("*") if path.is_file()]
            self.assertEqual(files, [])

    def test_unknown_weight_id_is_rejected(self):
        with self.assertRaisesRegex(weights.WeightError, "未対応"):
            weights.info("unknown")


if __name__ == "__main__":
    unittest.main()
