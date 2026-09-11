"""The permanent MTG shapes substrate: what it owns, and what it may not.

S7 created `mtj_foundry.mtg.shapes` and `mtj_foundry.mtg.text_match` and moved
the reusable ability-shape, target-class, locality and text-matching semantics
into them. Four properties matter more than the move itself.

**R6 / B10 — the CR half may never reach the shapes half.** `find_home` and
`keyword_homes()` now live in `shapes/delivery.py`, which is the whole repair:
they consume `parse_delivery`, so putting them under `mtg/cr/**` IS the cycle.
Every edge in that seam was a FUNCTION-LOCAL import, so the check walks the
whole AST. With the edge gone, the legacy `_twin` cross-module-instance state
sync has no reason to exist and is deleted rather than carried.

**G4b — L2 stays domain-free, structurally.** No codebook/axis/membership/
status/authority/DET-governance behaviour, no operator or process residue, no
fixture or report composition may live under `mtg/`. The signature sets are
DERIVED at run time from the schema owner and from the corpus, never typed, and
every derivation halts rather than degrading. Thirteen accepted negative
controls distinguish real violations from harmless vocabulary in text.

**The explicit-context law (S6.R1, carried into S7).** A permanent module may
not infer a repository root or require a repository file at import. Everything
repository-owned — the CR edition, the grammar, the CR-check registry, the
card-text primitives, the corpus — arrives explicitly from a composition
boundary.

**One derivation, one owner.** `keyword_homes()` is the single owner of the
CR-class fallback that live source used to implement twice, and
`build_keyword_homes` consumes it rather than re-deciding it.
"""

from __future__ import annotations

import ast
import gzip
import inspect
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

from tests.refoundation.helpers import REPO_ROOT  # noqa: F401  (sets sys.path)

SRC = REPO_ROOT / "src"
MTG_PKG = SRC / "mtj_foundry" / "mtg"
SHAPES_PKG = MTG_PKG / "shapes"
CR_PKG = MTG_PKG / "cr"
EXPERIMENTS = REPO_ROOT / "experiments"
# S9: the Gate-2 guard owner. Five responsibilities this file tracks moved
# here from the two mixed legacy shells.
GATE2_GUARDS = REPO_ROOT / "tests" / "guards" / "gate2"
CODEBOOK_OWNER = SRC / "mtj_foundry" / "codebook.py"

# The legacy boundaries are imported by this suite to prove the substrate keeps
# working THROUGH them. They are loose scripts, so the tree has to be reachable
# -- the same bootstrap every other legacy consumer performs.
if str(EXPERIMENTS) not in sys.path:
    sys.path.insert(0, str(EXPERIMENTS))

S7_MODULES = ("shapes/__init__.py", "shapes/delivery.py", "shapes/locality.py",
              "shapes/target_classes.py", "text_match.py")


def modules(root: Path) -> list[Path]:
    return sorted(p for p in root.rglob("*.py"))


def referenced_modules(source: str) -> set[str]:
    """Every module named by an import ANYWHERE in the file, including inside a
    function body. The seam's real edges were all deferred imports."""
    out = set()
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.Import):
            out |= {a.name for a in node.names}
        elif isinstance(node, ast.ImportFrom) and not node.level:
            out.add(node.module or "")
            out |= {f"{node.module}.{a.name}" for a in node.names}
    return out


def executable(node: ast.AST) -> ast.AST:
    """`node` with its docstring removed.

    G4b is defined over EXECUTABLE behaviour. A module whose prose explains the
    rejected shape must not be scored as having it -- the repository has been
    bitten by a substring check reading documentation as code twice already.
    """
    stripped = ast.Module(body=[], type_ignores=[])
    body = list(getattr(node, "body", []))
    if body and isinstance(body[0], ast.Expr) and \
            isinstance(body[0].value, ast.Constant) and \
            isinstance(body[0].value.value, str):
        body = body[1:]
    stripped.body = body
    return stripped


def executable_source(path: Path) -> str:
    """`path`'s source with EVERY docstring removed, re-rendered from the AST.

    A document is an API in this repository, and a guard that reads prose as
    code is its own defect class: this module's docstrings explain the `_twin`
    workaround and the rejected root shape by name, and a raw substring scan
    scores the explanation as the thing. Comments vanish with the AST; the
    docstrings have to be taken out by hand.
    """
    tree = ast.parse(path.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        body = getattr(node, "body", None)
        if not isinstance(body, list) or not body:
            continue
        if not isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef,
                                 ast.AsyncFunctionDef)):
            continue
        first = body[0]
        if isinstance(first, ast.Expr) and isinstance(first.value, ast.Constant) \
                and isinstance(first.value.value, str):
            node.body = body[1:] or [ast.Pass()]
    return ast.unparse(tree)


# ---------------------------------------------------------------------------
# G4b — the derived signature sets. Never typed; every derivation halts.
# ---------------------------------------------------------------------------

VALUE_CONSTANTS = ("AXIS_STATUSES", "CLASSES", "EVIDENCE_STATUSES", "LANES",
                   "TIERS", "SCHEMA_V1", "SCHEMA_V2", "DET_SOURCE_REF_PREFIX")
READ_METHODS = {"get", "setdefault", "pop"}

# CONTENT anchors, not counts. A count cannot see a substitution.
SCHEMA_KEY_ANCHORS = {"axes", "members", "assertions", "status", "locality"}
SCHEMA_VALUE_ANCHORS = {"active", "killed", "merged", "deferred", "quoted",
                        "foundry-codebook/2"}
CARD_KEY_ANCHORS = {"oracle_id", "oracle_text", "type_line", "card_faces",
                    "name", "legalities"}


class G4bDerivationError(RuntimeError):
    """A signature derivation that degraded instead of failing loudly."""


def key_reads(tree: ast.AST) -> list[tuple]:
    """[(key, node)] — every mapping-key READ in `tree`."""
    out = []
    for n in ast.walk(tree):
        if isinstance(n, ast.Subscript) and isinstance(n.slice, ast.Constant) \
                and isinstance(n.slice.value, str):
            out.append((n.slice.value, n))
        elif isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) \
                and n.func.attr in READ_METHODS and n.args \
                and isinstance(n.args[0], ast.Constant) \
                and isinstance(n.args[0].value, str):
            out.append((n.args[0].value, n))
        elif isinstance(n, ast.Compare) and len(n.ops) == 1 \
                and isinstance(n.ops[0], ast.In) \
                and isinstance(n.left, ast.Constant) \
                and isinstance(n.left.value, str):
            out.append((n.left.value, n))
    return out


def derive_schema_keys(tree: ast.AST) -> set:
    out = {k for k, _ in key_reads(tree)}
    missing = sorted(SCHEMA_KEY_ANCHORS - out)
    if missing:
        raise G4bDerivationError(
            f"the codebook schema owner no longer reads {missing}. The G4b key "
            f"derivation has degraded; fix the derivation, never fall back to a "
            f"typed list.")
    return out


def derive_schema_values(tree: ast.AST) -> set:
    vals = set()
    seen = set()
    for n in tree.body:
        if not isinstance(n, ast.Assign):
            continue
        names = {t.id for t in n.targets if isinstance(t, ast.Name)}
        hit = names & set(VALUE_CONSTANTS)
        if not hit:
            continue
        seen |= hit
        for c in ast.walk(n.value):
            if isinstance(c, ast.Constant) and isinstance(c.value, str):
                vals.add(c.value)
    missing = sorted(set(VALUE_CONSTANTS) - seen)
    if missing:
        raise G4bDerivationError(
            f"closed value vocabularies {missing} are gone from the codebook "
            f"schema owner; the G4b value derivation has degraded.")
    if SCHEMA_VALUE_ANCHORS - vals:
        raise G4bDerivationError(
            f"G4b value derivation lost {sorted(SCHEMA_VALUE_ANCHORS - vals)}")
    return vals


def derive_container_keys(tree: ast.AST) -> set:
    """Schema keys the OWNER ITSELF traverses as a container of objects.

    A key read is a CONTAINER read when its value is iterated, comprehended,
    subscripted again, or bound to a name that then is. Four keys qualify, and
    they are the only ones sufficient on their own to fail B3'-1 -- which is
    what keeps the gate off ordinary words like `status` or `quote`.
    """
    parents = {}
    for n in ast.walk(tree):
        for c in ast.iter_child_nodes(n):
            parents[id(c)] = n

    def traversed(node) -> bool:
        p = parents.get(id(node))
        if p is None:
            return False
        if isinstance(p, ast.Subscript) and p.value is node:
            return True
        if isinstance(p, ast.For) and p.iter is node:
            return True
        if isinstance(p, ast.comprehension) and p.iter is node:
            return True
        if isinstance(p, ast.Attribute) and p.attr in ("items", "values", "keys"):
            return True
        return False

    bound = {}
    for key, node in key_reads(tree):
        p = parents.get(id(node))
        if isinstance(p, ast.Assign):
            for t in p.targets:
                if isinstance(t, ast.Name):
                    bound.setdefault(t.id, set()).add(key)

    out = {key for key, node in key_reads(tree) if traversed(node)}
    for n in ast.walk(tree):
        if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Load) \
                and n.id in bound and traversed(n):
            out |= bound[n.id]
    if not {"axes", "members", "assertions"} <= out:
        raise G4bDerivationError(
            f"the container derivation lost a traversal anchor; got {sorted(out)}")
    return out


def derive_card_keys(corpus: Path) -> set:
    keys, records = set(), 0

    def walk(o):
        if isinstance(o, dict):
            for k, v in o.items():
                keys.add(k)
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)

    with gzip.open(corpus, "rt", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                walk(json.loads(line))
                records += 1
    if records < 30000 or not CARD_KEY_ANCHORS <= keys:
        raise G4bDerivationError(
            f"card-key closure truncated: {records} records, missing "
            f"{sorted(CARD_KEY_ANCHORS - keys)}")
    return keys


# ---------------------------------------------------------------------------
# G4b — the checker itself, per function, over the executable AST.
# ---------------------------------------------------------------------------

B1_PACKAGES = ("mtj_foundry.codebook", "mtj_foundry.codebook_store",
               "mtj_foundry.evidence", "mtj_foundry.thesaurus", "mtj_foundry.ops",
               "mtj_foundry.products", "mtj_foundry.runtime")
B1_TREES = ("tests", "benchmarks", "archive")
B2_PROPERTIES = ("legacy_codebook_json", "codebook_authority_selector",
                 "legacy_ruling_registry_json")
B2_LITERALS = ("codebook.json", "codebook-authority.json", "ruling_registry.json")
B4_LATTICE_KEYS = ("lattice", "corpus_hits", "corpus_hits_at_ratification",
                   "ratified_total", "membership_floor")
B5_CALLS = ("build_assertion", "merge_assertion", "remove_det_assertions",
            "write_atomic")
B8_IO_CALLS = ("print", "input")
B8_ARGV = ("ArgumentParser", "add_argument", "parse_args")
# PATH-SHAPED writes only. `str.replace` and `json.dumps` are not file I/O, and
# a clause that cannot tell them apart fires on every text helper in L2 -- it
# did, on the ACCEPTED S6 tree, which is how this was caught. The two
# module-qualified forms are matched by their receiver instead.
B8_WRITES = ("write_text", "write_bytes", "write_json",
             "mkdir", "unlink", "rename", "touch")
B8_QUALIFIED_WRITES = {("os", "replace"), ("shutil", "move"), ("shutil", "copy"),
                       ("json", "dump"), ("os", "remove"), ("os", "rename"),
                       ("os", "makedirs")}


class G4b:
    """The structural gate, run over an arbitrary permanent-package root.

    Taking the root as an argument is what makes the thirteen negative controls
    possible: each injects a behaviour into a COPY of the real tree and re-runs
    the same shipped checker, so a control can never pass because the checker
    was a different one.
    """

    def __init__(self, mtg_root: Path, schema_keys: set, schema_values: set,
                 container: set):
        self.root = mtg_root
        self.schema_keys = schema_keys
        self.schema_values = schema_values
        self.container = container

    # -- helpers ----------------------------------------------------------
    @staticmethod
    def _functions(tree):
        return [n for n in ast.walk(tree)
                if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]

    @staticmethod
    def _calls(node):
        out = set()
        for n in ast.walk(node):
            if not isinstance(n, ast.Call):
                continue
            if isinstance(n.func, ast.Name):
                out.add(n.func.id)
            elif isinstance(n.func, ast.Attribute):
                out.add(n.func.attr)
        return out

    @staticmethod
    def _depth(node, parents) -> int:
        """How many chained key reads stand between `node` and its base."""
        depth, cur = 1, node
        while True:
            p = parents.get(id(cur))
            if isinstance(p, ast.Subscript) and p.value is cur:
                depth += 1
                cur = p
                continue
            if isinstance(p, ast.Attribute) and p.attr in READ_METHODS:
                call = parents.get(id(p))
                if isinstance(call, ast.Call) and call.func is p:
                    depth += 1
                    cur = call
                    continue
            break
        return depth

    # -- the clauses ------------------------------------------------------
    def _module_findings(self, path: Path, tree: ast.AST) -> list:
        found = []
        for mod in referenced_modules(path.read_text(encoding="utf-8")):
            top = mod.split(".")[0]
            if mod.startswith(B1_PACKAGES) or top in B1_TREES \
                    or top in {"experiments", "tier_engine", "pipeline"} \
                    or top.startswith("foundry_"):
                found.append((path.name, "B1", mod))
        return found

    def _function_findings(self, path: Path, fn) -> list:
        found = []
        body = executable(fn)
        parents = {}
        for n in ast.walk(body):
            for c in ast.iter_child_nodes(n):
                parents[id(c)] = n
        calls = self._calls(body)
        reads = key_reads(body)
        read_keys = {k for k, _ in reads}

        # B2 -- the codebook/authority artifacts, by property or by literal.
        for n in ast.walk(body):
            if isinstance(n, ast.Attribute) and n.attr in B2_PROPERTIES:
                found.append((path.name, "B2", f"{fn.name}: .{n.attr}"))
            if isinstance(n, ast.Constant) and isinstance(n.value, str) \
                    and n.value in B2_LITERALS:
                found.append((path.name, "B2", f"{fn.name}: {n.value!r}"))

        # B3'-1 -- a key in EXCLUSIVE n CONTAINER is sufficient on its own.
        for key, _node in reads:
            if key in self.container:
                found.append((path.name, "B3'-1", f"{fn.name}: [{key!r}]"))

        # B3'-1c -- CONSTRUCTING such a key is B5's mirror, made mechanical.
        for n in ast.walk(body):
            if isinstance(n, ast.Dict):
                for k in n.keys:
                    if isinstance(k, ast.Constant) and k.value in self.container:
                        found.append((path.name, "B3'-1c",
                                      f"{fn.name}: {{{k.value!r}: ...}}"))

        # B3'-2 -- a schema key read AND a closed schema value compared, in one
        # function. Neither half alone is a finding, which is what keeps the
        # gate off ordinary words.
        if read_keys & self.schema_keys:
            for n in ast.walk(body):
                if isinstance(n, ast.Compare):
                    for c in [n.left, *n.comparators]:
                        if isinstance(c, ast.Constant) and \
                                c.value in self.schema_values:
                            found.append((path.name, "B3'-2",
                                          f"{fn.name}: == {c.value!r}"))
                if isinstance(n, ast.Compare) and any(
                        isinstance(o, (ast.In, ast.NotIn)) for o in n.ops):
                    if isinstance(n.left, ast.Constant) and \
                            n.left.value in self.schema_values:
                        found.append((path.name, "B3'-2",
                                      f"{fn.name}: {n.left.value!r} in ..."))

        # B3'-3 -- a schema key read at traversal depth >= 2.
        for key, node in reads:
            if key in self.schema_keys and self._depth(node, parents) >= 2:
                found.append((path.name, "B3'-3", f"{fn.name}: [{key!r}] deep"))

        # B4 -- DET-pattern governance.
        det = any(isinstance(n, ast.Constant) and isinstance(n.value, str)
                  and "det-patterns" in n.value for n in ast.walk(body))
        if det or (read_keys & set(B4_LATTICE_KEYS)):
            if read_keys & set(B4_LATTICE_KEYS) or any(
                    isinstance(n, ast.Constant) and n.value == "pre-filter"
                    for n in ast.walk(body)):
                found.append((path.name, "B4", fn.name))

        # B5 -- constructing or mutating a codebook axis or assertion.
        for c in calls & set(B5_CALLS):
            found.append((path.name, "B5", f"{fn.name}: {c}()"))

        # B7 -- composing `rule:` in an EXECUTABLE expression. A regex that only
        # MATCHES one is invisible here, which is NC-G4b-6's whole point.
        for n in ast.walk(body):
            if isinstance(n, ast.JoinedStr):
                for v in n.values:
                    if isinstance(v, ast.Constant) and \
                            isinstance(v.value, str) and "rule:" in v.value:
                        found.append((path.name, "B7", f"{fn.name}: f-string"))
            if isinstance(n, ast.BinOp) and isinstance(n.op, (ast.Add, ast.Mod)):
                for side in (n.left, n.right):
                    if isinstance(side, ast.Constant) and \
                            isinstance(side.value, str) and "rule:" in side.value:
                        found.append((path.name, "B7", f"{fn.name}: concat"))
            if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) \
                    and n.func.attr == "join" \
                    and isinstance(n.func.value, ast.Constant) \
                    and isinstance(n.func.value.value, str) \
                    and "rule:" in n.func.value.value:
                found.append((path.name, "B7", f"{fn.name}: join"))
        return found

    # -- B8 / B9, which are call-graph shaped -----------------------------
    def _direct_b8(self, fn) -> bool:
        body = executable(fn)
        calls = self._calls(body)
        if calls & set(B8_IO_CALLS) or calls & set(B8_ARGV):
            return True
        for n in ast.walk(body):
            if isinstance(n, ast.Attribute) and n.attr in ("exit", "argv"):
                return True
            if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute):
                if n.func.attr in B8_WRITES:
                    return True
                if isinstance(n.func.value, ast.Name) and \
                        (n.func.value.id, n.func.attr) in B8_QUALIFIED_WRITES:
                    return True
            if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) \
                    and n.func.id == "open":
                for a in list(n.args[1:]) + [k.value for k in n.keywords]:
                    if isinstance(a, ast.Constant) and isinstance(a.value, str) \
                            and set(a.value) & set("wa+"):
                        return True
        return False

    def run(self) -> dict:
        findings, defs, graph, direct = [], {}, {}, {}
        for path in modules(self.root):
            source = path.read_text(encoding="utf-8")
            tree = ast.parse(source)
            findings += self._module_findings(path, tree)
            for fn in self._functions(tree):
                qname = f"{path.name}:{fn.name}"
                defs[qname] = (path, fn)
                findings += self._function_findings(path, fn)
                direct[qname] = self._direct_b8(fn)
                graph[qname] = self._calls(executable(fn))

        # B8 is TRANSITIVE: a caller inherits its callee's I/O.
        by_name = {}
        for qname in defs:
            by_name.setdefault(qname.split(":", 1)[1], []).append(qname)
        b8 = {q for q, v in direct.items() if v}
        changed = True
        while changed:
            changed = False
            for qname, callees in graph.items():
                if qname in b8:
                    continue
                for callee in callees:
                    if any(t in b8 for t in by_name.get(callee, ())):
                        b8.add(qname)
                        changed = True
                        break
        for qname in sorted(b8):
            findings.append((qname.split(":", 1)[0], "B8", qname.split(":", 1)[1]))

        # B9 -- a fixture surface or report composer whose ONLY callers fail B8.
        callers = {q: set() for q in defs}
        for qname, callees in graph.items():
            for callee in callees:
                for target in by_name.get(callee, ()):
                    callers[target].add(qname)
        for qname, (path, fn) in defs.items():
            if not callers[qname]:
                continue                      # no caller at all is not B9
            if not all(c in b8 for c in callers[qname]):
                continue
            if self._is_fixture_or_report(fn):
                findings.append((path.name, "B9", fn.name))
        return {"findings": sorted(set(findings)),
                "functions": len(defs), "b8": sorted(b8)}

    @staticmethod
    def _is_fixture_or_report(fn) -> bool:
        """Returns a rendered document or a fixture TABLE.

        A formatted string consumed by another L2 function is NOT reporting --
        that is the accepted over-reach control. What counts is a return whose
        value is a multi-line rendered document, or a literal table of cases.
        """
        body = executable(fn)
        for n in ast.walk(body):
            if not isinstance(n, ast.Return) or n.value is None:
                continue
            v = n.value
            if isinstance(v, ast.Call) and isinstance(v.func, ast.Attribute) \
                    and v.func.attr == "join" \
                    and isinstance(v.func.value, ast.Constant) \
                    and "\n" in str(v.func.value.value):
                return True
            if isinstance(v, (ast.List, ast.Tuple)) and len(v.elts) >= 2 and \
                    all(isinstance(e, (ast.Tuple, ast.List)) for e in v.elts):
                return True
            if isinstance(v, ast.Name):
                for a in ast.walk(body):
                    if isinstance(a, ast.Assign) and any(
                            isinstance(t, ast.Name) and t.id == v.id
                            for t in a.targets) and \
                            isinstance(a.value, (ast.List, ast.Tuple)) and \
                            len(a.value.elts) >= 2 and all(
                                isinstance(e, (ast.Tuple, ast.List))
                                for e in a.value.elts):
                        return True
        return False


def gate(mtg_root: Path) -> dict:
    owner = ast.parse(CODEBOOK_OWNER.read_text(encoding="utf-8"))
    keys = derive_schema_keys(owner)
    values = derive_schema_values(owner)
    cards = derive_card_keys(
        REPO_ROOT / "data" / "raw" / "oracle-cards.jsonl.gz")
    container = (keys - cards) & derive_container_keys(owner)
    if container != {"axes", "members", "assertions", "locality"}:
        raise G4bDerivationError(
            f"EXCLUSIVE n CONTAINER is {sorted(container)}, not the four "
            f"measured container keys. The derivation moved; read it before "
            f"trusting any verdict computed with it.")
    return G4b(mtg_root, keys, values, container).run()


_SIGNATURES = None


def signatures() -> tuple:
    """The derived G4b signature sets, derived once per process.

    The card-key closure walks all 38,233 corpus records, so the thirteen
    negative controls would pay for it thirteen times over. Deriving once and
    reusing is a cost decision, never a strength decision: every control runs
    the SAME shipped checker with the SAME derived sets.
    """
    global _SIGNATURES
    if _SIGNATURES is None:
        owner = ast.parse(CODEBOOK_OWNER.read_text(encoding="utf-8"))
        keys = derive_schema_keys(owner)
        values = derive_schema_values(owner)
        cards = derive_card_keys(
            REPO_ROOT / "data" / "raw" / "oracle-cards.jsonl.gz")
        container = (keys - cards) & derive_container_keys(owner)
        if container != {"axes", "members", "assertions", "locality"}:
            raise G4bDerivationError(
                f"EXCLUSIVE n CONTAINER is {sorted(container)}, not the four "
                f"measured container keys. The derivation moved; read it "
                f"before trusting any verdict computed with it.")
        _SIGNATURES = (keys, values, cards, container)
    return _SIGNATURES


def gate(mtg_root: Path) -> dict:
    keys, values, _cards, container = signatures()
    return G4b(mtg_root, keys, values, container).run()


class _Injected:
    """A COPY of the permanent package with one behaviour injected.

    The controls never touch the real tree, so "restore byte-exact" is a
    property of the harness rather than a step that can be forgotten. The
    checker that grades them is the shipped one, reached through `gate()`.
    """

    def __init__(self, rel: str, snippet: str, replace: tuple = None):
        self.rel, self.snippet, self.replace = rel, snippet, replace

    def __enter__(self) -> Path:
        self.tmp = tempfile.mkdtemp(prefix="s7-nc-")
        dest = Path(self.tmp) / "mtj_foundry"
        shutil.copytree(SRC / "mtj_foundry", dest)
        target = dest / self.rel
        text = target.read_text(encoding="utf-8")
        if self.replace is not None:
            old, new = self.replace
            assert text.count(old) == 1, (self.rel, old[:60])
            text = text.replace(old, new)
        target.write_text(text + self.snippet, encoding="utf-8")
        return dest / "mtg"

    def __exit__(self, *exc):
        shutil.rmtree(self.tmp, ignore_errors=True)
        return False


def clauses(result: dict, only=None) -> list:
    return sorted(c for _f, c, _d in result["findings"]
                  if only is None or c in only)


# ---------------------------------------------------------------------------


class TestTheSignatureSetsAreDerivedAndPinnedByCONTENT(unittest.TestCase):
    """R5's B3' sets, re-derived here rather than copied forward.

    A count cannot see a substitution -- the CR 205 Oxford-comma lesson -- so
    every assertion below is content first and cardinality second."""

    @classmethod
    def setUpClass(cls):
        cls.keys, cls.values, cls.cards, cls.container = signatures()

    def test_the_schema_keys_come_from_the_schema_owner(self):
        self.assertTrue(SCHEMA_KEY_ANCHORS <= self.keys)
        self.assertEqual(len(self.keys), 17)

    def test_every_member_and_assertion_key_falls_out_of_the_derivation(self):
        """R5's own check on the derivation: the ordered key tuples the owner
        publishes must be a SUBSET of what the derivation found."""
        from mtj_foundry import codebook
        for name in ("MEMBER_KEY_ORDER", "ASSERTION_KEY_ORDER"):
            with self.subTest(constant=name):
                self.assertTrue(set(getattr(codebook, name)) <= self.keys)

    def test_the_closed_value_vocabularies_are_the_owners(self):
        self.assertTrue(SCHEMA_VALUE_ANCHORS <= self.values)
        self.assertEqual(len(self.values), 18)

    def test_the_card_key_closure_is_measured_over_the_live_corpus(self):
        self.assertTrue(CARD_KEY_ANCHORS <= self.cards)
        self.assertEqual(len(self.cards), 135)

    def test_oracle_id_is_the_ONLY_schema_key_that_is_also_a_card_key(self):
        """Which is the right answer: an `mtg` function keying on `oracle_id`
        is handling CARD data, and must not be scored as codebook behaviour."""
        self.assertEqual(sorted(self.keys & self.cards), ["oracle_id"])
        self.assertEqual(len(self.keys - self.cards), 16)

    def test_exactly_four_container_keys_and_they_are_the_measured_four(self):
        self.assertEqual(sorted(self.container),
                         ["assertions", "axes", "locality", "members"])

    def test_a_leaf_key_alone_is_never_sufficient(self):
        """The two-tier structure, asserted rather than described: `status`,
        `quote`, `tier` and friends are schema keys and NOT container keys, so
        reading one needs a closed schema value beside it (B3'-2) or a
        traversal (B3'-3) before anything fires."""
        for leaf in ("status", "quote", "tier", "class", "source_ref",
                     "corpus_ref", "schema", "evidence_status"):
            with self.subTest(key=leaf):
                self.assertIn(leaf, self.keys)
                self.assertNotIn(leaf, self.container)

    def test_the_derivation_halts_instead_of_degrading(self):
        """A lost anchor stops the gate. Shown, not asserted: the schema owner
        is replayed with its `axes` traversal removed."""
        owner = CODEBOOK_OWNER.read_text(encoding="utf-8")
        broken = owner.replace('"axes"', '"AXES_RENAMED"')
        self.assertNotEqual(broken, owner)
        with self.assertRaises(G4bDerivationError):
            derive_schema_keys(ast.parse(broken))


class TestG4bOverTheSliceSevenTree(unittest.TestCase):
    """The positive arm: the whole permanent MTG tree, all clauses, zero."""

    @classmethod
    def setUpClass(cls):
        cls.result = gate(MTG_PKG)

    def test_the_permanent_mtg_tree_produces_no_finding_at_all(self):
        self.assertEqual(self.result["findings"], [])

    def test_the_tree_actually_scanned_is_the_slice_seven_one(self):
        """A gate that scanned nothing also produces no finding."""
        self.assertGreaterEqual(self.result["functions"], 90)
        names = sorted(str(p.relative_to(MTG_PKG)) for p in modules(MTG_PKG))
        for rel in S7_MODULES:
            self.assertIn(rel, names)

    def test_no_permanent_mtg_function_carries_process_or_operator_residue(self):
        self.assertEqual(self.result["b8"], [])


class TestTheThirteenAcceptedNegativeControls(unittest.TestCase):
    """NC-G4b-1 .. NC-G4b-13, RUN rather than asserted.

    Five inject a forbidden behaviour and must go RED. Four inject codebook
    schema state through an ARGUMENT -- no import, no path read -- which is the
    hole B3' exists to close. Four are over-reach controls that must stay
    GREEN, because the gate is behavioural and not lexical."""

    def run_nc(self, rel, snippet, replace=None):
        with _Injected(rel, snippet, replace) as root:
            return gate(root)

    # -- 1..5: real violations ------------------------------------------
    def test_NC_G4b_1_a_codebook_import_in_an_mtg_module_is_RED(self):
        r = self.run_nc("mtg/shapes/delivery.py",
                        "\n\nfrom mtj_foundry import codebook  # NC-G4b-1\n")
        self.assertIn("B1", clauses(r))

    def test_NC_G4b_2_reading_the_codebook_path_property_is_RED(self):
        r = self.run_nc("mtg/shapes/delivery.py", '''

def _nc2(paths):                      # NC-G4b-2
    return paths.legacy_codebook_json.read_text(encoding="utf-8")
''')
        self.assertIn("B2", clauses(r))

    def test_NC_G4b_3_filtering_axes_on_active_is_RED(self):
        r = self.run_nc("mtg/shapes/delivery.py", '''

def _nc3(cb):                         # NC-G4b-3
    return [s for s, e in cb["axes"].items() if e["status"] == "active"]
''')
        self.assertTrue({"B3'-1", "B3'-2"} <= set(clauses(r)))

    def test_NC_G4b_4_the_membership_floor_read_is_RED(self):
        r = self.run_nc("mtg/shapes/target_classes.py", '''

def _nc4(path):                       # NC-G4b-4
    doc = json.loads(path.read_text(encoding="utf-8"))
    for p in doc.get("patterns", []):
        if isinstance(p.get("lattice"), dict):
            return p["lattice"]["stems"], p.get("corpus_hits")
    return None, None
''', replace=("import re\n", "import json\nimport re\n"))
        self.assertIn("B4", clauses(r))

    def test_NC_G4b_5_composing_a_rule_slug_is_RED(self):
        r = self.run_nc("mtg/shapes/target_classes.py", '''

def _nc5(stem, cls):                  # NC-G4b-5
    return f"rule:targeted-{stem}-{cls}"
''')
        self.assertIn("B7", clauses(r))

    # -- 6: over-reach ---------------------------------------------------
    def test_NC_G4b_6_prose_plus_a_matching_regex_stays_GREEN(self):
        r = self.run_nc("mtg/shapes/target_classes.py", '''

def _nc6(slug):                       # NC-G4b-6
    """This function mentions an axis, an axis slug and an axis status.

    The word `axis` in a docstring is not behaviour, and a regex that MATCHES
    `rule:` is not one that composes it.
    """
    return bool(re.match(r"rule:[a-z-]+", slug))
''')
        self.assertEqual(r["findings"], [])

    # -- 7..10: injected codebook state, no import and no path read ------
    def test_NC_G4b_7_an_injected_axis_status_comparison_is_RED(self):
        r = self.run_nc("mtg/shapes/locality.py", '''

def _nc7(axis):                       # NC-G4b-7
    return axis.get("status") == "active"
''')
        self.assertIn("B3'-2", clauses(r))

    def test_NC_G4b_8_an_injected_members_read_is_RED(self):
        r = self.run_nc("mtg/shapes/locality.py", '''

def _nc8(entry):                      # NC-G4b-8
    return entry["members"]
''')
        self.assertIn("B3'-1", clauses(r))

    def test_NC_G4b_9_a_nested_assertion_walk_is_RED_twice(self):
        r = self.run_nc("mtg/text_match.py", '''

def _nc9(entry):                      # NC-G4b-9
    out = []
    for m in entry["members"]:
        for a in m["assertions"]:
            out.append((a["class"], a["source_ref"]))
    return out
''')
        self.assertEqual(clauses(r, {"B3'-1"}).count("B3'-1"), 2)

    def test_NC_G4b_10_an_ALIASED_axes_walk_is_still_RED(self):
        r = self.run_nc("mtg/text_match.py", '''

def _nc10(doc):                       # NC-G4b-10
    axes = doc.get("axes")
    return [s for s, e in axes.items() if e["status"] != "killed"]
''')
        self.assertTrue({"B3'-1", "B3'-2"} <= set(clauses(r)))

    # -- 11..13: lookalikes that must stay GREEN -------------------------
    def test_NC_G4b_11_a_records_own_status_with_no_schema_value_stays_GREEN(self):
        r = self.run_nc("mtg/text_match.py", '''

def _nc11(rec):                       # NC-G4b-11
    return rec.get("status", "").upper()
''')
        self.assertEqual(r["findings"], [])

    def test_NC_G4b_12_reading_CARD_keys_stays_GREEN(self):
        r = self.run_nc("mtg/shapes/delivery.py", '''

def _nc12(card):                      # NC-G4b-12
    return card["oracle_id"], card["type_line"], card.get("card_faces", [])
''')
        self.assertEqual(r["findings"], [])

    def test_NC_G4b_13_CONSUMING_a_rule_string_stays_GREEN(self):
        r = self.run_nc("mtg/shapes/delivery.py", '''

def _nc13(slug):                      # NC-G4b-13
    return slug.split("rule:", 1)[-1]
''')
        self.assertEqual(r["findings"], [])


class TestTheB8AndB9Controls(unittest.TestCase):
    """Blocker 1's mechanical half, each control OBSERVED."""

    def run_nc(self, rel, snippet, replace=None):
        with _Injected(rel, snippet, replace) as root:
            return gate(root)

    def test_a_print_in_an_mtg_function_fails_B8(self):
        r = self.run_nc("mtg/shapes/locality.py", '''

def _b8_print(rows):
    print(rows)
''')
        self.assertIn("B8", clauses(r))

    def test_B8_is_TRANSITIVE_so_a_caller_inherits_its_callees_io(self):
        """The caller has no I/O of its own, which is exactly the shape a
        file-local scan calls clean."""
        r = self.run_nc("mtg/shapes/locality.py", '''

def _b8_writer(path, text):
    path.write_text(text, encoding="utf-8")


def _b8_caller(path, rows):
    return _b8_writer(path, str(rows))
''')
        b8 = {q.split(":", 1)[1] for q in r["b8"]}
        self.assertIn("_b8_writer", b8)
        self.assertIn("_b8_caller", b8)

    def test_a_fixture_table_reachable_only_from_an_io_function_fails_B9(self):
        r = self.run_nc("mtg/shapes/locality.py", '''

def _b9_fixtures():
    return [("a", 1), ("b", 2), ("c", 3)]


def _b9_report():
    print(_b9_fixtures())
''')
        self.assertIn("B9", clauses(r))

    def test_the_OVERREACH_control_a_formatted_string_consumed_at_L2_is_GREEN(self):
        """Composing text is not reporting. This function returns a formatted
        string and its only caller is another L2 function, so B9 must not fire
        -- and nothing else may fire either."""
        r = self.run_nc("mtg/shapes/locality.py", '''

def _l2_label(coord):
    return f"face {coord[0]} paragraph {coord[1]}"


def _l2_consumer(coord):
    return _norm(_l2_label(coord))
''')
        self.assertEqual(r["findings"], [])


# ---------------------------------------------------------------------------
# B10 — the one-way seam
# ---------------------------------------------------------------------------

SHAPES_SYMBOLS = {"parse_delivery", "parse_deliveries", "ratified_delivery_tokens",
                  "build_self_noun_rx", "build_keyword_homes", "keyword_homes",
                  "find_home", "deliveries_for_lines", "classify_clause",
                  "classes_for_card", "compute_full_hits", "matched_clause"}


def b10_findings(mtg_root: Path) -> list:
    """Every `mtg/cr/** -> mtg/shapes/**` edge, walked over the WHOLE AST.

    Imports AND names, because a deferred import binds a name and the call site
    is what makes the edge real -- and because every edge in this seam, in live
    source, was a function-local import."""
    out = []
    cr = mtg_root / "cr"
    for path in modules(cr):
        source = path.read_text(encoding="utf-8")
        for mod in referenced_modules(source):
            if "mtg.shapes" in mod or mod.endswith(".shapes") \
                    or "mtg.text_match" in mod:
                out.append(f"{path.name}: import {mod}")
        tree = executable(ast.parse(source))
        for node in ast.walk(tree):
            if isinstance(node, ast.Name) and node.id in SHAPES_SYMBOLS:
                out.append(f"{path.name}:{node.lineno} {node.id}")
            if isinstance(node, ast.Attribute) and node.attr in SHAPES_SYMBOLS:
                out.append(f"{path.name}:{node.lineno} .{node.attr}")
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) \
                    and node.name in SHAPES_SYMBOLS:
                out.append(f"{path.name}:{node.lineno} def {node.name}")
    return sorted(out)


class TestB10TheCrHalfNeverReachesTheShapesHalf(unittest.TestCase):
    """R6's repair, held open. The cycle was carried by ONE function; putting
    it back is the only way to recreate it, so that is what the controls do."""

    def test_the_permanent_cr_package_names_no_shapes_symbol_at_all(self):
        self.assertEqual(b10_findings(MTG_PKG), [])

    def test_B10_control_1_a_MODULE_LEVEL_cr_to_shapes_import_is_RED(self):
        with _Injected("mtg/cr/keywords.py",
                       "\n\nfrom mtj_foundry.mtg.shapes import delivery\n") as root:
            self.assertTrue(b10_findings(root))

    def test_B10_control_2_a_FUNCTION_LOCAL_cr_to_shapes_import_is_RED(self):
        """The exact shape live source used. A scan that reads only the import
        block sees none of these."""
        with _Injected("mtg/cr/keywords.py", '''

def _b10_deferred(kw, ratified):
    from mtj_foundry.mtg.shapes import delivery
    return delivery.find_home(kw, ratified)
''') as root:
            found = b10_findings(root)
            self.assertTrue(any("import" in f for f in found), found)
            self.assertTrue(any("find_home" in f for f in found), found)

    def test_B10_control_3_the_INTENDED_shapes_to_cr_direction_is_allowed(self):
        """The over-reach control. `shapes -> cr` is the accepted direction and
        must not trip anything -- it is already how delivery reaches the CR."""
        with _Injected("mtg/shapes/target_classes.py", '''

def _b10_allowed(path):
    from mtj_foundry.mtg.cr import keywords
    return keywords.type_vocabulary(path)
''') as root:
            self.assertEqual(b10_findings(root), [])
        source = (SHAPES_PKG / "delivery.py").read_text(encoding="utf-8")
        self.assertIn("mtj_foundry.mtg.cr", referenced_modules(source))

    def test_find_home_and_keyword_homes_landed_in_SHAPES_not_in_CR(self):
        from mtj_foundry.mtg.cr import keywords, edition, checks, keyword_buckets
        from mtj_foundry.mtg.shapes import delivery
        for module in (keywords, edition, checks, keyword_buckets):
            for name in ("find_home", "keyword_homes"):
                with self.subTest(module=module.__name__, symbol=name):
                    self.assertFalse(hasattr(module, name))
        self.assertTrue(callable(delivery.find_home))
        self.assertTrue(callable(delivery.keyword_homes))

    def test_the_twin_cross_instance_state_sync_is_GONE(self):
        """It existed only because the reverse edge could create a second module
        object. One owner means one instance, so the workaround is deleted
        rather than carried into the permanent design."""
        for path in modules(MTG_PKG) + [EXPERIMENTS / "foundry_shape_extractor.py",
                                        EXPERIMENTS / "foundry_cr702_classes.py"]:
            with self.subTest(module=path.name):
                self.assertNotIn("_twin", executable_source(path))

    def test_the_legacy_cr_module_no_longer_imports_the_shape_extractor_to_PARSE(self):
        """`foundry_cr702_classes` keeps `find_home` as a NAME, delegating into
        the permanent owner through the shapes boundary. What it must not have
        is a second implementation."""
        path = EXPERIMENTS / "foundry_cr702_classes.py"
        tree = ast.parse(path.read_text(encoding="utf-8"))
        fn = next(n for n in ast.walk(tree)
                  if isinstance(n, ast.FunctionDef) and n.name == "find_home")
        body = [x for x in fn.body if not (isinstance(x, ast.Expr)
                                           and isinstance(x.value, ast.Constant))]
        self.assertEqual(len(body), 2, ast.unparse(fn))
        self.assertEqual(ast.unparse(body[-1]), "return fse.find_home(kw, ratified)")
        # EXECUTABLE, not prose: the docstring above quotes the permanent
        # owner's reasoning, and a raw scan would read the quotation as a call.
        self.assertNotIn("parse_delivery", executable_source(path))


class TestTheShapesSubstrateDerivesNoRepositoryRoot(unittest.TestCase):
    """The S6.R1 law, carried into S7 and checked over the new modules.

    That defect passed every source-tree test because
    `<repo>/src/mtj_foundry/mtg/cr/edition.py` really is four parents below the
    repository -- and from a real site-packages install the SAME ancestry lands
    in the Python environment. The check below distinguishes USING a root from
    MANUFACTURING one."""

    ROOT_NAMES = {"ROOT", "_ROOT", "REPO_ROOT", "PROJECT_ROOT", "BASE_DIR"}
    NEW = [SHAPES_PKG / "delivery.py", SHAPES_PKG / "locality.py",
           SHAPES_PKG / "target_classes.py", MTG_PKG / "text_match.py",
           SHAPES_PKG / "__init__.py"]

    @staticmethod
    def root_derivations(path: Path) -> list:
        """Read from the AST, so a module's prose describing the rejected shape
        can neither satisfy nor trip this."""
        tree = ast.parse(path.read_text(encoding="utf-8"))
        out = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Attribute):
                if node.attr in {"parent", "parents", "resolve"} \
                        and "__file__" in ast.unparse(node):
                    out.append(f"{path.name}:{node.lineno} {ast.unparse(node)}")
                if node.attr in {"getcwd", "cwd", "discover_root", "rglob", "glob"}:
                    out.append(f"{path.name}:{node.lineno} .{node.attr}")
            if isinstance(node, ast.Constant) and node.value == ".git":
                out.append(f"{path.name}:{node.lineno} '.git'")
            targets = (node.targets if isinstance(node, ast.Assign)
                       else [node.target] if isinstance(node, ast.AnnAssign) else [])
            for t in targets:
                if isinstance(t, ast.Name) and \
                        t.id in TestTheShapesSubstrateDerivesNoRepositoryRoot.ROOT_NAMES:
                    out.append(f"{path.name}:{node.lineno} {t.id}")
        return out

    def test_no_new_module_derives_a_repository_root_in_any_form(self):
        offenders = []
        for path in self.NEW:
            offenders += self.root_derivations(path)
        self.assertEqual(offenders, [], f"root derivation in permanent MTG: {offenders}")

    def test_no_new_module_imports_the_layout_owner_at_all(self):
        """Using `ProjectPaths` is fine ONE LAYER UP. Down here it is how a
        second layout owner sneaks in: the library would still have to invent
        the root it passes."""
        for path in self.NEW:
            with self.subTest(module=path.name):
                self.assertNotIn("mtj_foundry.paths",
                                 referenced_modules(path.read_text(encoding="utf-8")))

    def test_no_new_module_imports_legacy_code(self):
        for path in self.NEW:
            for mod in referenced_modules(path.read_text(encoding="utf-8")):
                top = mod.split(".")[0]
                with self.subTest(module=path.name, imports=mod):
                    self.assertNotIn(top, {"experiments", "tier_engine", "pipeline"})
                    self.assertFalse(top.startswith("foundry_"))

    def test_the_shapes_substrate_imports_only_stdlib_and_the_layers_below(self):
        import sys
        allowed = ("mtj_foundry.mtg.cr", "mtj_foundry.mtg.shapes",
                   "mtj_foundry.infra")
        for path in self.NEW:
            for mod in referenced_modules(path.read_text(encoding="utf-8")):
                if not mod:
                    continue
                with self.subTest(module=path.name, imports=mod):
                    self.assertTrue(mod.split(".")[0] in sys.stdlib_module_names
                                    or mod.startswith(allowed), mod)

    def test_the_ROOT_DERIVATION_control_goes_RED_on_the_rejected_shape(self):
        """The exact shape the Manager rejected in S6, injected here."""
        with _Injected("mtg/shapes/delivery.py",
                       "\n\n_ROOT = Path(__file__).resolve().parents[4]\n") as root:
            path = root / "shapes" / "delivery.py"
            found = self.root_derivations(path)
            self.assertTrue(any("_ROOT" in f for f in found), found)
            self.assertTrue(any("parents" in f for f in found), found)
        # and the real file is untouched -- the control never ran against it
        self.assertEqual(self.root_derivations(SHAPES_PKG / "delivery.py"), [])

    def test_the_ROOT_SEARCH_control_goes_RED_too(self):
        with _Injected("mtg/shapes/locality.py", '''

def _nc_search(start):
    for parent in start.parents:
        if (parent / ".git").is_dir():
            return parent
    return None
''') as root:
            self.assertTrue(self.root_derivations(root / "shapes" / "locality.py"))


class TestEveryRepositoryOwnedInputArrivesEXPLICITLY(unittest.TestCase):
    """The positive half of the same law."""

    def test_no_permanent_entry_point_defaults_its_repository_input(self):
        from mtj_foundry.mtg.shapes import delivery, target_classes
        for fn in (delivery.ratified_delivery_tokens, delivery.cr_action_terms,
                   delivery.build_cr_enumerations, delivery.build_self_noun_rx,
                   delivery.build_landwalk_template, delivery.build_keyword_homes,
                   target_classes.permanent_types, target_classes.card_types,
                   target_classes.build_vocabulary):
            with self.subTest(fn=f"{fn.__module__}.{fn.__name__}"):
                for p in inspect.signature(fn).parameters.values():
                    self.assertIs(p.default, inspect.Parameter.empty, p.name)

    def test_the_corpus_arrives_as_an_argument_not_as_a_load(self):
        """`measure` and `residual_invariant` used to call the legacy corpus
        loader themselves, which is a repository read inside a library."""
        from mtj_foundry.mtg.shapes import target_classes
        for fn in (target_classes.measure, target_classes.residual_invariant,
                   target_classes.anchor_coverage):
            with self.subTest(fn=fn.__name__):
                self.assertIn("cards", inspect.signature(fn).parameters)

    def test_an_UNINSTALLED_substrate_REFUSES_rather_than_defaulting(self):
        """The refusal is loud. Run in a subprocess so this suite's own
        installed rules cannot make the check vacuous, and so reloading a
        module cannot leak an uninstalled state into a later test."""
        import subprocess
        import sys
        script = """
import mtj_foundry.mtg.shapes.delivery as d
import mtj_foundry.mtg.shapes.locality as l
import mtj_foundry.mtg.shapes.target_classes as t
out = []
for mod, err, call in ((d, d.ShapeError, lambda: d.ability_lines({})),
                       (l, l.LocalityError, lambda: l.units({})),
                       (t, t.LatticeError, lambda: list(t.clauses_for({}, "destroy")))):
    try:
        call()
        out.append(mod.__name__.rsplit(".", 1)[-1] + ":DEFAULTED")
    except err:
        out.append(mod.__name__.rsplit(".", 1)[-1] + ":REFUSED")
print(" ".join(out))
"""
        with tempfile.TemporaryDirectory() as tmp:
            res = subprocess.run([sys.executable, "-c", script], cwd=tmp,
                                 capture_output=True, text=True,
                                 env={"PYTHONPATH": str(SRC), "PATH": "/usr/bin:/bin"})
            self.assertEqual(res.returncode, 0, res.stderr)
            self.assertEqual(res.stdout.split(),
                             ["delivery:REFUSED", "locality:REFUSED",
                              "target_classes:REFUSED"])

    def test_the_boundaries_are_the_ones_that_supply_the_context(self):
        shape = (EXPERIMENTS / "foundry_shape_extractor.py").read_text(encoding="utf-8")
        self.assertIn("_delivery.use_card_text_rules(", shape)
        self.assertIn('GRAMMAR = fc.REPO_ROOT / "docs" / "CODEBOOK-NAMING-GRAMMAR.md"',
                      shape)
        self.assertIn('CR_CHECKS = fc.CONFIG_GENERATED / "cr-checks.json"', shape)
        loc = (EXPERIMENTS / "foundry_locality.py").read_text(encoding="utf-8")
        self.assertIn("_locality.use_card_face_rules(", loc)
        lat = (EXPERIMENTS / "foundry_object_lattice.py").read_text(encoding="utf-8")
        self.assertIn("_tc.use_clause_text_rules(", lat)
        self.assertIn("_tc.build_vocabulary(cr.text(), crc.type_vocabulary())", lat)

    def test_the_injected_rules_are_LATE_BOUND_to_the_provider(self):
        """A snapshot taken at install time would freeze a helper the boundary
        may legitimately replace -- and one ratified control does exactly that:
        the locality write-boundary fixture swaps the CARDNAME canonicaliser at
        run time to force a reflow. Captured VALUES made that control test
        nothing, and the full Gate-2 locality row is what caught it.

        Shown rather than argued: a provider is patched after install and the
        substrate follows."""
        from mtj_foundry.mtg.shapes import locality

        class Provider:
            def raw_faces(self, card):
                return [{"oracle_text": "first"}]

            def canonicalize_self_reference(self, raw, card):
                return raw

        provider = Provider()
        rules = locality.CardFaceRules(provider, {
            "raw_faces": "raw_faces",
            "canonicalize_self_reference": "canonicalize_self_reference"})
        self.assertEqual(rules.raw_faces({}), [{"oracle_text": "first"}])
        provider.raw_faces = lambda card: [{"oracle_text": "second"}]
        self.assertEqual(rules.raw_faces({}), [{"oracle_text": "second"}])

    def test_an_incomplete_or_wrong_provider_is_refused_at_INSTALL(self):
        from mtj_foundry.mtg.shapes import locality, delivery, target_classes
        with self.assertRaises(locality.LocalityError):
            locality.CardFaceRules(object(), {"raw_faces": "raw_faces"})
        with self.assertRaises(delivery.ShapeError):
            delivery.CardTextRules(object(), {})
        with self.assertRaises(target_classes.LatticeError):
            target_classes.ClauseTextRules(
                object(), {"det_scan_texts": "definitely_not_there"})

    def test_importing_every_new_module_needs_no_repository_file(self):
        """Import-time behaviour, checked by importing them in a subprocess with
        an empty cwd and no repository on the path."""
        import subprocess
        import sys
        with tempfile.TemporaryDirectory() as tmp:
            code = ("import mtj_foundry.mtg.shapes.delivery as d;"
                    "import mtj_foundry.mtg.shapes.locality as l;"
                    "import mtj_foundry.mtg.shapes.target_classes as t;"
                    "import mtj_foundry.mtg.text_match as m;"
                    "print(d.KEYWORD_HOME, l.OWNER, t.PERMANENT_TYPES,"
                    " m.compute_full_hits('x', {'a': ['x'], 'b': ['y']}))")
            out = subprocess.run([sys.executable, "-c", code], cwd=tmp,
                                 capture_output=True, text=True,
                                 env={"PYTHONPATH": str(SRC), "PATH": "/usr/bin:/bin"})
            self.assertEqual(out.returncode, 0, out.stderr)
            self.assertEqual(out.stdout.strip(), "None OWNER None ['a']")


class TestWhatSliceSevenPROMOTEDAndWhatItLEFT(unittest.TestCase):
    """The decomposition is by RESPONSIBILITY, not by file.

    Every name below is either accepted L2 substrate or accepted later-slice
    work, and the two lists are asserted as an absence and a presence rather
    than described."""

    PROMOTED = {
        "shapes/delivery.py": ("strip_reminder", "ability_word_prefix",
                               "build_self_noun_rx", "ratified_delivery_tokens",
                               "cr_action_terms", "ability_lines",
                               "deliveries_for_lines", "build_cr_enumerations",
                               "parse_delivery", "parse_deliveries", "scan",
                               "find_home", "keyword_homes",
                               "build_keyword_homes", "trigger_clause",
                               "landwalk_variant", "typecycling_variant",
                               "keyword_line_tokens", "keyword_form_tokens"),
        "shapes/target_classes.py": ("_split_cr_list", "permanent_types",
                                     "card_types", "_subtype_map", "names_type",
                                     "target_instruction", "target_noun_phrase",
                                     "_clause_re", "classify_clause",
                                     "clauses_for", "classes_for_card",
                                     "measure", "residual_invariant",
                                     "anchor_coverage"),
        "shapes/locality.py": ("_norm", "units", "resolve", "owning_header",
                               "mutually_exclusive", "_by_name"),
        "text_match.py": ("compute_full_hits", "matched_clause"),
    }

    # Accepted owners: codebook coverage (S11), operator tooling (S13), the
    # gate/test move (S9), DET governance (S11).
    LEFT_BEHIND = {
        "codebook_covered_actions", "cmd_gaps", "cmd_action", "cmd_rank",
        "cmd_homes", "cmd_report", "main",
        "slug_for", "_assert_vocabulary_agrees", "ratified_total",
        "assert_ratified_total", "baseline_metrics", "audit",
        "exclusivity_report", "_locality_of", "write_report", "fixtures",
        "validate_slug", "census", "schema_fixtures", "write_boundary_fixtures",
        "load_baseline_locality", "assert_ratchet_directions",
        "unaddressed_rows", "render_unaddressed_md", "_synthetic_codebook",
        "compute_special_hits", "load_axis_patterns", "expand_lattice_pattern",
        "lattice_axis_record", "quote_pattern_src", "cmd_apply",
        "cmd_generate_samples", "det_locality_owner",
    }

    def module_defs(self, rel: str) -> set:
        tree = ast.parse((MTG_PKG / rel).read_text(encoding="utf-8"))
        return {n.name for n in ast.walk(tree)
                if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))}

    def test_every_promoted_responsibility_landed_in_its_accepted_owner(self):
        for rel, names in self.PROMOTED.items():
            defs = self.module_defs(rel)
            for name in names:
                with self.subTest(module=rel, symbol=name):
                    self.assertIn(name, defs)

    def test_no_later_slice_responsibility_followed_it_down(self):
        everywhere = set()
        for path in modules(MTG_PKG):
            tree = ast.parse(path.read_text(encoding="utf-8"))
            everywhere |= {n.name for n in ast.walk(tree)
                           if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))}
        self.assertEqual(sorted(everywhere & self.LEFT_BEHIND), [])

    def test_the_later_owners_still_have_them(self):
        """The other half. A responsibility that was DELETED rather than left
        is a truth change, so the retained half is asserted too.

        S9 MOVED FIVE OF THESE AGAIN, and the guard follows them rather than
        dropping them. The lattice fixtures and the locality schema /
        write-boundary / ratchet surface are now owned by
        `tests/guards/gate2/`, so they are asserted THERE -- which keeps this
        test saying exactly what it always said: none of these responsibilities
        was deleted on the way past. What each shell still owns is unchanged
        and still asserted in place.
        """
        live = {
            EXPERIMENTS / "foundry_shape_extractor.py":
                ("codebook_covered_actions", "cmd_gaps", "cmd_action",
                 "cmd_rank", "main"),
            EXPERIMENTS / "foundry_object_lattice.py":
                ("slug_for", "_assert_vocabulary_agrees", "ratified_total",
                 "assert_ratified_total", "baseline_metrics", "audit",
                 "exclusivity_report", "_locality_of", "write_report",
                 "main"),
            GATE2_GUARDS / "test_object_lattice.py":              # S9
                ("fixtures", "main"),
            EXPERIMENTS / "foundry_locality.py":
                ("census", "unaddressed_rows", "render_unaddressed_md",
                 "cmd_report", "main"),
            GATE2_GUARDS / "test_locality.py":                    # S9
                ("fixtures", "schema_fixtures", "write_boundary_fixtures",
                 "load_baseline_locality", "assert_ratchet_directions",
                 "main"),
            EXPERIMENTS / "foundry_det_pass.py":
                ("compute_special_hits", "load_axis_patterns",
                 "expand_lattice_pattern", "lattice_axis_record",
                 "quote_pattern_src", "cmd_apply", "cmd_generate_samples",
                 "det_locality_owner", "main"),
            EXPERIMENTS / "foundry_cr702_classes.py": ("cmd_homes", "main"),
        }
        for path, names in live.items():
            tree = ast.parse(path.read_text(encoding="utf-8"))
            defs = {n.name for n in ast.walk(tree)
                    if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))}
            for name in names:
                with self.subTest(module=path.name, symbol=name):
                    self.assertIn(name, defs)

    def test_no_promoted_semantic_is_implemented_TWICE(self):
        """The shells delegate; they do not keep a second copy. Asserted over
        the EXECUTABLE source, because every one of these names is discussed in
        prose in the module that used to own it."""
        for path, names in (
                (EXPERIMENTS / "foundry_shape_extractor.py",
                 self.PROMOTED["shapes/delivery.py"]),
                (EXPERIMENTS / "foundry_object_lattice.py",
                 self.PROMOTED["shapes/target_classes.py"]),
                (EXPERIMENTS / "foundry_locality.py",
                 self.PROMOTED["shapes/locality.py"]),
                (EXPERIMENTS / "foundry_det_pass.py",
                 self.PROMOTED["text_match.py"])):
            tree = ast.parse(path.read_text(encoding="utf-8"))
            defs = {n.name for n in ast.walk(tree)
                    if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))}
            # A shell may keep a NAME as a thin boundary wrapper, but the
            # wrapper body must reach the permanent owner rather than restate
            # the derivation. Anything it still defines is checked for that.
            for name in sorted(defs & set(names)):
                fn = next(n for n in ast.walk(tree)
                          if isinstance(n, ast.FunctionDef) and n.name == name)
                src = ast.unparse(executable(fn))
                with self.subTest(module=path.name, symbol=name):
                    self.assertRegex(src, r"_delivery|_tc|_locality|_text_match|"
                                          r"_halting|fse\.|_keywords")

    def test_the_shells_keep_their_own_process_boundary(self):
        """A raised error that never becomes a halt is a truth change. Each
        shell re-establishes the historic `STOP — …` contract."""
        for path in (EXPERIMENTS / "foundry_shape_extractor.py",
                     EXPERIMENTS / "foundry_object_lattice.py",
                     EXPERIMENTS / "foundry_locality.py"):
            source = path.read_text(encoding="utf-8")
            with self.subTest(module=path.name):
                self.assertIn("def _halting(fn)", source)
                self.assertIn("fc.halt(str(exc))", source)

    def test_no_shell_DROPS_a_name_the_substrate_still_owns(self):
        """The defect this test exists for was shipped and caught by the full
        Gate-2 run, not by any narrower one: the locality shell bound its
        promoted names BY HAND and missed `_BULLET`, so the census raised
        `NameError` at run time. Every shell now re-exports mechanically, and
        this asserts the RESULT rather than the mechanism."""
        import foundry_shape_extractor as fse
        import foundry_locality as fl
        import foundry_object_lattice as fol
        from mtj_foundry.mtg.shapes import delivery, locality, target_classes
        for shell, owner in ((fse, delivery), (fl, locality), (fol, target_classes)):
            for name in vars(owner):
                if name.startswith("__") or name in ("annotations", "Any",
                                                     "Callable"):
                    continue
                if inspect.ismodule(getattr(owner, name)):
                    continue
                with self.subTest(shell=shell.__name__, name=name):
                    self.assertTrue(hasattr(shell, name))

    def test_every_shell_re_exports_MECHANICALLY(self):
        """A hand-written list is a list someone has to remember to extend."""
        for path in (EXPERIMENTS / "foundry_shape_extractor.py",
                     EXPERIMENTS / "foundry_locality.py",
                     EXPERIMENTS / "foundry_object_lattice.py"):
            source = path.read_text(encoding="utf-8")
            with self.subTest(module=path.name):
                self.assertIn("for _name, _obj in sorted(vars(", source)
                self.assertIn("globals()[_name] = _halting(_obj) "
                              "if inspect.isfunction(_obj) else _obj", source)

    def test_the_generator_boundary_is_wrapped_as_a_GENERATOR(self):
        """`deliveries_for_lines` yields. Wrapping it with a plain function
        would defer the halt to the first `next()` and let the exception escape
        the boundary uncaught -- which is losing a raised error."""
        source = (EXPERIMENTS / "foundry_shape_extractor.py").read_text(encoding="utf-8")
        self.assertIn("inspect.isgeneratorfunction(fn)", source)
        self.assertIn("yield from fn(*args, **kwargs)", source)


class TestTheKeywordHomeDerivationHasExactlyONEOwner(unittest.TestCase):
    """R6's §A.4 finding: live source implemented the CR-class fallback twice.

    The migration had to REMOVE the duplicate, not carry it."""

    @classmethod
    def setUpClass(cls):
        import foundry_shape_extractor as fse
        import foundry_common as fc
        from mtj_foundry.mtg.shapes import delivery
        cls.delivery = delivery
        cls.cards, _, _ = fc.load_corpus_gated()
        fse.build_self_noun_rx(cls.cards)
        cls.ratified = fse.ratified_delivery_tokens()
        fse.build_keyword_homes(cls.ratified)
        cls.fse = fse

    def test_membership_is_194_and_resolved_homes_are_151(self):
        """Two facts, not one. Asking a home map 'is this a keyword?' answered
        no for `awaken`, and `Awaken 4—{4}{W}` was read as a flavor word."""
        self.assertEqual(len(self.fse.CR_KEYWORD_NAMES), 194)
        self.assertEqual(len(self.fse.KEYWORD_HOME), 151)

    def test_the_two_fail_loudly_witnesses_hold(self):
        self.assertIn("battle cry", self.fse.KEYWORD_HOME)
        self.assertEqual(self.fse.KEYWORD_HOME["equip"], "activated")

    def test_build_keyword_homes_CONSUMES_the_single_derivation(self):
        tree = ast.parse((SHAPES_PKG / "delivery.py").read_text(encoding="utf-8"))
        fn = next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)
                  and n.name == "build_keyword_homes")
        calls = {n.func.id for n in ast.walk(fn)
                 if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)}
        self.assertIn("keyword_homes", calls)

    def test_the_CR_CLASS_FALLBACK_has_exactly_one_definition(self):
        """Structural: across the permanent package AND the legacy shells, the
        `["static"]` / `["spell"]` effective-class fallback appears in ONE
        function. It used to be in two, in the two modules on opposite ends of
        the cycle."""
        owners = []
        for path in modules(MTG_PKG) + [EXPERIMENTS / "foundry_cr702_classes.py",
                                        EXPERIMENTS / "foundry_shape_extractor.py"]:
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for fn in ast.walk(tree):
                if not isinstance(fn, ast.FunctionDef):
                    continue
                src = ast.unparse(executable(fn))
                if "['static']" in src and "['spell']" in src:
                    owners.append(f"{path.name}:{fn.name}")
        self.assertEqual(owners, ["delivery.py:keyword_homes"])

    def test_a_CR_spell_keyword_gets_a_HOME_and_NO_delivery_token(self):
        """The distinction that keeps the no-slot label out of the routing map.
        Collapsing them would put `(none — spell ability)` in `KEYWORD_HOME`
        and route corpus lines onto a token §2 does not ratify."""
        # ZERO MEMBERS IS A HYPOTHESIS, NOT AN ABSENCE -- the standing
        # `is-attacked-trigger` precedent. Measured against the 2026-08-07 CR,
        # NO CR 702 keyword currently has effective class `["spell"]`: the 194
        # split 91 by templated text, 60 by the `static` class fallback and 43
        # unresolved. So the arm is exercised on a CR-702-SHAPED record rather
        # than left untested because the live edition happens not to reach it.
        kws = self.delivery._keywords.load_702(self.fse.CR_PATH)
        live = self.delivery.keyword_homes(kws, self.ratified)
        self.assertEqual(
            [r["keyword"] for r in live.values()
             if r["home"] == self.delivery.NO_DELIVERY_HOME], [])

        synthetic = {9001: {"name": "Testspell",
                            "subrules": {"a": "Testspell is a spell ability."}}}
        rec = self.delivery.keyword_homes(synthetic, self.ratified)[9001]
        self.assertEqual(rec["home"], self.delivery.NO_DELIVERY_HOME)
        self.assertIsNone(rec["delivery"])
        self.assertEqual(rec["home_via"], self.delivery.CR_CLASS_VIA)
        self.assertNotIn(self.delivery.NO_DELIVERY_HOME,
                         set(self.fse.KEYWORD_HOME.values()))

    def test_the_live_split_is_91_by_text_plus_60_by_class_plus_43_unresolved(self):
        """The three arms, counted separately. `151 resolved` is a SUM, and a
        sum that stays right while its parts move is exactly the shape a count
        guard cannot see."""
        kws = self.delivery._keywords.load_702(self.fse.CR_PATH)
        recs = self.delivery.keyword_homes(kws, self.ratified)
        by_text = [r for r in recs.values()
                   if r["delivery"] and not r["home_via"]]
        by_class = [r for r in recs.values() if r["home_via"]]
        unresolved = [r for r in recs.values() if r["home"] is None]
        self.assertEqual(len(recs), 194)
        self.assertEqual((len(by_text), len(by_class), len(unresolved)),
                         (91, 60, 43))
        for r in unresolved:
            self.assertIsNotNone(r["unresolved_reason"])

    def test_the_map_built_from_the_records_IS_the_live_map(self):
        """Map equality, not cardinality: every key and every value."""
        kws = self.delivery._keywords.load_702(self.fse.CR_PATH)
        recs = self.delivery.keyword_homes(kws, self.ratified)
        rebuilt = {r["keyword"].lower(): r["delivery"]
                   for r in recs.values() if r["delivery"]}
        self.assertEqual(rebuilt, self.fse.KEYWORD_HOME)


class TestTheThreeStageBuildOrderIsPreserved(unittest.TestCase):
    """INERT UNTIL BUILT is a contract, not an accident. Stage 1 parses with no
    keyword map; stage 2 builds it; stage 3 becomes map-aware."""

    def test_stage_one_is_inert_by_construction(self):
        source = (SHAPES_PKG / "delivery.py").read_text(encoding="utf-8")
        tree = ast.parse(source)
        for name, guard in (("keyword_line_tokens", "KEYWORD_HOME"),
                            ("keyword_form_tokens", "KEYWORD_FORMS")):
            fn = next(n for n in ast.walk(tree)
                      if isinstance(n, ast.FunctionDef) and n.name == name)
            with self.subTest(fn=name):
                self.assertIn(guard, ast.unparse(executable(fn)))

    def test_stage_one_runs_with_the_map_unbuilt_and_stage_three_with_it(self):
        """Observed on the real substrate rather than argued: the same CR
        templated line parses on its own branches before the map exists."""
        import subprocess
        import sys
        script = """
import dataclasses, re, json
import mtj_foundry.mtg.shapes.delivery as d
class Rules:
    full_oracle_text = staticmethod(lambda c: c.get("oracle_text", ""))
    canonicalize_self_reference = staticmethod(lambda t, c: t)
    is_mode_line = staticmethod(lambda l: l.strip().startswith("*"))
    modal_header_re = re.compile("choose one")
    roll_instruction_re = re.compile("roll a d")
    die_row_re = re.compile("^[0-9]+ *[|]")
d.use_card_text_rules(d.CardTextRules(Rules(), {
    "full_oracle_text": "full_oracle_text",
    "canonicalize_self_reference": "canonicalize_self_reference",
    "is_mode_line": "is_mode_line",
    "modal_header_re": "modal_header_re",
    "roll_instruction_re": "roll_instruction_re",
    "die_row_re": "die_row_re"}))
print("KEYWORD_HOME", d.KEYWORD_HOME)
print("KEYWORD_FORMS", d.KEYWORD_FORMS)
print("line_tokens", d.keyword_line_tokens("flying"))
print("form_tokens", d.keyword_form_tokens("ward {2}"))
"""
        with tempfile.TemporaryDirectory() as tmp:
            res = subprocess.run([sys.executable, "-c", script], cwd=tmp,
                                 capture_output=True, text=True,
                                 env={"PYTHONPATH": str(SRC), "PATH": "/usr/bin:/bin"})
            self.assertEqual(res.returncode, 0, res.stderr)
            lines = res.stdout.split("\n")
            self.assertIn("KEYWORD_HOME None", lines)
            self.assertIn("KEYWORD_FORMS None", lines)
            self.assertIn("line_tokens []", lines)
            self.assertIn("form_tokens []", lines)

    def test_the_derived_state_list_matches_what_the_module_actually_rebinds(self):
        """`DERIVED_STATE` is what the legacy shell serves live. If a build step
        ever rebinds a name that is not on the list, the shell would hand out a
        stale copy of it -- the second-module hazard, one layer over."""
        from mtj_foundry.mtg.shapes import delivery
        tree = ast.parse((SHAPES_PKG / "delivery.py").read_text(encoding="utf-8"))
        rebound = set()
        for n in ast.walk(tree):
            if isinstance(n, ast.Global):
                rebound |= set(n.names)
        self.assertEqual(sorted(rebound - {"_CARD_TEXT_RULES"}),
                         sorted(delivery.DERIVED_STATE))

    def test_the_legacy_shell_serves_that_state_LIVE(self):
        import foundry_shape_extractor as fse
        from mtj_foundry.mtg.shapes import delivery
        for name in delivery.DERIVED_STATE:
            with self.subTest(name=name):
                self.assertIs(getattr(fse, name), getattr(delivery, name))
        self.assertNotIn("KEYWORD_HOME", vars(fse))

    def test_an_unknown_attribute_still_raises_AttributeError(self):
        import foundry_shape_extractor as fse
        with self.assertRaises(AttributeError):
            fse.definitely_not_a_shape_symbol


class TestTextMatchIsRegexAndTextAndNothingElse(unittest.TestCase):

    def test_it_imports_re_and_nothing_else(self):
        source = (MTG_PKG / "text_match.py").read_text(encoding="utf-8")
        self.assertEqual(
            sorted({m.split(".")[0] for m in referenced_modules(source)}),
            ["__future__", "re"])

    def test_it_owns_exactly_the_two_accepted_functions(self):
        tree = ast.parse((MTG_PKG / "text_match.py").read_text(encoding="utf-8"))
        self.assertEqual(
            sorted(n.name for n in ast.walk(tree)
                   if isinstance(n, ast.FunctionDef)),
            ["compute_full_hits", "matched_clause"])

    def test_it_knows_nothing_about_DET_records_or_the_codebook(self):
        src = executable_source(MTG_PKG / "text_match.py")
        for word in ("det-patterns", "resolved_slug", "lattice", "prefilter",
                     "pre-filter", "codebook", "rule:", "axis"):
            with self.subTest(word=word):
                self.assertNotIn(word, src)

    def test_the_legacy_pass_delegates_both_without_a_second_copy(self):
        source = (EXPERIMENTS / "foundry_det_pass.py").read_text(encoding="utf-8")
        self.assertIn("compute_full_hits = _text_match.compute_full_hits", source)
        self.assertIn("matched_clause = _text_match.matched_clause", source)
        tree = ast.parse(source)
        defs = [n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]
        self.assertNotIn("compute_full_hits", defs)
        self.assertNotIn("matched_clause", defs)

    def test_the_two_functions_behave(self):
        from mtj_foundry.mtg import text_match
        texts = {"b": ["nothing here"], "a": ["destroy target creature"],
                 "c": ["destroy target artifact"]}
        self.assertEqual(text_match.compute_full_hits(r"destroy target", texts),
                         ["a", "c"])
        import re as _re
        rx = _re.compile(r"destroy target \w+", _re.I)
        self.assertEqual(text_match.matched_clause(rx, texts["a"]),
                         "destroy target creature")
        self.assertIsNone(text_match.matched_clause(rx, texts["b"]))


# ---------------------------------------------------------------------------
# S7.R1 — the legacy import-time halt boundary
# ---------------------------------------------------------------------------

SHAPE_SHELL = EXPERIMENTS / "foundry_shape_extractor.py"

# The accepted-S6 failure contract, measured from an isolated byte-faithful copy
# of `27e32474099af8e333a037f2c9906e959adcea63` rather than remembered. `{root}`
# is the only thing that varies, because the message names an absolute path.
S6_MISSING_ARTIFACT = ("STOP — {root}/config/generated/cr-checks.json not found "
                       "— run experiments/foundry_cr_checks.py first")
S6_TRIGGER_ANCHOR_LOST = (
    "STOP — Trigger-verb vocabulary lost a known CR keyword action — refusing "
    "to run with a verb set that would silently extend trigger clauses into "
    "the effect half (CR 113.3c).")

# The rejected spelling, kept verbatim so the control below re-creates the real
# defect and not an approximation of it.
REJECTED_BOOTSTRAP = "_delivery.build_trigger_verbs(_delivery.cr_action_terms(CR_CHECKS))"
# The only names the shell may reach on the permanent module at MODULE level.
INSTALL_ONLY = {"use_card_text_rules", "CardTextRules"}
ACCEPTED_BOOTSTRAP = "build_trigger_verbs(cr_action_terms())"


class _ImportRoot:
    """A scratch repository root that is just big enough to IMPORT the shell.

    `src/`, `config/` and the three legacy modules the import chain touches --
    2.6 MB, so driving the failure path is cheap enough to do behaviourally
    rather than by reading source. The real tree is never mutated: every case
    edits this copy.
    """

    NEEDED = ("foundry_shape_extractor.py", "foundry_common.py", "foundry_cr.py")

    def __enter__(self) -> Path:
        # RESOLVED, because the message under test names an absolute path and
        # the boundary derives it through `Path(__file__).resolve()`. On macOS
        # `mkdtemp` hands back `/var/...` while `resolve()` yields
        # `/private/var/...`; comparing the unresolved form fails on a symlink,
        # not on a contract.
        self.tmp = Path(tempfile.mkdtemp(prefix="s7r1-import-")).resolve()
        shutil.copytree(SRC, self.tmp / "src")
        shutil.copytree(REPO_ROOT / "config", self.tmp / "config")
        (self.tmp / "experiments").mkdir()
        for name in self.NEEDED:
            shutil.copy2(EXPERIMENTS / name, self.tmp / "experiments" / name)
        return self.tmp

    def __exit__(self, *exc):
        shutil.rmtree(self.tmp, ignore_errors=True)
        return False


def import_the_shell(root: Path):
    """Import the legacy boundary in a subprocess. Returns (exit, out, err)."""
    import subprocess
    import sys
    res = subprocess.run(
        [sys.executable, "-c",
         "import sys; sys.path.insert(0, 'experiments');"
         " import foundry_shape_extractor as fse;"
         " print('IMPORT OK', len(fse.TRIGGER_VERB.pattern))"],
        cwd=root, capture_output=True, text=True,
        env={"PATH": "/usr/bin:/bin"})
    return res.returncode, res.stdout, res.stderr


def break_the_trigger_anchor(root: Path) -> None:
    """A STRUCTURALLY VALID registry that loses one required anchor.

    `build_trigger_verbs` requires `discard` among the derived keyword-action
    stems. Re-kinding that one term keeps the JSON parseable and the schema
    intact, so the failure that fires is the ratified vocabulary guard and not
    a JSON error -- which is the distinction the repair contract turns on.
    """
    path = root / "config" / "generated" / "cr-checks.json"
    doc = json.loads(path.read_text(encoding="utf-8"))
    hit = 0
    for term in doc["terms"]:
        if term["term"] == "discard" and term.get("kind") == "keyword-action":
            term["kind"] = "not-a-keyword-action"
            hit += 1
    if hit != 1:
        raise AssertionError(
            f"expected exactly one `discard` keyword-action term to re-kind, "
            f"found {hit}. The fixture no longer drives the guard it names.")
    path.write_text(json.dumps(doc, indent=1), encoding="utf-8")


class TestTheLegacyImportTimeHaltBoundary(unittest.TestCase):
    """S7.R1. The failure boundary is only observable on the failure path.

    The first S7 candidate built the trigger vocabulary at import by calling the
    PERMANENT functions directly:

        _delivery.build_trigger_verbs(_delivery.cr_action_terms(CR_CHECKS))

    Both of those RAISE. So a missing CR-check artifact, or a lost
    trigger-vocabulary anchor, stopped crossing this module's process boundary
    as `STOP — …` + exit 1 and escaped as an uncaught `ShapeError` traceback
    instead. The happy path was byte-identical, which is exactly why no corpus
    differential and no Gate-2 row could see it.

    Every expectation below is the accepted-S6 behaviour, measured from an
    isolated byte-faithful copy of that head -- not this file's opinion of it.
    """

    def test_a_normal_import_succeeds_and_builds_the_trigger_vocabulary(self):
        with _ImportRoot() as root:
            code, out, err = import_the_shell(root)
        self.assertEqual(code, 0, err)
        self.assertEqual(err, "")
        self.assertTrue(out.startswith("IMPORT OK "), out)
        self.assertGreater(int(out.split()[-1]), 100)

    def test_a_MISSING_cr_check_registry_halts_with_the_historic_message(self):
        with _ImportRoot() as root:
            (root / "config" / "generated" / "cr-checks.json").unlink()
            code, out, err = import_the_shell(root)
            expected = S6_MISSING_ARTIFACT.format(root=root)
        self.assertEqual(code, 1)
        self.assertEqual(out, "")
        self.assertEqual(err.strip(), expected)
        self.assertNotIn("Traceback", err)
        self.assertNotIn("ShapeError", err)

    def test_a_LOST_trigger_vocabulary_anchor_halts_with_the_historic_message(self):
        with _ImportRoot() as root:
            break_the_trigger_anchor(root)
            code, out, err = import_the_shell(root)
        self.assertEqual(code, 1)
        self.assertEqual(out, "")
        self.assertEqual(err.strip(), S6_TRIGGER_ANCHOR_LOST)
        self.assertNotIn("Traceback", err)
        self.assertNotIn("ShapeError", err)

    def test_THE_CONTROL_reinstating_the_rejected_bootstrap_turns_both_RED(self):
        """A guard never shown to fail is not known to be a guard.

        The rejected spelling is put back, verbatim, into a COPY of the shell,
        and both failure cases are re-observed. Each must stop being a
        `STOP — …` and become an uncaught `ShapeError` traceback -- which is
        what makes the two tests above regression tests rather than
        descriptions of today's behaviour.
        """
        for label, prepare in (("missing artifact",
                                lambda r: (r / "config" / "generated"
                                           / "cr-checks.json").unlink()),
                               ("lost anchor", break_the_trigger_anchor)):
            with self.subTest(case=label):
                with _ImportRoot() as root:
                    shell = root / "experiments" / "foundry_shape_extractor.py"
                    text = shell.read_text(encoding="utf-8")
                    self.assertEqual(
                        text.count("\n" + ACCEPTED_BOOTSTRAP + "\n"), 1,
                        "the accepted bootstrap spelling moved; this control "
                        "can no longer re-create the defect it grades")
                    shell.write_text(
                        text.replace("\n" + ACCEPTED_BOOTSTRAP + "\n",
                                     "\n" + REJECTED_BOOTSTRAP + "\n"),
                        encoding="utf-8")
                    prepare(root)
                    code, _out, err = import_the_shell(root)
                self.assertIn("Traceback", err)
                self.assertIn("ShapeError", err)
                self.assertNotIn("STOP — ", err)
                self.assertNotEqual(code, 0)

    def test_the_bootstrap_reaches_the_permanent_module_only_through_THIS_module(self):
        """Structural support for the behavioural proof above: no module-level
        statement may call a `_delivery.*` function that can raise.

        `use_card_text_rules` and the `CardTextRules` it is handed are the one
        permitted module-level reach into the permanent module -- they install
        the injected context, and their failure mode is a programming error in
        this file rather than a repository-state failure the accepted base
        converted to `STOP — …`. The accepted base had no equivalent call at
        all, and a missing provider name raised there too (`fc._MODAL_HEADER_RE`
        was read directly), so the parity question does not arise.
        """
        tree = ast.parse(SHAPE_SHELL.read_text(encoding="utf-8"))
        offenders = []
        for node in tree.body:
            if not isinstance(node, ast.Expr) or not isinstance(node.value, ast.Call):
                continue
            for call in ast.walk(node.value):
                if not isinstance(call, ast.Call):
                    continue
                fn = call.func
                if isinstance(fn, ast.Attribute) and isinstance(fn.value, ast.Name) \
                        and fn.value.id == "_delivery" \
                        and fn.attr not in INSTALL_ONLY:
                    offenders.append(f"line {node.lineno}: _delivery.{fn.attr}")
        self.assertEqual(offenders, [], f"import-time call past the halt "
                                        f"adapter: {offenders}")

    def test_the_message_adapter_is_the_boundarys_and_the_library_stays_neutral(self):
        """The two sentences are deliberately different, and both are asserted.

        `run experiments/foundry_cr_checks.py first` names a script in THIS
        repository; a module installed into an arbitrary `site-packages` must
        not tell its caller to run a file it cannot know exists.
        """
        shell = SHAPE_SHELL.read_text(encoding="utf-8")
        self.assertIn('f"{path} not found — run experiments/foundry_cr_checks.py '
                      'first"', shell)
        owner = (SHAPES_PKG / "delivery.py").read_text(encoding="utf-8")
        self.assertNotIn("foundry_cr_checks", owner)
        self.assertIn("generate the CR check ", owner)

    def test_the_permanent_owner_still_refuses_for_callers_that_skip_the_shell(self):
        """The adapter adds a message; it does not remove the library's guard."""
        from mtj_foundry.mtg.shapes import delivery
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(delivery.ShapeError):
                delivery.cr_action_terms(Path(tmp) / "definitely-not-here.json")

    def test_the_halt_boundary_prints_STOP_and_exits_one(self):
        """The shape of `fc.halt` itself, so the expectations above rest on a
        measured contract rather than on a remembered one."""
        import foundry_common as fc
        source = ast.unparse(ast.parse(
            (EXPERIMENTS / "foundry_common.py").read_text(encoding="utf-8")))
        self.assertIn("print(f'STOP — {message}', file=sys.stderr)", source)
        self.assertIn("sys.exit(1)", source)
        self.assertTrue(callable(fc.halt))


if __name__ == "__main__":
    unittest.main()
