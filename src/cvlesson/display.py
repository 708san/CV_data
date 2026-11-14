"""画像とCV推論結果を重ねて表示・保存する補助機能。"""
from __future__ import annotations

import base64
from html import escape
import io
import math
from pathlib import Path
from typing import Any


class DisplayError(RuntimeError):
    """画像表示用の変換・描画で発生したエラー。"""


def render(image: Any, result: Any = None, *, mask_alpha: int = 110, show_labels: bool = True):
    """画像へ推論結果を描き、合成したRGBのPillow Imageを返す。

    ``result``にはOCRResult、Detectionのリスト、Segmentation、DetectedSegmentの
    リストを指定できます。``None``なら画像をRGBへ変換して返します。
    入力画像や推論結果は変更しません。
    """
    Image, ImageDraw, ImageFont = _pillow()
    if not isinstance(mask_alpha, int) or isinstance(mask_alpha, bool) or not 0 <= mask_alpha <= 255:
        raise ValueError("mask_alphaは0から255の整数で指定してください。")
    if not isinstance(show_labels, bool):
        raise ValueError("show_labelsはTrueまたはFalseで指定してください。")
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
                _draw_ocr_line(draw, line, font, canvas.size, show_label=show_labels)
        else:
            raise DisplayError(f"未対応の推論結果です: {type(item).__name__}")
    return canvas


def render_ocr_report(image: Any, result: Any, *, crop_padding: int = 8) -> str:
    """OCR結果を読み順の一覧と、折りたたみ式の行別画像で表示するHTMLへ変換する。

    OCRResultやOCRLine、to_dict()の内容は変更しません。返すHTMLは単体で埋め込め、
    画像部分はデータURIに含めるため外部通信を行いません。
    """
    Image, _, _ = _pillow()
    if not isinstance(crop_padding, int) or isinstance(crop_padding, bool) or crop_padding < 0:
        raise ValueError("crop_paddingは0以上の整数で指定してください。")
    if not hasattr(result, "lines"):
        raise DisplayError("resultにはOCRResultを指定してください。")
    canvas = _open_rgb(image, Image)
    lines = list(result.lines)
    styles = (
        "<style>",
        ".cvlesson-ocr{font-family:system-ui,sans-serif;max-width:900px;color:#202124}",
        ".cvlesson-ocr h3{margin:.2em 0 .7em}",
        ".cvlesson-ocr ol{padding-left:2.2em}",
        ".cvlesson-ocr li{padding:.55em .7em;margin:.4em 0;border:1px solid #dadce0;border-radius:8px}",
        ".cvlesson-ocr .full-text{white-space:pre-wrap;overflow-wrap:anywhere;line-height:1.65;margin:0;padding:1em;background:#f8f7f2;border:1px solid #e5e1d5;border-radius:8px;font-family:ui-monospace,monospace}",
        ".cvlesson-ocr .line-details{margin-top:1em;border-top:1px solid #dadce0;padding-top:.6em}",
        ".cvlesson-ocr .line-details>summary{cursor:pointer;color:#1769aa;font-weight:600}",
        ".cvlesson-ocr .text{font-size:1.05em;overflow-wrap:anywhere}",
        ".cvlesson-ocr .confidence{color:#5f6368;font-size:.9em;margin-left:.5em}",
        ".cvlesson-ocr details{margin-top:.35em}",
        ".cvlesson-ocr summary{cursor:pointer;color:#1769aa}",
        ".cvlesson-ocr img{display:block;max-width:100%;height:auto;margin:.6em 0;background:white}",
        ".cvlesson-ocr .empty{padding:.8em;background:#f8f9fa;border-radius:8px}",
        "</style>",
    )
    rows = []
    for index, line in enumerate(lines, start=1):
        text = escape(str(getattr(line, "text", "")))
        try:
            confidence = float(line.confidence)
        except (AttributeError, TypeError, ValueError):
            confidence_text = "信頼度の目安: 不明"
        else:
            confidence_text = (
                f"信頼度の目安: {confidence:.1%}"
                if math.isfinite(confidence)
                else "信頼度の目安: 不明"
            )
        crop = _ocr_line_crop_data_uri(canvas, line, crop_padding, Image)
        if crop is None:
            image_detail = "<small>この行の位置情報はありません。</small>"
        else:
            image_detail = (
                "<details><summary>画像の該当部分を見る</summary>"
                f'<img src="{crop}" alt="{text} の画像部分">'
                "</details>"
            )
        rows.append(
            "<li>"
            f'<span class="text">{text or "（空の読み取り結果）"}</span>'
            f'<span class="confidence">{confidence_text}</span>'
            f"{image_detail}</li>"
        )
    recognized_text = str(getattr(result, "text", "\n".join(
        str(getattr(line, "text", "")) for line in lines
    )))
    if recognized_text:
        content = f'<pre class="full-text">{escape(recognized_text)}</pre>'
    else:
        content = '<p class="empty">文字を検出できませんでした。</p>'
    if rows:
        content += (
            f'<details class="line-details"><summary>行ごとの詳細（{len(rows)}行）</summary>'
            + "<ol>" + "".join(rows) + "</ol></details>"
        )
    title = "読み取った全文"
    return (
        "<section class=\"cvlesson-ocr\">"
        + "".join(styles)
        + f"<h3>{title}</h3>{content}</section>"
    )


def show_ocr(image: Any, result: Any, *, crop_padding: int = 8) -> None:
    """OCR結果をNotebookに一覧表示する。表示後に暗黙表示される値は返さない。"""
    markup = render_ocr_report(image, result, crop_padding=crop_padding)
    try:
        from IPython.display import HTML, display as notebook_display
    except ImportError as exc:
        raise DisplayError(
            "show_ocr()にはIPythonが必要です。別アプリではrender_ocr_report()が返すHTML、"
            "またはresult.to_dict()を利用してください。"
        ) from exc
    notebook_display(HTML(markup))


def _ocr_line_crop_data_uri(image: Any, line: Any, padding: int, image_module: Any) -> str | None:
    try:
        points = tuple(tuple(float(value) for value in point) for point in line.polygon)
    except (AttributeError, TypeError, ValueError):
        return None
    if len(points) < 4 or any(len(point) != 2 for point in points):
        return None
    coords = [coordinate for point in points for coordinate in point]
    if not all(math.isfinite(value) for value in coords):
        return None
    width, height = image.size
    left = max(0, math.floor(min(point[0] for point in points)) - padding)
    top = max(0, math.floor(min(point[1] for point in points)) - padding)
    right = min(width, math.ceil(max(point[0] for point in points)) + padding)
    bottom = min(height, math.ceil(max(point[1] for point in points)) + padding)
    if right <= left or bottom <= top:
        return None
    snippet = image.crop((left, top, right, bottom))
    output = io.BytesIO()
    snippet.save(output, format="PNG")
    encoded = base64.b64encode(output.getvalue()).decode("ascii")
    return f"data:image/png;base64,{encoded}"

def show(image: Any, result: Any = None, *, mask_alpha: int = 110, show_labels: bool = True):
    """合成画像をNotebookまたは既定の画像ビューアで表示して返す。"""
    rendered = render(image, result, mask_alpha=mask_alpha, show_labels=show_labels)
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
    show_labels: bool = True,
) -> Path:
    """合成画像を指定先へ保存し、保存先Pathを返す。"""
    destination = Path(path).expanduser()
    destination.parent.mkdir(parents=True, exist_ok=True)
    rendered = render(image, result, mask_alpha=mask_alpha, show_labels=show_labels)
    rendered.save(destination)
    return destination


def _pillow():
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError as exc:
        raise DisplayError(
            "画像表示にはPillowが必要です。python -m pip install cv-data-lesson を実行してください。"
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


def _draw_ocr_line(
    draw: Any,
    line: Any,
    font: Any,
    size: tuple[int, int],
    *,
    show_label: bool = True,
) -> None:
    polygon = tuple(tuple(float(value) for value in point) for point in line.polygon)
    if len(polygon) < 4 or any(len(point) != 2 for point in polygon):
        raise DisplayError("OCR polygonは画像上の(x, y)座標を4点以上指定してください。")
    for x, y in polygon:
        if not (0 <= x <= size[0] and 0 <= y <= size[1]):
            raise DisplayError("OCR polygonが画像の範囲外です。")
    draw.polygon(polygon, outline=(0, 210, 255, 255), width=3)
    if show_label:
        _draw_label(
            draw,
            min(point[0] for point in polygon),
            min(point[1] for point in polygon),
            f"{line.text} ({float(line.confidence):.2f})",
            font,
        )


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


__all__ = ["DisplayError", "render", "render_ocr_report", "save", "show", "show_ocr"]
