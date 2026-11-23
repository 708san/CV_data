"""画像とCV推論結果を重ねて表示・保存する補助機能。"""
from __future__ import annotations

from io import BytesIO
from pathlib import Path
from typing import Any


class DisplayError(RuntimeError):
    """画像表示用の変換・描画で発生したエラー。"""


def render(
    image: Any,
    result: Any = None,
    *,
    mask_alpha: int = 110,
    max_detections: int | None = None,
    max_ocr_lines: int | None = None,
):
    """画像へ推論結果を描き、合成したRGBのPillow Imageを返す。

    ``result``にはOCRResult、Detectionのリスト、Segmentation、DetectedSegmentの
    リストを指定できます。``None``なら画像をRGBへ変換して返します。
    検出結果は信頼度上位``max_detections``件だけを描画します。全件を描画する
    場合は``max_detections=None``を指定してください。推論結果そのものは変更しません。
    OCRは``max_ocr_lines``を指定した場合だけ、信頼度の高い行を指定数まで表示します。
    OCRResultの全行と文字列は保持されます。
    入力画像や推論結果は変更しません。
    """
    Image, ImageDraw, ImageFont = _pillow()
    if not isinstance(mask_alpha, int) or isinstance(mask_alpha, bool) or not 0 <= mask_alpha <= 255:
        raise ValueError("mask_alphaは0から255の整数で指定してください。")
    _validate_max_detections(max_detections)
    _validate_max_ocr_lines(max_ocr_lines)
    canvas = _open_rgb(image, Image)
    if result is None:
        return canvas

    draw = ImageDraw.Draw(canvas, "RGBA")
    font = _font(ImageFont)
    items = list(result) if isinstance(result, (list, tuple)) else [result]
    items = _limit_detection_items(items, max_detections)
    label_obstacles = _collect_label_obstacles(items)
    occupied_labels: list[tuple[float, float, float, float]] = []
    for item in items:
        if hasattr(item, "segmentation") and hasattr(item, "detection"):
            _draw_mask(canvas, item.segmentation.mask, mask_alpha, Image)
            _draw_detection(
                draw, item.detection, font, canvas.size, label_obstacles, occupied_labels
            )
        elif hasattr(item, "mask") and hasattr(item, "prompt_type"):
            _draw_mask(canvas, item.mask, mask_alpha, Image)
        elif hasattr(item, "box") and hasattr(item, "label") and hasattr(item, "score"):
            _draw_detection(draw, item, font, canvas.size, label_obstacles, occupied_labels)
        elif hasattr(item, "lines"):
            for line in _visible_ocr_lines(item.lines, max_ocr_lines):
                _draw_ocr_line(
                    draw, line, font, canvas.size, label_obstacles, occupied_labels
                )
        else:
            raise DisplayError(f"未対応の推論結果です: {type(item).__name__}")
    return canvas


def show(
    image: Any,
    result: Any = None,
    *,
    mask_alpha: int = 110,
    max_detections: int | None = None,
    max_ocr_lines: int | None = None,
):
    """合成画像をNotebookまたは既定の画像ビューアで表示して返す。"""
    rendered = render(
        image,
        result,
        mask_alpha=mask_alpha,
        max_detections=max_detections,
        max_ocr_lines=max_ocr_lines,
    )
    try:
        from IPython.display import display as notebook_display
    except ImportError:
        rendered.show()
    else:
        notebook_display(rendered)
    return rendered


def save(
    image: Any,
    path: str | Path,
    result: Any = None,
    *,
    mask_alpha: int = 110,
    max_detections: int | None = None,
    max_ocr_lines: int | None = None,
) -> Path:
    """合成画像を指定先へ保存し、保存先Pathを返す。"""
    destination = Path(path).expanduser()
    rendered = render(
        image,
        result,
        mask_alpha=mask_alpha,
        max_detections=max_detections,
        max_ocr_lines=max_ocr_lines,
    )
    image_module, _, _ = _pillow()
    image_format = image_module.registered_extensions().get(destination.suffix.lower())
    if image_format is None:
        raise ValueError(f"保存先の拡張子に対応する画像形式がありません: {destination.suffix or '(なし)'}")
    encoded = BytesIO()
    rendered.save(encoded, format=image_format)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(encoded.getvalue())
    return destination


def _pillow():
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError as exc:
        raise DisplayError(
            "画像表示にはPillowが必要です。pip install 'cv-data-lesson[display]'を実行してください。"
        ) from exc
    return Image, ImageDraw, ImageFont


def _open_rgb(image: Any, image_module: Any):
    if isinstance(image, (str, Path)):
        path = Path(image).expanduser()
        if not path.is_file():
            raise FileNotFoundError(f"画像ファイルが見つかりません: {path}")
        with image_module.open(path) as opened:
            return opened.convert("RGB")
    if isinstance(image, image_module.Image):
        return image.convert("RGB")
    raise TypeError("imageには画像ファイルのパスまたはPillow Imageを指定してください。")


def _font(font_module: Any):
    candidates = []
    try:
        import japanize_matplotlib
        japanese_font = japanize_matplotlib.get_font_ttf_path()
        if japanese_font:
            candidates.append(str(japanese_font))
    except (ImportError, AttributeError, OSError):
        pass
    candidates.extend((
        "/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc",
        "/System/Library/Fonts/ヒラギノ丸ゴ ProN W4.ttc",
        "C:/Windows/Fonts/meiryo.ttc",
        "C:/Windows/Fonts/YuGothM.ttc",
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ))
    for candidate in candidates:
        try:
            return font_module.truetype(candidate, 14)
        except OSError:
            continue
    return font_module.load_default()


def _validate_max_detections(max_detections: int | None) -> None:
    if max_detections is not None and (
        isinstance(max_detections, bool)
        or not isinstance(max_detections, int)
        or max_detections < 0
    ):
        raise ValueError("max_detectionsは0以上の整数またはNoneで指定してください。")


def _validate_max_ocr_lines(max_ocr_lines: int | None) -> None:
    if max_ocr_lines is not None and (
        isinstance(max_ocr_lines, bool)
        or not isinstance(max_ocr_lines, int)
        or max_ocr_lines < 0
    ):
        raise ValueError("max_ocr_linesは0以上の整数またはNoneで指定してください。")


def _visible_ocr_lines(lines: Any, max_ocr_lines: int | None) -> list[Any]:
    values = list(lines)
    if max_ocr_lines is None or len(values) <= max_ocr_lines:
        return values
    selected = sorted(
        enumerate(values),
        key=lambda pair: float(pair[1].confidence),
        reverse=True,
    )[:max_ocr_lines]
    # 表示は元画像の読み順へ戻す。OCRResult本体の順序は変更しない。
    return [
        line
        for _, line in sorted(
            selected,
            key=lambda pair: (
                min(float(point[1]) for point in pair[1].polygon),
                min(float(point[0]) for point in pair[1].polygon),
                pair[0],
            ),
        )
    ]


def _limit_detection_items(items: list[Any], max_detections: int | None) -> list[Any]:
    """表示専用に検出結果を信頼度順で絞る。入力結果は変更しない。"""
    if max_detections is None:
        return items
    detection_indexes = [
        index
        for index, item in enumerate(items)
        if (
            hasattr(item, "box") and hasattr(item, "label") and hasattr(item, "score")
        ) or (
            hasattr(item, "detection") and hasattr(item, "segmentation")
        )
    ]
    ranked = sorted(
        detection_indexes,
        key=lambda index: _display_detection_score(items[index]),
        reverse=True,
    )
    keep = set(ranked[:max_detections])
    return [item for index, item in enumerate(items) if index not in detection_indexes or index in keep]


def _display_detection_score(item: Any) -> float:
    if hasattr(item, "score"):
        return float(item.score)
    return float(getattr(item.detection, "score", 0.0))


def _draw_detection(
    draw: Any,
    detection: Any,
    font: Any,
    size: tuple[int, int],
    obstacles: list[tuple[float, float, float, float]],
    occupied_labels: list[tuple[float, float, float, float]],
) -> None:
    try:
        box = tuple(float(value) for value in detection.box)
    except (TypeError, ValueError) as exc:
        raise DisplayError("検出boxは数値の(x_min, y_min, x_max, y_max)で指定してください。") from exc
    if len(box) != 4:
        raise DisplayError("検出boxは(x_min, y_min, x_max, y_max)の4値が必要です。")
    _check_box(box, size)
    draw.rectangle(box, outline=(255, 190, 0, 255), width=3)
    text = f"{detection.label} {float(detection.score):.2f}"
    _draw_label(draw, box, text, font, size, obstacles, occupied_labels)


def _draw_ocr_line(
    draw: Any,
    line: Any,
    font: Any,
    size: tuple[int, int],
    obstacles: list[tuple[float, float, float, float]],
    occupied_labels: list[tuple[float, float, float, float]],
) -> None:
    try:
        polygon = tuple(tuple(float(value) for value in point) for point in line.polygon)
    except (TypeError, ValueError) as exc:
        raise DisplayError("OCR polygonは数値の画像座標で指定してください。") from exc
    if len(polygon) < 4 or any(len(point) != 2 for point in polygon):
        raise DisplayError("OCR polygonは画像上の(x, y)座標を4点以上指定してください。")
    for x, y in polygon:
        if not (0 <= x <= size[0] and 0 <= y <= size[1]):
            raise DisplayError("OCR polygonが画像の範囲外です。")
    draw.polygon(polygon, outline=(0, 210, 255, 255), width=3)
    box = (
        min(point[0] for point in polygon),
        min(point[1] for point in polygon),
        max(point[0] for point in polygon),
        max(point[1] for point in polygon),
    )
    _draw_label(
        draw,
        box,
        f"{line.text} ({float(line.confidence):.2f})",
        font,
        size,
        obstacles,
        occupied_labels,
    )


def _draw_label(
    draw: Any,
    anchor_box: tuple[float, float, float, float],
    text: str,
    font: Any,
    size: tuple[int, int],
    obstacles: list[tuple[float, float, float, float]],
    occupied_labels: list[tuple[float, float, float, float]],
) -> None:
    try:
        text = _fit_label_text(draw, str(text), font, size[0] - 8)
        bounds = draw.textbbox((0, 0), text, font=font)
        width, height = bounds[2] - bounds[0], bounds[3] - bounds[1]
        label_box = _place_label(
            anchor_box,
            (width + 8, height + 6),
            size,
            obstacles,
            occupied_labels,
        )
        draw.rectangle(label_box, fill=(20, 40, 55, 255), outline=(255, 255, 255, 255), width=1)
        draw.text(
            (label_box[0] + 4 - bounds[0], label_box[1] + 3 - bounds[1]),
            text,
            fill=(255, 255, 255, 255),
            font=font,
        )
        occupied_labels.append(label_box)
    except (UnicodeError, ValueError):
        # 日本語フォントがない環境でも枠は表示する。文字列自体は結果オブジェクトに残る。
        return


def _collect_label_obstacles(items: list[Any]) -> list[tuple[float, float, float, float]]:
    """注釈ラベルを置かない対象領域を、描画前に集める。"""
    obstacles: list[tuple[float, float, float, float]] = []
    for item in items:
        if hasattr(item, "segmentation") and hasattr(item, "detection"):
            box = _coerce_box(getattr(item.detection, "box", None))
            if box is not None:
                obstacles.append(box)
        elif hasattr(item, "box") and hasattr(item, "label") and hasattr(item, "score"):
            box = _coerce_box(getattr(item, "box", None))
            if box is not None:
                obstacles.append(box)
        elif hasattr(item, "lines"):
            for line in item.lines:
                try:
                    polygon = tuple(
                        tuple(float(value) for value in point) for point in line.polygon
                    )
                    if len(polygon) < 4 or any(len(point) != 2 for point in polygon):
                        continue
                    obstacles.append(
                        (
                            min(point[0] for point in polygon),
                            min(point[1] for point in polygon),
                            max(point[0] for point in polygon),
                            max(point[1] for point in polygon),
                        )
                    )
                except (TypeError, ValueError):
                    continue
    return obstacles


def _coerce_box(values: Any) -> tuple[float, float, float, float] | None:
    try:
        box = tuple(float(value) for value in values)
    except (TypeError, ValueError):
        return None
    if len(box) != 4:
        return None
    return box  # type: ignore[return-value]


def _fit_label_text(draw: Any, text: str, font: Any, max_width: float) -> str:
    """表示用文字列だけを画像幅に収める。OCRResult自体の文字列は変更しない。"""
    if draw.textbbox((0, 0), text, font=font)[2] <= max_width:
        return text
    suffix = "…"
    for length in range(len(text) - 1, 0, -1):
        candidate = text[:length] + suffix
        if draw.textbbox((0, 0), candidate, font=font)[2] <= max_width:
            return candidate
    return suffix


def _place_label(
    anchor_box: tuple[float, float, float, float],
    label_size: tuple[float, float],
    image_size: tuple[int, int],
    obstacles: list[tuple[float, float, float, float]],
    occupied_labels: list[tuple[float, float, float, float]],
) -> tuple[float, float, float, float]:
    """ラベルを対象領域の外側へ置き、既存注釈との重なりをできるだけ避ける。"""
    x1, y1, x2, y2 = anchor_box
    width, height = label_size
    gap = 4.0
    candidates: list[tuple[float, float, float, float]] = []
    for step in range(12):
        offset_y = step * (height + gap)
        offset_x = step * (width + gap)
        candidates.extend(
            (
                (x1, y1 - height - gap - offset_y, x1 + width, y1 - gap - offset_y),
                (x1, y2 + gap + offset_y, x1 + width, y2 + height + gap + offset_y),
                (x2 + gap + offset_x, y1, x2 + width + gap + offset_x, y1 + height),
                (x1 - width - gap - offset_x, y1, x1 - gap - offset_x, y1 + height),
            )
        )

    normalized: list[tuple[float, float, float, float]] = []
    seen: set[tuple[float, float, float, float]] = set()
    for candidate in candidates:
        left = max(0.0, min(candidate[0], image_size[0] - width))
        top = max(0.0, min(candidate[1], image_size[1] - height))
        rect = (left, top, left + width, top + height)
        if rect not in seen:
            normalized.append(rect)
            seen.add(rect)

    def overlap_area(first: tuple[float, float, float, float], second: tuple[float, float, float, float]) -> float:
        return max(0.0, min(first[2], second[2]) - max(first[0], second[0])) * max(
            0.0, min(first[3], second[3]) - max(first[1], second[1])
        )

    for candidate in normalized:
        if all(overlap_area(candidate, obstacle) == 0 for obstacle in obstacles) and all(
            overlap_area(candidate, occupied) == 0 for occupied in occupied_labels
        ):
            return candidate

    # 画像が注釈で埋まっている場合も、最も重なりの少ない位置を選び、描画自体は継続する。
    return min(
        normalized,
        key=lambda candidate: sum(overlap_area(candidate, obstacle) for obstacle in obstacles)
        + 2 * sum(overlap_area(candidate, occupied) for occupied in occupied_labels),
    )


def _draw_mask(canvas: Any, mask: Any, alpha: int, image_module: Any) -> None:
    try:
        import numpy as np
        values = np.asarray(mask)
    except (ImportError, TypeError, ValueError) as exc:
        raise DisplayError("マスクをNumPy配列へ変換できません。") from exc
    if values.ndim != 2 or values.shape != (canvas.height, canvas.width):
        raise DisplayError(
            f"マスク形状{values.shape}が画像サイズ{(canvas.height, canvas.width)}と一致しません。"
        )
    if values.dtype.kind not in {"b", "i", "u", "f"}:
        raise DisplayError("マスクはboolまたは有限な数値の2次元配列で指定してください。")
    if values.dtype.kind == "f" and not np.isfinite(values).all():
        raise DisplayError("マスクの数値にはNaNや無限大を含められません。")
    values = values.astype(np.bool_, copy=False)
    pixels = np.zeros((canvas.height, canvas.width, 4), dtype=np.uint8)
    pixels[values] = (40, 220, 100, alpha)
    overlay = image_module.fromarray(pixels)
    canvas.alpha_composite(overlay) if canvas.mode == "RGBA" else _composite_rgb(canvas, overlay)


def _composite_rgb(canvas: Any, overlay: Any) -> None:
    canvas.paste(overlay, (0, 0), overlay)


def _check_box(box: tuple[float, ...], size: tuple[int, int]) -> None:
    x1, y1, x2, y2 = box
    if not (0 <= x1 < x2 <= size[0] and 0 <= y1 < y2 <= size[1]):
        raise DisplayError(f"検出boxが画像の範囲外か不正です: box={box}, image_size={size}")


__all__ = ["DisplayError", "render", "save", "show"]
