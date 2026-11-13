"""画像とCV推論結果を重ねて表示・保存する補助機能。"""
from __future__ import annotations

from pathlib import Path
from typing import Any


class DisplayError(RuntimeError):
    """画像表示用の変換・描画で発生したエラー。"""


def render(image: Any, result: Any = None, *, mask_alpha: int = 110):
    """画像へ推論結果を描き、合成したRGBのPillow Imageを返す。

    ``result``にはOCRResult、Detectionのリスト、Segmentation、DetectedSegmentの
    リストを指定できます。``None``なら画像をRGBへ変換して返します。
    入力画像や推論結果は変更しません。
    """
    Image, ImageDraw, ImageFont = _pillow()
    if not isinstance(mask_alpha, int) or isinstance(mask_alpha, bool) or not 0 <= mask_alpha <= 255:
        raise ValueError("mask_alphaは0から255の整数で指定してください。")
    canvas = _open_rgb(image, Image)
    if result is None:
        return canvas

    draw = ImageDraw.Draw(canvas, "RGBA")
    font = _font(ImageFont)
    items = list(result) if isinstance(result, (list, tuple)) else [result]
    for item in items:
        if hasattr(item, "segmentation") and hasattr(item, "detection"):
            _draw_mask(canvas, item.segmentation.mask, mask_alpha, Image)
            _draw_detection(draw, item.detection, font, canvas.size)
        elif hasattr(item, "mask") and hasattr(item, "prompt_type"):
            _draw_mask(canvas, item.mask, mask_alpha, Image)
        elif hasattr(item, "box") and hasattr(item, "label") and hasattr(item, "score"):
            _draw_detection(draw, item, font, canvas.size)
        elif hasattr(item, "lines"):
            for line in item.lines:
                _draw_ocr_line(draw, line, font, canvas.size)
        else:
            raise DisplayError(f"未対応の推論結果です: {type(item).__name__}")
    return canvas


def show(image: Any, result: Any = None, *, mask_alpha: int = 110):
    """合成画像をNotebookまたは既定の画像ビューアで表示して返す。"""
    rendered = render(image, result, mask_alpha=mask_alpha)
    try:
        from IPython.display import display as notebook_display
    except ImportError:
        rendered.show()
    else:
        notebook_display(rendered)
    return rendered


def save(image: Any, path: str | Path, result: Any = None, *, mask_alpha: int = 110) -> Path:
    """合成画像を指定先へ保存し、保存先Pathを返す。"""
    destination = Path(path).expanduser()
    destination.parent.mkdir(parents=True, exist_ok=True)
    rendered = render(image, result, mask_alpha=mask_alpha)
    rendered.save(destination)
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
    candidates = (
        "/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc",
        "/System/Library/Fonts/ヒラギノ丸ゴ ProN W4.ttc",
        "C:/Windows/Fonts/meiryo.ttc",
        "C:/Windows/Fonts/YuGothM.ttc",
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    )
    for candidate in candidates:
        try:
            return font_module.truetype(candidate, 14)
        except OSError:
            continue
    return font_module.load_default()


def _draw_detection(draw: Any, detection: Any, font: Any, size: tuple[int, int]) -> None:
    box = tuple(float(value) for value in detection.box)
    if len(box) != 4:
        raise DisplayError("検出boxは(x_min, y_min, x_max, y_max)の4値が必要です。")
    _check_box(box, size)
    draw.rectangle(box, outline=(255, 190, 0, 255), width=3)
    text = f"{detection.label} {float(detection.score):.2f}"
    _draw_label(draw, box[0], box[1], text, font)


def _draw_ocr_line(draw: Any, line: Any, font: Any, size: tuple[int, int]) -> None:
    polygon = tuple(tuple(float(value) for value in point) for point in line.polygon)
    if len(polygon) < 4 or any(len(point) != 2 for point in polygon):
        raise DisplayError("OCR polygonは画像上の(x, y)座標を4点以上指定してください。")
    for x, y in polygon:
        if not (0 <= x <= size[0] and 0 <= y <= size[1]):
            raise DisplayError("OCR polygonが画像の範囲外です。")
    draw.polygon(polygon, outline=(0, 210, 255, 255), width=3)
    _draw_label(draw, min(point[0] for point in polygon), min(point[1] for point in polygon),
                f"{line.text} ({float(line.confidence):.2f})", font)


def _draw_label(draw: Any, x: float, y: float, text: str, font: Any) -> None:
    try:
        bounds = draw.textbbox((0, 0), text, font=font)
        width, height = bounds[2] - bounds[0], bounds[3] - bounds[1]
        top = max(0, y - height - 6)
        draw.rectangle((x, top, x + width + 8, top + height + 6), fill=(20, 40, 55, 210))
        draw.text((x + 4, top + 2), text, fill=(255, 255, 255, 255), font=font)
    except (UnicodeError, ValueError):
        # 日本語フォントがない環境でも枠は表示する。文字列自体は結果オブジェクトに残る。
        return


def _draw_mask(canvas: Any, mask: Any, alpha: int, image_module: Any) -> None:
    try:
        import numpy as np
        values = np.asarray(mask, dtype=np.bool_)
    except (ImportError, TypeError, ValueError) as exc:
        raise DisplayError("マスクをNumPyのbool配列へ変換できません。") from exc
    if values.ndim != 2 or values.shape != (canvas.height, canvas.width):
        raise DisplayError(
            f"マスク形状{values.shape}が画像サイズ{(canvas.height, canvas.width)}と一致しません。"
        )
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
