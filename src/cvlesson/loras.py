"""LoRA素材とLoRA設定の管理。

モデル重みを再配布せず、画像・キャプション・互換性・利用条件を管理する。
権利確認中の素材は正式一覧に含めない。
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from . import datasets


class LoraError(RuntimeError):
    """LoRA素材の取得・管理に失敗した場合。"""


@dataclass(frozen=True)
class LoraMaterial:
    id: str
    name_ja: str
    dataset_id: str
    base_model: str
    trigger_words: tuple[str, ...]
    rights_status: str
    rights_note: str
    source_info: dict[str, Any]
    license_info: dict[str, Any]
    preview: bool = False

    def get_data(self, *, cache_dir: str | Path | None = None,
                 allow_download: bool = True, allow_preview: bool = False) -> datasets.DatasetBundle:
        """画像・キャプション素材を取得する。重みは取得・配布しない。"""
        if self.preview and not allow_preview:
            raise LoraError("このLoRA素材はプレビューです。権利確認中のため明示指定が必要です。")
        return datasets.get(
            self.dataset_id,
            cache_dir=cache_dir,
            allow_download=allow_download,
            allow_preview=allow_preview or not self.preview,
        )


_MATERIALS: dict[str, LoraMaterial] = {}
_PREVIEW_MATERIALS: dict[str, LoraMaterial] = {
    "festival_icon_style": LoraMaterial(
        id="festival_icon_style",
        name_ja="文化祭案内アイコンのLoRA素材",
        dataset_id="festival_icons",
        base_model="未確定（重みは提供しない）",
        trigger_words=("universal_icon_style",),
        rights_status="under_review",
        rights_note="GitHub公開許可は確認済み。改変・商用利用・再配布は未確認。",
        source_info={
            "release_tag": "festival-v1.0.0",
            "repository": "https://github.com/708san/CV_sample_data",
        },
        license_info={
            "name": "標準ライセンス未設定",
            "redistribution": "未確認",
        },
        preview=True,
    ),
}


def list_available(*, audience: str = "student") -> list[dict[str, Any]]:
    """承認済みのLoRA素材を一覧表示する。現在は空。"""
    if audience not in {"student", "teacher"}:
        raise ValueError("audienceはstudentまたはteacherです。")
    return [
        {"id": item.id, "name_ja": item.name_ja, "base_model": item.base_model,
         "trigger_words": list(item.trigger_words), "rights_status": item.rights_status}
        for item in _MATERIALS.values()
    ]


def list_preview() -> list[dict[str, Any]]:
    """権利確認中の教師向けLoRA素材を一覧表示する。"""
    return [
        {"id": item.id, "name_ja": item.name_ja, "dataset_id": item.dataset_id,
         "rights_status": item.rights_status, "rights_note": item.rights_note}
        for item in _PREVIEW_MATERIALS.values()
    ]


def _material(material_id: str) -> LoraMaterial:
    if not isinstance(material_id, str):
        raise LoraError("LoRA素材IDは文字列で指定してください。")
    if material_id in _MATERIALS:
        return _MATERIALS[material_id]
    if material_id in _PREVIEW_MATERIALS:
        return _PREVIEW_MATERIALS[material_id]
    matches = [
        item for item in (*_MATERIALS.values(), *_PREVIEW_MATERIALS.values())
        if material_id == item.name_ja
    ]
    if len(matches) == 1:
        return matches[0]
    raise LoraError(f"未対応のLoRA素材です（完全一致のみ）: {material_id}")


def info(material_id: str) -> dict[str, Any]:
    item = _material(material_id)
    return {
        "id": item.id,
        "name_ja": item.name_ja,
        "dataset_id": item.dataset_id,
        "base_model": item.base_model,
        "trigger_words": list(item.trigger_words),
        "rights_status": item.rights_status,
        "rights_note": item.rights_note,
        "source_info": dict(item.source_info),
        "license_info": dict(item.license_info),
        "publication_status": "teacher_preview_only" if item.preview else "student_enabled",
    }


def get(material_id: str, *, cache_dir: str | Path | None = None,
        allow_download: bool = True, allow_preview: bool = False) -> LoraMaterial:
    """LoRA素材の管理情報を返す。画像取得は返却値のget_data()で明示する。"""
    item = _material(material_id)
    if item.preview and not allow_preview:
        raise LoraError("権利確認中のため、allow_preview=Trueが必要です。")
    return item


__all__ = ["LoraError", "LoraMaterial", "get", "info", "list_available", "list_preview"]
