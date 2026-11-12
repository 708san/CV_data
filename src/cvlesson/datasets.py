"""固定タグの公開Releaseから画像データを読み取り専用で取得する最小実装。

配布元は変更せず、固定URL・サイズ・SHA-256を照合して安全に展開する。
"""
from __future__ import annotations

import csv
import gzip
import hashlib
import json
import math
import os
import re
import shutil
import stat
import struct
import tempfile
import time
import urllib.request
import urllib.error
import zipfile
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Any, Sequence


RELEASE_REPOSITORY = "https://github.com/708san/CV_sample_data"
MAX_ARCHIVE_BYTES = 160_000_000
MAX_UNPACKED_BYTES = 600_000_000
MAX_FILES = 12_000


class DatasetError(RuntimeError):
    """データの取得・検証に失敗した場合。"""


@dataclass(frozen=True)
class ReleaseSource:
    id: str
    case_id: str
    tag: str
    sha256: str
    archive_size: int
    image_count: int
    kind: str
    name_ja: str
    rights_note: str
    aliases_ja: tuple[str, ...]
    task: str = "classification"
    audiences: tuple[str, ...] = ("teacher",)
    difficulty: str = "introductory"
    use_cases_ja: tuple[str, ...] = ()
    input_description_ja: str = ""
    output_description_ja: str = ""
    download_size_mb: float | None = None
    audit_status: str = "not_run"
    audit_report: str | None = None
    classes: tuple[str, ...] = ()
    class_names_ja: tuple[str, ...] = ()
    label_names_ja: dict[str, str] | None = None
    license_info: dict[str, Any] | None = None
    source_info: dict[str, Any] | None = None
    preview: bool = False
    published: bool = True
    file_urls: dict[str, str] = field(default_factory=dict)
    file_sha256: dict[str, str] = field(default_factory=dict)
    file_sizes: dict[str, int] = field(default_factory=dict)
    archive_root_name: str | None = None
    sample_count: int | None = None
    max_archive_bytes: int = MAX_ARCHIVE_BYTES
    max_unpacked_bytes: int = MAX_UNPACKED_BYTES
    max_files: int = MAX_FILES
    archive_root_folder: bool = True

    @property
    def url(self) -> str:
        # case_id, tagはコード内で固定された値。ユーザー入力を組み込まない。
        if self.file_urls:
            return next(iter(self.file_urls.values()))
        return f"{RELEASE_REPOSITORY}/releases/download/{self.tag}/{self.case_id}.zip"


@dataclass(frozen=True)
class DatasetBundle:
    """取得したデータの参照。元の画像・ラベルには変更を加えない。"""
    id: str
    kind: str
    root: Path
    manifest: dict[str, Any]
    source_url: str
    version: str
    rights_note: str

    @property
    def classes(self) -> tuple[str, ...]:
        """分類データの英語ラベル。LoRA素材では空 tuple。"""
        return tuple(self.manifest.get("classes", ()))

    @property
    def task(self) -> str:
        """教材で選ぶ課題タイプ。分類とLoRA素材を明確に分ける。"""
        return _source(self.id).task

    @property
    def audiences(self) -> tuple[str, ...]:
        """利用条件を確認済みの対象。権利確認済みとは限らない。"""
        return _source(self.id).audiences

    @property
    def class_names_ja(self) -> tuple[str, ...]:
        """英語ラベルと同じ順番の日本語ラベル。"""
        source = _source(self.id)
        names = source.label_names_ja or {}
        if not names and len(source.class_names_ja) == len(self.classes):
            return source.class_names_ja
        return tuple(names.get(label, label) for label in self.classes)

    @property
    def license_info(self) -> dict[str, Any]:
        """データのライセンス情報。コードのライセンスとは別管理。"""
        return dict(_source(self.id).license_info or {})

    @property
    def source_info(self) -> dict[str, Any]:
        """固定Releaseと元データの出典情報。"""
        return dict(_source(self.id).source_info or {})

    @property
    def images_dir(self) -> Path:
        return self.root / "images"

    @property
    def masks_dir(self) -> Path:
        """領域分割データのグレースケールマスク保存先。"""
        return self.root / "masks"

    @property
    def labels_csv(self) -> Path:
        return self.root / "labels.csv"

    @property
    def metadata_csv(self) -> Path:
        """ペア画像回帰データの測定値と画像対応表。"""
        return self.root / "metadata.csv"

    @property
    def annotations_jsonl(self) -> Path:
        return self.root / "annotations.jsonl"

    @property
    def metadata_jsonl(self) -> Path:
        return self.root / "metadata.jsonl"

    @property
    def train_dir(self) -> Path | None:
        path = self.images_dir / "train"
        return path if path.is_dir() else None

    @property
    def test_dir(self) -> Path | None:
        path = self.images_dir / "test"
        return path if path.is_dir() else None

    def to_df(self, *, val_fraction: float = 0.1, seed: int = 42):
        """画像とラベル・測定値の対応をDataFrameに変換する。

        元Releaseに検証用分割がない場合、公式testを保持したまま、trainだけを
        クラス比率を保つ決定的な方法でtrain/valへ分ける。元画像やCSVは変更しない。
        """
        try:
            import pandas as pd
        except ImportError as exc:
            raise DatasetError("DataFrame変換にはpandasが必要です。pip install pandas を実行してください。") from exc
        if self.kind == "detection":
            names = self.classes
            records = []
            for line in self.annotations_jsonl.read_text(encoding="utf-8").splitlines():
                if not line.strip():
                    continue
                item = json.loads(line)
                boxes = [
                    {
                        **annotation,
                        "class_name": names[annotation["class_id"]],
                        "class_name_ja": self.class_names_ja[annotation["class_id"]],
                    }
                    for annotation in item["annotations"]
                ]
                image = item["file_name"]
                records.append({
                    "image_path": str((self.root / image).resolve()),
                    "label_file": str((self.root / item["label_file"]).resolve()),
                    "boxes": boxes,
                    "split": item["split"],
                    "sample_id": _sample_id(image),
                })
            return pd.DataFrame(records, columns=[
                "image_path", "label_file", "boxes", "split", "sample_id",
            ])
        if self.kind == "segmentation":
            records = self._segmentation_records()
            return pd.DataFrame(records, columns=[
                "image_path", "mask_path", "label", "label_ja", "label_id", "split", "sample_id",
            ])
        if self.kind == "regression":
            records = []
            for row in _read_rows(self.metadata_csv):
                records.append({
                    "sample_id": row["sample_id"],
                    "source_record_id": int(row["source_record_id"]),
                    "food_category": row["food_category"],
                    "food_name_original": row["food_name_original"],
                    "image_before_path": str((self.root / row["image_before"]).resolve()),
                    "image_after_path": str((self.root / row["image_after"]).resolve()),
                    "weight_before_g": float(row["weight_before_g"]),
                    "weight_after_g": float(row["weight_after_g"]),
                    "consumed_weight_g": float(row["consumed_weight_g"]),
                    "leftover_ratio": float(row["leftover_ratio"]),
                    "visual_leftover_level": int(row["visual_leftover_level"]),
                    "weight_order_anomaly": row["weight_order_anomaly"].lower() == "true",
                    "source_image_before": row["source_image_before"],
                    "source_image_after": row["source_image_after"],
                    "food_category_id": int(row["food_category_id"]),
                    "split": row["split"],
                })
            return pd.DataFrame(records)
        if self.kind == "ocr":
            records = []
            for row in _read_rows(self.labels_csv):
                records.append({
                    "image_path": str((self.root / row["image"]).resolve()),
                    "ground_truth": json.loads(row["record_json"]),
                    "split": row["split"],
                    "sample_id": row["sample_id"],
                })
            return pd.DataFrame(records, columns=["image_path", "ground_truth", "split", "sample_id"])
        rows = _read_rows(self.labels_csv)
        if self.kind != "classification":
            return pd.DataFrame([
                {
                    "image_path": str((self.root / row["image"]).resolve()),
                    "caption": row["caption"],
                    "sample_id": _sample_id(row["image"]),
                }
                for row in rows
            ], columns=["image_path", "caption", "sample_id"])

        records = self._classification_records(val_fraction=val_fraction, seed=seed)
        return pd.DataFrame(records, columns=[
            "image_path", "label", "label_ja", "label_id", "split",
            "sample_id", "group_id", "source_split",
        ])

    def _classification_records(self, *, val_fraction: float = 0.1, seed: int = 42) -> list[dict[str, Any]]:
        rows = _read_rows(self.labels_csv)
        effective_splits = _effective_splits(rows, val_fraction=val_fraction, seed=seed)
        class_to_id = {label: i for i, label in enumerate(self.classes)}
        ja = dict(zip(self.classes, self.class_names_ja))
        records: list[dict[str, Any]] = []
        for row, split in zip(rows, effective_splits):
            image = row["image"]
            records.append({
                "image_path": str((self.root / image).resolve()),
                "label": row["label"],
                "label_ja": ja.get(row["label"], row["label"]),
                "label_id": class_to_id[row["label"]],
                "split": split,
                "sample_id": _sample_id(image),
                "group_id": row.get("group_id") or None,
                "source_split": row["split"],
            })
        return records

    def _segmentation_records(self) -> list[dict[str, Any]]:
        names_ja = dict(zip(self.classes, self.class_names_ja))
        records = []
        for row in _read_rows(self.labels_csv):
            image = row["image"]
            label = row["class_name"]
            records.append({
                "image_path": str((self.root / image).resolve()),
                "mask_path": str((self.root / row["mask"]).resolve()),
                "label": "複数クラスの画素マスク" if label == "__pixel_labels__" else label,
                "label_ja": "複数クラスの画素マスク" if label == "__pixel_labels__" else names_ja.get(label, label),
                "label_id": int(row["class_id"]),
                "split": row["split"],
                "sample_id": _sample_id(image),
            })
        return records

    @property
    def splits(self) -> dict[str, int]:
        """標準化後のtrain/val/test件数。"""
        if self.kind == "regression":
            counts = Counter(row["split"] for row in _read_rows(self.metadata_csv))
            return {name: int(counts.get(name, 0)) for name in ("train", "validation", "test")}
        if self.kind == "detection":
            counts = Counter()
            for line in self.annotations_jsonl.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    counts[json.loads(line)["split"]] += 1
            return {name: int(counts.get(name, 0)) for name in ("train", "valid", "test")}
        if self.kind == "segmentation":
            counts = Counter(row["split"] for row in _read_rows(self.labels_csv))
            return {name: int(counts.get(name, 0)) for name in ("train", "val", "test")}
        if self.kind != "classification":
            return {}
        rows = _read_rows(self.labels_csv)
        effective = _effective_splits(rows, val_fraction=0.1, seed=42)
        counts = Counter(effective)
        return {name: int(counts.get(name, 0)) for name in ("train", "val", "test")}

    def show_examples(self, n: int = 9, *, split: str | None = None, seed: int = 42):
        """画像例を表示する。表示にはPillowとmatplotlibが必要。"""
        if n <= 0:
            raise ValueError("nは1以上にしてください。")
        try:
            import matplotlib.pyplot as plt
            import numpy as np
            from PIL import Image
        except ImportError as exc:
            raise DatasetError("画像表示にはPillowとmatplotlibが必要です。") from exc
        frame = self.to_df(seed=seed)
        if self.kind == "regression":
            if split == "val":
                split = "validation"
            if split is not None:
                if split not in {"train", "validation", "test"}:
                    raise ValueError("splitはtrain、validation、testのいずれかです。")
                frame = frame[frame["split"] == split]
            if frame.empty:
                raise DatasetError("表示できる画像ペアがありません。")
            selected = frame.sample(n=min(n, len(frame)), random_state=seed).reset_index(drop=True)
            figure, axes = plt.subplots(len(selected), 2, squeeze=False,
                                        figsize=(8, max(3, len(selected) * 2.4)))
            for index, record in selected.iterrows():
                cells = (
                    (axes[index, 0], record["image_before_path"], f"食前 {record['weight_before_g']:g} g"),
                    (axes[index, 1], record["image_after_path"],
                     f"食後 {record['weight_after_g']:g} g / 残量比 {record['leftover_ratio']:.2f}"),
                )
                for axis, image_path, title in cells:
                    with Image.open(image_path) as image:
                        axis.imshow(image.convert("RGB"))
                    axis.set_title(title)
                    axis.axis("off")
            figure.tight_layout()
            plt.show()
            return figure
        if split == "val" and self.kind == "detection":
            split = "valid"
        if split is not None:
            valid_splits = {"train", "val", "valid", "test"}
            if split not in valid_splits:
                raise ValueError("splitはtrain、valid（またはval）、testのいずれかです。")
            frame = frame[frame["split"] == split]
        if frame.empty:
            raise DatasetError("表示できる画像がありません。")
        selected = frame.sample(n=min(n, len(frame)), random_state=seed)
        columns = min(3, len(selected))
        rows = (len(selected) + columns - 1) // columns
        figure, axes = plt.subplots(rows, columns, squeeze=False, figsize=(columns * 3, rows * 3))
        for axis, (_, record) in zip(axes.flat, selected.iterrows()):
            with Image.open(record["image_path"]) as image:
                axis.imshow(image.convert("RGB"))
            title = record.get("label_ja", record.get("caption", ""))
            if self.kind == "segmentation":
                with Image.open(record["mask_path"]) as mask:
                    mask_values = np.asarray(mask.convert("L"))
                    if self.manifest.get("mask_encoding") == "class_id_grayscale":
                        axis.imshow(
                            mask_values,
                            cmap="tab20",
                            vmin=-0.5,
                            vmax=max(0.5, len(self.classes) - 0.5),
                            alpha=0.5,
                            interpolation="nearest",
                        )
                    else:
                        axis.imshow(mask_values, cmap="Reds", vmin=0, vmax=255, alpha=0.45)
            if self.kind == "detection":
                from matplotlib.patches import Rectangle
                boxes = record["boxes"]
                title = ", ".join(dict.fromkeys(box["class_name"] for box in boxes)) or "対象ラベルなし"
                with Image.open(record["image_path"]) as image:
                    width, height = image.size
                for box in boxes:
                    left = (box["x_center"] - box["width"] / 2) * width
                    top = (box["y_center"] - box["height"] / 2) * height
                    axis.add_patch(Rectangle(
                        (left, top), box["width"] * width, box["height"] * height,
                        fill=False, edgecolor="yellow", linewidth=2,
                    ))
                    axis.text(left, top, box.get("class_name_ja", box["class_name"]), color="black", fontsize=7,
                              bbox={"facecolor": "yellow", "alpha": 0.75, "pad": 1})
            axis.set_title(title)
            axis.axis("off")
        for axis in axes.flat[len(selected):]:
            axis.axis("off")
        figure.tight_layout()
        plt.show()
        return figure

    def to_torch_dataset(
        self,
        *,
        split: str = "train",
        image_size: tuple[int, int] = (64, 64),
        val_fraction: float = 0.1,
        seed: int = 42,
    ):
        """画像を遅延読み込みするPyTorch Datasetへ変換する。"""
        if self.kind not in {"classification", "segmentation"}:
            raise DatasetError("PyTorch変換は画像分類と領域分割データに対応しています。")
        if split not in {"train", "val", "test"}:
            raise ValueError("splitはtrain、val、testのいずれかです。")
        if len(image_size) != 2 or any(not isinstance(x, int) or x <= 0 for x in image_size):
            raise ValueError("image_sizeは正の整数2つのtupleで指定してください。")
        try:
            import torch
        except ImportError as exc:
            raise DatasetError("PyTorch変換にはtorchが必要です。") from exc
        all_records = (self._segmentation_records() if self.kind == "segmentation"
                       else self._classification_records(val_fraction=val_fraction, seed=seed))
        records = [record for record in all_records if record["split"] == split]
        if not records:
            raise DatasetError(f"split={split}に画像がありません。")
        dataset_type = _TorchSegmentationDataset if self.kind == "segmentation" else _TorchClassificationDataset
        if self.kind == "segmentation":
            return dataset_type(
                records,
                image_size=image_size,
                torch_module=torch,
                mask_encoding=self.manifest.get("mask_encoding", "grayscale_0_255"),
                class_count=len(self.classes),
            )
        return dataset_type(records, image_size=image_size, torch_module=torch)

    def quality_summary(self, *, seed: int = 42, val_fraction: float = 0.1) -> dict[str, Any]:
        """標準化後の件数と分割方法を機械可読な辞書で返す。"""
        if self.kind == "detection":
            frame = self.to_df()
            object_counts = Counter(box["class_name"] for row in frame["boxes"] for box in row)
            return {
                "dataset_id": self.id, "kind": self.kind, "usable_images": int(len(frame)),
                "objects_by_class": dict(sorted(object_counts.items())), "splits": self.splits,
                "validated_at": _utc_now(),
            }
        if self.kind == "segmentation":
            frame = self.to_df()
            return {
                "dataset_id": self.id, "kind": self.kind,
                "usable_images": int(len(frame)),
                "classes": {str(k): int(v) for k, v in frame["label"].value_counts().sort_index().items()},
                "splits": self.splits, "validated_at": _utc_now(),
            }
        if self.kind == "regression":
            frame = self.to_df()
            return {
                "dataset_id": self.id, "kind": self.kind, "usable_pairs": int(len(frame)),
                "weight_order_anomalies": int(frame["weight_order_anomaly"].sum()),
                "splits": self.splits, "validated_at": _utc_now(),
            }
        if self.kind != "classification":
            return {"dataset_id": self.id, "kind": self.kind, "validated_at": _utc_now()}
        frame = self.to_df(seed=seed, val_fraction=val_fraction)
        return {
            "dataset_id": self.id,
            "kind": self.kind,
            "usable_images": int(len(frame)),
            "classes": {str(k): int(v) for k, v in frame["label"].value_counts().sort_index().items()},
            "splits": {name: int((frame["split"] == name).sum()) for name in ("train", "val", "test")},
            "split_method": "official_test_preserved; deterministic_stratified_train_val",
            "split_seed": seed,
            "val_fraction": val_fraction,
            "validated_at": _utc_now(),
        }


_SOURCES: dict[str, ReleaseSource] = {
    "rdd2020_japan": ReleaseSource(
        id="rdd2020_japan", case_id="rdd2020_japan", tag="rdd2020-japan-v0.1.0",
        sha256="f787feead7fd3b0d63f42c7cfb8e3db6f114e57c83b3b928d5f7c58bcb411955",
        archive_size=641_514_873, image_count=7900,
        kind="detection", name_ja="RDD2020 日本の道路損傷",
        rights_note=(
            "CC BY-NC 3.0。非商用の教育目的に限って利用できます。出典・変更内容を表示してください。"
            "商用利用はできません。2020年頃の道路画像で、現在の安全性や修繕順位は判断できません。"
        ),
        aliases_ja=("RDD2020", "日本の道路損傷", "道路のひび・穴"),
        task="detection", audiences=("student", "teacher"), difficulty="intermediate",
        use_cases_ja=(
            "通学路や地域道路のひび・穴を画像から探し、道路管理者へ相談する資料を作る",
            "検出結果と画像を照らし合わせ、見落としや誤検出を調べる",
        ),
        input_description_ja="日本の道路を車載スマートフォンで撮影した画像",
        output_description_ja="縦ひび・横ひび・亀甲ひび・ポットホールの位置と種類",
        download_size_mb=641.5, audit_status="full_source_image_and_annotation_audit_sample_visual_review",
        audit_report="docs/datasets/rdd2020_japan.md",
        classes=("D00", "D10", "D20", "D40"),
        class_names_ja=("縦ひび", "横ひび", "亀甲ひび", "ポットホール"),
        license_info={
            "name": "CC BY-NC 3.0",
            "url": "https://creativecommons.org/licenses/by-nc/3.0/",
            "rights_review": "Mendeley Data固定v2の表示を確認。非商用の教育利用に限定し、帰属・変更表示が必要。",
        },
        source_info={
            "dataset_name": "RDD2020: An Image Dataset for Smartphone-based Road Damage Detection and Classification",
            "provider": "Deeksha Arya et al. (2021)",
            "url": "https://doi.org/10.17632/5ty2wb6gvg.2",
            "release_repository": "https://github.com/708san/CV_data_artifacts",
            "release_tag": "rdd2020-japan-v0.1.0",
        },
        file_urls={
            "artifact": "https://github.com/708san/CV_data_artifacts/releases/download/rdd2020-japan-v0.1.0/rdd2020-japan-v0.1.0.zip",
        },
        max_archive_bytes=700_000_000, max_unpacked_bytes=700_000_000,
        max_files=20_000, archive_root_folder=False,
    ),
    "lefood_set": ReleaseSource(
        id="lefood_set", case_id="lefood_set", tag="lefood-set-v0.1.0",
        sha256="ca1846273d0636ea59f387a586c6f004cfc02d58a639ad5a3c7c844b66cb863a",
        archive_size=53_035_809, image_count=1048, sample_count=524,
        kind="regression", name_ja="LeFood-Set 食べ残しの計測",
        rights_note=(
            "CC BY 4.0。出典と変更内容を表示してください。インドネシアの病院食研究の画像で、"
            "日本の学校給食を代表しません。健康・栄養・医療の判断には使わないでください。"
        ),
        aliases_ja=("食べ残し画像ペア", "食事前後の重量", "LeFood-Set"),
        task="regression", audiences=("student", "teacher"), difficulty="introductory",
        use_cases_ja=(
            "食前・食後の画像を見比べ、見た目の評価と実測重量の関係を調べる",
            "家庭や学校で食べ残しを減らすために、どんな計測が必要か考える",
        ),
        input_description_ja="料理の食前・食後画像と食前・食後の実測重量",
        output_description_ja="実測重量差と7段階の見た目評価。残量比を画像から推定する課題にも使えます。",
        download_size_mb=53.0, audit_status="all_source_images_decoded_and_pairs_visually_reviewed",
        audit_report="docs/datasets/lefood_set.md",
        license_info={
            "name": "CC BY 4.0",
            "url": "https://creativecommons.org/licenses/by/4.0/",
            "rights_review": "Mendeley Data v1と論文の表示を確認。出典・ライセンス・変更表示が必要。",
        },
        source_info={
            "dataset_name": "LeFood-Set: Leftovers Food Dataset",
            "provider": "Sari, Yuita Arum; Wani, Yudi Arimba; Nakazawa, Atsushi (2025)",
            "url": "https://doi.org/10.17632/cchsk79jkt.1",
            "release_repository": "https://github.com/708san/CV_data_artifacts",
            "release_tag": "lefood-set-v0.1.0",
        },
        file_urls={
            "artifact": "https://github.com/708san/CV_data_artifacts/releases/download/lefood-set-v0.1.0/lefood-set-v0.1.0.zip",
        },
        archive_root_name="lefood-set-v0.1.0",
    ),
    "tomato_leaves": ReleaseSource(
        id="tomato_leaves", case_id="tomato-leaves", tag="tomato-v1.2.0",
        sha256="506560a5ce57394fd739fa73ac3b997a2646f87ea04257334dacb54497e0e1fa",
        archive_size=124_334_101, image_count=7209,
        kind="classification", name_ja="トマトの葉（5種類の分類）",
        rights_note="元データはCC0 1.0。出典と派生処理の説明を確認してください。",
        aliases_ja=("トマトの葉", "トマト葉"),
        task="classification",
        audiences=("student", "teacher"),
        difficulty="introductory",
        use_cases_ja=("植物の葉の状態を分類する", "分類結果と誤分類を確かめる"),
        input_description_ja="トマトの葉の画像",
        output_description_ja="5種類のラベル",
        download_size_mb=118.5,
        audit_status="full_image_audit",
        audit_report="reports/tomato-leaves-v1.2.0.json",
        class_names_ja=("輪紋病", "健全", "疫病", "白星病", "葉かび病"),
        label_names_ja={
            "early_blight": "輪紋病", "healthy": "健全", "late_blight": "疫病",
            "septoria_leaf_spot": "白星病", "leaf_mold": "葉かび病",
        },
        license_info={
            "name": "CC0 1.0",
            "url": "https://creativecommons.org/publicdomain/zero/1.0/",
            "rights_review": "配布元の表記を確認。教材での再配布承認は別途確認が必要。",
        },
        source_info={
            "dataset_name": "Data for: Identification of Plant Leaf Diseases Using a 9-layer Deep Convolutional Neural Network",
            "provider": "Pandianj, Arun; Geetharamanigopal (2019)",
            "url": "https://doi.org/10.17632/tywbtsjrjv.1",
            "release_repository": RELEASE_REPOSITORY,
            "release_tag": "tomato-v1.2.0",
        },
    ),
    "bangladeshi_ewaste_image": ReleaseSource(
        id="bangladeshi_ewaste_image", case_id="bangladeshi_ewaste",
        tag="bangladeshi-ewaste-v0.1.0",
        sha256="70f1bc03d605922370611a7b326d1647fd2bddf030e2acb95c60f55edb6eb6f3",
        archive_size=71_712_360, image_count=2157,
        kind="detection", name_ja="廃棄物品の物体検出（12種類）",
        rights_note="CC BY 4.0。作者・出典・変更の表示が必要。画像は撮影現場を再現せず、実際の分別・医療廃棄物処理には使わないでください。",
        aliases_ja=("廃棄物品の物体検出", "電子ごみ検出", "廃棄物画像"),
        task="detection", audiences=("student", "teacher"), difficulty="intermediate",
        use_cases_ja=("画像の中の廃棄物品を囲んで種類を付ける", "電子品・紙・金属などの画像を見比べる"),
        input_description_ja="緑色の布上で撮影され、640×640に整えられた廃棄物品画像",
        output_description_ja="物体の位置を囲む枠と12種類のラベル",
        download_size_mb=71.7, audit_status="full_image_and_annotation_audit",
        audit_report="docs/datasets/bangladeshi_ewaste_image.md",
        class_names_ja=(
            "電池ごみ", "ガラスごみ", "キーボード", "電球", "医療廃棄物", "金属ごみ",
            "携帯電話", "マウス", "生ごみ", "基板", "紙ごみ", "プラスチックごみ",
        ),
        license_info={"name": "CC BY 4.0", "url": "https://creativecommons.org/licenses/by/4.0/",
                      "rights_review": "公式ページとアーカイブ内READMEの表示を確認。作者・出典・変更表示を収録。"},
        source_info={
            "dataset_name": "Custom Bangladeshi E-Waste Image Dataset for Object Detection and Recognition",
            "provider": "Tanzila Afrin; Azizul Abedin Azmi",
            "url": "https://doi.org/10.17632/77383kmdnw.1",
            "release_repository": "https://github.com/708san/CV_data_artifacts",
            "release_tag": "bangladeshi-ewaste-v0.1.0",
        },
        file_urls={"artifact": "https://github.com/708san/CV_data_artifacts/releases/download/bangladeshi-ewaste-v0.1.0/bangladeshi_ewaste-v0.1.0.zip"},
        published=True,
    ),
    "recyclable_waste": ReleaseSource(
        id="recyclable_waste", case_id="recyclable_waste", tag="recyclable-waste-v0.1.1",
        sha256="71d71622b65c44d2748e296ff23e8ed49c2f3e4e788301f1d9128d34e0affd1f",
        archive_size=93_564_328, image_count=976, kind="classification",
        name_ja="リサイクル素材の画像（5種類）",
        rights_note="CC BY 4.0。作者・出典・変更を表示してください。撮影地の分別規則や実際の分別判断には使わないでください。",
        aliases_ja=("リサイクルごみ画像", "ごみ素材分類", "廃棄物素材の分類"),
        task="classification", audiences=("student", "teacher"), difficulty="introductory",
        use_cases_ja=("画像から紙・ガラスなどの素材を分類する", "背景や包装の写り方が分類に与える影響を比べる"),
        input_description_ja="ポルトガルで集められた段ボール・ガラス・金属・紙・プラスチックの画像",
        output_description_ja="5種類の素材ラベル",
        download_size_mb=89.2, audit_status="full_image_and_annotation_audit",
        audit_report="docs/datasets/recyclable_waste.md",
        classes=("cardboard", "glass", "metal", "paper", "plastic"),
        class_names_ja=("段ボール", "ガラス", "金属", "紙", "プラスチック"),
        license_info={"name": "CC BY 4.0", "url": "https://creativecommons.org/licenses/by/4.0/",
                      "rights_review": "Mendeley Data v1のCC BY 4.0表示と投稿者による収集説明を確認。出典・変更表示を収録。"},
        source_info={"dataset_name": "Recyclable Waste Image Dataset", "provider": "João Alves",
                     "url": "https://data.mendeley.com/datasets/h5pxbsdz4m/1", "doi": "10.17632/h5pxbsdz4m.1",
                     "release_repository": "https://github.com/708san/CV_data_artifacts", "release_tag": "recyclable-waste-v0.1.1"},
        file_urls={"artifact": "https://github.com/708san/CV_data_artifacts/releases/download/recyclable-waste-v0.1.1/recyclable_waste-v0.1.1.zip"},
        published=False,
    ),
    "pust_cafeteria_food": ReleaseSource(
        id="pust_cafeteria_food", case_id="pust_cafeteria_food", tag="pust-cafeteria-food-v0.1.0",
        sha256="97def37fae5a2368f4d0ea7bc4cffc0d299173b7581f49ad97bb43d08f496b4f",
        archive_size=36_085_147, image_count=691, kind="detection",
        name_ja="大学食堂の料理画像（16種類）",
        rights_note="CC BY 4.0。作者・出典・polygonから枠への変更を表示してください。栄養・アレルギー・衛生・価格は判定しません。",
        aliases_ja=("大学食堂の料理検出", "食堂メニュー画像", "料理の物体検出"),
        task="detection", audiences=("student", "teacher"), difficulty="intermediate",
        use_cases_ja=("料理画像の中から料理を見つけて囲む", "食堂で見かける料理の種類を画像から数える"),
        input_description_ja="バングラデシュの大学食堂で撮影された料理画像",
        output_description_ja="16種類の料理ラベルと物体位置の枠",
        download_size_mb=34.4, audit_status="full_image_and_annotation_audit",
        audit_report="docs/datasets/pust_cafeteria_food.md",
        classes=("chaa", "chola", "chop", "daal", "egg", "fish", "mashed_potato", "matha",
                 "meat", "puri", "rice", "ruti", "salad", "singara", "vegetable", "vegetable_roll"),
        class_names_ja=("チャー", "ひよこ豆料理", "揚げ物", "豆料理", "卵", "魚", "マッシュポテト", "マータ",
                        "肉料理", "プリ", "ごはん", "ロティ", "サラダ", "シンガラ", "野菜料理", "野菜ロール"),
        license_info={"name": "CC BY 4.0", "url": "https://creativecommons.org/licenses/by/4.0/",
                      "rights_review": "Mendeley Data v2のCC BY 4.0表示を確認。出典・変更表示を収録。"},
        source_info={"dataset_name": "PUST Cafeteria Food Dataset", "provider": "Marufa Yeasmin; Md. Razu Ahmed; Protiva Rani Kundu; Jannatul Mauya; Md. Shamim Reza",
                     "url": "https://data.mendeley.com/datasets/fn6yhzjz83/2", "doi": "10.17632/fn6yhzjz83.2", 
                     "release_repository": "https://github.com/708san/CV_data_artifacts", "release_tag": "pust-cafeteria-food-v0.1.0"},
        file_urls={"artifact": "https://github.com/708san/CV_data_artifacts/releases/download/pust-cafeteria-food-v0.1.0/pust_cafeteria_food-v0.1.0.zip"},
        published=True,
    ),
    "fashion_mnist": ReleaseSource(
        id="fashion_mnist", case_id="fashion_mnist", tag="fashion-mnist-v0.1.0",
        sha256="7b62741950bb9784980c9703806df874a1f1c3930dcc8a84477e2c6b5c6e871f",
        archive_size=45_813_814, image_count=70_000, kind="classification",
        name_ja="Fashion-MNIST（衣類画像10種類）",
        rights_note="元データはMIT License表記です。提供元・出典を確認し、低解像度の教材用データとして扱ってください。",
        aliases_ja=("ファッションMNIST", "衣類MNIST"),
        task="classification", audiences=("student", "teacher"), difficulty="introductory",
        use_cases_ja=("衣類画像を10種類に分類する", "正解率とクラス別の間違いを比べる"),
        input_description_ja="28×28画素の白黒衣類画像",
        output_description_ja="10種類の衣類・靴・バッグのラベル",
        download_size_mb=43.7, audit_status="full_image_and_annotation_audit",
        audit_report="docs/datasets/fashion_mnist.md",
        classes=("T-shirt_top", "Trouser", "Pullover", "Dress", "Coat", "Sandal", "Shirt", "Sneaker", "Bag", "Ankle_boot"),
        class_names_ja=("Tシャツ・トップス", "ズボン", "プルオーバー", "ワンピース", "コート", "サンダル", "シャツ", "スニーカー", "バッグ", "アンクルブーツ"),
        license_info={"name": "MIT License", "url": "https://github.com/zalandoresearch/fashion-mnist/blob/b2617bb6d3ffa2e429640350f613e3291e10b141/LICENSE",
                      "rights_review": "公式リポジトリの固定コミットにあるMIT表記を確認。整形済みデータの出典と変更内容を収録。"},
        source_info={"dataset_name": "Fashion-MNIST", "provider": "Zalando Research",
                     "url": "https://github.com/zalandoresearch/fashion-mnist/tree/b2617bb6d3ffa2e429640350f613e3291e10b141",
                     "commit": "b2617bb6d3ffa2e429640350f613e3291e10b141",
                     "release_repository": "https://github.com/708san/CV_data_artifacts", "release_tag": "fashion-mnist-v0.1.0"},
        file_urls={"artifact": "https://github.com/708san/CV_data_artifacts/releases/download/fashion-mnist-v0.1.0/fashion_mnist-v0.1.0.zip"},
        max_files=75_000, max_unpacked_bytes=450_000_000, published=True,
    ),
    "geoset_ennea": ReleaseSource(
        id="geoset_ennea", case_id="geoset_ennea", tag="geoset-ennea-v0.1.0",
        sha256="6185c0f8e631ec36913b6c229d4fbd51463d2a4fea1084f3c3e8021244ecd6e3",
        archive_size=7_531_941, image_count=136,
        kind="detection", name_ja="GeoSetEnnea（製図用具9種類の物体検出）",
        rights_note="CC BY 4.0。作者・出典・変更内容を表示してください。文具の商品名・ロゴが一部に写りますが、推薦・提携を示しません。",
        aliases_ja=("GeoSetEnnea", "製図用具の物体検出", "文具の物体検出"),
        task="detection", audiences=("student", "teacher"), difficulty="intermediate",
        use_cases_ja=("机の上の製図用具を見つけて数える", "片付ける前後の文具の場所を比べる"),
        input_description_ja="バングラデシュの文具店・図書館などで撮影した製図用具の画像",
        output_description_ja="136枚の画像に付いた9種類・1,188個の物体位置ラベル",
        download_size_mb=7.2, audit_status="full_image_and_annotation_audit",
        audit_report="reports/geoset_ennea-v1-audit.json",
        classes=(
            "Compass", "Divider", "Eraser", "Pencil", "Protractor_180deg",
            "Scale_15cm", "Set_Square_45deg", "Set_Square_60deg", "Sharpener",
        ),
        class_names_ja=(
            "コンパス", "ディバイダー", "消しゴム", "鉛筆", "分度器",
            "15cm定規", "45度三角定規", "60度三角定規", "鉛筆削り",
        ),
        license_info={
            "name": "CC BY 4.0",
            "url": "https://creativecommons.org/licenses/by/4.0/",
            "rights_review": "Mendeley Data v1の表示と著者による撮影説明を確認。136枚に絞り、出典・変更表示を収録。商品名・ロゴは付随的に写り、権利者の推薦を意味しません。",
        },
        source_info={
            "dataset_name": "GeoSetEnnea: A Multi-Class Image Dataset for Object Detection of Geometric Tools",
            "provider": "Sakhawat Hossain; Md Sadman Haque; Sadia Islam (2025)",
            "url": "https://data.mendeley.com/datasets/fg97mhsdbr/1",
            "doi": "10.17632/fg97mhsdbr.1",
            "release_repository": "https://github.com/708san/CV_data_artifacts",
            "release_tag": "geoset-ennea-v0.1.0",
        },
        file_urls={
            "artifact": "https://github.com/708san/CV_data_artifacts/releases/download/geoset-ennea-v0.1.0/geoset_ennea-v0.1.0.zip",
        },
        published=True,
    ),
    "road_traversing_knowledge": ReleaseSource(
        id="road_traversing_knowledge", case_id="road_traversing_knowledge",
        tag="road-traversing-knowledge-v0.1.0",
        sha256="e427708f7c31c85502e6ff06b0f94fb9e5b379e11bb6983d531fc242d189a63a",
        archive_size=101_584_942, image_count=701,
        kind="segmentation", name_ja="道路環境の領域分割（13クラス）",
        rights_note="CC BY 4.0。元データの著者・出典・共通形式への整理を表示します。道路の危険度や通行可否を判定する用途には使いません。",
        aliases_ja=("道路環境の領域分割", "道路のひび・穴の画像"),
        task="segmentation", audiences=("student", "teacher"), difficulty="intermediate",
        use_cases_ja=("通学路や地域の道路画像から、路面や水たまりなどの領域を分ける", "画素マスクを色分けして道路環境を見比べる"),
        input_description_ja="ブラジルの地方道路を撮影した352×288のPNG画像",
        output_description_ja="背景を含む13種類の画素クラスを示すIDマスク",
        download_size_mb=96.9, audit_status="full_image_and_mask_audit",
        classes=(
            "background", "road_asphalt", "road_paved", "road_unpaved", "road_marking",
            "speed_bump", "cats_eye", "storm_drain", "manhole_cover", "road_patch",
            "water_puddle", "pothole", "road_crack",
        ),
        class_names_ja=(
            "背景", "アスファルト舗装", "舗装道路", "未舗装道路", "道路標示",
            "減速帯", "道路鋲（キャッツアイ）", "雨水ます", "マンホール", "舗装補修跡",
            "水たまり", "道路の穴", "道路のひび割れ",
        ),
        label_names_ja={"__pixel_labels__": "複数クラスの画素マスク"},
        license_info={
            "name": "CC BY 4.0",
            "url": "https://creativecommons.org/licenses/by/4.0/",
            "rights_review": "固定版のMendeley Data掲載ライセンスを確認。著者・出典・画像再圧縮の変更表示を付けます。",
        },
        source_info={
            "dataset_name": "Road Traversing Knowledge",
            "provider": "Thiago Rateke; Aldo von Wangenheim; Rafael Toledo",
            "url": "https://doi.org/10.17632/hssswvmjwf.1",
            "source_file": "RTK.zip",
            "source_file_id": "2c72e75d-1f50-457a-86f0-a5e3a4174df9",
            "source_sha256": "78803e8df89eae6130139ee9c48de947edd08015fe56826c30fdacb2599841db",
            "release_repository": "https://github.com/708san/CV_data_artifacts",
            "release_tag": "road-traversing-knowledge-v0.1.0",
        },
        file_urls={
            "artifact": "https://github.com/708san/CV_data_artifacts/releases/download/road-traversing-knowledge-v0.1.0/road_traversing_knowledge-v0.1.0.zip",
        },
        published=True,
    ),
    "fabricspotdefect": ReleaseSource(
        id="fabricspotdefect", case_id="fabricspotdefect",
        tag="fabricspotdefect-v0.1.0",
        sha256="b40dca04e3879e92533face725d4e12bbfe9ba85e41b1c7ef59e290f1421943d",
        archive_size=744_311_786, image_count=1014,
        kind="detection", name_ja="衣類の汚れの位置（FabricSpotDefect）",
        rights_note="CC BY 4.0。出典・変更表示が必要です。見た目の汚れ候補を示す学習用で、衣類の清潔さ・着用可否・安全性は判定できません。",
        aliases_ja=("布の汚れ検出", "FabricSpotDefect"),
        task="detection", audiences=("student", "teacher"), difficulty="intermediate",
        use_cases_ja=("洗濯前に衣類の目立つ汚れを見つける補助を試作する", "布の柄や照明によって汚れの見つけやすさがどう変わるか調べる"),
        input_description_ja="家庭の布をスマートフォンで撮影した、サイズの異なるJPEG画像",
        output_description_ja="画像中のspot（汚れ・変色など）の位置を囲む矩形",
        download_size_mb=744.3, audit_status="full_image_decode_annotation_and_sample_visual_review",
        audit_report="reports/fabricspotdefect-v1-audit.json",
        classes=("spot",), class_names_ja=("汚れなどの目立つ跡",),
        license_info={
            "name": "CC BY 4.0",
            "url": "https://creativecommons.org/licenses/by/4.0/",
            "rights_review": "Mendeley Data v1のCC BY 4.0表示、著者による家庭の布の撮影説明、論文を確認。出典と共通形式への変更を同梱。",
        },
        source_info={
            "dataset_name": "FabricSpotDefect: An Annotated Dataset for Identifying Spot Defects in Different Fabric Types",
            "provider": "Sumaya; Farzana Islam; Md. Fahad Monir; Ashraful Islam",
            "url": "https://data.mendeley.com/datasets/6574nhzm8x/1",
            "doi": "10.17632/6574nhzm8x.1",
            "source_file": "Mendeley Data v1 ZIP",
            "source_sha256": "2e4fd58488734fe3b888c0c3633ca4d68da76f3a96f1e9bba08ec710645d6ab2",
            "release_repository": "https://github.com/708san/CV_data_artifacts",
            "release_tag": "fabricspotdefect-v0.1.0",
        },
        file_urls={
            "artifact": "https://github.com/708san/CV_data_artifacts/releases/download/fabricspotdefect-v0.1.0/fabricspotdefect-v0.1.0.zip",
        },
        max_archive_bytes=800_000_000, max_unpacked_bytes=800_000_000,
        max_files=5000, published=True,
    ),
    "bdroadsigns": ReleaseSource(
        id="bdroadsigns", case_id="bdroadsigns", tag="bdroadsigns-v0.1.0",
        sha256="33ab933d0a4f2e93104330ba0a22890ff47576e1a88e16810660c1afa146a20a",
        archive_size=191_037_362, image_count=5136,
        kind="classification", name_ja="バングラデシュの交通標識18種類",
        rights_note="CC BY 4.0。出典・変更表示が必要です。バングラデシュの標識画像を使う学習用で、日本の交通標識や実際の交通判断には使えません。",
        aliases_ja=("BDRoadSigns", "バングラデシュの道路標識"),
        task="classification", audiences=("student", "teacher"), difficulty="intermediate",
        use_cases_ja=("交通標識の見分けやすさを調べるクイズを試作する", "標識の図柄や背景によって伝わりやすさが変わるか比較する"),
        input_description_ja="バングラデシュで撮影された480×640ピクセルの道路標識画像",
        output_description_ja="道路標識18種類のカテゴリ名",
        download_size_mb=191.0, audit_status="full_image_decode_annotation_and_sample_visual_review",
        audit_report="reports/bdroadsigns-v1-audit.json",
        classes=(
            "college_front", "cross_road", "drop_off_or_pick_up", "height_limit_5_8m",
            "left_side_road", "market_front", "pass_either_side", "pedestrian_crossing",
            "pedestrian_crossing_ahead", "rail_crossing", "rickshaw_restricted", "right_turn",
            "roundabout", "side_road_left", "speed_limit_40km", "turn_left", "turn_right", "u_turn",
        ),
        class_names_ja=(
            "学校付近", "交差点", "乗降場所", "高さ制限5.8m", "左側支路", "市場付近",
            "左右どちらか通行", "横断歩道", "前方横断歩道", "踏切", "人力車通行禁止",
            "右カーブ", "環状交差点", "左側道", "最高速度40km/h", "左折", "右折", "Uターン",
        ),
        license_info={
            "name": "CC BY 4.0",
            "url": "https://creativecommons.org/licenses/by/4.0/",
            "rights_review": "Mendeley Data v1のCC BY 4.0表示と著者によるスマートフォン撮影の説明を確認。帰属・変更表示を同梱。",
        },
        source_info={
            "dataset_name": "BDRoadSigns: An Image-Based Dataset of Bangladeshi Traffic Signs for Supervised Classification Models",
            "provider": "Tawhid Ahmed Komol; Pulak Deb Nath; Rinvi Jaman Riti",
            "url": "https://data.mendeley.com/datasets/rnkd74xdtr/1",
            "doi": "10.17632/rnkd74xdtr.1",
            "source_file": "Traffic Dataset.zip; Compress Dataset subset",
            "source_sha256": "72efd61218343b6869b9bd415537137c978b9bfa3a91872e71e565fb8999f087",
            "inner_zip_sha256": "9e60702e9da73e9c1296ab1687f36036543e66813210929ed8ae06da21f3430b",
            "release_repository": "https://github.com/708san/CV_data_artifacts",
            "release_tag": "bdroadsigns-v0.1.0",
        },
        file_urls={
            "artifact": "https://github.com/708san/CV_data_artifacts/releases/download/bdroadsigns-v0.1.0/bdroadsigns-v0.1.0.zip",
        },
        max_archive_bytes=250_000_000, max_unpacked_bytes=250_000_000,
        max_files=6000, published=True,
    ),
    "orange_fruit": ReleaseSource(
        id="orange_fruit", case_id="orange_fruit", tag="orange-fruit-v0.1.0",
        sha256="69408ee9184638215c1f0e459b1a5e11a9ec853b4ce815ac6071a174294f8115",
        archive_size=112_621_346, image_count=15_000,
        kind="classification", name_ja="オレンジの見た目5カテゴリ",
        rights_note="CC BY 4.0。出典・変更表示が必要です。画像上のカテゴリであり、鮮度・食用可否・食品安全・病気の判断には使えません。",
        aliases_ja=("Orange Fruit Image Dataset", "オレンジ画像分類"),
        task="classification", audiences=("student", "teacher"), difficulty="intermediate",
        use_cases_ja=("食品ロスを考えるため、見た目カテゴリの分類を試作する", "背景・照明・角度が分類結果に与える影響を比べる"),
        input_description_ja="バングラデシュで撮影された224×224ピクセルのオレンジ画像",
        output_description_ja="見た目の5カテゴリ",
        download_size_mb=112.6, audit_status="full_image_decode_exact_duplicate_and_sample_visual_review",
        audit_report="reports/orange-fruit-v2-audit.json",
        classes=("blackspotted_orange", "cankered_orange", "fresh_orange", "green_orange", "rotten_orange"),
        class_names_ja=("黒点カテゴリ", "かいようカテゴリ", "見た目が新鮮とされたカテゴリ", "緑色カテゴリ", "腐敗カテゴリ"),
        license_info={
            "name": "CC BY 4.0",
            "url": "https://creativecommons.org/licenses/by/4.0/",
            "rights_review": "Mendeley Data v2のCC BY 4.0表示と、著者によるスマートフォン撮影の説明を確認。帰属・変更表示をartifactに同梱。",
        },
        source_info={
            "dataset_name": "Orange Fruit Image Dataset for Classification",
            "provider": "Ashif Shuvo; Most.Subrina Afrin Monika; Wahada Jinnat Oishy Bhuian",
            "url": "https://data.mendeley.com/datasets/zk4hzhtcdd/2",
            "doi": "10.17632/zk4hzhtcdd.2",
            "source_file": "OrangeClassificationDataset.zip",
            "source_sha256": "b486ee40af7316c4603d3d8354a636a7bc859c500beb126b3577ef79bf3f75e7",
            "inner_zip_sha256": "03d43104a0c6eda6681c23415bec8fe404ff6c919d44de35b247bb9b72105251",
            "release_repository": "https://github.com/708san/CV_data_artifacts",
            "release_tag": "orange-fruit-v0.1.0",
        },
        file_urls={
            "artifact": "https://github.com/708san/CV_data_artifacts/releases/download/orange-fruit-v0.1.0/orange_fruit-v0.1.0.zip",
        },
        max_archive_bytes=150_000_000, max_unpacked_bytes=150_000_000,
        max_files=20_000, published=True,
    ),
    "japan_ocr_receipts": ReleaseSource(
        id="japan_ocr_receipts", case_id="japan_ocr_receipts", tag="japan_ocr_receipts-v0.1.0",
        sha256="0c9739f12f11ea22c44afa5f2a5a151bf389badb9bc6ce4534dc956b9a8b8f4d",
        archive_size=860_275, image_count=10, sample_count=10,
        kind="ocr", task="ocr", name_ja="合成レシートでOCR・支出整理",
        rights_note="CC BY 4.0。Alpha10承認済みデータのみを使用しています。合成レシート10枚の小規模見本で、実際の取引・店舗・個人を表しません。全文OCR正解はありません。",
        aliases_ja=("日本語レシートOCR", "文化祭の支出整理", "Japan OCR Mini Benchmark Alpha10"),
        audiences=("student", "teacher"), difficulty="introductory",
        use_cases_ja=(
            "文化祭などの支出整理ツールを試作し、OCRで読んだ品目・金額を見本と照合する",
            "文字の大きさやレイアウトによる読み取り間違いを調べる",
        ),
        input_description_ja="店舗・取引・個人を模した架空の日本語レシート画像10枚",
        output_description_ja="品目・数量・金額・合計額などの構造化見本。全文の文字起こしではありません。",
        download_size_mb=0.86, audit_status="all_images_sha256_checked_and_visually_reviewed",
        audit_report="docs/datasets/japan_ocr_receipts.md",
        license_info={
            "name": "CC BY 4.0",
            "url": "https://creativecommons.org/licenses/by/4.0/",
            "rights_review": "固定revisionのAlpha10に限定したCC BY 4.0承認、公開ライセンス通知、合成データ注意を確認。",
        },
        source_info={
            "dataset_name": "Japan OCR Mini Benchmark (Alpha10)",
            "provider": "K10124",
            "url": "https://huggingface.co/datasets/K10124/japan-ocr-mini-benchmark/tree/c82efda5b823494424e6bc6e9ae7577396ded908/alpha10",
            "revision": "c82efda5b823494424e6bc6e9ae7577396ded908",
            "source_inventory_sha256": "57102d17d35d4a6c8dbc67a59004189b0593b39e1db86c74b623f8959b45ccd3",
            "release_repository": "https://github.com/708san/CV_data_artifacts",
            "release_tag": "japan_ocr_receipts-v0.1.0",
        },
        file_urls={
            "artifact": "https://github.com/708san/CV_data_artifacts/releases/download/japan_ocr_receipts-v0.1.0/japan_ocr_receipts-v0.1.0.zip",
        },
        max_archive_bytes=2_000_000, max_unpacked_bytes=2_000_000,
        max_files=40, published=False,
    ),
    "japanese_receipts_detailed": ReleaseSource(
        id="japanese_receipts_detailed", case_id="japanese_receipts_detailed", tag="japanese_receipts_detailed-v0.1.0",
        sha256="4f3a480f09eeacfda9f9ca4d84dd01ad8aefa49cce776ec06a7d64f5f25dfb5a",
        archive_size=130_013_467, image_count=100, sample_count=100,
        kind="ocr", task="ocr", name_ja="日本語レシートOCR（詳細版）",
        rights_note="CC BY-NC 4.0。非商用利用のみ。黒塗りは一部で、店舗情報・QRコード・取引番号が残る場合があります。OCR結果は人が原票と照合してください。",
        aliases_ja=("日本語レシートOCR（詳細版）", "Japanese Receipt Image Dataset Detailed", "レシートOCR"),
        audiences=("student", "teacher"), difficulty="introductory",
        use_cases_ja=(
            "文化祭や部活動の会計入力を補助するOCRを試作し、日付・明細・合計の候補を原票と照合する",
            "選択領域の正解を使い、日本語レシートの文字認識の得意・不得意を調べる",
        ),
        input_description_ja="日本の実レシート画像100枚。全画像は評価用です。",
        output_description_ja="選択された2,005領域のラベルと1,802件の文字転記。全文OCRの正解ではありません。",
        download_size_mb=130.0, audit_status="full_image_decode_annotation_and_visual_review",
        audit_report="reports/japanese_receipts_detailed-v1-full-audit.json",
        license_info={
            "name": "CC BY-NC 4.0",
            "url": "https://creativecommons.org/licenses/by-nc/4.0/",
            "rights_review": "配布元の固定revisionが表示するCC BY-NC 4.0を確認。再配布は非商用条件に限定。配布元の個人情報マスクは選択的で、完全な匿名化ではない。",
        },
        source_info={
            "dataset_name": "Japanese Receipt Image Dataset (Detailed Annotations)",
            "provider": "IngCrowd Inc.",
            "url": "https://huggingface.co/datasets/IngCrowd/japanese-receipts-detailed",
            "revision": "e679e42ba2a408038d4151ced36eb6f32589422c",
            "source_inventory_sha256": "72ed2708c57927730ede820b388f4e84bc65d1112198288b0b193b0dbf93db4e",
            "release_repository": "https://github.com/708san/CV_data_artifacts",
            "release_tag": "japanese_receipts_detailed-v0.1.0",
        },
        file_urls={
            "artifact": "https://github.com/708san/CV_data_artifacts/releases/download/japanese_receipts_detailed-v0.1.0/japanese_receipts_detailed-v0.1.0.zip",
        },
        max_archive_bytes=150_000_000, max_unpacked_bytes=150_000_000,
        max_files=200, published=True,
    ),
    "fruitseg30": ReleaseSource(
        id="fruitseg30", case_id="fruitseg30", tag="fruitseg30-v0.1.0",
        sha256="129384a6e9599b0b9eb756ec93abda25a90bdd70a514fd04f905a2ff2e8c5ba5",
        archive_size=68_242_354, image_count=1914,
        kind="segmentation", name_ja="FruitSeg30（果物の領域分割・29種類）",
        rights_note="CC BY 4.0の出典表示が必要です。Guava 55組を寸法不一致で除外し、元画像と濃淡マスクは変更していません。鮮度・品質の判断には使いません。",
        aliases_ja=("FruitSeg30", "果物の領域分割"),
        task="segmentation", audiences=("student", "teacher"), difficulty="intermediate",
        use_cases_ja=("果物の領域を画像から分ける", "マスクの境界や撮影背景による違いを調べる"),
        input_description_ja="512×512の果物画像",
        output_description_ja="果物の前景を示すグレースケールマスク",
        download_size_mb=65.3, audit_status="full_image_and_mask_audit",
        audit_report="reports/fruitseg30-v3-full-audit.json",
        classes=(
            "Apple_Gala", "Apple_Golden Delicious", "Avocado", "Banana", "Berry",
            "Burmese Grape", "Carambola", "Date Palm", "Dragon", "Elephant Apple",
            "Grape", "Green Coconut", "Hog Plum", "Kiwi", "Lichi", "Malta",
            "Mango Golden Queen", "Mango_Alphonso", "Mango_Amrapali", "Mango_Bari",
            "Mango_Himsagar", "Olive", "Orange", "Palm", "Persimmon", "Pineapple",
            "Pomegranate", "Watermelon", "White Pear",
        ),
        class_names_ja=(
            "ガラりんご", "ゴールデンデリシャス", "アボカド", "バナナ", "ベリー",
            "ビルマブドウ", "スターフルーツ", "ナツメヤシ", "ドラゴンフルーツ",
            "エレファントアップル", "ブドウ", "青いココナッツ", "ホグプラム",
            "キウイ", "ライチ", "マルタオレンジ", "マンゴー（ゴールデンクイーン）",
            "マンゴー（アルフォンソ）", "マンゴー（アムラパリ）", "マンゴー（バリ）",
            "マンゴー（ヒムサガル）", "オリーブ", "オレンジ", "パームフルーツ",
            "柿", "パイナップル", "ザクロ", "スイカ", "白梨",
        ),
        license_info={
            "name": "CC BY 4.0",
            "url": "https://creativecommons.org/licenses/by/4.0/",
            "rights_review": "Mendeley公式v3ページと関連論文の表記を確認。帰属表示とGuava 55組の除外を明記。",
        },
        source_info={
            "dataset_name": "FruitSeg30_Segmentation Dataset & Mask Annotations",
            "provider": "F. M. Javed Mehedi Shamrat; Rashiduzzaman Shakil; Mohd Yamani Idna Idris; Bonna Akter; Xujuan Zhou",
            "url": "https://data.mendeley.com/datasets/vkht8pfsp3/3",
            "doi": "10.17632/vkht8pfsp3.3",
            "release_repository": "https://github.com/708san/CV_data_artifacts",
            "release_tag": "fruitseg30-v0.1.0",
        },
        file_urls={
            "artifact": "https://github.com/708san/CV_data_artifacts/releases/download/fruitseg30-v0.1.0/fruitseg30-v0.1.0.zip",
        },
        published=True,
    ),
    "fresh_rotten_fruits": ReleaseSource(
        id="fresh_rotten_fruits", case_id="fresh_rotten_fruits",
        tag="fresh-rotten-fruits-v0.1.0",
        sha256="1ca92043fbb0ebbf86ddac5fec2c264e39151ab0d9def1b618002772d9b182eb",
        archive_size=150_919_158, image_count=3193,
        kind="classification", name_ja="果物8種類の見た目（新鮮・傷み）",
        rights_note="CC BY 4.0。出典・変更表示が必要です。見た目の研究ラベルで、食用可否や食品安全の判定には使えません。",
        aliases_ja=("果物の新鮮・傷み画像", "Fresh and Rotten Fruits"),
        task="classification", audiences=("student", "teacher"), difficulty="introductory",
        use_cases_ja=("果物の画像を種類と見た目の状態で分類する", "食品ロスを考え、見た目のラベルの限界を調べる"),
        input_description_ja="512px以下に整えた果物の画像",
        output_description_ja="8種類の果物それぞれについて、新鮮または傷みの16ラベル",
        download_size_mb=150.9, audit_status="full_image_decode_duplicate_audit_sample_visual_review",
        audit_report="reports/fresh_rotten_fruits-v1-full-audit.json",
        classes=(
            "fresh_apple", "fresh_banana", "fresh_grape", "fresh_guava",
            "fresh_jujube", "fresh_orange", "fresh_pomegranate", "fresh_strawberry",
            "rotten_apple", "rotten_banana", "rotten_grape", "rotten_guava",
            "rotten_jujube", "rotten_orange", "rotten_pomegranate", "rotten_strawberry",
        ),
        class_names_ja=(
            "新鮮なリンゴ", "新鮮なバナナ", "新鮮なブドウ", "新鮮なグアバ",
            "新鮮なナツメ", "新鮮なオレンジ", "新鮮なザクロ", "新鮮なイチゴ",
            "傷みのあるリンゴ", "傷みのあるバナナ", "傷みのあるブドウ", "傷みのあるグアバ",
            "傷みのあるナツメ", "傷みのあるオレンジ", "傷みのあるザクロ", "傷みのあるイチゴ",
        ),
        license_info={
            "name": "CC BY 4.0",
            "url": "https://creativecommons.org/licenses/by/4.0/",
            "rights_review": "固定v1のMendeley Data CC BY 4.0表示と著者による撮影説明を確認。元画像のみを使用し、出典・変更表示を同梱。64枚の代表目視では人物・ロゴ・無関係な写り込みは見つからず。",
        },
        source_info={
            "dataset_name": "Fresh and Rotten Fruits Dataset for Machine-Based Evaluation of Fruit Quality",
            "provider": "Nusrat Sultana; Musfika Jahan; Mohammad Shorif Uddin",
            "url": "https://data.mendeley.com/datasets/bdd69gyhv8/1",
            "doi": "10.17632/bdd69gyhv8.1",
            "release_repository": "https://github.com/708san/CV_data_artifacts",
            "release_tag": "fresh-rotten-fruits-v0.1.0",
        },
        file_urls={
            "artifact": "https://github.com/708san/CV_data_artifacts/releases/download/fresh-rotten-fruits-v0.1.0/fresh_rotten_fruits-v0.1.0.zip",
        },
        published=True,
    ),
    "food_waste_bangladesh": ReleaseSource(
        id="food_waste_bangladesh", case_id="food_waste_bangladesh",
        tag="food-waste-bangladesh-v0.1.1",
        sha256="bcbd7fe1f2b8d37a1b86952d59987b1067cdc55c0099199eee0217a4f805c57d",
        archive_size=30_760_217, image_count=633,
        kind="classification", name_ja="バングラデシュの食品廃棄画像（撮影場面）",
        rights_note="CC BY 4.0。作者・出典・変更の表示が必要。フォルダは撮影カテゴリで、食品廃棄量を表しません。",
        aliases_ja=("食品廃棄画像", "Food Waste Bangladesh"),
        task="classification", audiences=("student", "teacher"), difficulty="introductory",
        use_cases_ja=("画像を撮影場面ごとに分類する", "クラス数の偏りが分類結果に与える影響を調べる"),
        input_description_ja="食べ残しなどを撮影した画像",
        output_description_ja="ビュッフェ・一般・レストラン・野菜・婚礼の5カテゴリ",
        download_size_mb=30.8, audit_status="full_image_audit_redistribution_reviewed",
        audit_report="reports/food_waste_bangladesh-v0.1.1-full-audit.json",
        class_names_ja=("ビュッフェ", "一般", "レストラン", "野菜", "婚礼"),
        label_names_ja={
            "Buffet Food waste": "ビュッフェ",
            "Food waste (General)": "一般",
            "Restaurant food waste": "レストラン",
            "Vegetables waste": "野菜",
            "Wedding Food waste": "婚礼",
        },
        license_info={
            "name": "CC BY 4.0",
            "url": "https://creativecommons.org/licenses/by/4.0/",
            "rights_review": "固定v1のCC BY 4.0表示と撮影説明を確認。人物の一部が写る11枚とQR風表示1枚を除外。残る商品表示はブランドの推薦・承認を示しません。出典・変更表示が必要。",
        },
        source_info={
            "dataset_name": "An image dataset for food waste in Bangladesh",
            "provider": "Mohammad Manzurul Islam; Saifur Rahman; Fatema Tahsin; Zarif Syndeed Sikder",
            "url": "https://doi.org/10.17632/w68f9w6jmm.1",
            "release_repository": "https://github.com/708san/CV_data_artifacts",
            "release_tag": "food-waste-bangladesh-v0.1.1",
        },
        file_urls={
            "artifact": "https://github.com/708san/CV_data_artifacts/releases/download/food-waste-bangladesh-v0.1.1/food_waste_bangladesh-v0.1.1.zip",
        },
        published=True,
    ),
    "smallfishbd": ReleaseSource(
        id="smallfishbd", case_id="smallfishbd", tag="smallfishbd-v0.1.1",
        sha256="367b332bc0da479e9a708449f45cf7aa10eb190267a6bc1f1a87e5a38ce8f547",
        archive_size=29_799_609, image_count=1697,
        kind="classification", name_ja="バングラデシュの小魚10種",
        rights_note="CC BY 4.0。作者・出典・変更の表示が必要。青い背景に偏るため、実環境での魚種判定には使いません。",
        aliases_ja=("小魚10種", "SmallFishBD"),
        task="classification", audiences=("student", "teacher"), difficulty="introductory",
        use_cases_ja=("魚の画像を10種類に分類する", "背景や見た目の似た魚種による誤分類を調べる"),
        input_description_ja="青系の背景で撮影された320×320の魚画像",
        output_description_ja="バングラデシュの市場で使われる魚名10種類",
        download_size_mb=29.8, audit_status="full_image_audit_redistribution_reviewed",
        audit_report="reports/smallfishbd-v0.1.1-preparation-2026-11-09.json",
        class_names_ja=("ベレ", "チェラ", "グチ", "カチキ", "カタ・ファサ", "モラ", "ナマ・チャンダ", "パブダ", "プティ", "テングラ"),
        license_info={
            "name": "CC BY 4.0",
            "url": "https://creativecommons.org/licenses/by/4.0/",
            "rights_review": "CC BY 4.0。全画像の視覚レビューを含む再配布審査を完了。出典・変更表示が必要。増強画像は含めません。",
        },
        source_info={
            "dataset_name": "SmallFishBD: A Comprehensive Image Dataset of Common Small Fish Varieties in Bangladesh for Species Identification and Classification",
            "provider": "Md Hasanul Ferdaus et al. (11 contributors)",
            "url": "https://doi.org/10.17632/8jvxtvz52x.2",
            "release_repository": "https://github.com/708san/CV_data_artifacts",
            "release_tag": "smallfishbd-v0.1.1",
        },
        file_urls={
            "artifact": "https://github.com/708san/CV_data_artifacts/releases/download/smallfishbd-v0.1.1/smallfishbd-v0.1.1.zip",
        },
        published=True,
    ),
    "pistachio_image_dataset": ReleaseSource(
        id="pistachio_image_dataset", case_id="pistachio_image_dataset",
        tag="pistachio_image_dataset-v0.1.0",
        sha256="32bc15c4788052207e3dd52d4450cc15fec9efade3df169d59bb94556d715f24",
        archive_size=25_875_554, image_count=2148,
        kind="classification", name_ja="ピスタチオ2品種の画像",
        rights_note="CC BY 4.0。Murat Koklu氏・データ出典・変更と指定2論文を表示してください。品質・鮮度・食品安全の判定には使いません。",
        aliases_ja=("ピスタチオ2品種", "ピスタチオ画像"),
        task="classification", audiences=("student", "teacher"), difficulty="introductory",
        use_cases_ja=("ピスタチオ2品種を画像で分類する", "背景が固定された画像で誤分類を調べる"),
        input_description_ja="黒い背景上で撮影された600×600のピスタチオ試料画像",
        output_description_ja="Kirmizi種またはSiirt種のラベル",
        download_size_mb=24.7, audit_status="full_image_audit",
        audit_report="reports/pistachio_image_dataset-v1-full-audit.json",
        classes=("Kirmizi_Pistachio", "Siirt_Pistachio"),
        class_names_ja=("Kirmizi種", "Siirt種"),
        license_info={
            "name": "CC BY 4.0",
            "url": "https://creativecommons.org/licenses/by/4.0/",
            "rights_review": "Mendeley v1のCC BY 4.0表示と、研究者自身が試料を集めて画像を作成したとの論文記載を確認。Murat Koklu氏、出典、変更、指定2論文の引用が必要。",
        },
        source_info={
            "dataset_name": "Pistachio Image Dataset",
            "provider": "Murat Koklu (Mendeley Data contributor)",
            "url": "https://data.mendeley.com/datasets/h7pf57cgg9/1",
            "doi": "10.17632/h7pf57cgg9.1",
            "release_repository": "https://github.com/708san/CV_data_artifacts",
            "release_tag": "pistachio_image_dataset-v0.1.0",
        },
        file_urls={
            "artifact": "https://github.com/708san/CV_data_artifacts/releases/download/pistachio_image_dataset-v0.1.0/pistachio_image_dataset-v0.1.0.zip",
        },
        published=True,
    ),
    "indoor_plant_varieties": ReleaseSource(
        id="indoor_plant_varieties", case_id="indoor_plant_varieties",
        tag="indoor-plant-varieties-v0.1.0",
        sha256="0194a3631ecaf0293cc0271d938ffe6933b61ce58e58e648f8ca346bd1dbe714",
        archive_size=74_718_549, image_count=1162,
        kind="classification", name_ja="観葉植物の種類（7種類）",
        rights_note="CC BY 4.0。作者・出典・変更を表示してください。植物名の予測を有毒性・食用・病気・育て方の判定に使わないでください。",
        aliases_ja=("観葉植物", "観葉植物の種類", "観葉植物画像"),
        task="classification", audiences=("student", "teacher"), difficulty="introductory",
        use_cases_ja=("家や学校で見かける観葉植物を画像で分類する", "撮影条件で予測がどう変わるか調べる"),
        input_description_ja="長辺512px以下の観葉植物画像",
        output_description_ja="7種類の観葉植物ラベル",
        download_size_mb=71.3, audit_status="full_image_audit",
        audit_report="reports/indoor_plant_varieties-v0.1.0-audit.json",
        classes=("Aglaonema", "Cryptanthus", "Devil's Ivy", "Heartleaf philodendron", "N-Joy Pothos", "Rhaphidophora", "Zz plant"),
        class_names_ja=("アグラオネマ", "クリプタンサス", "ポトス", "ハートリーフ・フィロデンドロン", "エンジョイ・ポトス", "ヒメモンステラ", "ザミオクルカス"),
        license_info={
            "name": "CC BY 4.0",
            "url": "https://creativecommons.org/licenses/by/4.0/",
            "rights_review": "Mendeley v1のCC BY 4.0表示、著者による収集説明を確認。EXIF/GPSを全て除去し、10枚の完全一致重複を除外。作者・出典・変更の表示が必要。",
        },
        source_info={
            "dataset_name": "Indoor Plant Varieties for Computer Vision Applications: A Diverse Image Dataset",
            "provider": "Sajib Bin Mamun; Md Asraful Sharker Nirob; Md Taimur Ahad; Mashreka Akter; Pranta Saha; Md Assaduzzaman",
            "url": "https://data.mendeley.com/datasets/ct79299k27/1",
            "doi": "10.17632/ct79299k27.1",
            "release_repository": "https://github.com/708san/CV_data_artifacts",
            "release_tag": "indoor-plant-varieties-v0.1.0",
        },
        file_urls={
            "artifact": "https://github.com/708san/CV_data_artifacts/releases/download/indoor-plant-varieties-v0.1.0/indoor_plant_varieties-v0.1.0.zip",
        },
        published=True,
    ),
    "chakmalipi": ReleaseSource(
        id="chakmalipi", case_id="chakmalipi", tag="chakmalipi-v0.1.0",
        sha256="d9ef73e59c084492939b1d7b23d3ffde0fa865f76f132a29c5cba7c12cb19759",
        archive_size=99_131_569, image_count=36_258,
        kind="classification", name_ja="チャクマ文字・数字の手書き画像",
        rights_note="CC BY 4.0。作者・出典・変更内容を表示してください。これは文字画像の分類用で、文書OCRや書き手の識別には使えません。",
        aliases_ja=("チャクマ文字", "ChakmaLipī", "チャクマ文字画像"),
        task="classification", audiences=("student", "teacher"), difficulty="introductory",
        use_cases_ja=("手書き文字のデジタル保存や文字分類を考える", "文字の書き方の違いが画像分類に与える影響を調べる"),
        input_description_ja="40×40画素のRGB手書き文字・数字画像",
        output_description_ja="チャクマ文字38種類とチャクマ数字10種類の48クラス",
        download_size_mb=94.6, audit_status="full_image_audit",
        audit_report="https://github.com/708san/CV_data_artifacts/blob/main/reports/chakmalipi-v0.1.0-audit.json",
        classes=tuple([f"Character_{i}" for i in range(1, 39)] + [f"digit_{i}" for i in range(1, 11)]),
        class_names_ja=(
            "チャクマ文字 𑄇（Kaa）", "チャクマ文字 𑄈（Khaa）", "チャクマ文字 𑄉（Gaa）", "チャクマ文字 𑄊（Ghaa）",
            "チャクマ文字 𑄋（Ngaa）", "チャクマ文字 𑄌（Caa）", "チャクマ文字 𑄍（Chaa）", "チャクマ文字 𑄎（Jaa）",
            "チャクマ文字 𑄏（Jhaa）", "チャクマ文字 𑄐（Nyaa）", "チャクマ文字 𑄑（Ttaa）", "チャクマ文字 𑄒（Tthaa）",
            "チャクマ文字 𑄓（Ddaa）", "チャクマ文字 𑄔（Ddhaa）", "チャクマ文字 𑄕（Nnaa）", "チャクマ文字 𑄖（Taa）",
            "チャクマ文字 𑄗（Thaa）", "チャクマ文字 𑄘（Daa）", "チャクマ文字 𑄙（Dhaa）", "チャクマ文字 𑄚（Naa）",
            "チャクマ文字 𑄛（Paa）", "チャクマ文字 𑄜（Phaa）", "チャクマ文字 𑄝（Baa）", "チャクマ文字 𑄞（Bhaa）",
            "チャクマ文字 𑄟（Maa）", "チャクマ文字 𑄡（Yaa）", "チャクマ文字 𑄢（Raa）", "チャクマ文字 𑄣（Laa）",
            "チャクマ文字 𑄤（Waa）", "チャクマ文字 𑄥（Saa）", "チャクマ文字 𑄦（Haa）", "チャクマ文字 𑄠（Yyaa）",
            "チャクマ文字 𑄃（Aa）", "チャクマ文字 𑄆（E）", "チャクマ文字 𑄄（別形）（I（別形））", "チャクマ文字 𑄄（I）",
            "チャクマ文字 𑄅（U）", "チャクマ文字 𑅄（Lhaa）",
            "チャクマ数字 0（𑄶）", "チャクマ数字 1（𑄷）", "チャクマ数字 2（𑄸）", "チャクマ数字 3（𑄹）",
            "チャクマ数字 4（𑄺）", "チャクマ数字 5（𑄻）", "チャクマ数字 6（𑄼）", "チャクマ数字 7（𑄽）",
            "チャクマ数字 8（𑄾）", "チャクマ数字 9（𑄿）",
        ),
        license_info={
            "name": "CC BY 4.0",
            "url": "https://creativecommons.org/licenses/by/4.0/",
            "rights_review": "Mendeley Data v6のCC BY 4.0表示、論文の収集・同意・倫理審査の説明を確認。1,450枚の完全一致重複を除外し、作者・出典・変更の表示が必要。",
        },
        source_info={
            "dataset_name": "ChakmaLipī Dataset",
            "provider": "Jannatul Ferdeous; Md. Abdul Kayum; Ahmed Islam; Md Roman Nihal; ASM Shihavuddin; Muhammad Hasan",
            "url": "https://data.mendeley.com/datasets/rzjphbvz9f/6",
            "doi": "10.17632/rzjphbvz9f.6",
            "article_url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC13136726/",
            "release_repository": "https://github.com/708san/CV_data_artifacts",
            "release_tag": "chakmalipi-v0.1.0",
        },
        file_urls={
            "artifact": "https://github.com/708san/CV_data_artifacts/releases/download/chakmalipi-v0.1.0/chakmalipi-v0.1.0.zip",
        },
        archive_root_name="chakmalipi", max_files=40_000,
        published=True,
    ),
    "indoor_waste_image": ReleaseSource(
        id="indoor_waste_image", case_id="indoor_waste_image", tag="indoor-waste-image-v0.1.0",
        sha256="44a754d2fd7b00ed9b910d84aff5fb45ba5a1bcf1c033d58e2bfd19ff2bcccb7",
        archive_size=107_068_558, image_count=4000,
        kind="detection", name_ja="屋内に残ったごみの位置",
        rights_note="CC BY 4.0。出典・変更表示が必要です。屋内床面の画像で、日本の分別ルールは別に確認してください。",
        aliases_ja=("屋内ごみ検出", "Indoor Waste Image Dataset"),
        task="detection", audiences=("student", "teacher"), difficulty="intermediate",
        use_cases_ja=("学校行事後などに床に残ったごみの位置を示し、清掃箇所の確認を補助する",),
        input_description_ja="屋内の床面を撮影した画像",
        output_description_ja="紙・プラスチック・キャップ・殻の位置",
        download_size_mb=107.1, audit_status="full_image_annotation_audit_and_library_validation",
        audit_report="https://github.com/708san/CV_data_artifacts/blob/main/reports/indoor_waste_image-v0.1.0-audit.json",
        classes=("paper", "plastic", "cap", "shell"),
        class_names_ja=("紙ごみ", "プラスチック", "キャップ", "殻"),
        license_info={"name":"CC BY 4.0","url":"https://creativecommons.org/licenses/by/4.0/","rights_review":"Mendeley Data v1のライセンス表記を確認。画像画素を保ち、注釈変換・動画単位splitを記録。代表画像50枚を目視。"},
        source_info={"dataset_name":"Indoor Waste Image Dataset","provider":"Yangke L","url":"https://data.mendeley.com/datasets/dy7smxr93r/1","doi":"10.17632/dy7smxr93r.1","release_repository":"https://github.com/708san/CV_data_artifacts","release_tag":"indoor-waste-image-v0.1.0"},
        file_urls={"artifact":"https://github.com/708san/CV_data_artifacts/releases/download/indoor-waste-image-v0.1.0/indoor_waste_image-v0.1.0.zip"},
    ),
    "wastesegcluster": ReleaseSource(
        id="wastesegcluster", case_id="wastesegcluster", tag="wastesegcluster-v0.1.0",
        sha256="e5724fb933bc00fc5f8e5a0e987200cbc88d03e7aba6e68c2cceeedd9ccb6b5e",
        archive_size=100_808_464, image_count=1947,
        kind="detection", name_ja="水辺のごみ位置",
        rights_note="CC BY 4.0。出典・変更表示が必要です。ダッカ周辺の画像で、日本の水辺の状態・水質を表しません。",
        aliases_ja=("水辺ごみ検出", "WasteSegCluster"),
        task="detection", audiences=("student", "teacher"), difficulty="intermediate",
        use_cases_ja=("水辺に見えるごみの位置を記録し、清掃場所や活動計画の確認を補助する",),
        input_description_ja="バングラデシュ・ダッカ周辺の水路や水辺を撮影した画像",
        output_description_ja="複合材・ゴム・繊維、有機物、紙、プラスチックの位置",
        download_size_mb=100.8, audit_status="full_image_annotation_audit_and_library_validation",
        audit_report="https://github.com/708san/CV_data_artifacts/blob/main/reports/wastesegcluster-v0.1.0-audit.json",
        classes=("Composite_Rubber_Textile", "Organic", "Paper", "Plastic"),
        class_names_ja=("複合材・ゴム・繊維", "有機物", "紙", "プラスチック"),
        license_info={"name":"CC BY 4.0","url":"https://creativecommons.org/licenses/by/4.0/","rights_review":"Mendeley Data v4のページとCOCOメタデータのCC BY 4.0表示を確認。50枚を目視し、元COCO bboxをYOLO形式へ変換。"},
        source_info={"dataset_name":"WasteSegCluster: dataset of annotated waste images from urban water bodies in Bangladesh","provider":"Ratul et al.","url":"https://data.mendeley.com/datasets/3wnf3n242s/4","doi":"10.17632/3wnf3n242s.4","release_repository":"https://github.com/708san/CV_data_artifacts","release_tag":"wastesegcluster-v0.1.0"},
        file_urls={"artifact":"https://github.com/708san/CV_data_artifacts/releases/download/wastesegcluster-v0.1.0/wastesegcluster-v0.1.0.zip"},
    ),
    "fire_recognition_image": ReleaseSource(
        id="fire_recognition_image", case_id="fire_recognition_image", tag="fire-recognition-image-v0.1.0",
        sha256="df561876b5945592077b3ba1f5ec29ad11c4ad1cfb4f36695a26005cdf73bb9c",
        archive_size=286_615_690, image_count=1112,
        kind="classification", name_ja="火・煙の教材画像",
        rights_note="CC BY 4.0。出典・変更表示が必要です。元ラベルは実場面の安全性を示しません。警報・避難判断には使わないでください。",
        aliases_ja=("火災画像分類", "Fire Recognition Image Dataset"),
        task="classification", audiences=("student", "teacher"), difficulty="introductory",
        use_cases_ja=("火・煙などの例を分類し、周囲の人が確認する手順を考える",),
        input_description_ja="火・煙や火を扱う場面の400×400画像",
        output_description_ja="Fire、Smoke、Safe_Fire、Artificial_Fireの原作者カテゴリ",
        download_size_mb=286.6, audit_status="full_image_decode_duplicate_audit_sample_visual_review",
        audit_report="https://github.com/708san/CV_data_artifacts/blob/main/reports/fire_recognition_image-v0.1.0-audit.json",
        classes=("Artificial_Fire", "Fire", "Safe_Fire", "Smoke"),
        class_names_ja=("人工・装飾の火", "火", "火を扱う場面（原ラベル）", "煙"),
        license_info={"name":"CC BY 4.0","url":"https://creativecommons.org/licenses/by/4.0/","rights_review":"Mendeley Data v4のCC BY 4.0表示を確認。原画像1,112枚のみ収録し、代表48枚を目視。"},
        source_info={"dataset_name":"Fire Recognition Image Dataset","provider":"Snigdha Saha; Hridoy Sutradhar; Md Anwarul Islam; Md Mafiul Hasan Matin","url":"https://data.mendeley.com/datasets/7jk6xh7h6w/4","doi":"10.17632/7jk6xh7h6w.4","release_repository":"https://github.com/708san/CV_data_artifacts","release_tag":"fire-recognition-image-v0.1.0"},
        file_urls={"artifact":"https://github.com/708san/CV_data_artifacts/releases/download/fire-recognition-image-v0.1.0/fire_recognition_image-v0.1.0.zip"},
        max_archive_bytes=320_000_000, max_unpacked_bytes=320_000_000, max_files=2_000,
    ),
    "agrifreshnet": ReleaseSource(
        id="agrifreshnet", case_id="agrifreshnet", tag="agrifreshnet-v0.1.0",
        sha256="203ad9dd6a27971ee38b9f3751b50a27f04fae7202c6902d56709bba1c045ea4",
        archive_size=345_815_200, image_count=14084,
        kind="classification", name_ja="青果の見た目の段階",
        rights_note="CC BY 4.0。出典・変更表示が必要です。括弧内の日数は元ラベルで、残存日数・可食性・食品安全を示しません。",
        aliases_ja=("青果の見た目分類", "AgriFreshNET"),
        task="classification", audiences=("student", "teacher"), difficulty="introductory",
        use_cases_ja=("家庭や学食で先に現物を確認する青果の候補を考え、食品ロス削減を補助する",),
        input_description_ja="家庭・市場・農場などで撮影された青果画像",
        output_description_ja="8種類の青果についてFresh・Semi-Fresh・Rottenに対応する24原作者カテゴリ",
        download_size_mb=345.8, audit_status="full_image_duplicate_group_audit_sample_visual_review",
        audit_report="https://github.com/708san/CV_data_artifacts/blob/main/reports/agrifreshnet-v0.1.0-audit.json",
        classes=("Fresh Banana(1-4)","Fresh Bittermelon(1-3)","Fresh Cucumber(1-6)","Fresh eggplant(1-4)","Fresh Orange(1-9)","Fresh Papaya(1-4)","Fresh pineapple(1-15)","Fresh Tomato(1-10)","Rotten banana(7-13)","Rotten Bittermelon(5-8)","Rotten Cucumber(12-20)","Rotten eggplant(8-15)","Rotten Orange(20-35)","Rotten Papaya(7-12)","Rotten Pineapple(25-35)","Rotten Tomato(24-35)","Semi fresh banana(4-7)","Semi Fresh Bittermelon ( 3-5)","Semi Fresh Cucumber(6-12)","Semi fresh Orange(9-20)","Semi Fresh Papaya(4-7)","Semi fresh Pineapple (15-25)","Semi fresh Tomato(10-24)","Semi_Fresh eggplant(4-8)"),
        class_names_ja=("新鮮なバナナ","新鮮なゴーヤ","新鮮なキュウリ","新鮮なナス","新鮮なオレンジ","新鮮なパパイヤ","新鮮なパイナップル","新鮮なトマト","傷みのあるバナナ","傷みのあるゴーヤ","傷みのあるキュウリ","傷みのあるナス","傷みのあるオレンジ","傷みのあるパパイヤ","傷みのあるパイナップル","傷みのあるトマト","中間段階のバナナ","中間段階のゴーヤ","中間段階のキュウリ","中間段階のオレンジ","中間段階のパパイヤ","中間段階のパイナップル","中間段階のトマト","中間段階のナス"),
        license_info={"name":"CC BY 4.0","url":"https://creativecommons.org/licenses/by/4.0/","rights_review":"Mendeley Data v1のCC BY 4.0表示を確認。完全一致画像・ラベル競合に関わる76ファイルを除外し、出典・変更を同梱。"},
        source_info={"dataset_name":"AgriFreshNET Freshness and Shelf-Life Image Dataset","provider":"Fouzia Risdin; Hafsha Salauddin; Tasniya aziza tufa; Md Jakir Hossain","url":"https://data.mendeley.com/datasets/42m5tb7yv9/1","doi":"10.17632/42m5tb7yv9.1","release_repository":"https://github.com/708san/CV_data_artifacts","release_tag":"agrifreshnet-v0.1.0"},
        file_urls={"artifact":"https://github.com/708san/CV_data_artifacts/releases/download/agrifreshnet-v0.1.0/agrifreshnet-v0.1.0.zip"},
        max_archive_bytes=400_000_000, max_unpacked_bytes=400_000_000, max_files=20_000,
    ),
    "festival_icons": ReleaseSource(
        id="festival_icons", case_id="festival-icons", tag="festival-v1.0.0",
        sha256="7ed662a947ba364947fb2b10bec2a7fdc8a1019e12b3ff0f06001b61b55d2ccc",
        archive_size=2_838_163, image_count=168,
        kind="lora_training_images", name_ja="文化祭案内アイコン（LoRA学習用）",
        rights_note="GitHubでの公開許可あり。改変・商用利用・再配布の条件は未確定。",
        aliases_ja=("文化祭アイコン", "文化祭案内アイコン"),
        task="lora",
        audiences=("teacher",),
        difficulty="advanced",
        use_cases_ja=("画像生成の絵柄をそろえる", "画像とキャプションの関係を調べる"),
        input_description_ja="文化祭案内アイコンとキャプション",
        output_description_ja="学習用の画像表現（LoRAの重みは提供しない）",
        download_size_mb=2.7,
        audit_status="full_image_audit",
        audit_report="reports/festival-icons-v1.0.0.json",
        license_info={
            "name": "標準ライセンス未設定（公開許可の範囲のみ確認）",
            "url": "https://github.com/708san/CV_sample_data/tree/main/cases/festival-icons",
            "rights_review": "改変・商用利用・再配布は未確認。教材配布用の承認なし。",
        },
        source_info={
            "dataset_name": "文化祭案内アイコン",
            "provider": "CV_sample_data contributors",
            "url": "https://github.com/708san/CV_sample_data/tree/main/cases/festival-icons",
            "release_repository": RELEASE_REPOSITORY,
            "release_tag": "festival-v1.0.0",
        },
    ),
}


_PREVIEW_SOURCES: dict[str, ReleaseSource] = {}


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _read_rows(labels_csv: Path) -> list[dict[str, str]]:
    with labels_csv.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def _sample_id(image: str) -> str:
    path = PurePosixPath(image)
    return path.with_suffix("").as_posix()


def _effective_splits(rows: Sequence[dict[str, str]], *, val_fraction: float, seed: int) -> list[str]:
    if not 0 <= val_fraction < 1:
        raise ValueError("val_fractionは0以上1未満で指定してください。")
    if not rows:
        return []
    # Releaseの公式testは保持し、trainの中だけをラベルごとに分割する。
    result = [row["split"] if row.get("split") in {"val", "test"} else "train" for row in rows]
    by_label: dict[str, list[int]] = {}
    for index, row in enumerate(rows):
        if row.get("split") not in {"val", "test"}:
            by_label.setdefault(row.get("label", ""), []).append(index)
    for label, indices in by_label.items():
        count = int(round(len(indices) * val_fraction))
        if val_fraction > 0 and len(indices) >= 2:
            count = max(1, count)
        count = min(count, max(0, len(indices) - 1))
        ranked = sorted(
            indices,
            key=lambda i: hashlib.sha256(f"{seed}:{label}:{_sample_id(rows[i]['image'])}".encode()).hexdigest(),
        )
        for index in ranked[:count]:
            result[index] = "val"
    return result


class _TorchClassificationDataset:
    """torch.utils.data.Dataset互換の遅延読み込みラッパー。"""

    def __init__(self, records: list[dict[str, Any]], *, image_size: tuple[int, int], torch_module: Any) -> None:
        self._records = records
        self._image_size = image_size
        self._torch = torch_module
        self.targets = [int(record["label_id"]) for record in records]

    def __len__(self) -> int:
        return len(self._records)

    def __getitem__(self, index: int):
        try:
            from PIL import Image
        except ImportError as exc:
            raise DatasetError("画像読み込みにはPillowが必要です。") from exc
        import numpy as np

        record = self._records[index]
        with Image.open(record["image_path"]) as image:
            image = image.convert("RGB").resize(self._image_size[::-1], Image.Resampling.BILINEAR)
            array = np.asarray(image, dtype=np.float32) / 255.0
        tensor = self._torch.from_numpy(array).permute(2, 0, 1).contiguous()
        return tensor, int(record["label_id"])


class _TorchSegmentationDataset:
    """画像と濃淡またはクラスIDマスクを遅延読み込みするPyTorch Dataset互換クラス。"""

    def __init__(
        self,
        records: list[dict[str, Any]],
        *,
        image_size: tuple[int, int],
        torch_module: Any,
        mask_encoding: str = "grayscale_0_255",
        class_count: int = 0,
    ) -> None:
        self._records = records
        self._image_size = image_size
        self._torch = torch_module
        self._mask_encoding = mask_encoding
        self._class_count = class_count
        self.targets = [int(record["label_id"]) for record in records]

    def __len__(self) -> int:
        return len(self._records)

    def __getitem__(self, index: int):
        try:
            from PIL import Image
        except ImportError as exc:
            raise DatasetError("画像読み込みにはPillowが必要です。") from exc
        import numpy as np

        record = self._records[index]
        with Image.open(record["image_path"]) as image:
            image = image.convert("RGB").resize(self._image_size[::-1], Image.Resampling.BILINEAR)
            image_array = np.asarray(image, dtype=np.float32) / 255.0
        with Image.open(record["mask_path"]) as mask:
            mask = mask.convert("L").resize(self._image_size[::-1], Image.Resampling.NEAREST)
            if self._mask_encoding == "class_id_grayscale":
                mask_array = np.asarray(mask, dtype=np.int64)
                if mask_array.size and (mask_array.min() < 0 or mask_array.max() >= self._class_count):
                    raise DatasetError("画素マスクにmanifestのクラス範囲外のIDがあります。")
            else:
                mask_array = np.asarray(mask, dtype=np.float32)[None, :, :] / 255.0
        image_tensor = self._torch.from_numpy(image_array).permute(2, 0, 1).contiguous()
        mask_tensor = self._torch.from_numpy(mask_array).contiguous()
        return image_tensor, mask_tensor


_TASKS: dict[str, dict[str, str]] = {
    "ocr": {
        "name_ja": "文字認識・情報整理（OCR）",
        "description_ja": "画像の文字を読み取り、必要な項目を整理する課題。",
    },
    "classification": {
        "name_ja": "画像分類",
        "description_ja": "画像全体を、決めた種類のどれかに分ける課題。",
    },
    "detection": {
        "name_ja": "物体検出",
        "description_ja": "画像の中の物体の位置と種類を調べる課題。",
    },
    "regression": {
        "name_ja": "画像と実測値の関係を調べる",
        "description_ja": "画像の特徴と実際に測った数値を比べる課題。",
    },
    "segmentation": {
        "name_ja": "領域分割",
        "description_ja": "画像の画素を、物体や背景の領域に分ける課題。",
    },
    "lora": {
        "name_ja": "画像生成・LoRA",
        "description_ja": "画像と説明文を使い、表現の特徴をそろえる課題。",
    },
}


def _catalog_sources(*, include_preview: bool) -> tuple[ReleaseSource, ...]:
    sources = [source for source in _SOURCES.values() if source.published]
    if include_preview:
        sources.extend(_PREVIEW_SOURCES.values())
    return tuple(sources)


def _source_status(src: ReleaseSource) -> str:
    if not src.published:
        return "release_pending"
    if src.preview:
        return "teacher_preview_only"
    if "student" in src.audiences:
        return "student_enabled"
    return "teacher_only"


def list_available(*, task: str | None = None, audience: str | None = None,
                   include_preview: bool = False) -> list[dict[str, Any]]:
    """利用可能なデータを課題タイプ・対象者で絞り込む。

    デフォルトは後方互換のため正式一覧だけを返す。プレビューは
    ``include_preview=True``を明示した教師向け確認用であり、生徒向け一覧には
    ``audience="student"``を指定しても含まれない。
    """
    if task is not None and task not in _TASKS:
        raise ValueError(f"taskは{', '.join(_TASKS)}のいずれかです。")
    if audience is not None and audience not in {"student", "teacher"}:
        raise ValueError("audienceはstudentまたはteacherです。")
    result = []
    for src in _catalog_sources(include_preview=include_preview):
        if task is not None and src.task != task:
            continue
        if audience is not None and audience not in src.audiences:
            continue
        result.append({
            "id": src.id,
            "name_ja": src.name_ja,
            "aliases_ja": list(src.aliases_ja),
            "task": src.task,
            "kind": src.kind,
            "audiences": list(src.audiences),
            "difficulty": src.difficulty,
            "use_cases_ja": list(src.use_cases_ja),
            "input_description_ja": src.input_description_ja,
            "output_description_ja": src.output_description_ja,
            "画像数": src.image_count,
            "サンプル数": src.sample_count,
            "ダウンロードサイズMB": src.download_size_mb,
            "audit_status": src.audit_status,
            "audit_report": src.audit_report,
            "固定版": src.tag,
            "権利上の注意": src.rights_note,
            "publication_status": _source_status(src),
        })
    return result


def list_tasks(*, audience: str = "student", include_preview: bool = False) -> list[dict[str, Any]]:
    """課題タイプと、その条件で選べるデータIDを一覧表示する。"""
    if audience not in {"student", "teacher"}:
        raise ValueError("audienceはstudentまたはteacherです。")
    result = []
    for task, task_info in _TASKS.items():
        items = list_available(task=task, audience=audience, include_preview=include_preview)
        if not items:
            continue
        result.append({
            "task": task,
            **task_info,
            "datasets": [item["id"] for item in items],
        })
    return result


def info(dataset_id: str | None = None) -> dict[str, Any] | list[dict[str, Any]]:
    """配布元の公表情報を表示する。実ファイル監査結果ではない。"""
    if dataset_id is None:
        return list_available()
    src = _source(dataset_id)
    return {
        "id": src.id, "name_ja": src.name_ja, "aliases_ja": list(src.aliases_ja), "kind": src.kind,
        "task": src.task, "audiences": list(src.audiences), "difficulty": src.difficulty,
        "use_cases_ja": list(src.use_cases_ja), "input_description_ja": src.input_description_ja,
        "output_description_ja": src.output_description_ja,
        "ダウンロードサイズMB": src.download_size_mb, "publication_status": _source_status(src),
        "audit_status": src.audit_status, "audit_report": src.audit_report,
        "画像数（配布元申告）": src.image_count, "固定版": src.tag,
        "サンプル数": src.sample_count,
        "取得元": src.url,
        "ZIPのSHA-256": src.sha256,
        "ファイルSHA-256": dict(src.file_sha256),
        "権利上の注意": src.rights_note,
        "license_info": dict(src.license_info or {}),
        "source_info": dict(src.source_info or {}),
        "状態": (
            "共通artifactは準備済みですが、公開Releaseがまだありません。"
            if not src.published else
            "教師向けプレビュー。権利確認中のため正式一覧には未掲載。"
            if src.preview else "固定版の取得条件を確認済み。権利状態と実体監査は個別項目を参照。"
        ),
    }


def list_preview() -> list[dict[str, Any]]:
    """権利・公開確認中の教師向けプレビュー候補を一覧表示する。"""
    return [
        {
            "id": src.id,
            "name_ja": src.name_ja,
            "kind": src.kind,
            "fixed_version": src.tag,
            "publication_status": "teacher_preview_only",
            "rights_note": src.rights_note,
        }
        for src in _PREVIEW_SOURCES.values()
    ]


def _source(dataset_id: str) -> ReleaseSource:
    if not isinstance(dataset_id, str):
        raise DatasetError("データセット名は英語IDまたは登録済みの日本語名で指定してください。")
    if dataset_id in _SOURCES:
        return _SOURCES[dataset_id]
    if dataset_id in _PREVIEW_SOURCES:
        return _PREVIEW_SOURCES[dataset_id]
    matches = [
        src for src in (*_SOURCES.values(), *_PREVIEW_SOURCES.values())
        if dataset_id == src.name_ja or dataset_id in src.aliases_ja
    ]
    if len(matches) == 1:
        return matches[0]
    raise DatasetError(f"未対応のデータセットです（完全一致のID・別名のみ利用できます）: {dataset_id}")


def _cache_dir(cache_dir: str | Path | None) -> Path:
    if cache_dir is not None:
        return Path(cache_dir).expanduser()
    base = Path(os.environ.get("XDG_CACHE_HOME", "~/.cache")).expanduser()
    return base / "cvlesson"


def _cache_source_ids(dataset_id: str | None) -> list[str]:
    if dataset_id is not None:
        return [_source(dataset_id).id]
    return sorted({src.id for src in (*_SOURCES.values(), *_PREVIEW_SOURCES.values())})


def _cache_tree_bytes(root: Path) -> tuple[int, int]:
    """登録済みcache treeのregular fileだけを数え、symlink等は拒否する。"""
    total_bytes = 0
    file_count = 0
    def walk_error(exc: OSError) -> None:
        raise DatasetError(f"キャッシュを確認できません: {root}") from exc

    for current, dirs, files in os.walk(root, followlinks=False, onerror=walk_error):
        current_path = Path(current)
        for name in dirs:
            if (current_path / name).is_symlink():
                raise DatasetError(f"キャッシュ内にsymlinkがあります。削除前に確認してください: {current_path / name}")
        for name in files:
            path = current_path / name
            if path.is_symlink():
                raise DatasetError(f"キャッシュ内にsymlinkがあります。削除前に確認してください: {path}")
            try:
                file_stat = os.stat(path, follow_symlinks=False)
            except OSError as exc:
                raise DatasetError(f"キャッシュのサイズを確認できません: {path}") from exc
            if not stat.S_ISREG(file_stat.st_mode):
                raise DatasetError(f"通常ファイルではない項目がキャッシュ内にあります: {path}")
            total_bytes += file_stat.st_size
            file_count += 1
    return total_bytes, file_count


def cache_info(dataset_id: str | None = None, *, cache_dir: str | Path | None = None) -> dict[str, Any]:
    """登録済みデータのcheckout外キャッシュ容量を返す。ネットワークには接続しない。"""
    root = _cache_dir(cache_dir)
    if root.exists() and not root.is_dir():
        raise DatasetError(f"キャッシュ先がディレクトリではありません: {root}")
    sources_root = root / "sources"
    if sources_root.is_symlink():
        raise DatasetError(f"キャッシュのsourcesがsymlinkです。確認してください: {sources_root}")
    if not sources_root.exists():
        return {"cache_dir": str(root), "total_bytes": 0, "datasets": []}
    if not sources_root.is_dir():
        raise DatasetError(f"キャッシュのsourcesがディレクトリではありません: {sources_root}")

    items: list[dict[str, Any]] = []
    for source_id in _cache_source_ids(dataset_id):
        target = sources_root / source_id
        if target.is_symlink():
            raise DatasetError(f"データキャッシュがsymlinkです。確認してください: {target}")
        if not target.exists():
            continue
        if not target.is_dir():
            raise DatasetError(f"データキャッシュがディレクトリではありません: {target}")
        size, count = _cache_tree_bytes(target)
        versions = sorted(
            path.name for path in target.iterdir()
            if path.is_dir() and not path.is_symlink()
        )
        items.append({"dataset_id": source_id, "versions": versions, "bytes": size, "files": count})
    return {
        "cache_dir": str(root),
        "total_bytes": sum(item["bytes"] for item in items),
        "datasets": items,
    }


def clear_cache(dataset_id: str | None = None, *, cache_dir: str | Path | None = None) -> dict[str, Any]:
    """登録済みデータのキャッシュを削除する。学習・読み込み処理を止めてから実行する。"""
    root = _cache_dir(cache_dir)
    sources_root = root / "sources"
    before = cache_info(dataset_id, cache_dir=root)
    targets = [sources_root / item["dataset_id"] for item in before["datasets"]]
    removed_ids = [item["dataset_id"] for item in before["datasets"]]
    for target in targets:
        # cache_infoが全対象を事前検査してから削除し、symlinkを辿らない。
        shutil.rmtree(target)
    return {
        "cache_dir": str(root),
        "removed_bytes": before["total_bytes"],
        "removed_datasets": removed_ids,
    }


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _download(url: str, destination: Path, *, max_bytes: int) -> None:
    """固定公開Releaseから容量制限付きで取得。リダイレクト後のURLは記録しない。"""
    request = urllib.request.Request(url, headers={"User-Agent": "cvlesson/0.0.1"})
    last_error: Exception | None = None
    for attempt in range(3):
        try:
            total = 0
            with urllib.request.urlopen(request, timeout=45) as response, destination.open("wb") as f:
                while chunk := response.read(1024 * 1024):
                    total += len(chunk)
                    if total > max_bytes:
                        raise DatasetError("指定した上限よりダウンロードが大きいため停止しました。")
                    f.write(chunk)
            return
        except DatasetError:
            raise
        except (OSError, urllib.error.URLError, TimeoutError) as exc:
            last_error = exc
            destination.unlink(missing_ok=True)
            if attempt < 2:
                time.sleep(0.2 * (attempt + 1))
    raise DatasetError(f"固定Releaseのダウンロードに失敗しました: {last_error}") from last_error


def _archive_entries(archive: zipfile.ZipFile, src: ReleaseSource) -> list[zipfile.ZipInfo]:
    entries = archive.infolist()
    if len(entries) > src.max_files:
        raise DatasetError("ZIPのファイル数が上限を超えています。")
    total = 0
    seen: set[str] = set()
    root = src.archive_root_name or src.case_id
    for entry in entries:
        name = entry.filename
        path = PurePosixPath(name)
        is_root_directory = src.archive_root_folder and name.rstrip("/") == root and name.endswith("/")
        if (not name or "\\" in name or "\x00" in name or path.is_absolute()
                or len(path.parts) < (2 if src.archive_root_folder else 1) and not is_root_directory
                or src.archive_root_folder and path.parts[0] != root
                or not src.archive_root_folder and path.parts[0] not in {
                    "LICENSE.md", "README.md", "annotations.jsonl", "classes.json",
                    "metadata.jsonl", "manifest.json", "images", "labels",
                }
                or any(part in {"", ".", ".."} for part in path.parts)
                or re.match(r"^[A-Za-z]:", name)):
            raise DatasetError(f"安全でないZIP内のパスです: {name}")
        if name in seen:
            raise DatasetError(f"ZIP内に同じ名前が重複しています: {name}")
        seen.add(name)
        mode = (entry.external_attr >> 16) & 0xFFFF
        if stat.S_ISLNK(mode):
            raise DatasetError(f"ZIPにシンボリックリンクが含まれています: {name}")
        total += entry.file_size
        if total > src.max_unpacked_bytes:
            raise DatasetError("ZIPの展開後サイズが上限を超えています。")
    return entries


def _extract_verified(archive_path: Path, destination: Path, src: ReleaseSource) -> Path:
    """検証後に一時フォルダへ安全に展開する。存在する配布元は一切操作しない。"""
    with zipfile.ZipFile(archive_path) as archive:
        entries = _archive_entries(archive, src)
        for entry in entries:
            member = destination.joinpath(*PurePosixPath(entry.filename).parts)
            if entry.is_dir():
                member.mkdir(parents=True, exist_ok=True)
                continue
            member.parent.mkdir(parents=True, exist_ok=True)
            # ZIP内パスは上で検証済み。ファイルは直接展開せずチャンクコピー。
            with archive.open(entry) as reader, member.open("xb") as writer:
                shutil.copyfileobj(reader, writer, length=1024 * 1024)
    root = destination / (src.archive_root_name or src.case_id) if src.archive_root_folder else destination
    _validate_case(root, src)
    return root


def _validate_detection_case(root: Path, src: ReleaseSource, manifest: dict[str, Any]) -> dict[str, Any]:
    required = ("classes.json", "annotations.jsonl", "metadata.jsonl", "README.md")
    if not all((root / name).is_file() for name in required):
        raise DatasetError("物体検出artifactの必須ファイルがありません。")
    classes_data = json.loads((root / "classes.json").read_text(encoding="utf-8"))
    classes = classes_data.get("classes") if isinstance(classes_data, dict) else classes_data
    if (not isinstance(classes, list) or not classes or classes != manifest.get("classes")
            or any(not isinstance(name, str) for name in classes) or len(classes) != len(set(classes))):
        raise DatasetError("classes.jsonとmanifest.jsonのクラスが一致しません。")
    records = [json.loads(line) for line in (root / "annotations.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
    metadata_rows = [json.loads(line) for line in (root / "metadata.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
    if len(records) != src.image_count or len(metadata_rows) != src.image_count:
        raise DatasetError("物体検出artifactの注釈件数が画像数と一致しません。")
    metadata_by_file: dict[str, dict[str, Any]] = {}
    for item in metadata_rows:
        name = item.get("file_name")
        if not isinstance(name, str) or name in metadata_by_file:
            raise DatasetError("metadata.jsonlの画像パスが不正または重複しています。")
        metadata_by_file[name] = item

    observed_images: set[str] = set()
    expected_label_files: set[str] = set()
    for record in records:
        image = record.get("file_name")
        label_file = record.get("label_file")
        split = record.get("split")
        parts = PurePosixPath(image).parts if isinstance(image, str) else ()
        label_parts = PurePosixPath(label_file).parts if isinstance(label_file, str) else ()
        if (len(parts) != 3 or parts[0] != "images" or any(part in {"", ".", ".."} for part in parts)
                or "\\" in image or "\x00" in image or split not in {"train", "valid", "test"}
                or parts[1] != split or PurePosixPath(image).suffix.lower() not in {".jpg", ".jpeg", ".png"}
                or len(label_parts) != 3 or label_parts[:2] != ("labels", split)
                or any(part in {"", ".", ".."} for part in label_parts)
                or "\\" in label_file or "\x00" in label_file
                or PurePosixPath(label_file).suffix.lower() != ".txt"
                or PurePosixPath(label_file).stem != PurePosixPath(image).stem
                or image in observed_images):
            raise DatasetError(f"物体検出artifactの画像・ラベルパスが不正です: {image}")
        image_path, label_path = root / image, root / label_file
        if image_path.is_symlink() or not image_path.is_file() or label_path.is_symlink() or not label_path.is_file():
            raise DatasetError(f"物体検出artifactの画像またはラベルがありません: {image}")
        observed_images.add(image)
        expected_label_files.add(label_file)
        annotations = record.get("annotations")
        if not isinstance(annotations, list):
            raise DatasetError(f"物体検出annotationが配列ではありません: {image}")
        normalized_rows = []
        for annotation in annotations:
            if not isinstance(annotation, dict):
                raise DatasetError(f"物体検出annotationが不正です: {image}")
            try:
                class_id = annotation["class_id"]
                coords = [float(annotation[key]) for key in ("x_center", "y_center", "width", "height")]
            except (KeyError, TypeError, ValueError) as exc:
                raise DatasetError(f"物体検出annotationの値が不正です: {image}") from exc
            if (type(class_id) is not int or not 0 <= class_id < len(classes)
                    or any(not 0 <= value <= 1 for value in coords)
                    or coords[2] <= 0 or coords[3] <= 0
                    or coords[0] - coords[2] / 2 < 0 or coords[1] - coords[3] / 2 < 0
                    or coords[0] + coords[2] / 2 > 1 or coords[1] + coords[3] / 2 > 1
                    or annotation.get("source_annotation_format") not in {"bbox", "polygon"}):
                raise DatasetError(f"物体検出annotationが範囲外です: {image}")
            normalized_rows.append([class_id, *coords])
        label_rows = []
        for line in label_path.read_text(encoding="utf-8").splitlines():
            values = line.split()
            if not values:
                continue
            if len(values) != 5:
                raise DatasetError(f"共通形式の検出ラベルは5列で指定します: {label_file}")
            try:
                label_row = [int(values[0]), *map(float, values[1:])]
            except ValueError as exc:
                raise DatasetError(f"共通形式の検出ラベルが数値ではありません: {label_file}") from exc
            class_id, x_center, y_center, width, height = label_row
            if (not 0 <= class_id < len(classes) or any(not 0 <= value <= 1 for value in label_row[1:])
                    or width <= 0 or height <= 0 or x_center - width / 2 < 0 or y_center - height / 2 < 0
                    or x_center + width / 2 > 1 or y_center + height / 2 > 1):
                raise DatasetError(f"共通形式の検出ラベルが範囲外です: {label_file}")
            label_rows.append(label_row)
        if len(normalized_rows) != len(label_rows) or any(
            expected[0] != actual[0] or any(abs(a - b) > 1e-8 for a, b in zip(expected[1:], actual[1:]))
            for expected, actual in zip(normalized_rows, label_rows)
        ):
            raise DatasetError(f"annotations.jsonlとYOLOラベルが一致しません: {label_file}")
        meta = metadata_by_file.get(image)
        if meta != {"file_name": image, "label_file": label_file, "split": split, "annotation_count": len(annotations)}:
            raise DatasetError(f"metadata.jsonlとannotations.jsonlが一致しません: {image}")

    actual_images = {
        path.relative_to(root).as_posix() for path in (root / "images").rglob("*")
        if path.is_file() and not path.is_symlink()
    }
    actual_labels = {
        path.relative_to(root).as_posix() for path in (root / "labels").rglob("*")
        if path.is_file() and not path.is_symlink()
    }
    if observed_images != actual_images or expected_label_files != actual_labels or set(metadata_by_file) != observed_images:
        raise DatasetError("画像・ラベル・metadataのファイル集合が一致しません。")
    return manifest


def _validate_case(root: Path, src: ReleaseSource) -> dict[str, Any]:
    if src.kind == "regression":
        return _validate_regression_case(root, src)
    if src.kind == "segmentation":
        return _validate_segmentation_case(root, src)
    if src.kind == "detection":
        required = [root / x for x in ("manifest.json", "classes.json", "annotations.jsonl", "metadata.jsonl", "README.md")]
    else:
        required = [root / x for x in ("manifest.json", "labels.csv", "metadata.jsonl", "README.md")]
    if not all(p.is_file() for p in required):
        raise DatasetError("manifest.jsonなどの必須ファイルがありません。")
    manifest = json.loads((root / "manifest.json").read_text(encoding="utf-8"))
    version = src.tag if src.preview else "v" + src.tag.rsplit("-v", 1)[1]
    if (manifest.get("case_id") != src.case_id or manifest.get("version") != version
            or manifest.get("image_count") != src.image_count):
        raise DatasetError("manifest.jsonの版または画像枚数が固定Releaseの情報と一致しません。")
    if src.kind == "detection":
        return _validate_detection_case(root, src, manifest)
    with (root / "labels.csv").open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        if src.kind == "classification":
            required_cols = {"image", "label", "split"}
        elif src.kind == "ocr":
            required_cols = {"image", "record_json", "split", "sample_id"}
        else:
            required_cols = {"image", "caption"}
        if not required_cols.issubset(set(reader.fieldnames or [])):
            raise DatasetError("labels.csvの列名が期待と異なります。")
        rows = list(reader)
    if len(rows) != src.image_count:
        raise DatasetError("labels.csvの行数が画像数と一致しません。")
    observed: set[str] = set()
    expected_metadata: dict[str, dict[str, str]] = {}
    for row in rows:
        image = row["image"]
        parts = PurePosixPath(image).parts
        if (not parts or parts[0] != "images" or ".." in parts
                or "\\" in image or PurePosixPath(image).suffix.lower() not in {".png", ".jpg", ".jpeg", ".pgm"}
                or image in observed):
            raise DatasetError(f"画像パスが不正・重複しています: {image}")
        observed.add(image)
        if src.kind == "classification":
            label, split = row["label"], row["split"]
            if label not in manifest.get("classes", []) or split not in {"train", "val", "test"}:
                raise DatasetError(f"ラベルまたは分割に誤りがあります: {image}")
            if parts[:3] != ("images", split, label):
                raise DatasetError(f"画像配置とラベルが一致しません: {image}")
            expected_metadata[image] = {"label": label, "split": split}
        elif src.kind == "ocr":
            try:
                record = json.loads(row["record_json"])
            except (TypeError, json.JSONDecodeError) as exc:
                raise DatasetError(f"構造化見本のJSONが不正です: {image}") from exc
            split, sample_id = row["split"], row["sample_id"]
            if (not isinstance(record, dict) or split != "eval" or not sample_id
                    or parts[:2] != ("images", split)):
                raise DatasetError(f"OCR見本または画像配置に誤りがあります: {image}")
            expected_metadata[image] = {"record": record, "split": split, "sample_id": sample_id}
        else:
            caption = row["caption"]
            if not caption.strip():
                raise DatasetError(f"画像の説明文が空です: {image}")
            expected_metadata[image] = {"text": caption}
    found_images = {p.relative_to(root).as_posix() for p in (root / "images").rglob("*") if p.is_file()}
    if observed != found_images:
        raise DatasetError("画像ファイルとlabels.csvの記録が一致しません。")
    actual_metadata: dict[str, dict[str, str]] = {}
    for line in (root / "metadata.jsonl").read_text(encoding="utf-8").splitlines():
        if line.strip():
            item = json.loads(line)
            name = item["file_name"]
            if name in actual_metadata:
                raise DatasetError(f"metadata.jsonlに重複があります: {name}")
            if src.kind == "classification":
                actual_metadata[name] = {"label": item["label"], "split": item["split"]}
            elif src.kind == "ocr":
                actual_metadata[name] = {"record": item["record"], "split": item["split"], "sample_id": item["sample_id"]}
            else:
                actual_metadata[name] = {"text": item["text"]}
    if actual_metadata != expected_metadata:
        raise DatasetError("metadata.jsonlとlabels.csvが一致しません。")
    return manifest


def _validate_regression_case(root: Path, src: ReleaseSource) -> dict[str, Any]:
    required = ("manifest.json", "metadata.csv", "README.md", "LICENSE.txt")
    if not all((root / name).is_file() for name in required):
        raise DatasetError("ペア画像回帰artifactの必須ファイルがありません。")
    manifest = json.loads((root / "manifest.json").read_text(encoding="utf-8"))
    pair_count = src.sample_count
    if (manifest.get("dataset_id") != src.case_id
            or manifest.get("artifact_version") != "0.1.0"
            or manifest.get("source_license") != "CC BY 4.0"
            or manifest.get("transformation", {}).get("included_pairs") != pair_count
            or pair_count is None):
        raise DatasetError("ペア画像回帰manifestの版・ライセンス・ペア数が一致しません。")

    rows = _read_rows(root / "metadata.csv")
    if len(rows) != pair_count:
        raise DatasetError("metadata.csvの行数が固定Releaseのペア数と一致しません。")
    required_columns = {
        "sample_id", "source_record_id", "food_category", "food_name_original",
        "image_before", "image_after", "weight_before_g", "weight_after_g",
        "consumed_weight_g", "leftover_ratio", "visual_leftover_level",
        "weight_order_anomaly", "source_image_before", "source_image_after",
        "food_category_id", "split",
    }
    if not rows or not required_columns.issubset(rows[0]):
        raise DatasetError("metadata.csvの列が固定artifactの仕様と一致しません。")

    sample_ids: set[str] = set()
    image_names: set[str] = set()
    for row in rows:
        sample_id = row["sample_id"]
        before_name, after_name = row["image_before"], row["image_after"]
        before_parts = PurePosixPath(before_name).parts
        after_parts = PurePosixPath(after_name).parts
        if (not sample_id or sample_id in sample_ids
                or len(before_parts) != 3 or before_parts[0:2] != ("images", "before")
                or len(after_parts) != 3 or after_parts[0:2] != ("images", "after")
                or any(part in {"", ".", ".."} for part in (*before_parts, *after_parts))
                or "\\" in before_name or "\\" in after_name
                or PurePosixPath(before_name).suffix.lower() not in {".jpg", ".jpeg"}
                or PurePosixPath(after_name).suffix.lower() not in {".jpg", ".jpeg"}
                or before_name == after_name or before_name in image_names or after_name in image_names
                or row["split"] not in {"train", "validation", "test"}):
            raise DatasetError(f"食前・食後画像の対応、sample_id、またはsplitが不正です: {sample_id}")
        sample_ids.add(sample_id)
        image_names.update((before_name, after_name))
        try:
            source_record_id = int(row["source_record_id"])
            category_id = int(row["food_category_id"])
            visual_level = int(row["visual_leftover_level"])
            before_weight = float(row["weight_before_g"])
            after_weight = float(row["weight_after_g"])
            consumed_weight = float(row["consumed_weight_g"])
            leftover_ratio = float(row["leftover_ratio"])
        except (TypeError, ValueError) as exc:
            raise DatasetError(f"食事計測値が数値ではありません: {sample_id}") from exc
        values = (before_weight, after_weight, consumed_weight, leftover_ratio)
        anomaly_text = row["weight_order_anomaly"].lower()
        if (source_record_id <= 0 or category_id < 0 or not 1 <= visual_level <= 7
                or any(not math.isfinite(value) for value in values)
                or before_weight <= 0 or after_weight < 0
                or anomaly_text not in {"true", "false"}
                or (anomaly_text == "true") != (after_weight > before_weight)
                or not math.isclose(consumed_weight, before_weight - after_weight, rel_tol=1e-8, abs_tol=1e-8)
                or not math.isclose(leftover_ratio, after_weight / before_weight, rel_tol=1e-8, abs_tol=1e-8)):
            raise DatasetError(f"食事計測値または導出列が不正です: {sample_id}")

    found_images: set[str] = set()
    for path in (root / "images").rglob("*"):
        if path.is_symlink():
            raise DatasetError(f"ペア画像回帰artifactにsymlinkがあります: {path}")
        if path.is_file():
            found_images.add(path.relative_to(root).as_posix())
    if found_images != image_names or len(found_images) != src.image_count:
        raise DatasetError("食前・食後画像とmetadata.csvのファイル集合が一致しません。")
    return manifest



def _validate_segmentation_case(root: Path, src: ReleaseSource) -> dict[str, Any]:
    required = ("manifest.json", "labels.csv", "metadata.jsonl", "README.md", "LICENSE.md")
    if not all((root / name).is_file() for name in required):
        raise DatasetError("領域分割artifactの必須ファイルがありません。")
    manifest = json.loads((root / "manifest.json").read_text(encoding="utf-8"))
    if (manifest.get("dataset_id") != src.case_id
            or manifest.get("artifact_version") != "0.1.0"
            or manifest.get("image_count") != src.image_count
            or manifest.get("classes") != list(src.classes)):
        raise DatasetError("領域分割manifestの版・画像数・クラスが固定Releaseと一致しません。")
    multiclass = manifest.get("mask_encoding") == "class_id_grayscale"
    if multiclass:
        classes_path = root / "classes.json"
        if not classes_path.is_file():
            raise DatasetError("多クラス画素マスクartifactのclasses.jsonがありません。")
        class_items = json.loads(classes_path.read_text(encoding="utf-8")).get("classes")
        if (not isinstance(class_items, list) or not all(isinstance(item, dict) for item in class_items)
                or [item.get("name") for item in class_items] != list(src.classes)
                or [item.get("id") for item in class_items] != list(range(len(src.classes)))):
            raise DatasetError("classes.jsonの画素クラスIDとmanifestが一致しません。")
    rows = _read_rows(root / "labels.csv")
    if not rows or len(rows) != src.image_count:
        raise DatasetError("領域分割artifactのlabels.csv件数が画像数と一致しません。")
    expected_images: set[str] = set()
    expected_masks: set[str] = set()
    class_to_id = {name: index for index, name in enumerate(src.classes)}
    for row in rows:
        image, mask = row.get("image", ""), row.get("mask", "")
        image_parts, mask_parts = PurePosixPath(image).parts, PurePosixPath(mask).parts
        cls, split = row.get("class_name", ""), row.get("split", "")
        if multiclass:
            valid_layout = (
                len(image_parts) == 3 and len(mask_parts) == 3
                and PurePosixPath(image_parts[2]).stem == PurePosixPath(mask_parts[2]).stem
                and cls == "__pixel_labels__" and row.get("class_id") == "-1"
            )
        else:
            valid_layout = (
                len(image_parts) == 4 and len(mask_parts) == 4
                and cls in class_to_id and image_parts[2] == cls and mask_parts[2] == cls
                and mask_parts[-1] == PurePosixPath(image_parts[-1]).stem + "_mask.png"
                and row.get("class_id") == str(class_to_id.get(cls))
            )
        if ("\\" in image or "\\" in mask or image_parts[:2] != ("images", split)
                or mask_parts[:2] != ("masks", split) or split not in {"train", "val", "test"}
                or any(part in {"", ".", ".."} for part in (*image_parts, *mask_parts))
                or not valid_layout
                or PurePosixPath(image).suffix.lower() not in ({".jpg", ".jpeg", ".png"} if multiclass else {".jpg", ".jpeg"})
                or PurePosixPath(mask).suffix.lower() != ".png"
                or image in expected_images or mask in expected_masks):
            raise DatasetError(f"領域分割artifactの画像・マスク対応が不正です: {image}")
        image_path, mask_path = root / image, root / mask
        if any(path.is_symlink() or not path.is_file() for path in (image_path, mask_path)):
            raise DatasetError(f"領域分割artifactの画像またはマスクがありません: {image}")
        expected_images.add(image)
        expected_masks.add(mask)
    found_images = {path.relative_to(root).as_posix() for path in (root / "images").rglob("*") if path.is_file()}
    found_masks = {path.relative_to(root).as_posix() for path in (root / "masks").rglob("*") if path.is_file()}
    if found_images != expected_images or found_masks != expected_masks:
        raise DatasetError("領域分割artifactの画像・マスクとlabels.csvの集合が一致しません。")
    metadata_rows = [json.loads(line) for line in (root / "metadata.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
    expected_metadata = [{
        "image": row["image"], "mask": row["mask"], "class_name": row["class_name"],
        "class_id": int(row["class_id"]), "split": row["split"],
    } for row in rows]
    if metadata_rows != expected_metadata:
        raise DatasetError("領域分割artifactのmetadata.jsonlとlabels.csvが一致しません。")
    return manifest


def _read_idx_gzip(path: Path, *, image: bool) -> tuple[int, int, int, bytes] | tuple[int, bytes]:
    """IDX gzipを読み、ヘッダーとペイロードの長さを検査する。"""
    with gzip.open(path, "rb") as stream:
        if image:
            header = stream.read(16)
            if len(header) != 16:
                raise DatasetError(f"IDX画像ヘッダーが短すぎます: {path.name}")
            magic, count, rows, cols = struct.unpack(">IIII", header)
            if magic != 2051 or rows <= 0 or cols <= 0:
                raise DatasetError(f"IDX画像ヘッダーが不正です: {path.name}")
            payload = stream.read()
            expected = count * rows * cols
            if len(payload) != expected:
                raise DatasetError(f"IDX画像の件数またはサイズが一致しません: {path.name}")
            return count, rows, cols, payload
        header = stream.read(8)
        if len(header) != 8:
            raise DatasetError(f"IDXラベルヘッダーが短すぎます: {path.name}")
        magic, count = struct.unpack(">II", header)
        if magic != 2049:
            raise DatasetError(f"IDXラベルヘッダーが不正です: {path.name}")
        payload = stream.read()
        if len(payload) != count:
            raise DatasetError(f"IDXラベルの件数が一致しません: {path.name}")
        return count, payload


def _materialize_idx_case(raw: Path, destination: Path, src: ReleaseSource) -> Path:
    file_names = {name: raw / name for name in src.file_urls}
    train_count, rows, cols, train_pixels = _read_idx_gzip(
        file_names["train-images-idx3-ubyte.gz"], image=True
    )
    train_label_count, train_labels = _read_idx_gzip(
        file_names["train-labels-idx1-ubyte.gz"], image=False
    )
    test_count, test_rows, test_cols, test_pixels = _read_idx_gzip(
        file_names["t10k-images-idx3-ubyte.gz"], image=True
    )
    test_label_count, test_labels = _read_idx_gzip(
        file_names["t10k-labels-idx1-ubyte.gz"], image=False
    )
    if (train_count != train_label_count or test_count != test_label_count
            or rows != test_rows or cols != test_cols
            or train_count + test_count != src.image_count):
        raise DatasetError("IDX画像とラベルの件数、サイズ、固定版の公表件数が一致しません。")

    root = destination / (src.archive_root_name or src.case_id)
    images = root / "images"
    root.mkdir(parents=True, exist_ok=True)
    classes = [str(value) for value in range(10)]
    class_counts = Counter()
    csv_rows: list[tuple[str, str, str]] = []
    metadata_rows: list[str] = []
    pgm_header = f"P5\n{cols} {rows}\n255\n".encode("ascii")
    for split, count, pixels, labels in (
        ("train", train_count, train_pixels, train_labels),
        ("test", test_count, test_pixels, test_labels),
    ):
        for index in range(count):
            label = str(labels[index])
            class_counts[label] += 1
            relative = f"images/{split}/{label}/{index + 1:06d}.pgm"
            target = root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            start = index * rows * cols
            target.write_bytes(pgm_header + pixels[start:start + rows * cols])
            csv_rows.append((relative, label, split))
            metadata_rows.append(json.dumps({
                "file_name": relative, "label": label, "split": split,
            }, ensure_ascii=False))

    (root / "manifest.json").write_text(json.dumps({
        "case_id": src.case_id,
        "version": src.tag,
        "image_count": src.image_count,
        "classes": classes,
        "source_format": "IDX gzip; materialized deterministic PGM cache",
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    with (root / "labels.csv").open("w", encoding="utf-8", newline="") as stream:
        stream.write("image,label,split\n")
        stream.writelines(f"{image},{label},{split}\n" for image, label, split in csv_rows)
    (root / "metadata.jsonl").write_text("\n".join(metadata_rows) + "\n", encoding="utf-8")
    (root / "README.md").write_text(
        "固定コミットのIDX gzipを、元データを変更せずPGMへ変換したキャッシュです。\n",
        encoding="utf-8",
    )
    return root


def _get_idx_preview(src: ReleaseSource, *, cache_dir: str | Path | None,
                     allow_download: bool) -> DatasetBundle:
    base = _cache_dir(cache_dir) / "sources" / src.id / src.tag
    extracted = base / src.case_id
    ready = extracted / ".cvlesson-ready.json"
    if ready.is_file():
        try:
            marker = json.loads(ready.read_text(encoding="utf-8"))
            if marker.get("sha256") == src.file_sha256:
                manifest = _validate_case(extracted, src)
                return DatasetBundle(src.id, src.kind, extracted, manifest, src.url, src.tag, src.rights_note)
        except (ValueError, KeyError, OSError, DatasetError, json.JSONDecodeError):
            pass
    if not allow_download:
        raise DatasetError("キャッシュが見つからないため、ネットワークを利用せず停止しました。")
    base.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="cvlesson-idx-", dir=base) as work:
        workspace = Path(work)
        raw = workspace / "raw"
        raw.mkdir()
        for name, url in src.file_urls.items():
            destination = raw / name
            _download(url, destination, max_bytes=MAX_ARCHIVE_BYTES)
            if destination.stat().st_size != src.file_sizes[name]:
                raise DatasetError(f"固定ファイルのサイズが一致しません: {name}")
            if _sha256(destination) != src.file_sha256[name]:
                raise DatasetError(f"固定ファイルのSHA-256が一致しません: {name}")
        new_root = _materialize_idx_case(raw, workspace / "unpacked", src)
        (new_root / ".cvlesson-ready.json").write_text(
            json.dumps({"sha256": src.file_sha256, "source_url": src.url, "version": src.tag}, ensure_ascii=False),
            encoding="utf-8",
        )
        if extracted.exists():
            raise DatasetError("既存のプレビューキャッシュが不正です。別のcache_dirを指定してください。")
        shutil.move(str(new_root), extracted)
    manifest = _validate_case(extracted, src)
    return DatasetBundle(src.id, src.kind, extracted, manifest, src.url, src.tag, src.rights_note)


def get(dataset_id: str, *, cache_dir: str | Path | None = None,
        allow_download: bool = True, allow_preview: bool = False) -> DatasetBundle:
    """固定Releaseのデータを取得する。配布元へ書き込みは行わない。"""
    src = _source(dataset_id)
    if not src.published:
        raise DatasetError("データartifactは準備済みですが、公開Releaseがまだありません。公開後に再度お試しください。")
    if src.preview:
        if not allow_preview:
            raise DatasetError(
                "このデータセットは教師向けプレビューです。権利確認が完了するまで正式一覧には公開していません。"
            )
        return _get_idx_preview(src, cache_dir=cache_dir, allow_download=allow_download)
    base = _cache_dir(cache_dir) / "sources" / src.id / src.tag
    extracted = base / src.case_id
    ready = extracted / ".cvlesson-ready.json"
    if ready.is_file():
        try:
            marker = json.loads(ready.read_text(encoding="utf-8"))
            if marker.get("sha256") == src.sha256:
                manifest = _validate_case(extracted, src)
                return DatasetBundle(src.id, src.kind, extracted, manifest, src.url, src.tag, src.rights_note)
        except (ValueError, KeyError, OSError, DatasetError, json.JSONDecodeError):
            pass
    if not allow_download:
        raise DatasetError("キャッシュが見つからないため、ネットワークを利用せず停止しました。")
    base.mkdir(parents=True, exist_ok=True)
    # 一時ファイル・ディレクトリに作成し、完了後に置き換える。
    with tempfile.TemporaryDirectory(prefix="cvlesson-", dir=base) as work:
        workspace = Path(work)
        archive = workspace / f"{src.case_id}.zip"
        _download(src.url, archive, max_bytes=src.max_archive_bytes)
        if archive.stat().st_size != src.archive_size:
            raise DatasetError("ZIPのサイズが固定Releaseの登録値と異なります。")
        if _sha256(archive) != src.sha256:
            raise DatasetError("SHA-256が一致しません。取得したZIPを使用しません。")
        new_root = _extract_verified(archive, workspace / "unpacked", src)
        (new_root / ".cvlesson-ready.json").write_text(
            json.dumps({"sha256": src.sha256, "source_url": src.url, "version": src.tag}, ensure_ascii=False),
            encoding="utf-8",
        )
        if extracted.exists():
            # 使用中の内容を保護するため、既存のデータは上書きしない。
            raise DatasetError("既存のキャッシュが不正です。別のcache_dirを指定してください。")
        shutil.move(str(new_root), extracted)
    manifest = _validate_case(extracted, src)
    return DatasetBundle(src.id, src.kind, extracted, manifest, src.url, src.tag, src.rights_note)
