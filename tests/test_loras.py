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


if __name__ == "__main__":
    unittest.main()
