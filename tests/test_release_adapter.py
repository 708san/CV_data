"""外部ネットワークに接続しない公開Release取得機能のテスト。"""
from __future__ import annotations

import hashlib
import gzip
import importlib.util
import io
import json
import struct
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


def make_idx_gzip_files() -> dict[str, bytes]:
    image_header = struct.pack(">IIII", 2051, 1, 2, 2)
    label_header = struct.pack(">II", 2049, 1)
    def gz(payload):
        output = io.BytesIO()
        with gzip.GzipFile(fileobj=output, mode="wb") as stream:
            stream.write(payload)
        return output.getvalue()
    return {
        "train-images-idx3-ubyte.gz": gz(image_header + b"\x00\x01\x02\x03"),
        "train-labels-idx1-ubyte.gz": gz(label_header + b"\x00"),
        "t10k-images-idx3-ubyte.gz": gz(image_header + b"\x04\x05\x06\x07"),
        "t10k-labels-idx1-ubyte.gz": gz(label_header + b"\x01"),
    }


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
        self.assertEqual(datasets.info("tomato_leaves")["audit_status"], "full_image_audit")
        self.assertEqual(datasets.info("festival_icons")["audit_status"], "full_image_audit")

    def test_catalog_can_filter_by_task_and_audience(self):
        student = datasets.list_available(task="classification", audience="student")
        self.assertEqual([item["id"] for item in student], ["tomato_leaves"])
        self.assertEqual(student[0]["publication_status"], "student_enabled")
        self.assertEqual(datasets.list_available(task="lora", audience="student"), [])
        teacher = datasets.list_available(task="lora", audience="teacher")
        self.assertEqual([item["id"] for item in teacher], ["festival_icons"])

    def test_preview_is_only_in_teacher_catalog_when_requested(self):
        student = datasets.list_available(
            task="classification", audience="student", include_preview=True,
        )
        teacher = datasets.list_available(
            task="classification", audience="teacher", include_preview=True,
        )
        self.assertEqual([item["id"] for item in student], ["tomato_leaves"])
        self.assertEqual({item["id"] for item in teacher}, {"tomato_leaves", "fashion_mnist"})
        fashion = next(item for item in teacher if item["id"] == "fashion_mnist")
        self.assertEqual(fashion["publication_status"], "teacher_preview_only")

    def test_task_catalog_only_shows_usable_choices(self):
        tasks = datasets.list_tasks()
        self.assertEqual([item["task"] for item in tasks], ["classification"])
        self.assertEqual(tasks[0]["datasets"], ["tomato_leaves"])
        teacher_tasks = datasets.list_tasks(audience="teacher", include_preview=True)
        self.assertEqual(
            [item["task"] for item in teacher_tasks], ["classification", "lora"]
        )

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

    @unittest.skipUnless(importlib.util.find_spec("pandas"), "pandasが必要です")
    def test_japanese_alias_and_dataframe_schema(self):
        payload = make_zip(case="tomato-leaves")
        key, source = self.setup_source(payload, case="tomato-leaves")
        with patch.dict(datasets._SOURCES, {key: source}), patch.object(
            datasets, "_download", side_effect=lambda url, dst, *, max_bytes: dst.write_bytes(payload)
        ):
            data = datasets.get("トマトの葉", cache_dir=self.cache)
        frame = data.to_df()
        self.assertEqual(list(frame.columns), [
            "image_path", "label", "label_ja", "label_id", "split",
            "sample_id", "group_id", "source_split",
        ])
        self.assertEqual(frame.loc[0, "label"], "healthy")
        self.assertEqual(frame.loc[0, "label_ja"], "健全")
        self.assertEqual(data.splits, {"train": 1, "val": 0, "test": 0})

    def test_info_without_id_returns_catalog(self):
        catalog = datasets.info()
        self.assertIsInstance(catalog, list)
        self.assertEqual({item["id"] for item in catalog}, {"tomato_leaves", "festival_icons"})

    def test_preview_dataset_is_not_in_formal_catalog(self):
        self.assertNotIn("fashion_mnist", {item["id"] for item in datasets.list_available()})
        self.assertEqual(datasets.list_preview()[0]["id"], "fashion_mnist")
        with self.assertRaisesRegex(datasets.DatasetError, "教師向けプレビュー"):
            datasets.get("fashion_mnist", cache_dir=self.cache)

    def test_idx_preview_materializes_verified_pgm_cache(self):
        payloads = make_idx_gzip_files()
        base = datasets._PREVIEW_SOURCES["fashion_mnist"]
        source = replace(
            base,
            tag="github-test-idx",
            image_count=2,
            file_sha256={name: hashlib.sha256(payload).hexdigest() for name, payload in payloads.items()},
            file_sizes={name: len(payload) for name, payload in payloads.items()},
        )
        def fake_download(url, destination, *, max_bytes):
            destination.write_bytes(payloads[destination.name])
        with patch.dict(datasets._PREVIEW_SOURCES, {"fashion_mnist": source}), patch.object(
            datasets, "_download", side_effect=fake_download,
        ):
            data = datasets.get("fashion_mnist", cache_dir=self.cache, allow_preview=True)
        self.assertEqual(data.manifest["image_count"], 2)
        self.assertTrue((data.root / "images/train/0/000001.pgm").is_file())
        self.assertTrue((data.root / "images/test/1/000001.pgm").is_file())


if __name__ == "__main__":
    unittest.main()
