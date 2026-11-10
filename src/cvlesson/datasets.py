"""公開済みCV_sample_data Releaseを読み取り専用で取得する最小実装。

このモジュールは配布元を変更しない。既存Releaseの固定URLとSHA-256を照合する。
"""
from __future__ import annotations

import csv
import gzip
import hashlib
import json
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
        """分類または検出データを共通列のDataFrameに変換する。

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
            records.append({
                "image_path": str((self.root / image).resolve()),
                "mask_path": str((self.root / row["mask"]).resolve()),
                "label": row["class_name"],
                "label_ja": names_ja.get(row["class_name"], row["class_name"]),
                "label_id": int(row["class_id"]),
                "split": row["split"],
                "sample_id": _sample_id(image),
            })
        return records

    @property
    def splits(self) -> dict[str, int]:
        """標準化後のtrain/val/test件数。"""
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
            from PIL import Image
        except ImportError as exc:
            raise DatasetError("画像表示にはPillowとmatplotlibが必要です。") from exc
        frame = self.to_df(seed=seed)
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
                    axis.imshow(mask.convert("L"), cmap="Reds", vmin=0, vmax=255, alpha=0.45)
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
        id="bangladeshi_ewaste_image", case_id="bangladeshi_ewaste_image",
        tag="bangladeshi-ewaste-v0.1.0",
        sha256="fe06d5579e3a84010e0e6ccd7d90d8230ca72d5fcd39719d6d6d8731595007fa",
        archive_size=71_762_431, image_count=2157,
        kind="detection", name_ja="バングラデシュの廃棄物品画像（12種類）",
        rights_note="CC BY 4.0。作者・出典・変更の表示が必要。予測結果を現実のごみ分別や医療廃棄物処理に使わないでください。",
        aliases_ja=("廃棄物品の物体検出", "電子ごみ検出", "バングラデシュ電子ごみ"),
        task="detection", audiences=("student", "teacher"), difficulty="intermediate",
        use_cases_ja=("画像の中の廃棄物品を囲んで種類を付ける", "12種類の物品を見分ける"),
        input_description_ja="緑色の布上で撮影された640×640の廃棄物品画像",
        output_description_ja="物体の位置を囲む枠と12種類のラベル",
        download_size_mb=71.7, audit_status="full_image_and_annotation_audit",
        audit_report="reports/bangladeshi-ewaste-full-audit.json",
        class_names_ja=(
            "電池ごみ", "ガラスごみ", "キーボード", "電球", "医療廃棄物", "金属ごみ",
            "携帯電話", "マウス", "生ごみ", "基板", "紙ごみ", "プラスチックごみ",
        ),
        license_info={
            "name": "CC BY 4.0",
            "url": "https://creativecommons.org/licenses/by/4.0/",
            "rights_review": "公式ページとアーカイブ内READMEの表記を確認。帰属表示とpolygon変換の明記が必要。",
        },
        source_info={
            "dataset_name": "Custom Bangladeshi E-Waste Image Dataset for Object Detection and Recognition",
            "provider": "Tanzila Afrin; Azizul Abedin Azmi",
            "url": "https://doi.org/10.17632/77383kmdnw.1",
            "release_repository": "https://github.com/708san/CV_data_artifacts",
            "release_tag": "bangladeshi-ewaste-v0.1.0",
        },
        file_urls={
            "artifact": "https://github.com/708san/CV_data_artifacts/releases/download/bangladeshi-ewaste-v0.1.0/bangladeshi_ewaste-v0.1.0.zip",
        },
        published=False,
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


_PREVIEW_SOURCES: dict[str, ReleaseSource] = {
    "fashion_mnist": ReleaseSource(
        id="fashion_mnist",
        case_id="fashion-mnist",
        tag="github-b2617bb6d3ffa2e429640350f613e3291e10b141",
        sha256="",
        archive_size=0,
        image_count=70_000,
        kind="classification",
        name_ja="Fashion-MNIST",
        rights_note="公式リポジトリのMIT表記を確認済み。教材公開・再配布の最終確認中。正式一覧には未掲載。",
        aliases_ja=("ファッションMNIST", "衣類MNIST"),
        task="classification",
        audiences=("teacher",),
        difficulty="introductory",
        use_cases_ja=("衣類画像を分類する", "画像分類の評価方法を練習する"),
        input_description_ja="28×28の白黒衣類画像",
        output_description_ja="衣類10クラスのラベル",
        download_size_mb=29.5,
        audit_status="metadata_and_idx_checked",
        audit_report="reports/fashion-mnist-github-b2617bb6.json",
        class_names_ja=(
            "Tシャツ・トップス", "ズボン", "プルオーバー", "ワンピース", "コート",
            "サンダル", "シャツ", "スニーカー", "バッグ", "アンクルブーツ",
        ),
        label_names_ja={
            "0": "Tシャツ・トップス", "1": "ズボン", "2": "プルオーバー", "3": "ワンピース",
            "4": "コート", "5": "サンダル", "6": "シャツ", "7": "スニーカー",
            "8": "バッグ", "9": "アンクルブーツ",
        },
        license_info={
            "name": "MIT License（公式リポジトリの表記）",
            "url": "https://github.com/zalandoresearch/fashion-mnist/blob/b2617bb6d3ffa2e429640350f613e3291e10b141/LICENSE",
            "rights_review": "公式表記は確認済み。元画像の教材公開・再配布について人による最終確認が必要。",
        },
        source_info={
            "dataset_name": "Fashion-MNIST",
            "provider": "Zalando Research",
            "url": "https://github.com/zalandoresearch/fashion-mnist/tree/b2617bb6d3ffa2e429640350f613e3291e10b141",
            "commit": "b2617bb6d3ffa2e429640350f613e3291e10b141",
            "format": "IDX gzip",
        },
        preview=True,
        file_urls={
            name: f"https://raw.githubusercontent.com/zalandoresearch/fashion-mnist/b2617bb6d3ffa2e429640350f613e3291e10b141/data/fashion/{name}"
            for name in (
                "train-images-idx3-ubyte.gz", "train-labels-idx1-ubyte.gz",
                "t10k-images-idx3-ubyte.gz", "t10k-labels-idx1-ubyte.gz",
            )
        },
        file_sha256={
            "train-images-idx3-ubyte.gz": "3aede38d61863908ad78613f6a32ed271626dd12800ba2636569512369268a84",
            "train-labels-idx1-ubyte.gz": "a04f17134ac03560a47e3764e11b92fc97de4d1bfaf8ba1a3aa29af54cc90845",
            "t10k-images-idx3-ubyte.gz": "346e55b948d973a97e58d2351dde16a484bd415d4595297633bb08f03db6a073",
            "t10k-labels-idx1-ubyte.gz": "67da17c76eaffca5446c3361aaab5c3cd6d1c2608764d35dfb1850b086bf8dd5",
        },
        file_sizes={
            "train-images-idx3-ubyte.gz": 26_421_880,
            "train-labels-idx1-ubyte.gz": 29_515,
            "t10k-images-idx3-ubyte.gz": 4_422_102,
            "t10k-labels-idx1-ubyte.gz": 5_148,
        },
    ),
}


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
    """画像と濃淡マスクを遅延読み込みするPyTorch Dataset互換クラス。"""

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
            image_array = np.asarray(image, dtype=np.float32) / 255.0
        with Image.open(record["mask_path"]) as mask:
            mask = mask.convert("L").resize(self._image_size[::-1], Image.Resampling.NEAREST)
            mask_array = np.asarray(mask, dtype=np.float32)[None, :, :] / 255.0
        image_tensor = self._torch.from_numpy(image_array).permute(2, 0, 1).contiguous()
        mask_tensor = self._torch.from_numpy(mask_array).contiguous()
        return image_tensor, mask_tensor


_TASKS: dict[str, dict[str, str]] = {
    "classification": {
        "name_ja": "画像分類",
        "description_ja": "画像全体を、決めた種類のどれかに分ける課題。",
    },
    "detection": {
        "name_ja": "物体検出",
        "description_ja": "画像の中の物体の位置と種類を調べる課題。",
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
    if len(entries) > MAX_FILES:
        raise DatasetError("ZIPのファイル数が上限を超えています。")
    total = 0
    seen: set[str] = set()
    root = src.case_id
    for entry in entries:
        name = entry.filename
        path = PurePosixPath(name)
        is_root_directory = name.rstrip("/") == root and name.endswith("/")
        if (not name or "\\" in name or "\x00" in name or path.is_absolute()
                or len(path.parts) < 2 and not is_root_directory or path.parts[0] != root
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
        if total > MAX_UNPACKED_BYTES:
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
    root = destination / src.case_id
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
    if src.kind == "segmentation":
        return _validate_segmentation_case(root, src)
    if src.kind == "detection":
        required = [root / x for x in ("manifest.json", "classes.json", "annotations.jsonl", "metadata.jsonl", "README.md")]
    else:
        required = [root / x for x in ("manifest.json", "labels.csv", "metadata.jsonl", "README.md")]
    if not all(p.is_file() for p in required):
        raise DatasetError("manifest.jsonなどの必須ファイルがありません。")
    manifest = json.loads((root / "manifest.json").read_text(encoding="utf-8"))
    version = src.tag if src.preview else "v" + src.tag.split("-v", 1)[1]
    if (manifest.get("case_id") != src.case_id or manifest.get("version") != version
            or manifest.get("image_count") != src.image_count):
        raise DatasetError("manifest.jsonの版または画像枚数が固定Releaseの情報と一致しません。")
    if src.kind == "detection":
        return _validate_detection_case(root, src, manifest)
    with (root / "labels.csv").open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        required_cols = {"image", "label", "split"} if src.kind == "classification" else {"image", "caption"}
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
            actual_metadata[name] = ({"label": item["label"], "split": item["split"]}
                                     if src.kind == "classification" else {"text": item["text"]})
    if actual_metadata != expected_metadata:
        raise DatasetError("metadata.jsonlとlabels.csvが一致しません。")
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
        if ("\\" in image or "\\" in mask or image_parts[:2] != ("images", split)
                or mask_parts[:2] != ("masks", split) or split not in {"train", "val", "test"}
                or len(image_parts) != 4 or len(mask_parts) != 4
                or any(part in {"", ".", ".."} for part in (*image_parts, *mask_parts))
                or cls not in class_to_id or image_parts[2] != cls or mask_parts[2] != cls
                or mask_parts[-1] != PurePosixPath(image_parts[-1]).stem + "_mask.png"
                or row.get("class_id") != str(class_to_id[cls])
                or PurePosixPath(image).suffix.lower() not in {".jpg", ".jpeg"}
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

    root = destination / src.case_id
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
    """既存の固定Releaseを取得する。CV_sample_dataへの書込みは一切行わない。"""
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
        _download(src.url, archive, max_bytes=MAX_ARCHIVE_BYTES)
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
