"""外部ネットワークに接続しない公開Release取得機能のテスト。"""
from __future__ import annotations

import hashlib
import io
import json
import tempfile
import unittest
import zipfile
from dataclasses import replace
from pathlib import Path
from unittest.mock import patch

from cvlesson import datasets


def make_zip(case="festival-icons", *, corrupt=False, unsafe=False, symlink=False) -> bytes:
    image = "images/a.png"
    manifest = {
        "case_id": case, "version": "v1.0.0", "image_count": 1,
        "classes": ["healthy"] if case == "tomato-leaves" else None,
    }
    if case == "tomato-leaves":
        image = "images/train/healthy/a.png"
        csv_text = f"image,label,split\n{image},healthy,train\n"
        metadata = json.dumps({"file_name": image, "label": "healthy", "split": "train"}) + "\n"
    else:
        csv_text = f"image,caption\n{image},a simple icon\n"
        metadata = json.dumps({"file_name": image, "text": "a simple icon"}) + "\n"
    files = {
        f"{case}/manifest.json": json.dumps(manifest),
        f"{case}/labels.csv": csv_text,
        f"{case}/metadata.jsonl": metadata,
        f"{case}/README.md": "test",
        f"{case}/{image}": b"\x89PNG\r\n\x1a\n",
    }
    if corrupt:
        files[f"{case}/labels.csv"] = "image,caption\nimages/no.png,icon\n"
    if unsafe:
        files["../outside.txt"] = "escape"
    output = io.BytesIO()
    with zipfile.ZipFile(output, "w") as archive:
        for name, content in files.items():
            archive.writestr(name, content)
        if symlink:
            info = zipfile.ZipInfo(f"{case}/symlink")
            info.create_system = 3
            info.external_attr = 0o120777 << 16
            archive.writestr(info, "target")
    return output.getvalue()


class ReleaseTests(unittest.TestCase):
    def setUp(self) -> None:
        self.work = tempfile.TemporaryDirectory()
        self.addCleanup(self.work.cleanup)
        self.cache = Path(self.work.name)

    def setup_source(self, payload: bytes, case="festival-icons", sha=None):
        key = "festival_icons" if case == "festival-icons" else "tomato_leaves"
        base = datasets._SOURCES[key]
        source = replace(
            base,
            tag=("festival-v1.0.0" if case == "festival-icons" else "tomato-v1.0.0"),
            sha256=sha or hashlib.sha256(payload).hexdigest(),
            archive_size=len(payload), image_count=1,
        )
        return key, source

    def test_catalog_only_two_pinned_datasets(self):
        ids = {item["id"] for item in datasets.list_available()}
        self.assertEqual(ids, {"tomato_leaves", "festival_icons"})
        self.assertIn("festival-v1.0.0", str(datasets.info("festival_icons")))
        self.assertIn("未実施", datasets.info("tomato_leaves")["状態"])

    def test_festival_download_and_offline_cache(self):
        payload = make_zip()
        key, source = self.setup_source(payload)
        calls = []
        def fake_download(url, destination, *, max_bytes):
            calls.append(url)
            destination.write_bytes(payload)
        with patch.dict(datasets._SOURCES, {key: source}), patch.object(datasets, "_download", side_effect=fake_download):
            data = datasets.get(key, cache_dir=self.cache)
            self.assertEqual(data.kind, "lora_training_images")
            self.assertEqual(data.manifest["image_count"], 1)
            self.assertTrue(data.labels_csv.exists())
            self.assertIsNone(data.train_dir)
            again = datasets.get(key, cache_dir=self.cache, allow_download=False)
            self.assertEqual(again.root, data.root)
            self.assertEqual(len(calls), 1)

    def test_tomato_classification(self):
        payload = make_zip(case="tomato-leaves")
        key, source = self.setup_source(payload, case="tomato-leaves")
        with patch.dict(datasets._SOURCES, {key: source}), patch.object(datasets, "_download", side_effect=lambda url, dst, *, max_bytes: dst.write_bytes(payload)):
            data = datasets.get(key, cache_dir=self.cache)
            self.assertEqual(data.kind, "classification")
            self.assertIsNotNone(data.train_dir)
            self.assertIsNone(data.test_dir)

    def test_download_disabled(self):
        with self.assertRaisesRegex(datasets.DatasetError, "キャッシュ"):
            datasets.get("festival_icons", cache_dir=self.cache, allow_download=False)

    def test_wrong_sha_is_rejected(self):
        payload = make_zip()
        key, source = self.setup_source(payload, sha="0" * 64)
        with patch.dict(datasets._SOURCES, {key: source}), patch.object(datasets, "_download", side_effect=lambda url, dst, *, max_bytes: dst.write_bytes(payload)):
            with self.assertRaisesRegex(datasets.DatasetError, "SHA-256"):
                datasets.get(key, cache_dir=self.cache)
        self.assertFalse((self.cache / "sources" / key / source.tag / source.case_id).exists())

    def test_unsafe_zip_is_rejected(self):
        for unsafe, symlink in [(True, False), (False, True)]:
            with self.subTest(unsafe=unsafe, symlink=symlink):
                payload = make_zip(unsafe=unsafe, symlink=symlink)
                key, source = self.setup_source(payload)
                with patch.dict(datasets._SOURCES, {key: source}), patch.object(datasets, "_download", side_effect=lambda url, dst, *, max_bytes: dst.write_bytes(payload)):
                    with self.assertRaises(datasets.DatasetError):
                        datasets.get(key, cache_dir=self.cache / str(unsafe) / str(symlink))
        self.assertFalse((self.cache / "outside.txt").exists())

    def test_missing_label_image_rejected(self):
        payload = make_zip(corrupt=True)
        key, source = self.setup_source(payload)
        with patch.dict(datasets._SOURCES, {key: source}), patch.object(datasets, "_download", side_effect=lambda url, dst, *, max_bytes: dst.write_bytes(payload)):
            with self.assertRaisesRegex(datasets.DatasetError, "画像ファイル"):
                datasets.get(key, cache_dir=self.cache)

    def test_unknown_id(self):
        with self.assertRaises(datasets.DatasetError):
            datasets.get("not_registered", cache_dir=self.cache)


if __name__ == "__main__":
    unittest.main()
