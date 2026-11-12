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


def make_detection_zip(case="bangladeshi_ewaste", *, corrupt_label=False, root_folder=True, unsafe=False) -> bytes:
    image = "images/train/one.png"
    label = "labels/train/one.txt"
    annotation = {
        "class_id": 0, "x_center": 0.5, "y_center": 0.5,
        "width": 0.2, "height": 0.4, "source_annotation_format": "bbox",
    }
    detection_label = "0 0.5 0.5 0.2 0.4\n" if not corrupt_label else "0 1.4 0.5 0.2 0.4\n"
    manifest = {"case_id": case, "version": "v0.1.0", "image_count": 1, "classes": ["battery"]}
    records = [{"file_name": image, "label_file": label, "split": "train", "annotations": [annotation]}]
    metadata = [{"file_name": image, "label_file": label, "split": "train", "annotation_count": 1}]
    files = {
        f"{case}/manifest.json": json.dumps(manifest),
        f"{case}/classes.json": json.dumps({"classes": ["battery"]}),
        f"{case}/annotations.jsonl": json.dumps(records[0]) + "\n",
        f"{case}/metadata.jsonl": json.dumps(metadata[0]) + "\n",
        f"{case}/README.md": "test",
        f"{case}/{image}": b"\x89PNG\r\n\x1a\n",
        f"{case}/{label}": detection_label,
    }
    if unsafe:
        files["../outside.txt"] = b"escape"
    output = io.BytesIO()
    prefix = f"{case}/" if root_folder else ""
    with zipfile.ZipFile(output, "w") as archive:
        for name, content in files.items():
            archive.writestr(name.replace(f"{case}/", prefix, 1), content)
    return output.getvalue()


def make_regression_zip(*, unsafe_path=False, incorrect_ratio=False) -> bytes:
    root = "lefood-set-v0.1.0/"
    metadata = (
        "sample_id,source_record_id,food_category,food_name_original,image_before,image_after,"
        "weight_before_g,weight_after_g,consumed_weight_g,leftover_ratio,visual_leftover_level,"
        "weight_order_anomaly,source_image_before,source_image_after,food_category_id,split\n"
        "pair-0001,1,Nasi,Nasi,images/before/0001_before.jpg,images/after/0001_after.jpg,"
        f"100,75,25,{0.7 if incorrect_ratio else 0.75},3,False,source_before.JPG,source_after.JPG,1,train\n"
    )
    if unsafe_path:
        metadata = metadata.replace("images/before/0001_before.jpg", "../outside.jpg")
    manifest = {
        "dataset_id": "lefood_set", "artifact_version": "0.1.0", "source_license": "CC BY 4.0",
        "transformation": {"included_pairs": 1},
    }
    files = {
        root + "manifest.json": json.dumps(manifest),
        root + "metadata.csv": metadata,
        root + "README.md": "test artifact",
        root + "LICENSE.txt": "CC BY 4.0 attribution",
        root + "images/before/0001_before.jpg": b"before-image",
        root + "images/after/0001_after.jpg": b"after-image",
    }
    output = io.BytesIO()
    with zipfile.ZipFile(output, "w") as archive:
        for name, content in files.items():
            archive.writestr(name, content)
    return output.getvalue()


def make_indoor_plant_zip(case="indoor_plant_varieties") -> bytes:
    classes = ["Aglaonema", "Cryptanthus", "Devil's Ivy", "Heartleaf philodendron",
               "N-Joy Pothos", "Rhaphidophora", "Zz plant"]
    image = "images/train/Aglaonema/sample.jpg"
    row = {"file_name": image, "label": "Aglaonema", "label_id": 0,
           "split": "train", "sample_id": "images/train/Aglaonema/sample"}
    manifest = {"case_id": case, "version": "v0.1.0", "image_count": 1, "classes": classes}
    files = {
        f"{case}/manifest.json": json.dumps(manifest),
        f"{case}/labels.csv": "image,label,label_id,split,sample_id\n"
        f'"{image}",Aglaonema,0,train,"images/train/Aglaonema/sample"\n',
        f"{case}/metadata.jsonl": json.dumps(row) + "\n",
        f"{case}/README.md": "test",
        f"{case}/{image}": b"image-bytes",
    }
    output = io.BytesIO()
    with zipfile.ZipFile(output, "w") as archive:
        for name, content in files.items():
            archive.writestr(name, content)
    return output.getvalue()


def make_segmentation_zip(case="fruitseg30", *, omit_mask=False) -> bytes:
    image = "images/train/Avocado/1.jpg"
    mask = "masks/train/Avocado/1_mask.png"
    row = {"image": image, "mask": mask, "class_name": "Avocado", "class_id": 0, "split": "train"}
    manifest = {"dataset_id": case, "artifact_version": "0.1.0", "image_count": 1,
                "classes": ["Avocado"]}
    files = {
        f"{case}/manifest.json": json.dumps(manifest),
        f"{case}/labels.csv": "image,mask,class_name,class_id,split\n" +
        f"{image},{mask},Avocado,0,train\n",
        f"{case}/metadata.jsonl": json.dumps(row) + "\n",
        f"{case}/README.md": "test",
        f"{case}/LICENSE.md": "CC BY 4.0 attribution",
        f"{case}/{image}": b"image-bytes",
    }
    if not omit_mask:
        files[f"{case}/{mask}"] = b"mask-bytes"
    output = io.BytesIO()
    with zipfile.ZipFile(output, "w") as archive:
        for name, content in files.items():
            archive.writestr(name, content)
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

    def test_published_detection_and_pending_artifacts_have_correct_status(self):
        ids = {item["id"] for item in datasets.list_available()}
        self.assertEqual(ids, {"tomato_leaves", "festival_icons", "fruitseg30", "fresh_rotten_fruits", "road_traversing_knowledge", "rdd2020_japan", "lefood_set", "indoor_plant_varieties", "geoset_ennea", "bangladeshi_ewaste_image", "fabricspotdefect", "orange_fruit", "japanese_receipts_detailed", "indoor_waste_image", "wastesegcluster", "fire_recognition_image", "agrifreshnet", "brazil_road_potholes", "click_trash", "obstacles_assistance", "trashnet", "vifoodlabel", "energy_meter_digits"})
        self.assertIn("festival-v1.0.0", str(datasets.info("festival_icons")))
        self.assertEqual(datasets.info("tomato_leaves")["audit_status"], "full_image_audit")
        self.assertEqual(datasets.info("festival_icons")["audit_status"], "full_image_audit")
        self.assertEqual(datasets.info("bangladeshi_ewaste_image")["task"], "detection")
        self.assertEqual(datasets.info("bangladeshi_ewaste_image")["権利上の注意"].split("。")[0], "CC BY 4.0")
        self.assertEqual(datasets.info("bangladeshi_ewaste_image")["publication_status"], "student_enabled")
        self.assertEqual(datasets.info("rdd2020_japan")["publication_status"], "student_enabled")
        self.assertEqual(datasets.info("rdd2020_japan")["task"], "detection")
        self.assertEqual(datasets.info("rdd2020_japan")["ZIPのSHA-256"], datasets._SOURCES["rdd2020_japan"].sha256)
        self.assertEqual(datasets.info("lefood_set")["publication_status"], "student_enabled")
        self.assertEqual(datasets.info("lefood_set")["サンプル数"], 524)

    def test_fruitseg30_is_available_after_fixed_release_is_published(self):
        self.assertEqual(datasets.info("fruitseg30")["publication_status"], "student_enabled")
        ids = {item["id"] for item in datasets.list_available(task="segmentation", audience="student")}
        self.assertEqual(ids, {"fruitseg30", "road_traversing_knowledge", "brazil_road_potholes"})

    @unittest.skipUnless(importlib.util.find_spec("pandas"), "pandasが必要です")
    def test_segmentation_artifact_download_cache_and_dataframe(self):
        payload = make_segmentation_zip()
        source = replace(
            datasets._SOURCES["fruitseg30"], sha256=hashlib.sha256(payload).hexdigest(),
            archive_size=len(payload), image_count=1, published=True,
            classes=("Avocado",), class_names_ja=("アボカド",),
        )
        with patch.dict(datasets._SOURCES, {"fruitseg30": source}), patch.object(
            datasets, "_download", side_effect=lambda url, dst, *, max_bytes: dst.write_bytes(payload)
        ):
            data = datasets.get("fruitseg30", cache_dir=self.cache)
            frame = data.to_df()
            self.assertEqual(data.task, "segmentation")
            self.assertEqual(frame.loc[0, "label_ja"], "アボカド")
            self.assertTrue(Path(frame.loc[0, "mask_path"]).is_file())
            self.assertEqual(data.splits, {"train": 1, "val": 0, "test": 0})
            self.assertEqual(data.quality_summary()["usable_images"], 1)
            cached = datasets.get("fruitseg30", cache_dir=self.cache, allow_download=False)
            self.assertEqual(cached.root, data.root)

    def test_segmentation_missing_mask_is_rejected(self):
        payload = make_segmentation_zip(omit_mask=True)
        source = replace(
            datasets._SOURCES["fruitseg30"], sha256=hashlib.sha256(payload).hexdigest(),
            archive_size=len(payload), image_count=1, published=True,
            classes=("Avocado",), class_names_ja=("アボカド",),
        )
        with patch.dict(datasets._SOURCES, {"fruitseg30": source}), patch.object(
            datasets, "_download", side_effect=lambda url, dst, *, max_bytes: dst.write_bytes(payload)
        ):
            with self.assertRaisesRegex(datasets.DatasetError, "画像またはマスク"):
                datasets.get("fruitseg30", cache_dir=self.cache)

    def test_catalog_can_filter_by_task_and_audience(self):
        student = datasets.list_available(task="classification", audience="student")
        self.assertEqual([item["id"] for item in student], ["tomato_leaves", "orange_fruit", "fresh_rotten_fruits", "indoor_plant_varieties", "trashnet", "energy_meter_digits", "fire_recognition_image", "agrifreshnet"])
        self.assertEqual(student[0]["publication_status"], "student_enabled")
        self.assertEqual(datasets.list_available(task="lora", audience="student"), [])
        teacher = datasets.list_available(task="lora", audience="teacher")
        self.assertEqual([item["id"] for item in teacher], ["festival_icons"])

    def test_student_datasets_are_also_available_to_teachers(self):
        student = datasets.list_available(
            task="classification", audience="student", include_preview=True,
        )
        teacher = datasets.list_available(
            task="classification", audience="teacher", include_preview=True,
        )
        self.assertEqual([item["id"] for item in student], ["tomato_leaves", "orange_fruit", "fresh_rotten_fruits", "indoor_plant_varieties", "trashnet", "energy_meter_digits", "fire_recognition_image", "agrifreshnet"])
        self.assertEqual({item["id"] for item in teacher}, {"tomato_leaves", "fresh_rotten_fruits", "indoor_plant_varieties", "orange_fruit", "fire_recognition_image", "agrifreshnet", "trashnet", "energy_meter_digits"})

    def test_task_catalog_only_shows_usable_choices(self):
        tasks = datasets.list_tasks()
        self.assertEqual([item["task"] for item in tasks], ["ocr", "classification", "detection", "regression", "segmentation"])
        self.assertEqual(tasks[0]["datasets"], ["japanese_receipts_detailed", "vifoodlabel"])
        self.assertEqual(tasks[1]["datasets"], ["tomato_leaves", "orange_fruit", "fresh_rotten_fruits", "indoor_plant_varieties", "trashnet", "energy_meter_digits", "fire_recognition_image", "agrifreshnet"])
        self.assertEqual(tasks[2]["datasets"], ["rdd2020_japan", "bangladeshi_ewaste_image", "geoset_ennea", "fabricspotdefect", "indoor_waste_image", "wastesegcluster", "click_trash", "obstacles_assistance"])
        self.assertEqual(tasks[3]["datasets"], ["lefood_set"])
        teacher_tasks = datasets.list_tasks(audience="teacher", include_preview=True)
        self.assertEqual(
            [item["task"] for item in teacher_tasks], ["ocr", "classification", "detection", "regression", "segmentation", "lora"]
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

    def test_cache_info_reports_size_and_version_without_download(self):
        payload = make_zip()
        key, source = self.setup_source(payload)
        with patch.dict(datasets._SOURCES, {key: source}), patch.object(
            datasets, "_download", side_effect=lambda url, dst, *, max_bytes: dst.write_bytes(payload)
        ):
            data = datasets.get(key, cache_dir=self.cache)
            info = datasets.cache_info(cache_dir=self.cache)
            self.assertEqual(info["cache_dir"], str(self.cache))
            self.assertEqual(info["datasets"], [{
                "dataset_id": key,
                "versions": [source.tag],
                "bytes": sum(path.stat().st_size for path in data.root.rglob("*") if path.is_file()),
                "files": sum(1 for path in data.root.rglob("*") if path.is_file()),
            }])
            self.assertGreater(info["total_bytes"], 0)

    def test_clear_cache_removes_selected_dataset_and_preserves_unrelated_files(self):
        payload = make_zip()
        key, source = self.setup_source(payload)
        with patch.dict(datasets._SOURCES, {key: source}), patch.object(
            datasets, "_download", side_effect=lambda url, dst, *, max_bytes: dst.write_bytes(payload)
        ):
            datasets.get(key, cache_dir=self.cache)
            before = datasets.cache_info(cache_dir=self.cache)
            unrelated = self.cache / "sources" / "notes.txt"
            unrelated.write_text("keep", encoding="utf-8")
            result = datasets.clear_cache("festival_icons", cache_dir=self.cache)
            self.assertEqual(result["removed_datasets"], [key])
            self.assertEqual(result["removed_bytes"], before["total_bytes"])
            self.assertFalse((self.cache / "sources" / key).exists())
            self.assertEqual(unrelated.read_text(encoding="utf-8"), "keep")
            self.assertEqual(datasets.cache_info(cache_dir=self.cache)["total_bytes"], 0)

    def test_clear_cache_all_removes_registered_ids_only(self):
        sources = self.cache / "sources"
        (sources / "festival_icons" / "v1").mkdir(parents=True)
        (sources / "festival_icons" / "v1" / "cached.bin").write_bytes(b"cache")
        (sources / "unknown_dataset").mkdir()
        (sources / "unknown_dataset" / "keep.bin").write_bytes(b"keep")
        result = datasets.clear_cache(cache_dir=self.cache)
        self.assertEqual(result["removed_datasets"], ["festival_icons"])
        self.assertEqual(result["removed_bytes"], len(b"cache"))
        self.assertTrue((sources / "unknown_dataset" / "keep.bin").is_file())

    def test_cache_management_rejects_symlinks(self):
        external = self.cache / "external"
        external.mkdir()
        protected = external / "keep.bin"
        protected.write_bytes(b"keep")
        sources = self.cache / "sources"
        sources.mkdir()
        (sources / "festival_icons").symlink_to(external, target_is_directory=True)
        with self.assertRaisesRegex(datasets.DatasetError, "symlink"):
            datasets.cache_info(cache_dir=self.cache)
        with self.assertRaisesRegex(datasets.DatasetError, "symlink"):
            datasets.clear_cache(cache_dir=self.cache)
        self.assertTrue(protected.is_file())

    def test_cache_management_rejects_non_directory_cache_root(self):
        cache_file = self.cache / "cache-file"
        cache_file.write_text("keep", encoding="utf-8")
        with self.assertRaisesRegex(datasets.DatasetError, "ディレクトリではありません"):
            datasets.cache_info(cache_dir=cache_file)
        with self.assertRaisesRegex(datasets.DatasetError, "ディレクトリではありません"):
            datasets.clear_cache(cache_dir=cache_file)
        self.assertEqual(cache_file.read_text(encoding="utf-8"), "keep")

    def test_tomato_classification(self):
        payload = make_zip(case="tomato-leaves")
        key, source = self.setup_source(payload, case="tomato-leaves")
        with patch.dict(datasets._SOURCES, {key: source}), patch.object(datasets, "_download", side_effect=lambda url, dst, *, max_bytes: dst.write_bytes(payload)):
            data = datasets.get(key, cache_dir=self.cache)
            self.assertEqual(data.kind, "classification")
            self.assertIsNotNone(data.train_dir)
            self.assertIsNone(data.test_dir)

    @unittest.skipUnless(importlib.util.find_spec("pandas"), "pandasが必要です")
    def test_detection_artifact_download_cache_and_dataframe(self):
        payload = make_detection_zip()
        key = "bangladeshi_ewaste_image"
        source = replace(datasets._SOURCES[key], sha256=hashlib.sha256(payload).hexdigest(),
                         archive_size=len(payload), image_count=1, class_names_ja=("電池ごみ",), published=True)
        with patch.dict(datasets._SOURCES, {key: source}), patch.object(
            datasets, "_download", side_effect=lambda url, dst, *, max_bytes: dst.write_bytes(payload)
        ):
            data = datasets.get(key, cache_dir=self.cache)
            frame = data.to_df()
            self.assertEqual(data.kind, "detection")
            self.assertEqual(data.splits, {"train": 1, "valid": 0, "test": 0})
            self.assertEqual(frame.loc[0, "boxes"][0]["class_name"], "battery")
            self.assertEqual(frame.loc[0, "boxes"][0]["class_name_ja"], "電池ごみ")
            self.assertEqual(data.quality_summary()["usable_images"], 1)
            cached = datasets.get(key, cache_dir=self.cache, allow_download=False)
            self.assertEqual(cached.root, data.root)

    def test_detection_artifact_label_mismatch_is_rejected(self):
        payload = make_detection_zip(corrupt_label=True)
        key = "bangladeshi_ewaste_image"
        source = replace(datasets._SOURCES[key], sha256=hashlib.sha256(payload).hexdigest(),
                         archive_size=len(payload), image_count=1, published=True)
        with patch.dict(datasets._SOURCES, {key: source}), patch.object(
            datasets, "_download", side_effect=lambda url, dst, *, max_bytes: dst.write_bytes(payload)
        ):
            with self.assertRaisesRegex(datasets.DatasetError, "範囲外"):
                datasets.get(key, cache_dir=self.cache)

    def test_rdd2020_rootless_archive_uses_dataset_specific_limits(self):
        payload = make_detection_zip(case="rdd2020_japan", root_folder=False)
        source = replace(
            datasets._SOURCES["rdd2020_japan"], sha256=hashlib.sha256(payload).hexdigest(),
            archive_size=len(payload), image_count=1, max_archive_bytes=len(payload),
            max_unpacked_bytes=1_000_000, max_files=20,
        )

        def download(url, destination, *, max_bytes):
            self.assertEqual(max_bytes, len(payload))
            destination.write_bytes(payload)

        with patch.dict(datasets._SOURCES, {"rdd2020_japan": source}), patch.object(
            datasets, "_download", side_effect=download
        ):
            data = datasets.get("rdd2020_japan", cache_dir=self.cache)
            self.assertEqual(data.kind, "detection")
            self.assertTrue((data.root / "manifest.json").is_file())
            self.assertTrue((data.root / "images/train/one.png").is_file())
            self.assertEqual(data.splits, {"train": 1, "valid": 0, "test": 0})

    def test_rdd2020_rootless_archive_rejects_parent_paths(self):
        payload = make_detection_zip(case="rdd2020_japan", root_folder=False, unsafe=True)
        source = replace(
            datasets._SOURCES["rdd2020_japan"], sha256=hashlib.sha256(payload).hexdigest(),
            archive_size=len(payload), image_count=1,
        )
        with patch.dict(datasets._SOURCES, {"rdd2020_japan": source}), patch.object(
            datasets, "_download", side_effect=lambda url, dst, *, max_bytes: dst.write_bytes(payload)
        ):
            with self.assertRaisesRegex(datasets.DatasetError, "安全でないZIP内のパス"):
                datasets.get("rdd2020_japan", cache_dir=self.cache)

    def test_lefood_pair_release_is_cached_and_split_counts_are_preserved(self):
        payload = make_regression_zip()
        source = replace(
            datasets._SOURCES["lefood_set"], sha256=hashlib.sha256(payload).hexdigest(),
            archive_size=len(payload), image_count=2, sample_count=1,
        )
        with patch.dict(datasets._SOURCES, {"lefood_set": source}), patch.object(
            datasets, "_download", side_effect=lambda url, dst, *, max_bytes: dst.write_bytes(payload)
        ):
            data = datasets.get("lefood_set", cache_dir=self.cache)
            self.assertEqual(data.kind, "regression")
            self.assertTrue((data.root / "manifest.json").is_file())
            self.assertTrue((data.root / "images/before/0001_before.jpg").is_file())
            self.assertEqual(data.splits, {"train": 1, "validation": 0, "test": 0})
            cached = datasets.get("lefood_set", cache_dir=self.cache, allow_download=False)
            self.assertEqual(cached.root, data.root)

    @unittest.skipUnless(importlib.util.find_spec("pandas"), "pandasが必要です")
    def test_lefood_dataframe_keeps_paired_paths_and_measured_targets(self):
        payload = make_regression_zip()
        source = replace(
            datasets._SOURCES["lefood_set"], sha256=hashlib.sha256(payload).hexdigest(),
            archive_size=len(payload), image_count=2, sample_count=1,
        )
        with patch.dict(datasets._SOURCES, {"lefood_set": source}), patch.object(
            datasets, "_download", side_effect=lambda url, dst, *, max_bytes: dst.write_bytes(payload)
        ):
            frame = datasets.get("lefood_set", cache_dir=self.cache).to_df()
        self.assertEqual(len(frame), 1)
        self.assertTrue(Path(frame.loc[0, "image_before_path"]).is_file())
        self.assertTrue(Path(frame.loc[0, "image_after_path"]).is_file())
        self.assertEqual(frame.loc[0, "weight_before_g"], 100.0)
        self.assertEqual(frame.loc[0, "consumed_weight_g"], 25.0)
        self.assertAlmostEqual(frame.loc[0, "leftover_ratio"], 0.75)

    def test_lefood_regression_validator_rejects_unsafe_paths_and_wrong_derived_values(self):
        for kwargs, message in (
            ({"unsafe_path": True}, "対応、sample_id、またはsplit"),
            ({"incorrect_ratio": True}, "計測値または導出列"),
        ):
            with self.subTest(kwargs=kwargs):
                payload = make_regression_zip(**kwargs)
                source = replace(
                    datasets._SOURCES["lefood_set"], sha256=hashlib.sha256(payload).hexdigest(),
                    archive_size=len(payload), image_count=2, sample_count=1,
                )
                with patch.dict(datasets._SOURCES, {"lefood_set": source}), patch.object(
                    datasets, "_download", side_effect=lambda url, dst, *, max_bytes: dst.write_bytes(payload)
                ):
                    with self.assertRaisesRegex(datasets.DatasetError, message):
                        datasets.get("lefood_set", cache_dir=self.cache)

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

    @unittest.skipUnless(importlib.util.find_spec("pandas"), "pandasが必要です")
    def test_indoor_plant_classification(self):
        payload = make_indoor_plant_zip()
        key = "indoor_plant_varieties"
        source = replace(
            datasets._SOURCES[key], sha256=hashlib.sha256(payload).hexdigest(),
            archive_size=len(payload), image_count=1, published=True,
        )
        with patch.dict(datasets._SOURCES, {key: source}), patch.object(
            datasets, "_download", side_effect=lambda url, dst, *, max_bytes: dst.write_bytes(payload)
        ):
            data = datasets.get(key, cache_dir=self.cache)
            frame = data.to_df()
            self.assertEqual(data.kind, "classification")
            self.assertEqual(frame.loc[0, "label_ja"], "アグラオネマ")
            self.assertEqual(data.classes, source.classes)
            self.assertEqual(data.splits, {"train": 1, "val": 0, "test": 0})

    def test_info_without_id_returns_catalog(self):
        catalog = datasets.info()
        self.assertIsInstance(catalog, list)
        self.assertEqual({item["id"] for item in catalog}, {"tomato_leaves", "festival_icons", "fruitseg30", "fresh_rotten_fruits", "road_traversing_knowledge", "rdd2020_japan", "lefood_set", "indoor_plant_varieties", "geoset_ennea", "bangladeshi_ewaste_image", "fabricspotdefect", "orange_fruit", "japanese_receipts_detailed", "indoor_waste_image", "wastesegcluster", "fire_recognition_image", "agrifreshnet", "brazil_road_potholes", "click_trash", "obstacles_assistance", "trashnet", "vifoodlabel", "energy_meter_digits"})

    def test_fashion_mnist_is_removed_from_catalog(self):
        ids = {item["id"] for item in datasets.list_available()}
        self.assertNotIn("fashion_mnist", ids)
        self.assertEqual(datasets.list_preview(), [])




if __name__ == "__main__":
    unittest.main()
