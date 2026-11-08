"""固定版の学習済みLoRA重みを配布元から取得する。

画像・キャプション素材は ``loras``、学習済み重みはこのモジュールで管理する。
取得は ``get`` の明示呼び出し時だけ行い、重みはcheckout外のcacheに保存する。
"""
from __future__ import annotations

import hashlib
import os
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from . import datasets


class WeightError(RuntimeError):
    """LoRA重みの取得または検証に失敗した場合。"""


@dataclass(frozen=True)
class LoraWeight:
    id: str
    name_ja: str
    version: str
    repository: str
    filename: str
    url: str
    model_card_url: str
    size_bytes: int
    sha256: str
    license_name: str
    license_url: str
    base_model: str
    base_model_license: str
    base_model_license_url: str
    trigger_words: tuple[str, ...]
    use_case_ja: str
    system_requirement_ja: str
    requires_license_acceptance: bool = False


_WEIGHTS: dict[str, LoraWeight] = {
    "tcd_sd15": LoraWeight(
        id="tcd_sd15",
        name_ja="少ないステップで生成するTCD LoRA（SD 1.5）",
        version="449a99f6bbded2bdbbc66386b2a4fbf8db8d3807",
        repository="h1t/TCD-SD15-LoRA",
        filename="pytorch_lora_weights.safetensors",
        url=(
            "https://huggingface.co/h1t/TCD-SD15-LoRA/resolve/"
            "449a99f6bbded2bdbbc66386b2a4fbf8db8d3807/"
            "pytorch_lora_weights.safetensors"
        ),
        model_card_url=(
            "https://huggingface.co/h1t/TCD-SD15-LoRA/blob/"
            "449a99f6bbded2bdbbc66386b2a4fbf8db8d3807/README.md"
        ),
        size_bytes=134_621_556,
        sha256="eaecb24a1cda4411eab67275b1d991071216ac93693e8fa0c9226c9df0386232",
        license_name="MIT（LoRA重み）",
        license_url=(
            "https://huggingface.co/h1t/TCD-SD15-LoRA/blob/"
            "449a99f6bbded2bdbbc66386b2a4fbf8db8d3807/README.md"
        ),
        base_model="runwayml/stable-diffusion-v1-5",
        base_model_license="CreativeML Open RAIL-M（基盤モデル側の条件）",
        base_model_license_url="https://github.com/CompVis/stable-diffusion/blob/main/LICENSE",
        trigger_words=(),
        use_case_ja="生成ステップ数と画像の違いを比べる課題",
        system_requirement_ja=(
            "画像生成には別途Stable Diffusion 1.5の基盤モデルとDiffusersが必要です。"
            "基盤モデルの利用条件を確認してください。GPUを推奨します。"
        ),
    ),
    "watercolor_sd15": LoraWeight(
        id="watercolor_sd15",
        name_ja="水彩表現LoRA（SD 1.5）",
        version="cec30d1ee75123fa7662a4f058899fa0dc3adba0",
        repository="fladdict/watercolor",
        filename="fladdict-watercolor-sd-1-5.safetensors",
        url=(
            "https://huggingface.co/fladdict/watercolor/resolve/"
            "cec30d1ee75123fa7662a4f058899fa0dc3adba0/"
            "fladdict-watercolor-sd-1-5.safetensors"
        ),
        model_card_url=(
            "https://huggingface.co/fladdict/watercolor/blob/"
            "cec30d1ee75123fa7662a4f058899fa0dc3adba0/README.md"
        ),
        size_bytes=302_107_990,
        sha256="7a4575799077438d47435e841d5ad4560e0f83d0ade5ce7e15a6125c7b443d99",
        license_name="CreativeML OpenRAIL-M",
        license_url="https://huggingface.co/spaces/CompVis/stable-diffusion-license",
        base_model="runwayml/stable-diffusion-v1-5",
        base_model_license="CreativeML Open RAIL-M（基盤モデル側の条件）",
        base_model_license_url="https://github.com/CompVis/stable-diffusion/blob/main/LICENSE",
        trigger_words=("watercolor painting", "impressionism, watercolor painting"),
        use_case_ja="同じ題材で水彩表現の有無を比べる課題",
        system_requirement_ja=(
            "画像生成には別途Stable Diffusion 1.5の基盤モデルとDiffusersが必要です。"
            "重みと基盤モデルのOpenRAIL-M条件を確認してください。GPUを推奨します。"
        ),
        requires_license_acceptance=True,
    ),
}


def _weight(weight_id: str) -> LoraWeight:
    if not isinstance(weight_id, str):
        raise WeightError("LoRA重みIDは文字列で指定してください。")
    try:
        return _WEIGHTS[weight_id]
    except KeyError as exc:
        raise WeightError(f"未対応のLoRA重みです（完全一致のみ）: {weight_id}") from exc


def _as_dict(item: LoraWeight) -> dict[str, Any]:
    return {
        "id": item.id,
        "name_ja": item.name_ja,
        "version": item.version,
        "repository": item.repository,
        "filename": item.filename,
        "size_bytes": item.size_bytes,
        "download_size_mb": round(item.size_bytes / 1_000_000, 1),
        "sha256": item.sha256,
        "license": {"name": item.license_name, "url": item.license_url},
        "base_model": item.base_model,
        "base_model_license": {
            "name": item.base_model_license,
            "url": item.base_model_license_url,
        },
        "trigger_words": list(item.trigger_words),
        "use_case_ja": item.use_case_ja,
        "system_requirement_ja": item.system_requirement_ja,
        "source_url": item.url,
        "model_card_url": item.model_card_url,
        "publication_status": "student_enabled",
        "requires_license_acceptance": item.requires_license_acceptance,
    }


def list_available() -> list[dict[str, Any]]:
    """取得条件・固定版を確認した学習済みLoRA重みを一覧表示する。通信しない。"""
    return [_as_dict(item) for item in _WEIGHTS.values()]


def info(weight_id: str) -> dict[str, Any]:
    """重みの固定版、取得サイズ、SHA-256、利用条件を返す。通信しない。"""
    return _as_dict(_weight(weight_id))


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _mkdir_checked(path: Path) -> None:
    """作成または再利用するcache pathの各要素がsymlinkでないことを確認する。"""
    absolute = path.expanduser().absolute()
    current = Path(absolute.anchor)
    for part in absolute.parts[1:]:
        current = current / part
        if current.is_symlink():
            raise WeightError(f"LoRA cache内のsymlinkは使用できません: {current}")
        if current.exists() and not current.is_dir():
            raise WeightError(f"LoRA cacheの保存先がディレクトリではありません: {current}")
    absolute.mkdir(parents=True, exist_ok=True)


def _download(item: LoraWeight, destination: Path) -> None:
    request = urllib.request.Request(item.url, headers={"User-Agent": "cvlesson/0.0.1"})
    temporary = destination.with_name(destination.name + ".part")
    temporary.unlink(missing_ok=True)
    try:
        total = 0
        with urllib.request.urlopen(request, timeout=45) as response, temporary.open("wb") as stream:
            while chunk := response.read(1024 * 1024):
                total += len(chunk)
                if total > item.size_bytes:
                    raise WeightError("登録サイズを超えたためダウンロードを停止しました。")
                stream.write(chunk)
        if total != item.size_bytes:
            raise WeightError(f"LoRA重みのサイズが一致しません: {total} bytes")
        if _sha256(temporary) != item.sha256:
            raise WeightError("LoRA重みのSHA-256が一致しません。ファイルは保存しません。")
        os.replace(temporary, destination)
    except WeightError:
        temporary.unlink(missing_ok=True)
        raise
    except (OSError, urllib.error.URLError, TimeoutError) as exc:
        temporary.unlink(missing_ok=True)
        raise WeightError(f"固定版LoRA重みを取得できませんでした: {exc}") from exc


def get(weight_id: str, *, cache_dir: str | Path | None = None,
        allow_download: bool = True, accept_license: bool = False) -> Path:
    """固定版重みを取得して検証し、cache内のファイルパスを返す。

    この関数を呼ぶと最大サイズ分のネットワーク通信が発生する。
    重みはPyPIやGitに含めず、既定ではcheckout外のcacheへ保存する。
    """
    item = _weight(weight_id)
    if item.requires_license_acceptance and not accept_license:
        raise WeightError(
            "このLoRA重みはOpenRAIL-Mです。利用条件を確認した後、"
            "accept_license=Trueを指定してください。"
        )
    root = datasets._cache_dir(cache_dir) / "weights" / item.id / item.version
    _mkdir_checked(root)
    destination = root / item.filename
    if destination.is_symlink():
        raise WeightError(f"LoRA cacheのファイルがsymlinkです: {destination}")
    if destination.exists():
        if destination.stat().st_size == item.size_bytes and _sha256(destination) == item.sha256:
            return destination
        raise WeightError("既存のLoRA cacheが登録内容と一致しません。別のcache_dirを指定してください。")
    if not allow_download:
        raise WeightError("LoRA重みがcacheにありません。allow_download=Trueで取得してください。")
    _download(item, destination)
    return destination


__all__ = ["WeightError", "get", "info", "list_available"]
