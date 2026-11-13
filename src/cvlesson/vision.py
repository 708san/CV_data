"""固定版Transformerモデルによる物体検出とプロンプト式領域分割。"""
from __future__ import annotations

from dataclasses import dataclass
import math
from pathlib import Path
import re
from typing import Any, Iterable


class VisionError(RuntimeError):
    """検出・領域分割モデルの準備や推論に関するエラー。"""


_DETECTOR_ID = "facebook/detr-resnet-50"
_DETECTOR_REVISION = "557a3b6fcdb1be415f074c22da2e16ab4f7e8265"
_SEGMENTER_ID = "facebook/sam-vit-base"
_SEGMENTER_REVISION = "70c1a07f894ebb5b307fd9eaaee97b9dfc16068f"


@dataclass(frozen=True)
class Detection:
    """検出した物体。boxは元画像上の(x_min, y_min, x_max, y_max)。"""

    label: str
    score: float
    box: tuple[float, float, float, float]
    source_size: tuple[int, int] | None = None  # (width, height)


@dataclass(frozen=True)
class Segmentation:
    """SAMが返す二値マスク。scoreは範囲保証のない予測品質値で、対象名は予測しない。"""

    mask: Any  # numpy.ndarray[bool]。型注釈でNumPyをimportしない。
    score: float
    prompt_type: str
    prompt: tuple[float, ...]


@dataclass(frozen=True)
class DetectedSegment:
    """検出結果と、その枠を使ってSAMが作ったマスクの組。"""

    detection: Detection
    segmentation: Segmentation


class ObjectDetector:
    """読み込み済みDETR。COCOの既定カテゴリだけを検出する。"""

    def __init__(self, processor: Any, model: Any, torch: Any, device: str) -> None:
        self._processor = processor
        self._model = model
        self._torch = torch
        self.device = device

    def predict(self, image: Any, *, threshold: float = 0.5) -> list[Detection]:
        """パスまたはPillow ImageのCOCOカテゴリを検出し、元画像座標の枠を返す。"""
        if not 0 <= threshold <= 1:
            raise ValueError("thresholdは0から1の範囲で指定してください。")
        rgb = _open_image(image)
        width, height = rgb.size
        inputs = self._processor(images=rgb, return_tensors="pt")
        inputs = _to_device(inputs, self.device)
        with self._torch.no_grad():
            outputs = self._model(**inputs)
        result = self._processor.post_process_object_detection(
            outputs, threshold=threshold, target_sizes=[(height, width)]
        )[0]
        labels = self._model.config.id2label
        detections = []
        for box, score, label_id in zip(result["boxes"], result["scores"], result["labels"]):
            coords = _clip_detection_box(_as_list(box), width, height)
            if coords is None:
                continue
            detections.append(
                Detection(
                    label=str(labels[int(label_id)]),
                    score=float(score),
                    box=coords,  # type: ignore[arg-type]
                    source_size=(width, height),
                )
            )
        return detections


class PromptSegmenter:
    """読み込み済みSAM。点または枠で指定された対象のマスクを返す。"""

    def __init__(self, processor: Any, model: Any, torch: Any, numpy: Any, device: str) -> None:
        self._processor = processor
        self._model = model
        self._torch = torch
        self._numpy = numpy
        self.device = device

    def predict(
        self,
        image: Any,
        *,
        box: Iterable[float] | None = None,
        point: Iterable[float] | None = None,
    ) -> Segmentation:
        """点(x,y)か矩形(x_min,y_min,x_max,y_max)の一方を指定してマスクを作る。"""
        if (box is None) == (point is None):
            raise ValueError("boxかpointのどちらか一方を指定してください。")
        rgb = _open_image(image)
        width, height = rgb.size
        if box is not None:
            prompt = _validate_box(box, width, height)
            inputs = self._processor(images=rgb, input_boxes=[[[list(prompt)]]], return_tensors="pt")
            prompt_type = "box"
        else:
            prompt = _validate_point(point, width, height)  # type: ignore[arg-type]
            inputs = self._processor(images=rgb, input_points=[[list(prompt)]], return_tensors="pt")
            prompt_type = "point"
        inputs = _to_device(inputs, self.device)
        with self._torch.no_grad():
            outputs = self._model(**inputs)
        masks = self._processor.image_processor.post_process_masks(
            outputs.pred_masks.cpu(),
            inputs["original_sizes"].cpu(),
            inputs["reshaped_input_sizes"].cpu(),
        )[0][0]
        scores = outputs.iou_scores[0][0]
        best = int(scores.argmax().item())
        mask = masks[best].numpy().astype(self._numpy.bool_, copy=False)
        return Segmentation(mask=mask, score=float(scores[best].item()), prompt_type=prompt_type, prompt=prompt)

    def segment_detections(
        self, image: Any, detections: Iterable[Detection]
    ) -> list[DetectedSegment]:
        """検出枠ごとにSAMを呼ぶ。検出ラベルはSAMの推論ラベルではない。"""
        results = []
        width, height = _open_image(image).size
        for detection in detections:
            box = detection.box
            if detection.source_size is not None:
                source_width, source_height = detection.source_size
                if source_width <= 0 or source_height <= 0:
                    raise ValueError("Detection.source_sizeは正の(width, height)で指定してください。")
                scale_x, scale_y = width / source_width, height / source_height
                box = (
                    box[0] * scale_x,
                    box[1] * scale_y,
                    box[2] * scale_x,
                    box[3] * scale_y,
                )
            box = _clip_detection_box(box, width, height)
            if box is None:
                continue
            mask = self.predict(image, box=box)
            results.append(DetectedSegment(detection=detection, segmentation=mask))
        return results


def available_devices() -> dict[str, bool]:
    """PyTorchで利用できるCPU、CUDA、Apple MPSを返す。"""
    torch = _import_torch()
    devices = {"cpu": True, "cuda:0": bool(torch.cuda.is_available()), "mps": False}
    try:
        devices["mps"] = bool(torch.backends.mps.is_available())
    except (AttributeError, RuntimeError):
        pass
    if devices["cuda:0"]:
        for index in range(1, int(torch.cuda.device_count())):
            devices[f"cuda:{index}"] = True
    return devices


def load_detector(
    *, device: str = "cpu", model_id: str | None = None, revision: str | None = None,
    cache_dir: str | Path | None = None, local_files_only: bool = False
) -> ObjectDetector:
    """既定DETRか互換検出モデルを読み込む。別モデルは40桁revisionが必須。"""
    model_id, revision = _resolve_model(model_id, revision, _DETECTOR_ID, _DETECTOR_REVISION)
    torch = _check_device(device)
    try:
        from transformers import AutoImageProcessor, AutoModelForObjectDetection
    except ImportError as exc:
        raise VisionError("検出にはTransformersが必要です。python -m pip install --pre 'cv-data-lesson[vision]'を実行してください。") from exc
    kwargs = _load_kwargs(cache_dir, local_files_only)
    try:
        processor = AutoImageProcessor.from_pretrained(model_id, revision=revision, **kwargs)
        model = AutoModelForObjectDetection.from_pretrained(model_id, revision=revision, **kwargs)
        model.to(device)
        model.eval()
    except Exception as exc:
        raise VisionError(f"固定版DETRを読み込めませんでした。通信・キャッシュ・依存関係を確認してください: {exc}") from exc
    return ObjectDetector(processor, model, torch, device)


def load_segmenter(
    *, device: str = "cpu", model_id: str | None = None, revision: str | None = None,
    cache_dir: str | Path | None = None, local_files_only: bool = False
) -> PromptSegmenter:
    """既定SAMか互換SAMモデルを読み込む。別モデルは40桁revisionが必須。"""
    model_id, revision = _resolve_model(model_id, revision, _SEGMENTER_ID, _SEGMENTER_REVISION)
    torch = _check_device(device)
    try:
        import numpy
        from transformers import SamModel, SamProcessor
    except ImportError as exc:
        raise VisionError("領域分割にはNumPyとTransformersが必要です。python -m pip install --pre 'cv-data-lesson[vision]'を実行してください。") from exc
    kwargs = _load_kwargs(cache_dir, local_files_only)
    try:
        processor = SamProcessor.from_pretrained(model_id, revision=revision, **kwargs)
        model = SamModel.from_pretrained(model_id, revision=revision, **kwargs)
        model.to(device)
        model.eval()
    except Exception as exc:
        raise VisionError(f"固定版SAMを読み込めませんでした。通信・キャッシュ・依存関係を確認してください: {exc}") from exc
    return PromptSegmenter(processor, model, torch, numpy, device)


def _import_torch():
    try:
        import torch
    except ImportError as exc:
        raise VisionError(
            "検出・領域分割にはPyTorchが必要です。公式サイトでCPU/GPUに合うPyTorchを導入してから、"
            "python -m pip install --pre 'cv-data-lesson[vision]'を実行してください。"
        ) from exc
    return torch


def _check_device(device: str):
    torch = _import_torch()
    if device == "cpu":
        return torch
    if device == "mps":
        available = bool(getattr(getattr(torch.backends, "mps", None), "is_available", lambda: False)())
    elif device.startswith("cuda:") and device[5:].isdigit():
        index = int(device[5:])
        available = bool(torch.cuda.is_available() and index < torch.cuda.device_count())
    else:
        raise ValueError("deviceは'cpu'、'cuda:0'、'mps'など明示してください。")
    if not available:
        raise VisionError(f"device={device!r}は利用できません。vision.available_devices()で確認してください。")
    return torch


def _open_image(image: str | Path):
    try:
        from PIL import Image
    except ImportError as exc:
        raise VisionError("画像処理にはPillowが必要です。python -m pip install --pre 'cv-data-lesson[vision]'を実行してください。") from exc
    if isinstance(image, (str, Path)):
        path = Path(image).expanduser()
        if not path.is_file():
            raise FileNotFoundError(f"画像ファイルが見つかりません: {path}")
        with Image.open(path) as opened:
            return opened.convert("RGB")
    if isinstance(image, Image.Image):
        return image.convert("RGB").copy()
    raise TypeError("imageには画像ファイルのパスまたはPillow Imageを指定してください。NumPy配列は未対応です。")


def _validate_box(box: Iterable[float], width: int, height: int) -> tuple[float, float, float, float]:
    values = tuple(float(value) for value in box)
    if len(values) != 4:
        raise ValueError("boxは(x_min, y_min, x_max, y_max)の4値で指定してください。")
    x1, y1, x2, y2 = values
    if not (0 <= x1 < x2 <= width and 0 <= y1 < y2 <= height):
        raise ValueError(f"boxは画像範囲内({width}×{height})の正しい矩形にしてください。")
    return values  # type: ignore[return-value]


def _clip_detection_box(
    box: Iterable[float], width: int, height: int
) -> tuple[float, float, float, float] | None:
    """有限な検出座標を画像範囲へ収め、面積0の枠を除外する。"""
    values = tuple(float(value) for value in box)
    if len(values) != 4 or not all(math.isfinite(value) for value in values):
        return None
    x1, y1, x2, y2 = values
    clipped = (
        min(max(x1, 0.0), float(width)),
        min(max(y1, 0.0), float(height)),
        min(max(x2, 0.0), float(width)),
        min(max(y2, 0.0), float(height)),
    )
    if clipped[0] >= clipped[2] or clipped[1] >= clipped[3]:
        return None
    return clipped


def _validate_point(point: Iterable[float], width: int, height: int) -> tuple[float, float]:
    values = tuple(float(value) for value in point)
    if len(values) != 2:
        raise ValueError("pointは(x, y)の2値で指定してください。")
    x, y = values
    if not (0 <= x < width and 0 <= y < height):
        raise ValueError(f"pointは画像範囲内({width}×{height})で指定してください。")
    return values  # type: ignore[return-value]


def _load_kwargs(cache_dir: str | Path | None, local_files_only: bool) -> dict[str, Any]:
    kwargs: dict[str, Any] = {"local_files_only": local_files_only}
    if cache_dir is not None:
        kwargs["cache_dir"] = str(Path(cache_dir).expanduser())
    return kwargs


def _resolve_model(
    model_id: str | None, revision: str | None, default_id: str, default_revision: str
) -> tuple[str, str]:
    if model_id is None and revision is None:
        return default_id, default_revision
    if not isinstance(model_id, str) or not model_id.strip():
        raise ValueError("別モデルを使うときはmodel_idと固定revisionを両方指定してください。")
    if not isinstance(revision, str) or not re.fullmatch(r"[0-9a-fA-F]{40}", revision):
        raise ValueError("別モデルのrevisionには完全な40桁のGit commit SHAを指定してください。")
    return model_id.strip(), revision.lower()


def _to_device(inputs: Any, device: str):
    if hasattr(inputs, "to"):
        return inputs.to(device)
    return {key: value.to(device) if hasattr(value, "to") else value for key, value in inputs.items()}


def _as_list(value: Any) -> list[Any]:
    if hasattr(value, "tolist"):
        return value.tolist()
    return list(value)
