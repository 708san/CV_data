"""固定Releaseを読み取り専用で検査する。通常のテストではダウンロードしない。"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from . import datasets


def inspect_release(
    dataset_id: str,
    *,
    cache_dir: str | Path | None = None,
    allow_download: bool = True,
    check_images: bool = False,
    check_similar: bool = False,
) -> dict[str, Any]:
    """固定Releaseの整合性を検査する。画像・ラベルには変更を加えない。"""
    data = datasets.get(dataset_id, cache_dir=cache_dir, allow_download=allow_download)
    source = datasets._source(dataset_id)
    with data.labels_csv.open(encoding="utf-8-sig", newline="") as stream:
        rows = list(csv.DictReader(stream))

    image_paths = [data.root / row["image"] for row in rows]
    result: dict[str, Any] = {
        "dataset_id": dataset_id,
        "name_ja": source.name_ja,
        "kind": data.kind,
        "release_tag": data.version,
        "source_url": data.source_url,
        "archive_sha256": source.sha256,
        "expected_images": source.image_count,
        "raw_image_count": len(rows),
        "usable_image_count": len(rows),
        "observed_images": len(rows),
        "metadata_consistency": "passed",
        "image_decode": "not_checked",
        "image_decode_checked": 0,
        "image_decode_failed": 0,
        "image_decode_failures": [],
        "duplicate_candidate_count": 0,
        "label_mismatch_count": 0,
        "similar_image_check": "not_performed",
        "similar_image_candidate_count": 0,
        "similar_image_method": "not_performed",
        "similar_image_pairs": [],
        "excluded_data": [],
        "split_method": (
            "official_test_preserved; deterministic_stratified_train_val"
            if data.kind == "classification" else "not_applicable_lora_training_material"
        ),
        "split_seed": 42 if data.kind == "classification" else None,
        "leakage_risks": [
            (
                "group_idが元データにないため、同一個体・撮影系列の分離は保証していません。"
                if data.kind == "classification" else "LoRA素材のため分類用splitは作成していません。"
            ),
            (
                "類似画像候補を平均ハッシュで抽出しました。候補は目視確認が必要です。"
                if check_similar else "類似画像の自動判定は実施していません。"
            ),
        ],
        "validated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "status": "passed",
        "rights_note": data.rights_note,
        "rights_review": "not_performed",
    }
    if data.kind == "classification":
        result["classes"] = dict(sorted(Counter(row["label"] for row in rows).items()))
        result["source_splits"] = dict(sorted(Counter(row["split"] for row in rows).items()))
        effective_splits = datasets._effective_splits(rows, val_fraction=0.1, seed=42)
        result["splits"] = dict(sorted(Counter(effective_splits).items()))
    else:
        result["captions_present"] = sum(bool(row["caption"].strip()) for row in rows)

    if check_images:
        try:
            from PIL import Image
        except ImportError as exc:
            raise datasets.DatasetError(
                "画像検査にはPillowが必要です。"
                "python -m pip install --pre cv-data-lesson を実行してください。"
            ) from exc
        bad: list[str] = []
        hashes: dict[str, list[dict[str, str]]] = {}
        perceptual: list[tuple[int, str, dict[str, str]]] = []
        for row, path in zip(rows, image_paths):
            try:
                with Image.open(path) as image:
                    image.verify()
                with Image.open(path) as image:
                    image.load()
                    if image.width <= 0 or image.height <= 0:
                        raise ValueError("画像の大きさが不正です")
                    average_hash = _average_hash(image) if check_similar else None
                digest = hashlib.sha256(path.read_bytes()).hexdigest()
                hashes.setdefault(digest, []).append(row)
                if average_hash is not None:
                    perceptual.append((average_hash, digest, row))
            except (OSError, ValueError, SyntaxError, Image.DecompressionBombError):
                if len(bad) < 10:
                    bad.append(path.relative_to(data.root).as_posix())
                result["image_decode_failed"] += 1
            result["image_decode_checked"] += 1
        result["image_decode"] = "failed" if result["image_decode_failed"] else "passed"
        result["image_decode_failures"] = bad
        result["usable_image_count"] = len(rows) - result["image_decode_failed"]
        result["excluded_data"] = [
            {"image": image, "reason": "image_decode_failed"}
            for image in bad
        ]
        duplicate_groups = [items for items in hashes.values() if len(items) > 1]
        result["duplicate_candidate_count"] = sum(len(items) - 1 for items in duplicate_groups)
        if data.kind == "classification":
            mismatches = [items for items in duplicate_groups if len({item["label"] for item in items}) > 1]
            result["label_mismatch_count"] = sum(len(items) for items in mismatches)
            result["duplicate_groups"] = [
                {"sha256": digest, "images": [item["image"] for item in items]}
                for digest, items in hashes.items() if len(items) > 1
            ][:20]
        if check_similar:
            candidates: list[dict[str, Any]] = []
            for index, (left_hash, left_digest, left_row) in enumerate(perceptual):
                for right_hash, right_digest, right_row in perceptual[index + 1:]:
                    if left_digest == right_digest:
                        continue
                    distance = (left_hash ^ right_hash).bit_count()
                    if distance <= 4:
                        candidates.append({
                            "hamming_distance": distance,
                            "images": [left_row["image"], right_row["image"]],
                        })
            result["similar_image_check"] = "performed"
            result["similar_image_method"] = "8x8 average hash; hamming_distance <= 4; review_only"
            result["similar_image_candidate_count"] = len(candidates)
            result["similar_image_pairs"] = candidates[:20]
        if result["image_decode_failed"]:
            result["status"] = "failed"
    return result


def _average_hash(image: Any) -> int:
    """Pillow画像からレビュー用の軽量な平均ハッシュを作る。"""
    gray = image.convert("L").resize((8, 8))
    if hasattr(gray, "get_flattened_data"):
        values = list(gray.get_flattened_data())
    else:
        values = list(gray.getdata())
    average = sum(values) / len(values)
    result = 0
    for value in values:
        result = (result << 1) | int(value >= average)
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="固定Releaseの実ファイルとラベルを検査します。")
    parser.add_argument("dataset_id", choices=("festival_icons", "tomato_leaves"))
    parser.add_argument("--cache-dir", type=Path)
    parser.add_argument("--no-download", action="store_true")
    parser.add_argument("--check-images", action="store_true")
    parser.add_argument("--check-similar", action="store_true")
    parser.add_argument("--report", type=Path)
    args = parser.parse_args(argv)
    try:
        report = inspect_release(
            args.dataset_id, cache_dir=args.cache_dir,
            allow_download=not args.no_download, check_images=args.check_images,
            check_similar=args.check_similar,
        )
    except (datasets.DatasetError, OSError, ValueError, ImportError) as exc:
        report = {
            "dataset_id": args.dataset_id, "status": "failed",
            "error": str(exc), "rights_review": "not_performed",
        }
    content = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.report is not None:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(content, encoding="utf-8")
    sys.stdout.write(content)
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
