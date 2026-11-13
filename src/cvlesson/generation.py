"""SDXLの画像生成・画像から画像への変換を簡単に使うAPI。

モデルはload()を呼んだときだけ取得し、学習済みLoRAは固定revisionとSHA-256を検証する。
"""
from __future__ import annotations

import hashlib
import math
from pathlib import Path
from typing import Any

from . import loras


class GenerationError(RuntimeError):
    """画像生成の準備・実行に失敗した場合。"""


def available_devices() -> dict[str, bool]:
    """利用可能なCPU・CUDA GPU・Apple MPSを確認する。"""
    try:
        import torch
    except ImportError as exc:
        raise GenerationError("画像生成にはtorchが必要です。pip install 'cv-data-lesson[diffusion]'を実行してください。") from exc
    mps = getattr(getattr(torch.backends, "mps", None), "is_available", lambda: False)()
    return {"cpu": True, "cuda": bool(torch.cuda.is_available()), "mps": bool(mps)}


class ImageGenerator:
    """読み込み済み画像生成モデル。"""

    def __init__(self, pipeline: Any, task: str, device: str, torch_module: Any,
                 trigger_words: tuple[str, ...] = ()) -> None:
        self._pipeline = pipeline
        self.task = task
        self.device = device
        self._torch = torch_module
        self.trigger_words = trigger_words

    def generate(
        self,
        prompt: str,
        *,
        image: Any = None,
        strength: float = 0.65,
        negative_prompt: str | None = None,
        num_inference_steps: int = 25,
        guidance_scale: float = 7.0,
        seed: int | None = None,
        width: int | None = None,
        height: int | None = None,
        use_trigger: bool = True,
    ) -> Any:
        """文章から画像を作るか、元画像を文章に沿って描き変える。

        image-to-imageのstrengthは0に近いほど元画像を保ち、1に近いほど大きく変える。
        戻り値はPillowのImage。画像生成には正確な文字描画は期待できない。
        """
        if not isinstance(prompt, str) or not prompt.strip():
            raise ValueError("promptには空でない説明文を指定してください。")
        _validate_generation_settings(
            strength=strength,
            negative_prompt=negative_prompt,
            num_inference_steps=num_inference_steps,
            guidance_scale=guidance_scale,
            seed=seed,
            width=width,
            height=height,
            use_trigger=use_trigger,
        )
        if self.task == "image-to-image":
            if image is None:
                raise ValueError("image-to-imageでは変換元のimageが必要です。")
            image = _open_rgb_image(image)
        elif image is not None:
            raise ValueError("imageを使う場合はtask='image-to-image'でモデルを読み込んでください。")

        full_prompt = prompt.strip()
        if use_trigger:
            for trigger in self.trigger_words:
                if trigger.casefold() not in full_prompt.casefold():
                    full_prompt = f"{trigger}, {full_prompt}"

        kwargs: dict[str, Any] = {
            "prompt": full_prompt,
            "num_inference_steps": num_inference_steps,
            "guidance_scale": guidance_scale,
        }
        if self.task == "image-to-image":
            kwargs.update(image=image, strength=strength)
        if negative_prompt is not None:
            kwargs["negative_prompt"] = negative_prompt
        if width is not None:
            kwargs["width"] = width
        if height is not None:
            kwargs["height"] = height
        if seed is not None:
            kwargs["generator"] = self._torch.Generator(device=self.device).manual_seed(seed)
        result = self._pipeline(**kwargs)
        return result.images[0]


def load(
    *,
    task: str = "text-to-image",
    lora: str | None = "fluent_emoji_3d",
    base_model: str | None = None,
    base_revision: str | None = None,
    device: str = "cpu",
    cache_dir: str | Path | None = None,
    local_files_only: bool = False,
) -> ImageGenerator:
    """固定版SDXLと任意の登録済みLoRAを読み込む。

    GPUは自動選択しない。GPUを使う場合は利用可能か確認したうえでdevice="cuda"を明示する。
    モデルの重みはcheckoutやPyPIに含めず、Hugging Faceのキャッシュへ取得する。
    """
    if task not in {"text-to-image", "image-to-image"}:
        raise ValueError("taskは'text-to-image'または'image-to-image'です。")
    if device not in {"cpu", "cuda", "mps"}:
        raise ValueError("deviceは'cpu'、'cuda'、'mps'から選んでください。GPUは自動選択しません。")
    try:
        import torch
        from diffusers import AutoPipelineForImage2Image, AutoPipelineForText2Image
    except ImportError as exc:
        raise GenerationError("画像生成にはdiffusion追加依存が必要です。pip install 'cv-data-lesson[diffusion]'を実行してください。") from exc

    devices = {"cpu": True, "cuda": bool(torch.cuda.is_available())}
    devices["mps"] = bool(getattr(getattr(torch.backends, "mps", None), "is_available", lambda: False)())
    if not devices[device]:
        raise GenerationError(f"device={device!r}はこの環境で利用できません。available_devices()で確認してください。")

    adapter = loras.get_model(lora) if lora is not None else None
    if adapter is None:
        if not base_model:
            base_model = "stabilityai/stable-diffusion-xl-base-1.0"
            base_revision = base_revision or "cae78213d9dd74e36e0eb4c99ca83b4aeb94fb1a"
        elif not base_revision:
            raise ValueError("独自のbase_modelには固定したbase_revisionも指定してください。")
    else:
        if base_model is not None and base_model != adapter.base_model:
            raise ValueError("このLoRAはSDXL 1.0用です。別の基盤モデルではlora=Noneを指定してください。")
        if base_revision is not None and base_revision != adapter.base_revision:
            raise ValueError("登録LoRAとの互換性を保つため、基盤モデルrevisionは登録値から変更できません。")
        base_model = adapter.base_model
        base_revision = adapter.base_revision

    dtype = torch.float16 if device == "cuda" else torch.float32
    pipeline_class = AutoPipelineForImage2Image if task == "image-to-image" else AutoPipelineForText2Image
    load_kwargs: dict[str, Any] = {
        "revision": base_revision,
        "torch_dtype": dtype,
        "use_safetensors": True,
        "local_files_only": local_files_only,
    }
    if cache_dir is not None:
        load_kwargs["cache_dir"] = str(cache_dir)
    try:
        pipeline = pipeline_class.from_pretrained(base_model, **load_kwargs)
        pipeline.to(device)
        if adapter is not None:
            from huggingface_hub import hf_hub_download

            adapter_path = Path(hf_hub_download(
                repo_id=adapter.repository,
                filename=adapter.filename,
                revision=adapter.revision,
                cache_dir=str(cache_dir) if cache_dir is not None else None,
                local_files_only=local_files_only,
            ))
            actual_sha256 = _sha256(adapter_path)
            if actual_sha256 != adapter.sha256:
                raise GenerationError(
                    f"LoRAのSHA-256が一致しません。取得を中断しました: {actual_sha256}"
                )
            pipeline.load_lora_weights(str(adapter_path), adapter_name=adapter.id)
    except GenerationError:
        raise
    except Exception as exc:
        raise GenerationError(f"画像生成モデルを読み込めませんでした: {exc}") from exc
    triggers = adapter.trigger_words if adapter is not None else ()
    return ImageGenerator(pipeline, task, device, torch, triggers)


def _is_finite_number(value: int | float) -> bool:
    try:
        return math.isfinite(value)
    except OverflowError:
        return False


def _validate_generation_settings(
    *,
    strength: float,
    negative_prompt: str | None,
    num_inference_steps: int,
    guidance_scale: float,
    seed: int | None,
    width: int | None,
    height: int | None,
    use_trigger: bool,
) -> None:
    if (
        not isinstance(num_inference_steps, int)
        or isinstance(num_inference_steps, bool)
        or num_inference_steps < 1
    ):
        raise ValueError("num_inference_stepsは1以上の整数にしてください。")
    if (
        not isinstance(guidance_scale, (int, float))
        or isinstance(guidance_scale, bool)
        or not _is_finite_number(guidance_scale)
        or guidance_scale < 0
    ):
        raise ValueError("guidance_scaleは有限の0以上の数にしてください。")
    if (
        not isinstance(strength, (int, float))
        or isinstance(strength, bool)
        or not _is_finite_number(strength)
        or not 0 <= strength <= 1
    ):
        raise ValueError("strengthは有限の0から1の数にしてください。")
    if seed is not None and (not isinstance(seed, int) or isinstance(seed, bool)):
        raise ValueError("seedは整数またはNoneにしてください。")
    for name, value in (("width", width), ("height", height)):
        if value is not None and (
            not isinstance(value, int)
            or isinstance(value, bool)
            or value < 8
            or value % 8 != 0
        ):
            raise ValueError(f"{name}は8以上の8の倍数の整数にしてください。")
    if negative_prompt is not None and not isinstance(negative_prompt, str):
        raise ValueError("negative_promptは文字列またはNoneにしてください。")
    if not isinstance(use_trigger, bool):
        raise ValueError("use_triggerはTrueまたはFalseにしてください。")


def _open_rgb_image(image: Any) -> Any:
    try:
        from PIL import Image
    except ImportError as exc:
        raise GenerationError("画像の読み込みにはPillowが必要です。pip install 'cv-data-lesson[diffusion]'を実行してください。") from exc
    if isinstance(image, (str, Path)):
        with Image.open(image) as opened:
            return opened.convert("RGB")
    if isinstance(image, Image.Image):
        return image.convert("RGB")
    raise TypeError("imageには画像ファイルのパスまたはPillow Imageを指定してください。")


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for block in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


__all__ = ["GenerationError", "ImageGenerator", "available_devices", "load"]
