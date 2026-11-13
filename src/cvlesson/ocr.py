"""日本語OCR推論。PaddleOCRとHugging Face Hubはload()時だけ読み込む。"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any


class OCRError(RuntimeError):
    """OCRモデルの準備・推論に関するエラー。"""


_DETECTION_REPO = "PaddlePaddle/PP-OCRv5_mobile_det"
_DETECTION_REVISION = "0d63e78e2b680928f6b1747d76a08db6e645efb7"
_RECOGNITION_REPO = "PaddlePaddle/PP-OCRv5_mobile_rec"
_RECOGNITION_REVISION = "682f20538d8c086cb2128e5cfac775e6c4904e85"


@dataclass(frozen=True)
class OCRLine:
    """画像中の1行分のOCR結果。polygonは左上から時計回りの画像座標。"""

    text: str
    confidence: float
    polygon: tuple[tuple[float, float], ...]


@dataclass(frozen=True)
class OCRResult:
    """画像1枚に対するOCR結果。"""

    lines: tuple[OCRLine, ...]
    source: str

    @property
    def text(self) -> str:
        """行ごとに改行した読み取り文字列。"""
        return "\n".join(line.text for line in self.lines)

    def to_dict(self) -> dict[str, Any]:
        """標準Python型の辞書へ変換する。"""
        return {
            "source": self.source,
            "text": self.text,
            "lines": [
                {
                    "text": line.text,
                    "confidence": line.confidence,
                    "polygon": [list(point) for point in line.polygon],
                }
                for line in self.lines
            ],
        }


class OCR:
    """読み込み済みOCRモデル。OCR学習や微調整は行わない。"""

    def __init__(self, pipeline: Any, *, device: str, language: str) -> None:
        self._pipeline = pipeline
        self.device = device
        self.language = language

    def predict(self, image: str | Path) -> OCRResult:
        """画像ファイルを読み取り、文字・信頼度・位置を返す。"""
        path = Path(image).expanduser()
        if not path.is_file():
            raise FileNotFoundError(f"画像ファイルが見つかりません: {path}")
        try:
            raw_results = self._pipeline.predict(input=str(path))
            if raw_results is None:
                raw_results = []
            elif not isinstance(raw_results, (list, tuple)):
                raw_results = [raw_results]
            lines: list[OCRLine] = []
            for raw in raw_results:
                lines.extend(_parse_result(raw))
        except OCRError:
            raise
        except Exception as exc:
            raise OCRError(f"OCRを実行できませんでした: {exc}") from exc
        return OCRResult(lines=tuple(lines), source=str(path.resolve()))


def available_devices() -> dict[str, bool]:
    """PaddlePaddle環境でCPUとCUDA GPUの利用可否を返す。"""
    return _devices_from_paddle(_import_paddle())


def load(
    *,
    device: str = "cpu",
    language: str = "japan",
    cache_dir: str | Path | None = None,
    local_files_only: bool = False,
    detection_model_dir: str | Path | None = None,
    recognition_model_dir: str | Path | None = None,
) -> OCR:
    """PP-OCRv5 mobileを読み込む。既定は日本語・CPU。

    モデルはこの関数を呼んだときに限り、固定したHugging Face revisionから
    キャッシュへ取得する。別モデルを使う場合は、対応するPaddle推論モデルの
    ディレクトリを検出・認識の両方で指定する。
    """
    if language != "japan":
        raise ValueError("既定モデルで利用できるlanguageは現在 japan のみです。")
    if device != "cpu" and not (device.startswith("gpu:") and device[4:].isdigit()):
        raise ValueError("deviceは'cpu'または'gpu:0'形式で指定してください。GPUは自動選択しません。")
    if (detection_model_dir is None) != (recognition_model_dir is None):
        raise ValueError("別のモデルを使うときはdetection_model_dirとrecognition_model_dirを両方指定してください。")

    paddle = _import_paddle()
    devices = _devices_from_paddle(paddle)
    if not devices.get(device, False):
        raise OCRError(
            f"device={device!r}はこの環境で利用できません。CPU版/GPU版PaddlePaddleを確認し、"
            "ocr.available_devices()で利用可否を確認してください。"
        )

    try:
        from paddleocr import PaddleOCR
    except ImportError as exc:
        raise OCRError("OCRにはpaddleocrが必要です。pip install 'cv-data-lesson[ocr]'を実行してください。") from exc

    if detection_model_dir is None:
        try:
            from huggingface_hub import snapshot_download
        except ImportError as exc:
            raise OCRError(
                "既定OCRモデルの取得にはhuggingface_hubが必要です。pip install 'cv-data-lesson[ocr]'を実行してください。"
            ) from exc
        try:
            detection_path = snapshot_download(
                repo_id=_DETECTION_REPO,
                revision=_DETECTION_REVISION,
                cache_dir=str(cache_dir) if cache_dir is not None else None,
                local_files_only=local_files_only,
            )
            recognition_path = snapshot_download(
                repo_id=_RECOGNITION_REPO,
                revision=_RECOGNITION_REVISION,
                cache_dir=str(cache_dir) if cache_dir is not None else None,
                local_files_only=local_files_only,
            )
        except Exception as exc:
            raise OCRError(f"固定版OCRモデルを取得できませんでした。ネットワークとキャッシュを確認してください: {exc}") from exc
    else:
        detection_path = Path(detection_model_dir).expanduser()
        recognition_path = Path(recognition_model_dir).expanduser()
        for label, path in (("検出", detection_path), ("認識", recognition_path)):
            if not path.is_dir():
                raise FileNotFoundError(f"{label}モデルのディレクトリが見つかりません: {path}")

    try:
        pipeline_args = {
            "device": device,
            "text_detection_model_dir": str(detection_path),
            "text_recognition_model_dir": str(recognition_path),
            "use_doc_orientation_classify": False,
            "use_doc_unwarping": False,
            "use_textline_orientation": False,
        }
        if detection_model_dir is None:
            # Explicit names pair the pinned local model files with PaddleOCR.
            # PaddleOCR ignores `lang`/`ocr_version` when model paths are set.
            pipeline_args.update(
                text_detection_model_name="PP-OCRv5_mobile_det",
                text_recognition_model_name="PP-OCRv5_mobile_rec",
            )
        pipeline = PaddleOCR(**pipeline_args)
    except Exception as exc:
        raise OCRError(f"PaddleOCRを初期化できませんでした。モデル形式と依存関係を確認してください: {exc}") from exc
    return OCR(pipeline, device=device, language=language)


def _import_paddle():
    try:
        import paddle
    except ImportError as exc:
        raise OCRError(
            "OCR実行エンジンのPaddlePaddleが必要です。"
            "docs/installation.mdのOCR手順からCPU版または環境に合うGPU版を導入してください。"
        ) from exc
    return paddle


def _devices_from_paddle(paddle: Any) -> dict[str, bool]:
    devices = {"cpu": True}
    try:
        count = paddle.device.cuda.device_count() if paddle.is_compiled_with_cuda() else 0
    except Exception:
        count = 0
    for index in range(count):
        devices[f"gpu:{index}"] = True
    devices.setdefault("gpu:0", False)
    return devices


def _parse_result(result: Any) -> list[OCRLine]:
    payload = getattr(result, "json", result)
    if callable(payload):
        payload = payload()
    if not isinstance(payload, dict):
        raise OCRError("OCRバックエンドの結果形式が想定と異なります。")
    data = payload.get("res", payload)
    if not isinstance(data, dict):
        raise OCRError("OCRバックエンドの結果にresデータがありません。")

    texts = _as_list(data.get("rec_texts", []))
    scores = _as_list(data.get("rec_scores", []))
    polygons = _as_list(data.get("rec_polys", data.get("dt_polys", [])))
    lines = []
    for index, text in enumerate(texts):
        text = str(text).strip()
        if not text:
            continue
        score = float(scores[index]) if index < len(scores) else 0.0
        score = min(1.0, max(0.0, score))
        polygon = _polygon(polygons[index]) if index < len(polygons) else ()
        lines.append(OCRLine(text=text, confidence=score, polygon=polygon))
    return lines


def _as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if hasattr(value, "tolist"):
        value = value.tolist()
    return list(value)


def _polygon(value: Any) -> tuple[tuple[float, float], ...]:
    points = _as_list(value)
    polygon = tuple((float(point[0]), float(point[1])) for point in points if len(point) >= 2)
    if len(polygon) != 4:
        return ()
    return polygon
