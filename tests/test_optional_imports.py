"""基本importで重い任意依存を読み込まないことを確認する。"""
from __future__ import annotations

import os
import subprocess
import sys
import unittest
from pathlib import Path


class OptionalImportTests(unittest.TestCase):
    def test_package_import_does_not_load_optional_frameworks(self):
        source_root = Path(__file__).resolve().parents[1] / "src"
        env = os.environ.copy()
        env["PYTHONPATH"] = os.pathsep.join(
            [str(source_root), env.get("PYTHONPATH", "")]
        ).rstrip(os.pathsep)
        script = """
import sys
import cvlesson
optional = (
    'torch', 'torchvision', 'pandas', 'PIL', 'matplotlib',
    'diffusers', 'transformers', 'huggingface_hub', 'paddle', 'paddleocr',
)
loaded = sorted(name for name in optional if name in sys.modules)
if loaded:
    raise SystemExit('unexpected optional imports: ' + ', '.join(loaded))
"""
        result = subprocess.run(
            [sys.executable, "-c", script],
            check=False,
            capture_output=True,
            text=True,
            env=env,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
