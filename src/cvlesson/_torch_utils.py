"""Torch device aliases shared by the optional model features."""
from __future__ import annotations


def normalize_torch_device(device: str, *, allow_auto: bool = False) -> str:
    """Validate a PyTorch device string without changing its meaning.

    ``cuda`` and ``cuda:0`` are both accepted, but are kept distinct because
    PyTorch uses ``cuda`` for the current CUDA device and ``cuda:0`` for the
    explicitly indexed first device.
    """
    if not isinstance(device, str):
        raise ValueError("deviceは文字列で指定してください。")
    if allow_auto and device == "auto":
        return device
    if device in {"cpu", "mps"}:
        return device
    if device == "cuda":
        return device
    if device.startswith("cuda:") and device[5:].isdigit():
        return device
    raise ValueError("deviceは'auto'、'cpu'、'cuda'（cuda:0も入力可）などのCUDA表記、または'mps'で指定してください。")


def choose_torch_device(device: str, available: dict[str, bool]) -> tuple[str, bool]:
    """Resolve ``auto`` to a usable accelerator, returning (device, fallback)."""
    normalized = normalize_torch_device(device, allow_auto=True)
    if normalized != "auto":
        return normalized, False
    if available.get("cuda", False) or available.get("cuda:0", False):
        return "cuda", False
    if available.get("mps", False):
        return "mps", False
    return "cpu", True


def cuda_device_aliases(device_count: int, available: bool) -> dict[str, bool]:
    """Build canonical CUDA entries used by ``available_devices``.

    Availability maps use ``cuda`` as the aggregate/current-device CUDA entry.
    ``cuda:0`` is accepted as an explicit input, but is not emitted as a
    duplicate first-device entry. Additional indexed devices remain visible.
    """
    devices = {"cuda": bool(available)}
    if available:
        for index in range(1, max(0, int(device_count))):
            devices[f"cuda:{index}"] = True
    return devices


def torch_device_available(device: str, available: dict[str, bool]) -> bool:
    """Check an explicit PyTorch device against a canonical availability map."""
    normalized = normalize_torch_device(device)
    if normalized in {"cpu", "mps", "cuda"}:
        return bool(available.get(normalized, False))
    if normalized == "cuda:0":
        return bool(available.get("cuda:0", available.get("cuda", False)))
    return bool(available.get(normalized, False))
