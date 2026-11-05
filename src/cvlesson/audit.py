"""固定Releaseを読み取り専用で検査する。通常のテストではダウンロードしない。"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

from . import datasets


def inspect_release(
    dataset_id: str,
    *,
    cache_dir: str | Path | None = None,
    allow_download: bool = True,
    check_images: bool = False,
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
        "observed_images": len(rows),
        "metadata_consistency": "passed",
        "image_decode": "not_checked",
        "image_decode_checked": 0,
        "image_decode_failed": 0,
        "image_decode_failures": [],
        "status": "passed",
        "rights_note": data.rights_note,
        "rights_review": "not_performed",
    }
    if data.kind == "classification":
        result["classes"] = dict(sorted(Counter(row["label"] for row in rows).items()))
        result["splits"] = dict(sorted(Counter(row["split"] for row in rows).items()))
    else:
        result["captions_present"] = sum(bool(row["caption"].strip()) for row in rows)

    if check_images:
        try:
            from PIL import Image
        except ImportError as exc:
            raise datasets.DatasetError(
                "画像検査にはPillowが必要です。python -m pip install Pillow を実行してください。"
            ) from exc
        bad: list[str] = []
        for path in image_paths:
            try:
                with Image.open(path) as image:
                    image.verify()
                with Image.open(path) as image:
                    image.load()
                    if image.width <= 0 or image.height <= 0:
                        raise ValueError("画像の大きさが不正です")
            except (OSError, ValueError, SyntaxError, Image.DecompressionBombError):
                if len(bad) < 10:
                    bad.append(path.relative_to(data.root).as_posix())
                result["image_decode_failed"] += 1
            result["image_decode_checked"] += 1
        result["image_decode"] = "failed" if result["image_decode_failed"] else "passed"
        result["image_decode_failures"] = bad
        if result["image_decode_failed"]:
            result["status"] = "failed"
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="固定Releaseの実ファイルとラベルを検査します。")
    parser.add_argument("dataset_id", choices=("festival_icons", "tomato_leaves"))
    parser.add_argument("--cache-dir", type=Path)
    parser.add_argument("--no-download", action="store_true")
    parser.add_argument("--check-images", action="store_true")
    parser.add_argument("--report", type=Path)
    args = parser.parse_args(argv)
    try:
        report = inspect_release(
            args.dataset_id, cache_dir=args.cache_dir,
            allow_download=not args.no_download, check_images=args.check_images,
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
