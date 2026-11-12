"""画像生成APIのネットワーク・GPU不要テスト。"""
from __future__ import annotations

import unittest
from unittest.mock import patch

from cvlesson.generation import ImageGenerator


class _FakeGenerator:
    def __init__(self, device):
        self.device = device

    def manual_seed(self, seed):
        self.seed = seed
        return self


class _FakeTorch:
    Generator = _FakeGenerator


class _FakePipeline:
    def __call__(self, **kwargs):
        self.kwargs = kwargs
        return type("Result", (), {"images": ["generated image"]})()


class GenerationTests(unittest.TestCase):
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
