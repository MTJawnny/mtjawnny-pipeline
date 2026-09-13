#!/usr/bin/env python3
"""Read-only Objective-1 census for experiments/foundry_common.py.

Evidence tooling only. Uses `git ls-files` as the authoritative tracked-file
universe, parses Python imports/attribute uses with AST, records string-level
symbol references used by dynamic provider patterns, and separately records
non-Python/current-document textual references. It mutates nothing.
"""
from __future__ import annotations

import argparse
import ast
import csv
import json
import subprocess
from collections import defaultdict
from pathlib import Path

FC_MODULES = {"foundry_common", "experiments.foundry_common"}
TEXT_SUFFIXES = {
    ".py", ".md", ".txt", ".yaml", ".yml", ".json", ".toml", ".ini",
    ".cfg", ".sh", ".bash", ".zsh", ".fish", ".ps1", ".html", ".js",
    ".ts", ".tsx", ".jsx", ".csv",
}


def git(*args: str, cwd: Path) -> str:
    return subprocess.check_output(["git", *args], cwd=cwd, text=True)


def tracked_files(root: Path) -> list[str]:
    return [p for p in git("ls-files", "-z", cwd=root).split("\0") if p]


def module_surface(path: Path) -> dict[str, dict]:
    src = path.read_text(encoding="utf-8")
    tree = ast.parse(src, filename=str(path))
    out: dict[str, dict] = {}
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            out[node.name] = {"kind": "function", "line": node.lineno, "end_line": getattr(node, "end_lineno", node.lineno)}
        elif isinstance(node, ast.ClassDef):
            out[node.name] = {"kind": "class", "line": node.lineno, "end_line": getattr(node, "end_lineno", node.lineno)}
        elif isinstance(node, (ast.Assign, ast.AnnAssign)):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            for target in targets:
                if isinstance(target, ast.Name):
                    out[target.id] = {"kind": "constant_or_global", "line": node.lineno, "end_line": getattr(node, "end_lineno", node.lineno)}
    return out


def is_archive(path: str) -> bool:
    parts = Path(path).parts
    return "archive" in parts or "to-be-deleted" in parts


def consumer_scope(path: str) -> str:
    p = Path(path)
    s = path.replace("\\", "/")
    if is_archive(path):
        return "archive_history"
    if s.startswith("experiments/aq4_benchmark/"):
        return "aq4_frozen_benchmark"
    if s.startswith("tests/"):
        return "test_negative_control"
    if s.startswith(".claude/"):
        return "operator_command"
    if s.startswith("experiments/measure/"):
        return "reporter_census"
    if s.startswith("experiments/"):
        return "legacy_executable"
    if s.startswith("pipeline/"):
        return "pipeline_batch"
    if p.suffix == ".py":
        return "other_python"
    if s.startswith("docs/") or p.suffix in {".md", ".yaml", ".yml"}:
        return "document_contract_or_reference"
    return "other"


def caller_class(path: str, text: str) -> str:
    s = path.replace("\\", "/").lower()
    t = text.lower()
    if is_archive(path):
        return "historical/one-off"
    if s.startswith("experiments/aq4_benchmark/"):
        return "AQ4/frozen benchmark"
    if s.startswith("tests/"):
        return "test/negative control"
    if "authority" in s or "rclone" in s or "manifest" in s and "foundry" in s:
        return "authority/transport"
    if any(x in s for x in ("gate", "check", "lint", "audit", "guard")):
        return "gate/check"
    if any(x in s for x in ("report", "census", "measure", "probe", "visibility")):
        return "reporter/census"
    if any(x in s for x in ("codebook", "emit", "reconcile", "consolidate", "det_pass", "adapt_batch")) or any(x in t for x in ("write_codebook", "membership", "merge_assertion", "members")):
        return "codebook or membership mutation"
    if any(x in s for x in ("stage", "batch", "pipeline", "sweep")):
        return "pipeline/batch"
    if s.startswith(".claude/") or "argparse" in t or "if __name__" in t:
        return "operator/CLI"
    return "other"


class UseVisitor(ast.NodeVisitor):
    def __init__(self, surface: set[str]):
        self.surface = surface
        self.module_aliases: set[str] = set()
        self.from_aliases: dict[str, str] = {}
        self.refs: list[dict] = []
        self.dynamic_modules: list[dict] = []
        self.star_import = False

    def add(self, symbol: str, kind: str, node: ast.AST, detail: str = "") -> None:
        self.refs.append({
            "symbol": symbol,
            "reference_kind": kind,
            "line": getattr(node, "lineno", None),
            "detail": detail,
        })

    def visit_Import(self, node: ast.Import) -> None:
        for alias in node.names:
            if alias.name in FC_MODULES:
                bound = alias.asname or alias.name.split(".")[-1]
                self.module_aliases.add(bound)
                self.add("<module>", "import_module", node, f"{alias.name} as {bound}")
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        if node.module in FC_MODULES:
            for alias in node.names:
                if alias.name == "*":
                    self.star_import = True
                    self.add("*", "star_import", node)
                else:
                    bound = alias.asname or alias.name
                    self.from_aliases[bound] = alias.name
                    self.add(alias.name, "from_import", node, f"as {bound}")
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:
        # importlib.import_module("foundry_common") / __import__("foundry_common")
        fn = node.func
        dynamic = False
        if isinstance(fn, ast.Name) and fn.id == "__import__":
            dynamic = True
        elif isinstance(fn, ast.Attribute) and fn.attr == "import_module":
            dynamic = True
        if dynamic and node.args and isinstance(node.args[0], ast.Constant) and node.args[0].value in FC_MODULES:
            self.dynamic_modules.append({"line": node.lineno, "module": node.args[0].value})
            self.add("<module>", "dynamic_import", node, str(node.args[0].value))
        # getattr(fc, "symbol")
        if isinstance(fn, ast.Name) and fn.id == "getattr" and len(node.args) >= 2:
            obj, key = node.args[0], node.args[1]
            if isinstance(obj, ast.Name) and obj.id in self.module_aliases and isinstance(key, ast.Constant) and isinstance(key.value, str):
                self.add(key.value, "dynamic_getattr", node, f"provider={obj.id}")
        self.generic_visit(node)

    def visit_Attribute(self, node: ast.Attribute) -> None:
        if isinstance(node.value, ast.Name) and node.value.id in self.module_aliases:
            self.add(node.attr, "qualified_attribute", node, f"provider={node.value.id}")
        self.generic_visit(node)

    def visit_Name(self, node: ast.Name) -> None:
        if isinstance(node.ctx, ast.Load) and node.id in self.from_aliases:
            self.add(self.from_aliases[node.id], "from_import_use", node, f"bound={node.id}")
        self.generic_visit(node)

    def visit_Constant(self, node: ast.Constant) -> None:
        # Dynamic provider contracts (e.g. CardTextRules) name private symbols
        # by string. Restrict this to strings that are actual module-level names.
        if self.module_aliases and isinstance(node.value, str) and node.value in self.surface:
            self.add(node.value, "string_symbol_reference", node)
        self.generic_visit(node)


def parse_python(path: Path, rel: str, surface: set[str]) -> tuple[list[dict], str | None]:
    try:
        text = path.read_text(encoding="utf-8")
        tree = ast.parse(text, filename=rel)
    except (UnicodeDecodeError, SyntaxError) as exc:
        return [], f"{type(exc).__name__}: {exc}"
    v = UseVisitor(surface)
    v.visit(tree)
    # de-duplicate exact repeated visitor events while preserving line specificity
    seen = set()
    out = []
    for r in v.refs:
        key = (r["symbol"], r["reference_kind"], r["line"], r["detail"])
        if key not in seen:
            seen.add(key)
            out.append(r)
    return out, None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", required=True)
    ap.add_argument("--csv", required=True)
    args = ap.parse_args()

    root = Path(git("rev-parse", "--show-toplevel", cwd=Path.cwd()).strip())
    accepted = git("rev-parse", "HEAD", cwd=root).strip()
    tracked = tracked_files(root)
    fc_rel = "experiments/foundry_common.py"
    surface_info = module_surface(root / fc_rel)
    surface = set(surface_info)

    python_files = [p for p in tracked if p.endswith(".py")]
    matrix: dict[str, list[dict]] = {}
    parse_errors: dict[str, str] = {}
    for rel in python_files:
        refs, err = parse_python(root / rel, rel, surface)
        if err:
            parse_errors[rel] = err
        if refs:
            text = (root / rel).read_text(encoding="utf-8", errors="replace")
            matrix[rel] = refs

    # Literal references in every tracked text-like file, excluding the provider
    # itself. These expose docs/commands/subprocess contracts not represented as
    # Python imports. Archive is retained but separately classified.
    textual: list[dict] = []
    binary_or_ignored = []
    for rel in tracked:
        p = root / rel
        if rel == fc_rel or (p.suffix.lower() not in TEXT_SUFFIXES and p.name not in {"CLAUDE.md", "README", "Makefile"}):
            continue
        try:
            text = p.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            binary_or_ignored.append(rel)
            continue
        if "foundry_common" in text:
            lines = [i for i, line in enumerate(text.splitlines(), 1) if "foundry_common" in line]
            textual.append({
                "path": rel,
                "lines": lines,
                "archive": is_archive(rel),
                "scope": consumer_scope(rel),
                "caller_class": caller_class(rel, text),
            })

    importers = {}
    symbol_callers: dict[str, set[str]] = defaultdict(set)
    for rel, refs in sorted(matrix.items()):
        concrete = sorted({r["symbol"] for r in refs if r["symbol"] not in {"<module>", "*"}})
        has_import = any(r["reference_kind"] in {"import_module", "from_import", "star_import", "dynamic_import"} for r in refs)
        if has_import:
            text = (root / rel).read_text(encoding="utf-8", errors="replace")
            importers[rel] = {
                "symbols": concrete,
                "references": refs,
                "scope": consumer_scope(rel),
                "caller_class": caller_class(rel, text),
                "archive": is_archive(rel),
            }
            for sym in concrete:
                symbol_callers[sym].add(rel)

    externally_referenced = sorted(symbol_callers)
    symbols = []
    for name, info in sorted(surface_info.items(), key=lambda kv: (kv[1]["line"], kv[0])):
        callers = sorted(symbol_callers.get(name, set()))
        symbols.append({
            "symbol": name,
            **info,
            "direct_or_dynamic_callers": callers,
            "external_live": any(not is_archive(p) for p in callers),
            "private_name": name.startswith("_"),
        })

    # Independent tracked-universe cross-check: every on-disk Python file that
    # git knows about should be represented in the git-ls-files Python set.
    disk_py = sorted(str(p.relative_to(root)).replace("\\", "/") for p in root.rglob("*.py") if ".git" not in p.parts)
    tracked_py = sorted(python_files)
    disk_untracked_py = sorted(set(disk_py) - set(tracked_py))
    tracked_missing_on_disk = sorted(set(tracked_py) - set(disk_py))

    result = {
        "schema": "mtj-foundry-common-census/1",
        "accepted_head_measured": accepted,
        "provider": fc_rel,
        "methodology": {
            "tracked_universe": "git ls-files -z",
            "python_analysis": "AST import/from-import/module-qualified/getattr plus actual module-name string references",
            "text_analysis": "literal foundry_common across tracked text-like files",
            "archive_policy": "included in raw evidence, explicitly tagged; never counted as live solely by presence",
            "filesystem_crosscheck": "Path.rglob('*.py') compared against tracked Python set",
        },
        "counts": {
            "tracked_files": len(tracked),
            "tracked_python_files": len(python_files),
            "parsed_python_files": len(python_files) - len(parse_errors),
            "python_parse_errors": len(parse_errors),
            "foundry_common_importers_all": len(importers),
            "foundry_common_importers_outside_archive": sum(1 for p in importers if not is_archive(p)),
            "externally_referenced_surface_names_all": len(externally_referenced),
            "externally_referenced_surface_names_outside_archive": len({s for s, ps in symbol_callers.items() if any(not is_archive(p) for p in ps)}),
            "module_level_names_defined": len(surface_info),
            "tracked_textual_reference_files": len(textual),
            "tracked_textual_reference_files_outside_archive": sum(1 for r in textual if not r["archive"]),
            "disk_untracked_python_files": len(disk_untracked_py),
            "tracked_python_missing_on_disk": len(tracked_missing_on_disk),
        },
        "parse_errors": parse_errors,
        "disk_untracked_python_files": disk_untracked_py,
        "tracked_python_missing_on_disk": tracked_missing_on_disk,
        "symbols": symbols,
        "importers": importers,
        "textual_references": textual,
    }

    out_json = root / args.json
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    out_csv = root / args.csv
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    with out_csv.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["importer", "archive", "scope", "caller_class", "symbol", "reference_kinds", "lines"])
        for rel, rec in sorted(importers.items()):
            by_symbol: dict[str, list[dict]] = defaultdict(list)
            for ref in rec["references"]:
                if ref["symbol"] not in {"<module>", "*"}:
                    by_symbol[ref["symbol"]].append(ref)
            for sym, refs in sorted(by_symbol.items()):
                w.writerow([
                    rel,
                    rec["archive"],
                    rec["scope"],
                    rec["caller_class"],
                    sym,
                    ";".join(sorted({r["reference_kind"] for r in refs})),
                    ";".join(str(x) for x in sorted({r["line"] for r in refs if r["line"] is not None})),
                ])

    print(json.dumps(result["counts"], indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
