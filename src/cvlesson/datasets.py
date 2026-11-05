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
    class_names_ja: tuple[str, ...] = ()
    label_names_ja: dict[str, str] | None = None
    license_info: dict[str, Any] | None = None
    source_info: dict[str, Any] | None = None
    preview: bool = False
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
    def labels_csv(self) -> Path:
        return self.root / "labels.csv"

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
        """分類データを共通列のDataFrameに変換する。

        元Releaseに検証用分割がない場合、公式testを保持したまま、trainだけを
        クラス比率を保つ決定的な方法でtrain/valへ分ける。元画像やCSVは変更しない。
        """
        try:
            import pandas as pd
        except ImportError as exc:
            raise DatasetError("DataFrame変換にはpandasが必要です。pip install pandas を実行してください。") from exc
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

    @property
    def splits(self) -> dict[str, int]:
        """標準化後のtrain/val/test件数。"""
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
        if split is not None:
            if split not in {"train", "val", "test"}:
                raise ValueError("splitはtrain、val、testのいずれかです。")
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
            axis.set_title(record.get("label_ja", record.get("caption", "")))
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
        if self.kind != "classification":
            raise DatasetError("PyTorch変換は現在、画像分類データだけに対応しています。")
        if split not in {"train", "val", "test"}:
            raise ValueError("splitはtrain、val、testのいずれかです。")
        if len(image_size) != 2 or any(not isinstance(x, int) or x <= 0 for x in image_size):
            raise ValueError("image_sizeは正の整数2つのtupleで指定してください。")
        try:
            import torch
        except ImportError as exc:
            raise DatasetError("PyTorch変換にはtorchが必要です。") from exc
        records = [
            record for record in self._classification_records(val_fraction=val_fraction, seed=seed)
            if record["split"] == split
        ]
        if not records:
            raise DatasetError(f"split={split}に画像がありません。")
        return _TorchClassificationDataset(records, image_size=image_size, torch_module=torch)

    def quality_summary(self, *, seed: int = 42, val_fraction: float = 0.1) -> dict[str, Any]:
        """標準化後の件数と分割方法を機械可読な辞書で返す。"""
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
    sources = list(_SOURCES.values())
    if include_preview:
        sources.extend(_PREVIEW_SOURCES.values())
    return tuple(sources)


def _source_status(src: ReleaseSource) -> str:
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


def _validate_case(root: Path, src: ReleaseSource) -> dict[str, Any]:
    required = [root / x for x in ("manifest.json", "labels.csv", "metadata.jsonl", "README.md")]
    if not all(p.is_file() for p in required):
        raise DatasetError("manifest.jsonなどの必須ファイルがありません。")
    manifest = json.loads((root / "manifest.json").read_text(encoding="utf-8"))
    version = src.tag if src.preview else "v" + src.tag.split("-v", 1)[1]
    if (manifest.get("case_id") != src.case_id or manifest.get("version") != version
            or manifest.get("image_count") != src.image_count):
        raise DatasetError("manifest.jsonの版または画像枚数が固定Releaseの情報と一致しません。")
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
