"""ネットワークを使わない固定Release監査機能のテスト。"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path
from unittest.mock import patch

from cvlesson import audit, datasets
from test_release_adapter import make_zip


class AuditTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.cache = Path(self.tmp.name)

    def fixture(self, case="festival-icons"):
        name = "festival_icons" if case == "festival-icons" else "tomato_leaves"
        payload = make_zip(case=case)
        src = replace(
            datasets._SOURCES[name],
            tag="festival-v1.0.0" if case == "festival-icons" else "tomato-v1.0.0",
            sha256=hashlib.sha256(payload).hexdigest(),
            archive_size=len(payload), image_count=1,
        )
        return name, src, payload

    def test_festival_report_distinguishes_unchecked_items(self):
        name, source, payload = self.fixture()
        with patch.dict(datasets._SOURCES, {name: source}), patch.object(
            datasets, "_download",
            side_effect=lambda url, dest, *, max_bytes: dest.write_bytes(payload),
        ):
            report = audit.inspect_release(name, cache_dir=self.cache)
        self.assertEqual(report["captions_present"], 1)
        self.assertEqual(report["status"], "passed")
        self.assertEqual(report["image_decode"], "not_checked")
        self.assertEqual(report["rights_review"], "not_performed")

    def test_tomato_counts(self):
        name, source, payload = self.fixture("tomato-leaves")
        with patch.dict(datasets._SOURCES, {name: source}), patch.object(
            datasets, "_download",
            side_effect=lambda url, dest, *, max_bytes: dest.write_bytes(payload),
        ):
            report = audit.inspect_release(name, cache_dir=self.cache)
        self.assertEqual(report["classes"], {"healthy": 1})
        self.assertEqual(report["splits"], {"train": 1})

    @unittest.skipUnless(importlib.util.find_spec("PIL"), "Pillowが必要です")
    def test_invalid_image_is_detected(self):
        name, source, payload = self.fixture()
        with patch.dict(datasets._SOURCES, {name: source}), patch.object(
            datasets, "_download",
            side_effect=lambda url, dest, *, max_bytes: dest.write_bytes(payload),
        ):
            report = audit.inspect_release(name, cache_dir=self.cache, check_images=True)
        self.assertEqual(report["status"], "failed")
        self.assertEqual(report["image_decode_failed"], 1)
        self.assertEqual(report["rights_review"], "not_performed")

    @unittest.skipUnless(importlib.util.find_spec("PIL"), "Pillowが必要です")
    def test_similar_check_is_review_only(self):
        name, source, payload = self.fixture()
        with patch.dict(datasets._SOURCES, {name: source}), patch.object(
            datasets, "_download",
            side_effect=lambda url, dest, *, max_bytes: dest.write_bytes(payload),
        ):
            report = audit.inspect_release(
                name, cache_dir=self.cache, check_images=True, check_similar=True,
            )
        self.assertEqual(report["similar_image_check"], "performed")
        self.assertIn("review_only", report["similar_image_method"])
        self.assertEqual(report["similar_image_candidate_count"], 0)

    def test_offline_error_report(self):
        result_file = self.cache / "report.json"
        with patch("sys.stdout"):
            status = audit.main([
                "festival_icons", "--cache-dir", str(self.cache),
                "--no-download", "--report", str(result_file),
            ])
        self.assertEqual(status, 1)
        self.assertEqual(json.loads(result_file.read_text())["status"], "failed")


if __name__ == "__main__":
    unittest.main()
