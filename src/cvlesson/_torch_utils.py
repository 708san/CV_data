"""Torch device aliases shared by the optional model features."""
from __future__ import annotations


def normalize_torch_device(device: str, *, allow_auto: bool = False) -> str:
    """Return a canonical CPU/MPS/CUDA device string.

    ``cuda`` is the common shorthand for the first CUDA device and is kept as
    a supported public spelling alongside ``cuda:0``.
    """
    if not isinstance(device, str):
        raise ValueError("deviceは文字列で指定してください。")
    if allow_auto and device == "auto":
        return device
    if device in {"cpu", "mps"}:
        return device
    if device == "cuda":
        return "cuda:0"
    if device.startswith("cuda:") and device[5:].isdigit():
        return device
    raise ValueError("deviceは'auto'、'cpu'、'cuda'、'cuda:0'などのCUDA表記、または'mps'で指定してください。")


def choose_torch_device(device: str, available: dict[str, bool]) -> tuple[str, bool]:
    """Resolve ``auto`` to a usable accelerator, returning (device, fallback)."""
    normalized = normalize_torch_device(device, allow_auto=True)
    if normalized != "auto":
        return normalized, False
    if available.get("cuda:0", False):
        return "cuda:0", False
    if available.get("mps", False):
        return "mps", False
    return "cpu", True


def cuda_device_aliases(device_count: int, available: bool) -> dict[str, bool]:
    """Build the public CUDA entries used by ``available_devices``."""
    devices = {"cuda": bool(available), "cuda:0": bool(available)}
    if available:
        for index in range(1, max(0, int(device_count))):
            devices[f"cuda:{index}"] = True
    return devices
