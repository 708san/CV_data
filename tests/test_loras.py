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
            ["fluent_emoji_3d", "watercolor_sdxl", "pixel_art_sdxl", "thomas_cole_landscape"],
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
        self.assertIn("学習元データ: 未記載", item["rights_status"])
        self.assertEqual(item["trigger_words"], [])

    def test_added_models_have_use_case_rights_and_pinned_file_hashes(self):
        pixel = loras.model_info("pixel_art_sdxl")
        self.assertEqual(pixel["license"]["name"], "CreativeML Open RAIL++-M（SDXLから継承と配布元表示）")
        self.assertEqual(pixel["training_dataset"]["license"], "CC0（モデルカードの表示）")
        self.assertEqual(pixel["revision"], "85565b5401663e1277c70b51fd34a8b8c2b9e3f9")
        self.assertEqual(pixel["sha256"], "acbae146be564ea1bcbc65c233b374a30972249aea15c8a0bcf383983603c297")
        self.assertIn("単体の物体", pixel["capabilities_ja"])
        self.assertTrue(any("ゲーム" in example for example in pixel["use_examples_ja"]))

        landscape = loras.model_info("thomas_cole_landscape")
        self.assertEqual(landscape["license"]["name"], "MIT（LoRA重み。基盤モデルは別ライセンス）")
        self.assertEqual(landscape["revision"], "30373be8e89838dff2a4c6bfa2001d4188632695")
        self.assertEqual(landscape["sha256"], "6ad18bdf606c25be342c2acda1fbcd02ad669c40163f25027d886022b52bea8a")
        self.assertIn("画像ごとの出典記録は保持されていない", landscape["rights_note"])
        self.assertIn("風景油彩画", landscape["capabilities_ja"])
        self.assertGreaterEqual(len(landscape["use_examples_ja"]), 2)
        self.assertFalse(landscape["weights_included"])


if __name__ == "__main__":
    unittest.main()
