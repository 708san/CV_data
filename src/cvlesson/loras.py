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


@dataclass(frozen=True)
class LoraModel:
    """配布元から利用者が直接取得する学習済みLoRA。"""

    id: str
    name_ja: str
    repository: str
    filename: str
    revision: str
    sha256: str
    base_model: str
    base_revision: str
    trigger_words: tuple[str, ...]
    license_name: str
    license_url: str
    training_dataset: str
    training_dataset_url: str
    training_dataset_license: str
    source_url: str
    rights_note: str
    use_case_ja: str
    limitations_ja: str


_MODELS: dict[str, LoraModel] = {
    "fluent_emoji_3d": LoraModel(
        id="fluent_emoji_3d",
        name_ja="丸みのある3Dアイコン・絵文字風",
        repository="klibaner/fluent-emoji-style-sdxl",
        filename="microsoft-fluent-emoji-sdxl.safetensors",
        revision="7ff36ef02e53e75a4ca3bd5bd326de3f30a41fba",
        sha256="43689df28723d9ce4f9dbdd745cd95d6d5fa35f1ed5b774eb71e03be93da8c09",
        base_model="stabilityai/stable-diffusion-xl-base-1.0",
        base_revision="cae78213d9dd74e36e0eb4c99ca83b4aeb94fb1a",
        trigger_words=("msemj style",),
        license_name="MIT",
        license_url="https://huggingface.co/klibaner/fluent-emoji-style-sdxl",
        training_dataset="Norod78/microsoft-fluentui-emoji-512-whitebg",
        training_dataset_url="https://huggingface.co/datasets/Norod78/microsoft-fluentui-emoji-512-whitebg",
        training_dataset_license="MIT（配布元表示）",
        source_url="https://github.com/microsoft/fluentui-emoji",
        rights_note=(
            "モデルカードと学習データカードはMITと表示。Microsoftの元絵を含むため、"
            "商標・第三者権利と生成物の利用条件は利用者が確認する。Microsoft公式モデルではない。"
        ),
        use_case_ja="課題ポスターや発表資料に使う、単体のアイコン・挿絵を作る。",
        limitations_ja=(
            "単体で中央に置く絵向け。画像内の文字は正確に描けない。"
            "Microsoftの公式モデルではなく、Microsoftとの提携・承認もありません。"
        ),
    ),
    "watercolor_sdxl": LoraModel(
        id="watercolor_sdxl",
        name_ja="写真・風景の水彩イラスト風",
        repository="ostris/watercolor_style_lora_sdxl",
        filename="watercolor_v1_sdxl.safetensors",
        revision="0b65af0ac64347c8a35b82b4695ef5eadeffd5d7",
        sha256="d375ae7e68e1377305c168b0550a0fda33925421f570f87870fb19278786e9ac",
        base_model="stabilityai/stable-diffusion-xl-base-1.0",
        base_revision="cae78213d9dd74e36e0eb4c99ca83b4aeb94fb1a",
        trigger_words=(),
        license_name="Apache-2.0",
        license_url="https://huggingface.co/ostris/watercolor_style_lora_sdxl",
        training_dataset="モデルカードに記載なし",
        training_dataset_url="",
        training_dataset_license="未記載",
        source_url="https://huggingface.co/ostris/watercolor_style_lora_sdxl",
        rights_note=(
            "LoRA重みは配布元がApache-2.0と表示。SDXL 1.0用でトリガー語不要。"
            "学習元データの出典・ライセンスはモデルカードに記載がなく、別途確認できていない。"
        ),
        use_case_ja="許可を得た写真を水彩風にし、地域課題の説明画像やポスターの背景・挿絵にする。",
        limitations_ja=(
            "文字は正確に描けない。学習元データの来歴は未記載。"
            "出力の著作権・肖像権・第三者権利は利用者が確認する。"
        ),
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


def list_models() -> list[dict[str, Any]]:
    """利用者が配布元から取得する、権利情報を記録した学習済みLoRA一覧。"""
    return [model_info(item.id) for item in _MODELS.values()]


def model_info(model_id: str) -> dict[str, Any]:
    """学習済みLoRAの出典、固定版、権利、利用上の注意を返す。"""
    item = _model(model_id)
    return {
        "id": item.id,
        "name_ja": item.name_ja,
        "repository": item.repository,
        "filename": item.filename,
        "revision": item.revision,
        "sha256": item.sha256,
        "base_model": item.base_model,
        "base_revision": item.base_revision,
        "trigger_words": list(item.trigger_words),
        "license": {"name": item.license_name, "url": item.license_url},
        "training_dataset": {
            "repository": item.training_dataset,
            "url": item.training_dataset_url,
            "license": item.training_dataset_license,
        },
        "source_url": item.source_url,
        "rights_status": (
            "配布元ライセンス表記あり（学習元非記載）"
            if item.training_dataset == "モデルカードに記載なし"
            else "配布元がMIT表記（第三者権利・生成物は利用者確認）"
        ),
        "rights_note": item.rights_note,
        "use_case_ja": item.use_case_ja,
        "limitations_ja": item.limitations_ja,
        "weights_included": False,
        "download": "generation.load()を明示したときだけ配布元から取得",
        "base_model_license": "CreativeML Open RAIL++-M（別途適用）",
    }


def get_model(model_id: str) -> LoraModel:
    """学習済みLoRAの固定取得情報を返す。重みの取得は行わない。"""
    return _model(model_id)


def _model(model_id: str) -> LoraModel:
    if not isinstance(model_id, str):
        raise LoraError("学習済みLoRA IDは文字列で指定してください。")
    try:
        return _MODELS[model_id]
    except KeyError as exc:
        raise LoraError(f"未登録の学習済みLoRAです: {model_id}") from exc


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


__all__ = [
    "LoraError", "LoraMaterial", "LoraModel", "get", "info", "list_available",
    "get_model", "list_models", "list_preview", "model_info",
]
