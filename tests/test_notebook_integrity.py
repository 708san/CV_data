"""Catch common notebook editing errors without requiring Jupyter packages."""
from __future__ import annotations

import builtins
import json
import re
import shlex
import symtable
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NOTEBOOKS = ROOT / "notebooks"


def _source_lines(cell: dict) -> list[str]:
    return "".join(cell.get("source", [])).splitlines()


def _python_source(lines: list[str]) -> str:
    return "\n".join(
        line for line in lines
        if not line.lstrip().startswith(("%", "!"))
    )


class NotebookIntegrityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # `reference` contains an untouched source lesson, not a runnable CV notebook.
        cls.paths = sorted(
            path for path in NOTEBOOKS.rglob("*.ipynb")
            if "reference" not in path.relative_to(NOTEBOOKS).parts
        )

    def test_all_notebooks_are_valid_json(self):
        self.assertTrue(self.paths)
        for path in self.paths:
            with self.subTest(notebook=path.relative_to(ROOT)):
                json.loads(path.read_text(encoding="utf-8"))

    def test_code_cells_parse_and_global_names_exist_before_use(self):
        for path in self.paths:
            notebook = json.loads(path.read_text(encoding="utf-8"))
            defined_before: set[str] = set()
            for cell_number, cell in enumerate(notebook["cells"]):
                if cell.get("cell_type") != "code":
                    continue
                source = _python_source(_source_lines(cell))
                if not source.strip():
                    continue
                with self.subTest(notebook=path.relative_to(ROOT), cell=cell_number):
                    ast_table = symtable.symtable(source, str(path), "exec")
                    names_defined_here = {
                        symbol.get_name()
                        for symbol in ast_table.get_symbols()
                        if symbol.is_assigned() or symbol.is_imported()
                    }
                    global_references: set[str] = set()

                    def collect_globals(table):
                        for symbol in table.get_symbols():
                            if symbol.is_referenced() and symbol.is_global():
                                global_references.add(symbol.get_name())
                        for child in table.get_children():
                            collect_globals(child)

                    collect_globals(ast_table)
                    undefined = global_references - defined_before - names_defined_here - set(dir(builtins))
                    self.assertFalse(
                        undefined,
                        f"未定義の変数: {', '.join(sorted(undefined))}",
                    )
                    defined_before.update(names_defined_here)

    def test_install_magics_have_balanced_quotes_and_precede_imports(self):
        for path in self.paths:
            notebook = json.loads(path.read_text(encoding="utf-8"))
            pip_seen = False
            for cell_number, cell in enumerate(notebook["cells"]):
                if cell.get("cell_type") != "code":
                    continue
                for line in _source_lines(cell):
                    stripped = line.strip()
                    if stripped.startswith("%pip install "):
                        with self.subTest(notebook=path.relative_to(ROOT), cell=cell_number):
                            try:
                                shlex.split(stripped.removeprefix("%pip "))
                            except ValueError as exc:
                                self.fail(f"pip行の引用符が不正です: {exc}")
                        if "CV_data.git@" in stripped:
                            self.assertRegex(
                                stripped,
                                r"CV_data\.git@[0-9a-f]{40}(?:[\"']|\s|$)",
                                "GitHub install参照は40桁のcommit SHAで固定してください",
                            )
                        pip_seen = True
                    elif stripped.startswith(("from cvlesson ", "import cvlesson")):
                        self.assertTrue(
                            pip_seen,
                            f"cvlesson importより前にpip installがありません（cell {cell_number}）",
                        )

    def test_public_colab_smoke_notebooks_install_the_same_pypi_release(self):
        paths = [
            ROOT / "notebooks/cv/classification_v1.ipynb",
            *sorted((ROOT / "notebooks/colab").glob("*.ipynb")),
        ]
        self.assertTrue(paths)
        for path in paths:
            notebook = json.loads(path.read_text(encoding="utf-8"))
            install_lines = [
                line.strip()
                for cell in notebook["cells"] if cell.get("cell_type") == "code"
                for line in _source_lines(cell)
                if line.strip().startswith("%pip install") and "cv-data-lesson" in line
            ]
            with self.subTest(notebook=path.relative_to(ROOT)):
                self.assertTrue(install_lines, "公開PyPI版のinstall行がありません")
                self.assertTrue(
                    any("==0.1.0a8" in line for line in install_lines),
                    "Colab確認は対象PyPI版を固定してください",
                )
                self.assertFalse(
                    any("CV_data.git@" in line for line in install_lines),
                    "実際の配布wheelではなくGit checkoutをinstallしています",
                )

    def test_ocr_notebook_installs_cpu_backend_from_ocr_extra_only(self):
        notebook = json.loads((ROOT / "notebooks/colab/ocr_smoke_test.ipynb").read_text())
        code = "\n".join(
            "".join(cell.get("source", []))
            for cell in notebook["cells"] if cell.get("cell_type") == "code"
        )
        self.assertIn("cv-data-lesson[ocr]==0.1.0a8", code)
        self.assertNotIn("pip install paddlepaddle", code)
        self.assertIn("cv_display.show_ocr(image, result)", code)
        self.assertIn("result.to_dict()", code)

    def test_generation_notebook_only_generates_selected_lora_once(self):
        notebook = json.loads((ROOT / "notebooks/colab/generation_smoke_test.ipynb").read_text())
        code = "\n".join(
            "".join(cell.get("source", []))
            for cell in notebook["cells"] if cell.get("cell_type") == "code"
        )
        self.assertIn("LORA_ID =", code)
        self.assertIn("generated = generator.generate(PROMPT, **kwargs)", code)
        self.assertNotIn("for model_id, task, prompt in cases", code)


if __name__ == "__main__":
    unittest.main()
