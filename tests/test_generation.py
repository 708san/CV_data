"""画像生成APIのネットワーク・GPU不要テスト。"""
from __future__ import annotations

import unittest
import sys
import types
from unittest.mock import patch

from cvlesson import generation
from cvlesson.generation import ImageGenerator


class _FakeGenerator:
    def __init__(self, device):
        self.device = device

    def manual_seed(self, seed):
        self.seed = seed
        return self


class _FakeTorch:
    Generator = _FakeGenerator
    float16 = "float16"
    float32 = "float32"


class _FakePipeline:
    def __call__(self, **kwargs):
        self.kwargs = kwargs
        return type("Result", (), {"images": ["generated image"]})()


class GenerationTests(unittest.TestCase):
    def test_explicit_sdxl_loader_rejects_cpu(self):
        fake_diffusers = types.ModuleType("diffusers")
        with patch.dict(sys.modules, {"torch": _FakeTorch, "diffusers": fake_diffusers}), patch(
            "cvlesson.generation.available_devices",
            return_value={"cpu": True, "cuda": False, "cuda:0": False, "mps": False},
        ), self.assertRaisesRegex(generation.GenerationError, "SDXLはCPU実行"):
            generation.load(model="sdxl", device="cpu")

    def test_auto_sdxl_rejects_cpu_before_pipeline_download(self):
        class ForbiddenPipeline:
            @classmethod
            def from_pretrained(cls, *args, **kwargs):
                raise AssertionError("SDXL pipeline must not be downloaded on CPU")

        fake_diffusers = types.ModuleType("diffusers")
        fake_diffusers.DiffusionPipeline = ForbiddenPipeline
        fake_diffusers.AutoPipelineForImage2Image = ForbiddenPipeline
        fake_diffusers.AutoPipelineForText2Image = ForbiddenPipeline
        with patch.dict(sys.modules, {"torch": _FakeTorch, "diffusers": fake_diffusers}), patch(
            "cvlesson.generation.available_devices",
            return_value={"cpu": True, "cuda": False, "mps": False},
        ), self.assertRaisesRegex(generation.GenerationError, "SDXLはCPU実行"):
            generation.load(model="sdxl", device="auto", lora=None, local_files_only=True)

    def test_auto_cpu_rejects_lora_before_tiny_sd_download(self):
        class ForbiddenPipeline:
            @classmethod
            def from_pretrained(cls, *args, **kwargs):
                raise AssertionError("Tiny-SD must not be downloaded when LoRA is incompatible")

        fake_diffusers = types.ModuleType("diffusers")
        fake_diffusers.DiffusionPipeline = ForbiddenPipeline
        fake_diffusers.AutoPipelineForImage2Image = ForbiddenPipeline
        fake_diffusers.AutoPipelineForText2Image = ForbiddenPipeline
        with patch.dict(sys.modules, {"torch": _FakeTorch, "diffusers": fake_diffusers}), patch(
            "cvlesson.generation.available_devices",
            return_value={"cpu": True, "cuda": False, "mps": False},
        ), self.assertRaisesRegex(ValueError, "LoRA"):
            generation.load(model="auto", device="auto", lora="pixel_art_sdxl", local_files_only=True)

    def test_auto_cpu_rejects_image_to_image_before_tiny_sd_download(self):
        class ForbiddenPipeline:
            @classmethod
            def from_pretrained(cls, *args, **kwargs):
                raise AssertionError("Tiny-SD must not be downloaded for image-to-image")

        fake_diffusers = types.ModuleType("diffusers")
        fake_diffusers.DiffusionPipeline = ForbiddenPipeline
        fake_diffusers.AutoPipelineForImage2Image = ForbiddenPipeline
        fake_diffusers.AutoPipelineForText2Image = ForbiddenPipeline
        with patch.dict(sys.modules, {"torch": _FakeTorch, "diffusers": fake_diffusers}), patch(
            "cvlesson.generation.available_devices",
            return_value={"cpu": True, "cuda": False, "mps": False},
        ), self.assertRaisesRegex(ValueError, "text-to-image"):
            generation.load(task="image-to-image", model="auto", device="auto", lora=None, local_files_only=True)

    def test_auto_cpu_uses_tiny_sd_without_lora(self):
        calls = []

        class DiffusionPipeline:
            @classmethod
            def from_pretrained(cls, model_id, **kwargs):
                calls.append((model_id, kwargs))
                return _FakePipelineWithTo()

        fake_diffusers = types.ModuleType("diffusers")
        fake_diffusers.DiffusionPipeline = DiffusionPipeline
        fake_diffusers.AutoPipelineForImage2Image = DiffusionPipeline
        fake_diffusers.AutoPipelineForText2Image = DiffusionPipeline
        fake_torch = types.ModuleType("torch")
        fake_torch.Generator = _FakeGenerator
        fake_torch.float16 = "float16"
        fake_torch.float32 = "float32"
        with patch.dict(sys.modules, {"torch": fake_torch, "diffusers": fake_diffusers}), patch(
            "cvlesson.generation.available_devices",
            return_value={"cpu": True, "cuda": False, "cuda:0": False, "mps": False},
        ), self.assertWarnsRegex(RuntimeWarning, "Tiny-SD") as warning:
            generator = generation.load(device="auto", local_files_only=True)
        self.assertIn("Tiny-SD", str(warning.warning))
        self.assertEqual(generator.model, "tiny-sd")
        self.assertEqual(generator.device, "cpu")
        self.assertEqual(calls[0][0], generation._TINY_SD_ID)
        self.assertEqual(calls[0][1]["revision"], generation._TINY_SD_REVISION)

    def test_tiny_sd_rejects_lora_and_image_to_image(self):
        with self.assertRaisesRegex(ValueError, "LoRA"):
            generation.load(model="tiny-sd", device="cpu", lora="fluent_emoji_3d")
        with self.assertRaisesRegex(ValueError, "text-to-image"):
            generation.ImageGenerator(_FakePipeline(), "image-to-image", "cpu", _FakeTorch, model="tiny-sd").generate(
                "変換", image="source.png"
            )

    def test_text_to_image_adds_registered_trigger_and_seed(self):
        pipeline = _FakePipeline()
        generator = ImageGenerator(pipeline, "text-to-image", "cpu", _FakeTorch,
                                   ("msemj style",))
        self.assertEqual(generator.generate("a blue bicycle", seed=42), "generated image")
        self.assertEqual(pipeline.kwargs["prompt"], "msemj style, a blue bicycle")
        self.assertEqual(pipeline.kwargs["generator"].seed, 42)
        self.assertNotIn("image", pipeline.kwargs)

    def test_image_to_image_requires_image_and_passes_strength(self):
        pipeline = _FakePipeline()
        generator = ImageGenerator(pipeline, "image-to-image", "cpu", _FakeTorch)
        with self.assertRaisesRegex(ValueError, "変換元"):
            generator.generate("水彩画風にする")
        with patch("cvlesson.generation._open_rgb_image", return_value="rgb image"):
            generator.generate("水彩画風にする", image="source.png", strength=0.4)
        self.assertEqual(pipeline.kwargs["image"], "rgb image")
        self.assertEqual(pipeline.kwargs["strength"], 0.4)

    def test_invalid_image_to_image_strength_is_rejected(self):
        generator = ImageGenerator(_FakePipeline(), "image-to-image", "cpu", _FakeTorch)
        with patch("cvlesson.generation._open_rgb_image", return_value="rgb image"):
            with self.assertRaisesRegex(ValueError, "0から1"):
                generator.generate("変換", image="source.png", strength=1.2)


if __name__ == "__main__":
    unittest.main()


class _FakePipelineWithTo(_FakePipeline):
    def to(self, device):
        self.device = device
        return self
