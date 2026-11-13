"""画像生成APIのネットワーク・GPU不要テスト。"""
from __future__ import annotations

import unittest
from unittest.mock import Mock, patch

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

    def test_explicit_generation_settings_are_passed_to_pipeline(self):
        pipeline = _FakePipeline()
        generator = ImageGenerator(pipeline, "text-to-image", "cpu", _FakeTorch)
        generator.generate(
            "a blue bicycle",
            negative_prompt="blurry",
            num_inference_steps=32,
            guidance_scale=6.5,
            seed=7,
            width=768,
            height=512,
            use_trigger=False,
        )
        self.assertEqual(pipeline.kwargs["prompt"], "a blue bicycle")
        self.assertEqual(pipeline.kwargs["negative_prompt"], "blurry")
        self.assertEqual(pipeline.kwargs["num_inference_steps"], 32)
        self.assertEqual(pipeline.kwargs["guidance_scale"], 6.5)
        self.assertEqual(pipeline.kwargs["width"], 768)
        self.assertEqual(pipeline.kwargs["height"], 512)
        self.assertEqual(pipeline.kwargs["generator"].seed, 7)

    def test_default_generation_settings_are_used(self):
        pipeline = _FakePipeline()
        generator = ImageGenerator(pipeline, "text-to-image", "cpu", _FakeTorch)
        generator.generate("a blue bicycle")
        self.assertEqual(pipeline.kwargs["num_inference_steps"], 25)
        self.assertEqual(pipeline.kwargs["guidance_scale"], 7.0)
        self.assertNotIn("generator", pipeline.kwargs)
        self.assertNotIn("width", pipeline.kwargs)
        self.assertNotIn("height", pipeline.kwargs)

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

    def test_invalid_settings_are_rejected_before_pipeline_call(self):
        invalid_settings = [
            ({"num_inference_steps": 0}, "num_inference_steps"),
            ({"num_inference_steps": 2.5}, "num_inference_steps"),
            ({"num_inference_steps": True}, "num_inference_steps"),
            ({"guidance_scale": -1}, "guidance_scale"),
            ({"guidance_scale": float("nan")}, "guidance_scale"),
            ({"guidance_scale": float("inf")}, "guidance_scale"),
            ({"strength": float("nan")}, "strength"),
            ({"strength": float("inf")}, "strength"),
            ({"seed": 1.5}, "seed"),
            ({"seed": True}, "seed"),
            ({"width": 0}, "width"),
            ({"width": 513}, "width"),
            ({"height": -8}, "height"),
            ({"height": True}, "height"),
            ({"negative_prompt": 12}, "negative_prompt"),
            ({"use_trigger": "yes"}, "use_trigger"),
        ]
        for settings, message in invalid_settings:
            with self.subTest(settings=settings):
                pipeline = Mock()
                generator = ImageGenerator(pipeline, "text-to-image", "cpu", _FakeTorch)
                with patch("cvlesson.generation._open_rgb_image") as open_image:
                    with self.assertRaisesRegex(ValueError, message):
                        generator.generate("テスト", **settings)
                pipeline.assert_not_called()
                open_image.assert_not_called()

    def test_boundary_generation_settings_reach_pipeline(self):
        pipeline = _FakePipeline()
        generator = ImageGenerator(pipeline, "image-to-image", "cpu", _FakeTorch)
        with patch("cvlesson.generation._open_rgb_image", return_value="rgb image"):
            generator.generate(
                "test", image="source.png", strength=0, guidance_scale=0,
                num_inference_steps=1, seed=-1, width=8, height=8,
            )
        self.assertEqual(pipeline.kwargs["strength"], 0)
        self.assertEqual(pipeline.kwargs["width"], 8)
        self.assertEqual(pipeline.kwargs["height"], 8)


if __name__ == "__main__":
    unittest.main()
