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


if __name__ == "__main__":
    unittest.main()
