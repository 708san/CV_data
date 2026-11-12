"""LoRA素材カタログのネットワーク不要テスト。"""
from __future__ import annotations

import unittest

from cvlesson import loras


class LoraCatalogTests(unittest.TestCase):
    def test_student_catalog_does_not_publish_unreviewed_material(self):
        self.assertEqual(loras.list_available(), [])
        self.assertEqual(loras.list_preview()[0]["id"], "festival_icon_style")

    def test_preview_requires_explicit_permission(self):
        with self.assertRaisesRegex(loras.LoraError, "allow_preview"):
            loras.get("festival_icon_style")
        item = loras.get("festival_icon_style", allow_preview=True)
        self.assertEqual(item.trigger_words, ("universal_icon_style",))
        self.assertEqual(item.rights_status, "under_review")

    def test_registered_model_has_fixed_revision_and_checksum(self):
        models = loras.list_models()
        self.assertEqual(
            [item["id"] for item in models],
            ["fluent_emoji_3d", "watercolor_sdxl"],
        )
        item = loras.model_info("fluent_emoji_3d")
        self.assertEqual(item["license"]["name"], "MIT")
        self.assertEqual(item["revision"], "7ff36ef02e53e75a4ca3bd5bd326de3f30a41fba")
        self.assertEqual(len(item["sha256"]), 64)
        self.assertFalse(item["weights_included"])

    def test_watercolor_model_records_license_and_missing_training_data(self):
        item = loras.model_info("watercolor_sdxl")
        self.assertEqual(item["license"]["name"], "Apache-2.0")
        self.assertEqual(item["training_dataset"]["license"], "未記載")
        self.assertIn("学習元非記載", item["rights_status"])
        self.assertEqual(item["trigger_words"], [])


if __name__ == "__main__":
    unittest.main()
