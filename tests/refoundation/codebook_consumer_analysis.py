"""C8.5X — the transitive consumer reasoning of C8.5V, as executable analysis.

Stdlib only, fully static, and read-only. Nothing here imports or executes a
legacy module, and nothing here writes repository state. The only subprocess is
`git ls-files`, a read-only question about the repository.

WHY THIS MODULE EXISTS
----------------------
C8.5T shipped a one-file cohort instead of two because `foundry_r5_attribution`
calls into `foundry_consolidate_run1` inside an `except SystemExit`, and the
permanent store raises a `RuntimeError` that such a handler does not catch. That
finding was **not** visible in the candidate's own file: the candidate has no
try/except at all. It was found by hand, and C8.5V then re-derived the same
class of fact for fifteen candidates — also by hand, and also into a comment.

Captain's direction 5575012543 is that this reasoning stop being rediscovered
per slice. So the axes C8.5V argued in prose are derived here instead, each as
its own function, each answerable against a synthetic fixture as well as against
the live repository.

WHAT IS DERIVED, AND WHY EACH IS SEPARATE
-----------------------------------------
1. FACADE BINDING — `import foundry_codebook as fcb` and `from foundry_codebook
   import load_codebook as load` are the same read under two spellings. A name
   match (`"load_codebook" in source`) resolves neither, and would also score a
   comment. Bindings are resolved from each file's own import statements.
2. READ SITE / READ OWNER — a call, and the function that owns it. The owner is
   what reachability has to reach; the file is not, because a caller may reach a
   different function in the same file and never trigger the read.
3. STATIC IMPORTER — who imports the candidate by bare module name.
4. DYNAMIC LOADER SITE — who loads it by path or string. `tests/refoundation`
   loads legacy modules through `load_legacy(...)`, which a static-import scan is
   structurally blind to. Reported SEPARATELY, because a dynamic load is not
   evidence that the read executes.
5. REACHING CALL PATH — from the caller's entry point into the candidate, down
   the candidate's own call graph, to a read owner. This is the axis that turned
   C8.5T's finding from a guess into a fact, and the axis that keeps
   `foundry_r5_attribution`'s handler from being charged against
   `foundry_consolidate_run1_classify`, whose `classify_a15` does not reach the
   read owner.
6. CATCHING HANDLER — only counted when 5 succeeds. A `try/finally` with no
   `except` catches nothing and is reported as such. TWO ORIGINS, because a
   handler does not have to be an importer's: `LOCAL_READ` rows are the
   candidate's OWN try/except around its OWN read (C8.5X.R2), which is the
   shortest reaching path of all and was missing entirely while the analyzer
   walked only external callers.
7. FAILURE OBSERVABILITY — the conclusion of 5 and 6 together.
8. BOOTSTRAP DEPENDENCY — whether the candidate can reach `mtj_foundry` at all
   from its existing execution context. Derived, including the fact that
   `foundry_common` is what puts `src` on `sys.path`; if that provider cannot be
   read, the answer is UNKNOWN rather than an assumption.
9. FACADE DISPOSITION — SPLIT or DROP, derived from the facade symbols that
   remain bound after removing ONLY the `load_codebook` read.
10. OUTPUT TRUTH BOUNDARY — where the candidate mutates an artifact, and whether
    that mutation is ordered before or after the read. Ordering is claimed only
    when both sites are straight-line statements of the same function body;
    anything else is UNKNOWN. Proximity is never evidence.

THE UNKNOWN LAW
---------------
Every axis that cannot be resolved by this bounded model emits UNKNOWN carrying
its unresolved evidence, and `classification` may return SAFE only when no
unresolved evidence exists at all. UNKNOWN is never promoted to SAFE; a BLOCK
outranks an UNKNOWN, because a proven blocker is a stronger statement than an
unread edge, and neither is a pass.

SCOPE
-----
This is the analyzer for the CURRENT `foundry_codebook` read-consumer migration,
not a general whole-program analyzer. Its call graph resolves module-level
functions and `self.<method>` within a class, which is the shape the legacy tree
actually uses; anything else it cannot resolve is recorded as an unresolved edge
rather than silently dropped.
"""

from __future__ import annotations

import argparse
import ast
import builtins
import json
import subprocess
import sys
from pathlib import Path

# The output contract. Bumped only when the record shape changes, so a
# consumer of this JSON can tell a shape change from a repository change.
# /2 (C8.5X.R3): every handler row gains `unresolved_frontier`. `_reachability`
# always computed that evidence and every caller dropped it, so an UNKNOWN row
# said "UNKNOWN" and nothing about WHY. Leaving the constant at /1 while adding a
# field is the failure this constant exists to prevent.
SCHEMA = "mtj-codebook-consumer-analysis/2"

# The facade under migration and the one symbol a READ repoint retires.
FACADE_MODULE = "foundry_codebook"
READ_SYMBOL = "load_codebook"

# The permanent boundary a repointed consumer has to be able to import. WHICH
# module puts `src` on `sys.path` is deliberately NOT a constant here: it is
# `foundry_common` today, and `bootstrap_dependency` finds it by parsing the
# import chain, so a fixture root without it answers UNKNOWN truthfully instead
# of inheriting this repository's arrangement.
PERMANENT_PACKAGE = "mtj_foundry"

# Loader surfaces that can execute a legacy module without importing its name.
# `load_legacy` is `tests/refoundation`'s own path loader.
DYNAMIC_LOADERS = ("load_legacy", "importlib.import_module", "__import__",
                   "importlib.util.spec_from_file_location")

# Calls that mutate something outside the process, in two lists because a bare
# method name is not evidence of a write. `replace` is `str.replace` far more
# often than it is `os.replace`, and `foundry_reaudit` prints two of them inside
# a quote normalizer; a single name list scored both as artifact mutations. The
# unqualified list therefore holds only names `str` does not define, and
# everything ambiguous must be spelled with its module.
#
# THE ENUMERATION IS BOUNDED AND SAYS SO IN ITS OWN OUTPUT. There is no derivable
# closed list of "every write in Python", so `output_truth_boundary` reports what
# it found together with the list it looked for, and never claims completeness.
WRITE_METHODS = ("write_text", "write_bytes", "mkdir", "touch", "unlink",
                 "rmdir", "symlink_to", "hardlink_to", "chmod", "writelines")
WRITE_DOTTED = ("os.replace", "os.rename", "os.remove", "os.makedirs",
                "os.unlink", "os.rmdir", "os.write", "json.dump",
                "shutil.copy", "shutil.copy2", "shutil.copyfile",
                "shutil.copytree", "shutil.move", "shutil.rmtree")
WRITE_MODES = ("w", "a", "x", "wb", "ab", "xb", "w+", "a+", "r+")


# ---------------------------------------------------------------------------
# Universe
# ---------------------------------------------------------------------------


def python_files(root: Path) -> list[Path]:
    """Every `.py` file in the analysis universe, repository-relative, sorted.

    `git ls-files` when the root is a git work tree — the same read-only query
    `layout_census` uses, and therefore the same universe, so a file this
    analyzer sees is a file that census counts. A root with no `.git` is a
    synthetic fixture and is walked instead: the negative controls need a
    universe they can build in a temp directory without initialising a
    repository first.

    Both modes sort, so neither depends on filesystem or `git` output order.
    """
    if (root / ".git").exists():
        out = subprocess.run(["git", "-C", str(root), "ls-files", "*.py"],
                             capture_output=True, text=True, check=True).stdout
        return sorted(Path(line) for line in out.splitlines() if line)
    return sorted(path.relative_to(root) for path in root.rglob("*.py")
                  if "__pycache__" not in path.parts)


def module_name(rel: Path) -> str:
    """The bare name a legacy sibling import would use for this file."""
    return rel.stem


# ---------------------------------------------------------------------------
# Binding resolution
# ---------------------------------------------------------------------------


def all_module_bindings(tree: ast.AST) -> dict:
    """`{imported module: bindings}` for every module a file imports, one pass.

    `module_bindings` answers for ONE target and is what the controls read; this
    answers for all of them at once, because nineteen candidates measured against
    every file in the universe asked the single-target question 2,603 times and
    each one walked the whole tree.
    """
    found: dict = {}

    def slot(name: str) -> dict:
        return found.setdefault(name, {"aliases": [], "symbols": {},
                                       "star": False})

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for name in node.names:
                slot(name.name)["aliases"].append(name.asname or name.name)
        elif isinstance(node, ast.ImportFrom) and node.module:
            entry = slot(node.module)
            for name in node.names:
                if name.name == "*":
                    entry["star"] = True
                else:
                    entry["symbols"][name.asname or name.name] = name.name
    for entry in found.values():
        entry["aliases"] = sorted(set(entry["aliases"]))
    return found


def module_bindings(tree: ast.AST, target: str) -> dict:
    """How a file binds `target`, resolved from its own import statements.

    Returns `{"aliases": [...], "symbols": {local: original}, "star": bool}`.

    THE STAR CASE IS KEPT RATHER THAN IGNORED. `from <target> import *` binds
    names this analyzer cannot enumerate without importing the module, so it is
    an unresolved edge and has to arrive at `classification` as one. Dropping it
    would turn an unreadable file into a clean one.
    """
    aliases: list[str] = []
    symbols: dict[str, str] = {}
    star = False
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for name in node.names:
                if name.name == target:
                    aliases.append(name.asname or name.name)
        elif isinstance(node, ast.ImportFrom) and node.module == target:
            for name in node.names:
                if name.name == "*":
                    star = True
                else:
                    symbols[name.asname or name.name] = name.name
    return {"aliases": sorted(set(aliases)), "symbols": symbols, "star": star}


def facade_symbol_references(tree: ast.AST, bindings: dict) -> list[str]:
    """Facade-side symbol names this file references, sorted.

    Attribute loads through a module alias, and bare loads of a `from`-imported
    name. The answer is stated in the FACADE's vocabulary, not the importer's,
    so `from foundry_codebook import load_codebook as load` reports
    `load_codebook` — otherwise one read would be filed under two symbols
    depending on how the importer spelled it, and the disposition rule below
    would see two different facades.
    """
    found: set[str] = set()
    aliases = set(bindings["aliases"])
    for node in ast.walk(tree):
        if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name) \
                and node.value.id in aliases:
            found.add(node.attr)
        elif isinstance(node, ast.Name) and node.id in bindings["symbols"]:
            found.add(bindings["symbols"][node.id])
    return sorted(found)


def read_call_sites(tree: ast.AST, bindings: dict) -> list:
    """Every call that resolves, through a binding, to the facade read.

    Both import forms land here, which is the point: the alias form and the
    `from`-import form are the same read, and a name-string search would score
    them differently — as well as scoring the word in a comment.
    """
    aliases = set(bindings["aliases"])
    local_names = {local for local, original in bindings["symbols"].items()
                   if original == READ_SYMBOL}
    sites = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        if isinstance(func, ast.Attribute) and isinstance(func.value, ast.Name) \
                and func.value.id in aliases and func.attr == READ_SYMBOL:
            sites.append(node)
        elif isinstance(func, ast.Name) and func.id in local_names:
            sites.append(node)
    return sites


# ---------------------------------------------------------------------------
# Scope, call graph and reachability
# ---------------------------------------------------------------------------


MODULE_SCOPE = "<module>"


def _qualified_scopes(tree: ast.AST) -> dict:
    """`{id(node): owning function qname}`; nodes at module scope are absent.

    Qualified with the enclosing class (`Class.method`), so two methods of the
    same name are two nodes of the call graph rather than one. INNERMOST wins,
    which is what makes a nested helper its own owner instead of silently
    reporting its parent as the owner of a read it does not contain.
    """
    scopes: dict = {}

    def walk(node: ast.AST, prefix: str, owner: str) -> None:
        for child in ast.iter_child_nodes(node):
            if isinstance(child, ast.ClassDef):
                walk(child, f"{prefix}{child.name}.", owner)
                continue
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                name = f"{prefix}{child.name}"
                scopes[id(child)] = name
                walk(child, "", name)
                continue
            if owner:
                scopes[id(child)] = owner
            walk(child, prefix, owner)

    walk(tree, "", "")
    return scopes


def owner_of(scopes: dict, node: ast.AST) -> str:
    """The function that owns a node, or `<module>` for import-time code."""
    return scopes.get(id(node), MODULE_SCOPE)


def _resolved_call_edges(tree: ast.AST, scopes: dict, edges: dict) -> list:
    """`(callee qname, call node)` for every call the graph resolved.

    Shared with the handler walk deliberately: a handler may only be charged
    against an edge the reachability answer actually used, and the way to
    guarantee that is for both to read the same resolution.
    """
    defined = {scopes[id(n)] for n in ast.walk(tree)
               if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
               and id(n) in scopes}
    found = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        if isinstance(func, ast.Name) and func.id in defined:
            found.append((func.id, node))
        elif isinstance(func, ast.Attribute) and isinstance(func.value, ast.Name) \
                and func.value.id == "self":
            caller = owner_of(scopes, node)
            enclosing = caller.rsplit(".", 1)[0] if "." in caller else ""
            qname = f"{enclosing}.{func.attr}" if enclosing else func.attr
            if qname in defined:
                found.append((qname, node))
    return found


def call_graph(tree: ast.AST) -> tuple:
    """`({caller qname: {callee qname}}, [(node, unresolved edge), ...])`.

    Two shapes resolve, and they are the two the legacy tree uses:

    * a bare call to a function this module defines — `build()` inside `main()`;
    * `self.<method>()` inside a class, resolved to `Class.method`.

    EVERYTHING ELSE THAT COULD BE AN EDGE IS RETURNED, NOT DISCARDED. Two shapes
    qualify: a call through some other object whose attribute happens to name a
    function this module defines, and a REFERENCE to a defined function that is
    not itself the callee of a call — `sorted(key=build)` hands `build` to
    someone else to call. A negative reachability answer is only as good as the
    graph it was computed on, so these are what `_reachability` needs in order to
    return UNKNOWN instead of False.

    THE NODE TRAVELS WITH THE EDGE (C8.5X.R3). An unresolved edge answers two
    different questions, and R1/R2 only ever asked the first: *why is a negative
    reachability answer untrustworthy* needs the edge, but *is this uncertainty
    sitting inside a candidate-local `try`* needs the NODE. Rediscovering these
    two families a second time somewhere else to get the node is how one rule
    becomes two implementations that drift, so the node is carried here and
    `Module` keeps the JSON-safe view beside it. `defines` names the function the
    edge is uncertain about, which is what a forward pass has to ask about.
    """
    scopes = _qualified_scopes(tree)
    defined = {scopes[id(n)] for n in ast.walk(tree)
               if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
               and id(n) in scopes}
    edges: dict = {}
    unresolved: list = []
    called_directly: set = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        caller = owner_of(scopes, node)
        func = node.func
        callee = None
        if isinstance(func, ast.Name) and func.id in defined:
            called_directly.add(id(func))
            callee = func.id
        elif isinstance(func, ast.Attribute) and isinstance(func.value, ast.Name) \
                and func.value.id == "self":
            enclosing = caller.rsplit(".", 1)[0] if "." in caller else ""
            qname = f"{enclosing}.{func.attr}" if enclosing else func.attr
            if qname in defined:
                callee = qname
        elif isinstance(func, ast.Attribute) and func.attr in defined:
            unresolved.append((node, {
                "caller": caller, "lineno": node.lineno,
                "expr": ast.unparse(func), "defines": func.attr,
                "reason": "call through an object whose attribute "
                          "names a function this module defines"}))
        if callee is not None:
            edges.setdefault(caller, set()).add(callee)
    for node in ast.walk(tree):
        if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load) \
                and node.id in defined and id(node) not in called_directly:
            unresolved.append((node, {
                "caller": owner_of(scopes, node), "lineno": node.lineno,
                "expr": node.id, "defines": node.id,
                "reason": "a defined function is referenced "
                          "without being called here"}))
    return edges, sorted(unresolved, key=lambda pair: (pair[1]["lineno"],
                                                       pair[1]["expr"]))


def reachable(edges: dict, start: str) -> set:
    """Every qname reachable from `start`, `start` included."""
    seen = {start}
    stack = [start]
    while stack:
        for nxt in sorted(edges.get(stack.pop(), ())):
            if nxt not in seen:
                seen.add(nxt)
                stack.append(nxt)
    return seen


def call_path(edges: dict, start: str, target: str):
    """One shortest call path `start -> ... -> target`, or None.

    Breadth-first over SORTED successors, so the reported path is a property of
    the graph rather than of set iteration order — the determinism law applies
    to the evidence, not only to the verdict.
    """
    if start == target:
        return [start]
    queue = [[start]]
    seen = {start}
    while queue:
        path = queue.pop(0)
        for nxt in sorted(edges.get(path[-1], ())):
            if nxt in seen:
                continue
            if nxt == target:
                return path + [nxt]
            seen.add(nxt)
            queue.append(path + [nxt])
    return None


# ---------------------------------------------------------------------------
# Handlers
# ---------------------------------------------------------------------------


def try_body_map(tree: ast.AST) -> dict:
    """`{id(node): [enclosing Try, ...]}` for every node inside a try BODY.

    The BODY, never the whole statement. A call in an `except` arm is not
    protected by that `except`, and a call in a `finally` arm runs ON the failure
    path rather than under a handler. Both would pass a containment test that did
    not say which arm, and both are wrong in the direction that reads as safe.

    Built in ONE descent and cached on the module. The obvious spelling — walk
    every `Try` and ask whether it contains this node — is quadratic, and on a
    3,000-line legacy module with a hundred call sites it dominated the run.
    """
    found: dict = {}

    def descend(node: ast.AST, stack: tuple) -> None:
        for child in ast.iter_child_nodes(node):
            if stack:
                found[id(child)] = list(stack)
            if isinstance(child, ast.Try):
                for statement in child.body:
                    found[id(statement)] = list(stack) + [child]
                    descend(statement, stack + (child,))
                for arm in (child.handlers, child.orelse, child.finalbody):
                    for statement in arm:
                        descend(statement, stack)
                continue
            descend(child, stack)

    descend(tree, ())
    return found


def enclosing_tries(tree: ast.AST, node: ast.AST) -> list:
    """Every `ast.Try` whose BODY contains `node`, in line order.

    Kept as a function over a tree so a caller with no `Module` in hand — a
    control, a probe — can ask the question directly; `Module` caches the map.
    """
    return sorted(try_body_map(tree).get(id(node), []), key=lambda t: t.lineno)


def except_classes(handler: ast.ExceptHandler) -> set:
    """The exception classes ONE `except` arm names; `{"BARE"}` for a bare one.

    Leaf names, so `except codebook_store.CodebookReadError` and
    `except CodebookReadError` are one answer — the module spelling is the
    importer's business and the class is the same class.
    """
    if handler.type is None:
        return {"BARE"}
    node = handler.type
    return {ast.unparse(part).rsplit(".", 1)[-1]
            for part in (node.elts if isinstance(node, ast.Tuple) else [node])}


def handler_classes(try_node) -> list:
    """The exception classes a `try` catches; `[]` for a `try/finally`.

    The EMPTY LIST is the load-bearing case: `try/finally` catches nothing, and
    calling it a handler would charge a caller with observing a failure it never
    sees — while `finally` in fact runs on the failure path.
    """
    caught: set = set()
    for handler in try_node.handlers:
        caught |= except_classes(handler)
    return sorted(caught)


# ---------------------------------------------------------------------------
# The failure transition
# ---------------------------------------------------------------------------
#
# C8.5X SHIPPED A FALSE BLOCKER HERE AND THE MANAGER REJECTED IT
# (issue:1#issuecomment-5585684318). Two frozen name sets stood in for the
# question, and `observes_read_failure` was then `bool(catch_classes)` — so ANY
# reaching handler became a blocker. `except BaseException` catches the legacy
# `SystemExit` AND the permanent typed error, so the repoint changes nothing it
# observes; C8.5R's accepted result says exactly that about
# `foundry_object_lattice`, and this analyzer contradicted it. A conservative
# false blocker is still false derived infrastructure.
#
# The repair is to DERIVE the transition instead of naming it, and the facade is
# its own translation table: `foundry_codebook.load_codebook` catches the store's
# typed read errors and calls `fc.halt`, which prints a STOP line and exits. So
# the classes that get translated, the class the legacy side raises instead, and
# the side effect that disappears are all parsed out of the two modules that
# perform the translation — the same law the CR work runs on. A universe where
# that cannot be parsed answers UNKNOWN rather than inheriting this
# repository's arrangement.


def class_hierarchy(universe: dict) -> dict:
    """`{class name: [base class names]}` for every class defined in the universe.

    Leaf names only, because that is how a handler is written: `except
    codebook_store.CodebookReadError` and `except CodebookReadError` are the same
    handler. Two classes of the same name in different modules would merge, which
    is declared rather than defended — this analyzer is scoped to one migration,
    and the classes that matter are defined once.
    """
    found: dict = {}
    for _, module in sorted(universe.items()):
        for node in ast.walk(module.tree):
            if isinstance(node, ast.ClassDef):
                found.setdefault(node.name, sorted(
                    {ast.unparse(base).rsplit(".", 1)[-1] for base in node.bases}))
    return found


def ancestors_of(name: str, hierarchy: dict):
    """Every class `except <ancestor>` would catch `name` by, or None.

    Builtin exceptions are resolved through the RUNNING INTERPRETER's `__mro__`
    rather than a written-out table: `SystemExit` is not an `Exception`, and that
    fact is the whole difference between the old-only and symmetric cases. A
    table would be a hand-list of the standard exception tree, which is the
    defect family this repository names most often.

    None means the name resolves nowhere — not a builtin exception, not a class
    the universe defines. That is UNKNOWN, never "no".
    """
    seen: set = set()
    stack = [name]
    resolved = False
    while stack:
        current = stack.pop()
        if current in seen:
            continue
        seen.add(current)
        builtin = getattr(builtins, current, None)
        if isinstance(builtin, type) and issubclass(builtin, BaseException):
            seen |= {cls.__name__ for cls in builtin.__mro__}
            resolved = True
            continue
        if current in hierarchy:
            resolved = True
            stack += hierarchy[current]
    return seen if resolved else None


def catches(handler_classes: list, target: str, hierarchy: dict):
    """Does a handler catching `handler_classes` catch a `target` failure?

    True / False / "UNKNOWN". A bare `except:` catches everything. An unresolved
    handler class cannot be ruled out, so it produces UNKNOWN unless some other
    class in the same handler already answers True — a handler that definitely
    catches is not made uncertain by a second name nobody can resolve.
    """
    if "BARE" in handler_classes:
        return True
    family = ancestors_of(target, hierarchy)
    if family is None:
        return "UNKNOWN"
    unresolved = False
    for name in handler_classes:
        if name in family:
            return True
        if ancestors_of(name, hierarchy) is None:
            unresolved = True
    return "UNKNOWN" if unresolved else False


def failure_transition(universe: dict) -> dict:
    """What the codebook read raises on each side of the repoint, DERIVED.

    Read out of the facade, which is the translation itself:

        def load_codebook(path=None):
            try:
                return _codebook_store.read(...)
            except _codebook_store.CodebookNotFoundError as error:
                fc.halt(str(error))
            except _codebook_store.SchemaMismatchError as error:
                ...
                fc.halt(str(error))

    The caught classes ARE the translated failures — the ones a repoint changes
    the class of. Everything the facade does not catch (`OSError`,
    `json.JSONDecodeError`, `UnicodeDecodeError`) propagates raw on both sides
    and is a pass-through, which needs no list here: a handler catching only
    those is an ancestor of neither side and falls out as NEITHER.

    The legacy class comes from the halt: `foundry_common.halt` prints a STOP
    line to stderr and calls `sys.exit`, so the class is `SystemExit` and the
    stderr line is the side effect that disappears. Both are parsed; a universe
    whose facade or halt cannot be read reports `status: UNKNOWN` and every
    catchability answer downstream becomes UNKNOWN with it.
    """
    facade = next((m for _, m in sorted(universe.items())
                   if m.name == FACADE_MODULE), None)
    if facade is None:
        return {"status": "UNKNOWN", "legacy_class": None, "permanent_classes": [],
                "evidence": [f"no {FACADE_MODULE} module in this universe"]}
    reader = next((n for n in ast.walk(facade.tree)
                   if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
                   and n.name == READ_SYMBOL), None)
    if reader is None:
        return {"status": "UNKNOWN", "legacy_class": None, "permanent_classes": [],
                "evidence": [f"{FACADE_MODULE} defines no {READ_SYMBOL}"]}

    translated: set = set()
    halts: set = set()
    for node in ast.walk(reader):
        if not isinstance(node, ast.Try):
            continue
        for handler in node.handlers:
            calls = {ast.unparse(c.func) for c in ast.walk(handler)
                     if isinstance(c, ast.Call)}
            halt_calls = {name for name in calls
                          if name == "halt" or name.endswith(".halt")}
            if not halt_calls:
                continue
            translated |= {name for name in except_classes(handler)
                           if name != "BARE"}
            halts |= halt_calls
    if not translated or not halts:
        return {"status": "UNKNOWN", "legacy_class": None,
                "permanent_classes": sorted(translated),
                "evidence": [f"{READ_SYMBOL} translates no typed failure through "
                             f"a halt call that this model can read"]}

    legacy, stderr_line, halt_evidence = _halt_behavior(facade, halts, universe)
    if legacy is None:
        return {"status": "UNKNOWN", "legacy_class": None,
                "permanent_classes": sorted(translated),
                "evidence": halt_evidence}
    return {
        "status": "DERIVED",
        "legacy_class": legacy,
        "permanent_classes": sorted(translated),
        "legacy_side_effect": stderr_line,
        "evidence": [f"{facade.rel.as_posix()}:{READ_SYMBOL} translates "
                     f"{', '.join(sorted(translated))} through "
                     f"{', '.join(sorted(halts))}"] + halt_evidence,
        "pass_through_rule": "a class the facade does not catch propagates "
                             "unchanged on both sides and is not a transition",
    }


def _halt_behavior(facade: Module, halts: set, universe: dict) -> tuple:
    """`(exception class, stderr side effect, evidence)` for the legacy halt.

    Followed through the facade's own import alias to the module that defines
    `halt`, and read there. `sys.exit` raises `SystemExit`, which is a fact about
    the interpreter and not about this repository — so the class NAME is taken
    from the call, and its position in the exception tree comes from `__mro__`
    like every other class here.
    """
    by_name = {m.name: m for _, m in sorted(universe.items())}
    for spelling in sorted(halts):
        alias = spelling.rsplit(".", 1)[0] if "." in spelling else None
        owner = facade
        if alias is not None:
            target = next((module for module, entry
                           in sorted(facade._bindings.items())
                           if alias in entry["aliases"]), None)
            owner = by_name.get(target.split(".")[0]) if target else None
        if owner is None:
            continue
        function = next((n for n in ast.walk(owner.tree)
                         if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
                         and n.name == spelling.rsplit(".", 1)[-1]), None)
        if function is None:
            continue
        stderr = ("a line is printed to stderr before the exit"
                  if any(ast.unparse(keyword.value).endswith("stderr")
                         for call in ast.walk(function)
                         if isinstance(call, ast.Call)
                         for keyword in call.keywords if keyword.arg == "file")
                  else "no stderr line accompanies the exit")
        for node in ast.walk(function):
            if isinstance(node, ast.Raise) and node.exc is not None:
                name = ast.unparse(node.exc).split("(")[0].rsplit(".", 1)[-1]
                return name, stderr, [f"{owner.rel.as_posix()}:{function.name} "
                                      f"raises {name}"]
            if isinstance(node, ast.Call) and ast.unparse(node.func) in (
                    "sys.exit", "exit", "os._exit"):
                return "SystemExit", stderr, [
                    f"{owner.rel.as_posix()}:{function.name} calls "
                    f"{ast.unparse(node.func)}, which raises SystemExit"]
    return None, None, ["the halt function could not be read in this universe"]


def handler_catchability(classes: list, model: dict) -> dict:
    """Whether a handler's catchability CHANGES across the read repoint.

    The two sides are asked SEPARATELY, which is the repair. Five answers:

    * OLD_ONLY — catches the legacy `SystemExit` and none of the permanent
      classes. The C8.5T shape, and a real blocker.
    * NEW_ONLY — catches the permanent typed failure and not the legacy one.
      `except Exception` is the whole group: it never caught `SystemExit`, so the
      repoint hands it a failure it now swallows.
    * SYMMETRIC_BOTH — catches both. NO catchability delta, which is C8.5R's
      accepted finding about `except BaseException`. Reported as a fact, not
      promoted to "safe": the legacy STOP line on stderr still disappears, and
      that output delta is a separate question this axis does not answer.
    * NEITHER — catches neither side. `except CodebookStoreError` is the sharp
      case: the store's read errors descend from `RuntimeError` DIRECTLY, not
      from `CodebookStoreError`, so that handler sees no read failure at all. So
      is `except OSError`, which is a pass-through unchanged on both sides.
    * PARTIAL_OLD_ONLY — catches the legacy class and only SOME permanent
      classes. A change for the rest, named.
    """
    if model["status"] != "DERIVED":
        return {"legacy_caught": "UNKNOWN", "permanent_caught": "UNKNOWN",
                "permanent_caught_classes": [], "permanent_uncaught_classes": [],
                "transition": "UNKNOWN", "changes_catchability": "UNKNOWN",
                "evidence": model["evidence"]}
    hierarchy = model["hierarchy"]
    legacy = catches(classes, model["legacy_class"], hierarchy)
    caught, uncaught, unknown = [], [], []
    for name in model["permanent_classes"]:
        answer = catches(classes, name, hierarchy)
        (caught if answer is True else uncaught if answer is False
         else unknown).append(name)
    if legacy == "UNKNOWN" or unknown:
        return {"legacy_caught": legacy, "permanent_caught": "UNKNOWN",
                "permanent_caught_classes": sorted(caught),
                "permanent_uncaught_classes": sorted(uncaught),
                "transition": "UNKNOWN", "changes_catchability": "UNKNOWN",
                "evidence": [f"unresolved handler class against {name}"
                             for name in sorted(unknown)] or
                            ["the legacy class could not be resolved"]}
    permanent = ("ALL" if caught and not uncaught else
                 "NONE" if not caught else "SOME")
    if legacy and permanent == "ALL":
        transition, changes = "SYMMETRIC_BOTH", False
    elif legacy and permanent == "NONE":
        transition, changes = "OLD_ONLY", True
    elif legacy:
        transition, changes = "PARTIAL_OLD_ONLY", True
    elif permanent == "NONE":
        transition, changes = "NEITHER", False
    else:
        transition, changes = "NEW_ONLY", True
    return {"legacy_caught": bool(legacy), "permanent_caught": permanent,
            "permanent_caught_classes": sorted(caught),
            "permanent_uncaught_classes": sorted(uncaught),
            "transition": transition, "changes_catchability": changes,
            "evidence": []}


# ---------------------------------------------------------------------------
# One file, parsed once
# ---------------------------------------------------------------------------


class Module:
    """One parsed repository file and the derived facts the axes need."""

    def __init__(self, root: Path, rel: Path):
        self.rel = rel
        self.name = module_name(rel)
        self.source = (root / rel).read_text(encoding="utf-8")
        self.tree = ast.parse(self.source)
        self.scopes = _qualified_scopes(self.tree)
        self.edges, self.unresolved_surfaces = call_graph(self.tree)
        # TWO VIEWS OF ONE LIST. `unresolved_edges` is the JSON-safe one every
        # reachability answer carries; `unresolved_surfaces` keeps the AST node
        # beside it so a forward pass can ask which of them a `try` protects.
        self.unresolved_edges = [edge for _, edge in self.unresolved_surfaces]
        self.facade = module_bindings(self.tree, FACADE_MODULE)
        self.reads = read_call_sites(self.tree, self.facade)
        self.read_owners = sorted({owner_of(self.scopes, node)
                                   for node in self.reads})
        # Derived once per file. Nineteen candidates are each measured against
        # every file in the universe, so anything recomputed per pair is
        # recomputed 2,600 times; these four maps are the whole difference
        # between a tool a gate can run and one it cannot.
        self.tries = try_body_map(self.tree)
        self._bindings = all_module_bindings(self.tree)
        self.constants = _module_constants(self.tree)
        self.parameters = _parameter_names(self.tree)
        self.loader_calls = _loader_calls(self)
        self._ancestors: dict = {}
        self._reachability: dict = {}
        self._calls_by_callee: dict = {}
        for callee, node in _resolved_call_edges(self.tree, self.scopes, self.edges):
            self._calls_by_callee.setdefault(callee, []).append(node)

    def tries_around(self, node: ast.AST) -> list:
        return sorted(self.tries.get(id(node), []), key=lambda t: t.lineno)

    def bindings_for(self, target: str) -> dict:
        return self._bindings.get(target, EMPTY_BINDINGS)

    def calls_to(self, names: set) -> list:
        """`(callee qname, call node)` for calls resolving into `names`."""
        found = []
        for name in sorted(names):
            found += [(name, node) for node in self._calls_by_callee.get(name, ())]
        return found

    def resolved_calls(self) -> list:
        """`(callee qname, call node)` for EVERY resolved local call edge.

        The forward-pass counterpart of `calls_to`, which asks about a named set
        decided in advance. A forward pass cannot name the set in advance --
        that is the backward walk whose resolved-only `ancestors_of` set is
        exactly what hid the C8.5X.R2 UNKNOWN class."""
        return self.calls_to(set(self._calls_by_callee))

    def ancestors_of(self, target: str) -> set:
        if target not in self._ancestors:
            self._ancestors[target] = _ancestors(self.edges, target)
        return self._ancestors[target]

    @property
    def import_time_read(self) -> bool:
        """A read at module scope executes on IMPORT, which is the one case
        where merely loading the module — statically or dynamically — triggers
        it. Every other read needs a call, and that is what reachability asks."""
        return MODULE_SCOPE in self.read_owners

    def sys_path_inserts(self) -> list:
        return [n for n in ast.walk(self.tree)
                if isinstance(n, ast.Call)
                and isinstance(n.func, ast.Attribute)
                and n.func.attr in ("insert", "append")
                and isinstance(n.func.value, ast.Attribute)
                and n.func.value.attr == "path"
                and isinstance(n.func.value.value, ast.Name)
                and n.func.value.value.id == "sys"]

    def imports(self) -> set:
        names = set()
        for module, entry in self._bindings.items():
            names.add(module)
            names |= {f"{module}.{symbol}" for symbol in entry["symbols"].values()}
        return names


EMPTY_BINDINGS = {"aliases": [], "symbols": {}, "star": False}


def _module_constants(tree: ast.AST) -> dict:
    """`{name: [string components]}` for module-level `/`-join constants.

    One hop, and deliberately only one. It exists to resolve a loader argument
    like `LEGACY_PATH = EXPERIMENTS / "foundry_audit_baseline.py"` into the module
    it names; a deeper evaluator would be a small interpreter, and the honest
    answer for anything it could not follow is UNKNOWN rather than a guess.
    """
    found: dict = {}
    for statement in tree.body:
        if not isinstance(statement, ast.Assign):
            continue
        parts = [n.value for n in ast.walk(statement.value)
                 if isinstance(n, ast.Constant) and isinstance(n.value, str)]
        if not parts:
            continue
        for target in statement.targets:
            if isinstance(target, ast.Name):
                found[target.id] = parts
    return found


def _parameter_names(tree: ast.AST) -> set:
    """Every parameter name of every function in the file.

    Used to tell a loader DEFINITION from a loader CALL. `load_legacy(name)`
    builds its path from its own parameter, so that site names no particular
    module; its callers do, and they are analyzed as their own sites.
    """
    names: set = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            args = node.args
            for arg in (args.posonlyargs + args.args + args.kwonlyargs):
                names.add(arg.arg)
            for arg in (args.vararg, args.kwarg):
                if arg is not None:
                    names.add(arg.arg)
    return names


# ---------------------------------------------------------------------------
# Bootstrap
# ---------------------------------------------------------------------------


def _inserts_src(module: Module) -> bool:
    """Does this module put a `src` directory on `sys.path`?

    PARSED, NEVER ASSUMED, and it has to follow one name hop: the boundary
    spells it `_BOOTSTRAP_SRC = _BOOTSTRAP_ROOT / "src"` and inserts the NAME, so
    a scan that only looked for the literal inside the call answered no about the
    one module in the repository that does it. A fixture root without a provider
    must be able to answer no truthfully, which is why this is a measurement.
    """
    constants = module.constants
    for call in module.sys_path_inserts():
        for node in ast.walk(call):
            if isinstance(node, ast.Constant) and node.value == "src":
                return True
            if isinstance(node, ast.Name) and "src" in constants.get(node.id, ()):
                return True
    return False


def bootstrap_dependency(module: Module, universe: dict) -> dict:
    """Can this file import the permanent boundary from where it already runs?

    THE CHAIN IS FOLLOWED, NOT ASSUMED. `foundry_common` is the module that puts
    `src` on `sys.path` today, but a candidate need not import it directly:
    `foundry_slug_dossier` imports only the facade, and the facade imports the
    boundary provider. A rule that looked for one named provider answered UNKNOWN
    about a file whose bootstrap is two hops away and entirely present — a
    false blocker, which is the same failure class as a false clean.

    So the search is a deterministic breadth-first walk over IN-UNIVERSE imports,
    and it reports the chain it walked. UNKNOWN is returned when the walk ends
    without finding a `src` insert: "no evidence of a problem" is not evidence of
    a working import, and this axis decides whether a repoint would need new
    bootstrap code, which the migration forbids.
    """
    by_name = {m.name: m for m in universe.values()}
    imports = module.imports()
    if any(name == PERMANENT_PACKAGE or name.startswith(PERMANENT_PACKAGE + ".")
           for name in imports):
        return {"status": "ALREADY_IMPORTS_BOUNDARY", "via": PERMANENT_PACKAGE,
                "chain": [module.rel.as_posix()],
                "evidence": sorted(n for n in imports
                                   if n.startswith(PERMANENT_PACKAGE))}
    if _inserts_src(module):
        return {"status": "SATISFIED_LOCALLY", "via": module.name,
                "chain": [module.rel.as_posix()],
                "evidence": ["a local sys.path insert names 'src'"]}
    queue = [[module]]
    seen = {module.name}
    while queue:
        chain = queue.pop(0)
        for name in sorted(chain[-1].imports()):
            head = name.split(".")[0]
            if head in seen or head not in by_name:
                continue
            seen.add(head)
            nxt = by_name[head]
            if _inserts_src(nxt):
                walked = chain + [nxt]
                return {"status": "SATISFIED_VIA_PROVIDER", "via": nxt.name,
                        "chain": [m.rel.as_posix() for m in walked],
                        "evidence": [f"{nxt.rel.as_posix()} inserts 'src' on "
                                     f"sys.path, reached in "
                                     f"{len(walked) - 1} import hop(s)"]}
            queue.append(chain + [nxt])
    return {"status": "UNKNOWN", "via": None,
            "chain": [module.rel.as_posix()],
            "evidence": ["no boundary import, and no in-universe module reachable "
                         "through this file's imports inserts 'src' on sys.path"]}


# ---------------------------------------------------------------------------
# Output truth boundary
# ---------------------------------------------------------------------------


def _body_index(function_node, node: ast.AST):
    """Which straight-line statement of a function body contains `node`.

    None when the node sits inside a compound statement — an `if`, a loop, a
    `with`, a nested function. The ordering claim below is made only between two
    straight-line statements, so a read inside a branch and a write after it
    produce UNKNOWN instead of a confident AFTER_READ that the branch falsifies.
    """
    for index, statement in enumerate(function_node.body):
        if not isinstance(statement, (ast.Assign, ast.AugAssign, ast.AnnAssign,
                                      ast.Expr, ast.Return)):
            continue
        if any(node is inner for inner in ast.walk(statement)):
            return index
    return None


def _is_write_call(node: ast.Call) -> str | None:
    """The write family a call belongs to, or None.

    Three tests, and the split is the whole point. A bare attribute name is only
    accepted when `str` does not define it — `f.replace(...)` is a string
    normalizer in `foundry_reaudit` and was scored as an artifact mutation by a
    name-only list. Anything ambiguous must arrive spelled with its module, and
    `open()` is read through its MODE argument rather than its name.
    """
    dotted = ast.unparse(node.func)
    if dotted in WRITE_DOTTED:
        return "DOTTED"
    if isinstance(node.func, ast.Attribute) and node.func.attr in WRITE_METHODS:
        return "METHOD"
    if dotted in ("open", "io.open", "Path.open") or (
            isinstance(node.func, ast.Attribute) and node.func.attr == "open"):
        for arg in list(node.args[1:]) + [k.value for k in node.keywords
                                          if k.arg == "mode"]:
            if isinstance(arg, ast.Constant) and arg.value in WRITE_MODES:
                return "OPEN_FOR_WRITE"
    return None


def output_truth_boundary(module: Module) -> dict:
    """Where the file mutates an artifact, and how that orders against the read.

    Ordering is asserted only when the write and the read are straight-line
    statements of the SAME function body; everything else is UNKNOWN. That is the
    axis on which C8.5V's `foundry_reaudit` argument differed in KIND from
    C8.5U's `foundry_cr_checks`: cr_checks writes its artifact BEFORE the read,
    so the artifact survives every failure, while reaudit reads first and writes
    after, so no artifact is produced on any failure path. Same conclusion —
    artifact truth preserved — reached by opposite arguments, and only the ORDER
    separates them. Proximity is never the evidence.
    """
    functions = {module.scopes[id(n)]: n for n in ast.walk(module.tree)
                 if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
                 and id(n) in module.scopes}
    read_positions: dict = {}
    for node in module.reads:
        owner = owner_of(module.scopes, node)
        function_node = functions.get(owner)
        if function_node is None:
            continue
        index = _body_index(function_node, node)
        if index is not None:
            read_positions[owner] = index

    sites = []
    for node in ast.walk(module.tree):
        if not isinstance(node, ast.Call):
            continue
        family = _is_write_call(node)
        if family is None:
            continue
        owner = owner_of(module.scopes, node)
        order = "UNKNOWN"
        if owner in read_positions:
            index = _body_index(functions[owner], node)
            if index is not None and index < read_positions[owner]:
                order = "BEFORE_READ"
            elif index is not None and index > read_positions[owner]:
                order = "AFTER_READ"
        sites.append({"function": owner, "lineno": node.lineno,
                      "expr": ast.unparse(node.func), "family": family,
                      "order": order})
    sites.sort(key=lambda s: (s["lineno"], s["expr"]))
    return {"enumeration": "BOUNDED",
            "looked_for": {"methods": list(WRITE_METHODS),
                           "dotted": list(WRITE_DOTTED),
                           "open_modes": list(WRITE_MODES)},
            "sites": sites,
            "ordered_before_read": sum(1 for s in sites if s["order"] == "BEFORE_READ"),
            "ordered_after_read": sum(1 for s in sites if s["order"] == "AFTER_READ"),
            "unordered": sum(1 for s in sites if s["order"] == "UNKNOWN")}


# ---------------------------------------------------------------------------
# Callers: static, dynamic, and what they reach
# ---------------------------------------------------------------------------


def _binding_key(expr: ast.expr) -> str:
    """The key a bound name is filed under, `self`/`cls` normalized away.

    `cls.module = load_legacy("foundry_definition_drift")` in `setUpClass` and
    `self.module.emit_reports()` in a test method are the SAME binding, and a
    key built from the unparsed expression files them apart — which is how a
    real dynamic consumer reads as having zero calls. Attribute bindings are
    keyed by the attribute name within the FILE, deliberately over-inclusive:
    two classes in one file sharing an attribute name would over-attribute a
    caller, and over-attribution reports an extra handler while under-attribution
    hides one. Only one of those two errors is safe here.
    """
    if isinstance(expr, ast.Attribute) and isinstance(expr.value, ast.Name) \
            and expr.value.id in ("self", "cls"):
        return expr.attr
    return ast.unparse(expr)


def _entry_calls(caller: Module, binding_keys: set) -> list:
    """`(entry function name, call node)` for calls through a bound name."""
    found = []
    for node in ast.walk(caller.tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) \
                and _binding_key(node.func.value) in binding_keys:
            found.append((node.func.attr, node))
    return found


def _reachability(candidate: Module, entry: str) -> dict:
    """Does `entry` reach a read owner — and is the negative answer trustworthy?

    THREE ANSWERS, NOT TWO. `True` comes with the paths that prove it. `False` is
    only returned when the candidate's call graph is COMPLETE over everything
    reachable from `entry`; if an unresolved edge sits anywhere on that reachable
    set, the answer is UNKNOWN, because a negative reachability claim is exactly
    as good as the graph it was computed on. This is the distinction that keeps
    "no path found" from being reported as "no path exists".
    """
    if entry in candidate._reachability:
        return candidate._reachability[entry]
    paths = []
    for owner in candidate.read_owners:
        path = call_path(candidate.edges, entry, owner)
        if path is not None:
            paths.append(" -> ".join(path))
    if paths:
        answer = {"reaches": True, "paths": sorted(paths), "unresolved": []}
    else:
        seen = reachable(candidate.edges, entry)
        frontier = [edge for edge in candidate.unresolved_edges
                    if edge["caller"] in seen]
        answer = ({"reaches": "UNKNOWN", "paths": [], "unresolved": frontier}
                  if frontier else
                  {"reaches": False, "paths": [], "unresolved": []})
    candidate._reachability[entry] = answer
    return answer


def _ancestors(edges: dict, target: str) -> set:
    """Every function that can reach `target`, `target` itself included."""
    return {name for name in set(edges) | {target}
            if target in reachable(edges, name)}


def _handlers_around(caller: Module, node: ast.AST) -> list:
    """Every handler that can catch a failure raised by `node`, with its origin.

    TWO KINDS, AND THE SECOND IS THE WHOLE POINT OF THIS MODULE. A DIRECT handler
    lexically encloses the call into the candidate. A TRANSITIVE handler encloses
    a call to a function OF THE CALLER that in turn reaches the call — which is
    exactly the C8.5T shape:

        main():                                  # <- the handler lives here
            try:
                a15 = a15_sizes_for_current_codebook()
            except SystemExit as e: ...

        def a15_sizes_for_current_codebook():
            result = run1.classify_run1_instances()   # <- the call is here

    `foundry_r5_attribution` has NO try around its call into
    `foundry_consolidate_run1`, so a scan that stopped at the lexical enclosure
    of the call site reports that file as unhandled — and C8.5T found the
    opposite BY HAND, after the cohort had already been drawn. The walk is up the
    caller's own call graph, so it terminates on the graph and needs no depth
    limit.
    """
    found = [{"try": try_node, "origin": "DIRECT", "through": None}
             for try_node in caller.tries_around(node)]
    owner = owner_of(caller.scopes, node)
    if owner == MODULE_SCOPE:
        return found
    for name, call in caller.calls_to(caller.ancestors_of(owner)):
        for try_node in caller.tries_around(call):
            if any(try_node is row["try"] for row in found):
                continue
            found.append({"try": try_node, "origin": "TRANSITIVE",
                          "through": f"{name} (line {call.lineno})"})
    return sorted(found, key=lambda row: (row["try"].lineno, row["origin"]))


def _caller_rows(caller: Module, candidate: Module, entries: list,
                 origin: str, model: dict) -> tuple:
    """Call rows and handler rows for one caller of one candidate.

    A HANDLER IS CHARGED ONLY WHEN THE CALL REACHES A READ OWNER, which is the
    correction C8.5T's finding demanded and C8.5V then had to re-derive by hand
    for fifteen candidates. `foundry_r5_attribution` wraps `clf.classify_a15` in
    `except SystemExit`, and that handler is entirely real — it simply cannot
    observe a read that `classify_a15` never reaches. A scan that stopped at
    "this caller has a try/except" would block a safe candidate; a scan that
    only read the candidate's own file would clear a blocked one.
    """
    calls, handlers = [], []
    for entry, node in entries:
        reach = _reachability(candidate, entry)
        calls.append({"caller": caller.rel.as_posix(), "origin": origin,
                      "lineno": node.lineno, "entry": entry,
                      "owner_in_caller": owner_of(caller.scopes, node),
                      "reaches_read_owner": reach["reaches"],
                      "reaching_paths": reach["paths"]})
        for row in _handlers_around(caller, node):
            handlers.append(_handler_row(caller.rel.as_posix(), origin, row,
                                         entry, node.lineno, reach, model))
    return calls, handlers


def _handler_row(caller_rel: str, origin: str, row: dict, entry: str,
                 lineno: int, reach: dict, model: dict) -> dict:
    """ONE handler row, and the ONLY place a handler's verdict is computed.

    Extracted rather than repeated (C8.5X.R2). The candidate's own handlers ask
    the identical question of the identical machinery — `handler_classes`,
    `handler_catchability`, and the two-condition observability rule below — so
    a second, local-only exception model cannot drift away from this one. The
    caller supplies WHERE the handler was found; nothing about the verdict
    depends on that.
    """
    classes = handler_classes(row["try"])
    catchability = (handler_catchability(classes, model) if classes else
                    {"legacy_caught": False, "permanent_caught": "NONE",
                     "permanent_caught_classes": [],
                     "permanent_uncaught_classes": [],
                     "transition": "NOT_A_HANDLER",
                     "changes_catchability": False,
                     "evidence": ["try/finally catches nothing"]})
    # TWO CONDITIONS, AND BOTH MUST HOLD. A handler observes the class change
    # only if the failure can REACH it and its catchability actually differs
    # across the transition. C8.5X asserted the first and assumed the second,
    # which made every reaching handler a blocker and contradicted C8.5R's
    # accepted `except BaseException` result.
    change = catchability["changes_catchability"]
    if change is False:
        observes = False
    elif change == "UNKNOWN" and reach["reaches"] is not False:
        observes = "UNKNOWN"
    elif reach["reaches"] == "UNKNOWN":
        observes = "UNKNOWN"
    else:
        observes = bool(reach["reaches"] is True)
    return {"caller": caller_rel, "origin": origin,
            "handler_origin": row["origin"], "through": row["through"],
            "lineno": lineno, "entry": entry,
            "try_lineno": row["try"].lineno,
            "catches": classes,
            "is_catching_handler": bool(classes),
            "catchability": catchability,
            "reaches_read_owner": reach["reaches"],
            # WHY, NOT JUST WHETHER (C8.5X.R3). `_reachability` has always
            # computed the unresolved frontier behind an UNKNOWN and every
            # caller dropped it, so a reviewer met a bare "UNKNOWN" with nothing
            # to check. Empty on a decided row, by construction.
            "unresolved_frontier": reach["unresolved"],
            "observes_failure_class_change": observes}


def _local_rows(candidate: Module, model: dict) -> list:
    """The candidate's OWN handlers around its OWN read — as a FORWARD pass.

    C8.5X.R2 established that a handler inside the candidate is a real handler:
    `_consumer_record` walks the universe for EXTERNAL callers and skips
    `rel == candidate.rel`, so `foundry_system_map.main` and
    `foundry_shape_extractor.codebook_covered_actions` — each performing
    `fcb.load_codebook()` directly inside `try/except Exception` — came back SAFE.

    R2 FOUND THOSE ROWS BY WALKING BACKWARD AND THAT DIRECTION HAS A FALSE-SAFE
    CLASS (C8.5X.R3, issue:1#issuecomment-5589050334). It reused
    `_handlers_around`, whose transitive arm asks `ancestors_of(read owner)` — a
    set built from RESOLVED edges only. So:

        def read_owner():
            return fcb.load_codebook()

        def helper():
            obj.read_owner()        # unresolved: an attribute names a function
                                    # this module defines
        def main():
            try:
                helper()            # resolved entry; its route to the read is UNKNOWN
            except Exception:
                return fallback

    `_reachability(helper)` is UNKNOWN — the unresolved edge sits on helper's
    frontier — but `helper` is not in `ancestors_of(read_owner)`, so the backward
    walk produced NO ROW AT ALL and the candidate classified SAFE. The importer
    side never had this hole, because `_caller_rows` asks `_reachability` per
    entry and can therefore say UNKNOWN. R2 declared the asymmetry a resolution
    boundary; it is not one, because the candidate's own unresolved edges have no
    second route into `record["unresolved"]` either. An absence the analyzer
    manufactured was being read as evidence.

    SO THE QUESTION IS ASKED FORWARD, FROM WHAT A `try` PROTECTS, in three
    surfaces — and every one of them ends at the SAME `_reachability` and the
    SAME `_handler_row` the importer rows use:

    1. DIRECT — the try protects the read itself. Reachability is not in doubt
       and is still asked rather than written in as True.
    2. TRANSITIVE, RESOLVED — the try protects a call to a local function.
       `True` charges the handler (this is R2's set, reproduced exactly);
       `False` does not charge it; `UNKNOWN` charges nothing and hides nothing —
       it emits the row carrying its frontier, which is the repair.
    3. TRANSITIVE, UNRESOLVED — the try protects one of the two unresolved-edge
       families `call_graph` already emits: a call through an object whose
       attribute names a function defined here, or a reference to a defined
       function handed to somebody else to call. The EDGE is the uncertainty, so
       these are UNKNOWN by construction; they are emitted only when the function
       named could reach a read owner, since one that provably cannot is not
       uncertainty about this migration.

    WHAT AN UNKNOWN ROW MAY AND MAY NOT DO IS NOT DECIDED HERE. It goes through
    `_handler_row` like every other row, so a SYMMETRIC_BOTH or NEITHER handler
    still observes nothing whatever its reachability — an unresolved route does
    not manufacture an asymmetric blocker — while a handler whose catchability
    WOULD change becomes undecided rather than absent, and `_classify` keeps
    UNKNOWN below a proven blocker and above SAFE.
    """
    rel = candidate.rel.as_posix()
    rows: dict = {}

    def add(try_node, origin, through, entry, lineno, reach):
        # Two read sites can share one enclosing try around one call that
        # reaches both, and a surface can be named by more than one family.
        # That is one handler, not several.
        key = (origin, entry, try_node.lineno, lineno)
        if key not in rows:
            rows[key] = _handler_row(
                rel, "LOCAL_READ",
                {"try": try_node, "origin": origin, "through": through},
                entry, lineno, reach, model)

    # 1. the try protects the read itself.
    direct = set()
    for node in sorted(candidate.reads, key=lambda n: n.lineno):
        owner = owner_of(candidate.scopes, node)
        reach = _reachability(candidate, owner)
        for try_node in candidate.tries_around(node):
            direct.add(id(try_node))
            add(try_node, "DIRECT", None, owner, node.lineno, reach)

    # 2. the try protects a resolved call to a local function.
    for callee, call in candidate.resolved_calls():
        reach = _reachability(candidate, callee)
        if reach["reaches"] is False:
            continue
        for try_node in candidate.tries_around(call):
            if id(try_node) in direct:
                continue
            add(try_node, "TRANSITIVE", f"{callee} (line {call.lineno})",
                callee, call.lineno, reach)

    # 3. the try protects an unresolved edge that names a local function.
    for node, edge in candidate.unresolved_surfaces:
        if _reachability(candidate, edge["defines"])["reaches"] is False:
            continue
        # NOT `_reachability`'s answer about the NAME. The name may well reach a
        # read owner -- it may BE one -- and that is not the question. The
        # question is whether THIS protected surface reaches the read, and the
        # edge into it is the thing nobody can resolve. So the answer is UNKNOWN
        # and the edge is the frontier that says why.
        reach = {"reaches": "UNKNOWN", "paths": [], "unresolved": [edge]}
        for try_node in candidate.tries_around(node):
            if id(try_node) in direct:
                continue
            add(try_node, "TRANSITIVE",
                f"{edge['expr']} (line {edge['lineno']}, unresolved)",
                edge["defines"], edge["lineno"], reach)

    return [rows[key] for key in sorted(rows)]


def _loader_calls(module) -> list:
    """Every dynamic-loader call in one file, its argument resolved ONCE.

    Three argument shapes are separated, and the third is what keeps the whole
    repository from reading as unresolved:

    * a LITERAL — `load_legacy("foundry_definition_drift")` names its module;
    * a MODULE CONSTANT — `spec_from_file_location(..., LEGACY_PATH)`, resolved
      one hop through `_module_constants`;
    * a PARAMETER of the enclosing function — `load_legacy`'s own body builds
      `EXPERIMENTS / f"{name}.py"`. That site is the loader DEFINITION and names
      no module at all; its call sites do, and they are analyzed as their own
      sites. Filing it as unresolved would make every candidate in the repository
      UNKNOWN on the strength of one generic three-line helper.

    Anything else is OPAQUE and is reported as such.
    """
    leaves = {name.rsplit(".", 1)[-1] for name in DYNAMIC_LOADERS}
    assigned: dict = {}
    for node in ast.walk(module.tree):
        if isinstance(node, ast.Assign) and isinstance(node.value, ast.Call):
            assigned[id(node.value)] = [_binding_key(t) for t in node.targets]
    rows = []
    for node in ast.walk(module.tree):
        if not isinstance(node, ast.Call):
            continue
        loader = ast.unparse(node.func)
        if loader.rsplit(".", 1)[-1] not in leaves:
            continue
        literal, resolved, opaque, parameterized = [], [], [], False
        for arg in node.args:
            if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                literal.append(Path(arg.value).stem)
                continue
            names = {n.id for n in ast.walk(arg) if isinstance(n, ast.Name)}
            hit = False
            for name in sorted(names):
                if name in module.constants:
                    resolved += [Path(part).stem for part in module.constants[name]]
                    hit = True
            if not hit:
                if names & module.parameters:
                    parameterized = True
                else:
                    opaque.append(ast.unparse(arg))
        rows.append({"node": node, "loader": loader,
                     "literal": set(literal), "resolved": set(resolved),
                     "opaque": sorted(opaque), "parameterized": parameterized,
                     "targets": assigned.get(id(node), [])})
    return rows


def _dynamic_sites(caller: Module, candidate: Module) -> tuple:
    """Dynamic loads of the candidate in one caller: sites, bindings, unresolved.

    A DYNAMIC LOAD IS REPORTED, NEVER PROMOTED. Whether the read executes still
    depends on what the caller calls on the loaded module, so the binding is
    resolved and its calls are measured for reachability exactly as a static
    import's are. The one exception is a read at MODULE scope, where loading IS
    executing — which is why `import_time_read` decides whether an unresolved
    loader argument is evidence about this candidate at all, rather than a
    permanent UNKNOWN charged to every file in the repository.
    """
    sites, bindings, unresolved = [], set(), []
    for row in caller.loader_calls:
        names = row["literal"] | row["resolved"]
        if candidate.name in names:
            sites.append({"caller": caller.rel.as_posix(),
                          "lineno": row["node"].lineno, "loader": row["loader"],
                          "argument": "LITERAL" if candidate.name in row["literal"]
                                      else "MODULE_CONSTANT"})
            bindings |= set(row["targets"])
            continue
        if row["opaque"]:
            unresolved.append({"caller": caller.rel.as_posix(),
                               "lineno": row["node"].lineno,
                               "loader": row["loader"],
                               "reason": "loader argument does not resolve to a "
                                         "module name",
                               "args": row["opaque"],
                               "inert_unless_import_time_read": True})
    return sites, sorted(bindings), unresolved


# ---------------------------------------------------------------------------
# The consumer record
# ---------------------------------------------------------------------------


def _classify(record: dict) -> str:
    """SAFE only when nothing blocks AND nothing is unresolved.

    The order is deliberate. A PROVEN blocker outranks an unresolved edge because
    it is the stronger statement and both are refusals; and UNKNOWN outranks SAFE
    unconditionally, which is the law this analyzer exists to make mechanical
    instead of remembered. `SAFE_NO_TRANSITIVE_HANDLER` remains a statement about
    ONE axis — C8.5V said so in prose and it is said here in the name — so a
    retained facade symbol is a blocker in `blockers`, not a downgrade here.
    """
    for handler in record["catching_handlers"]:
        if handler["observes_failure_class_change"] is not True:
            continue
        transition = handler["catchability"]["transition"]
        if transition in ("OLD_ONLY", "PARTIAL_OLD_ONLY"):
            return "BLOCK_SYSTEMEXIT_DEPENDENCY"
        if transition == "NEW_ONLY":
            return "BLOCK_EXCEPTION_CATCH"
        return "BLOCK_OTHER"
    if not record["read_sites"]:
        return "NOT_A_READ_CONSUMER"
    if record["failure_observability"]["status"] == "UNKNOWN":
        return "UNKNOWN"
    if record["bootstrap_dependency"]["status"] == "UNKNOWN":
        return "UNKNOWN"
    if record["unresolved"]:
        return "UNKNOWN"
    if record["failure_observability"]["status"] == "SYMMETRIC_CATCH_NO_CLASS_DELTA":
        # SAID AS ITS OWN VERDICT, not folded into the no-handler one. There IS a
        # reaching handler here; what there is not is a catchability delta. The
        # two facts have different consequences for a reviewer, and C8.5R's
        # accepted stderr question still applies to this row and not to the
        # other.
        return "SAFE_NO_FAILURE_CLASS_DELTA"
    return "SAFE_NO_TRANSITIVE_HANDLER"


def _observability(record: dict) -> dict:
    """What a reaching handler would see differently after the repoint.

    FOUR STATUSES, and the second one is the repair. A handler that catches BOTH
    sides is reported as a symmetric catch with NO class delta rather than as an
    observer — C8.5R accepted exactly that about `foundry_object_lattice`'s
    `except BaseException`, and the first cut of this module contradicted it.
    Symmetric is not promoted to "safe": the legacy STOP line on stderr still
    disappears for a translated failure, and that output delta is a different
    question, answered by `failure_model.legacy_side_effect`, not here.
    """
    handlers = record["catching_handlers"]
    observing = [h for h in handlers if h["observes_failure_class_change"] is True]
    undecided = [h for h in handlers
                 if h["observes_failure_class_change"] == "UNKNOWN"]
    symmetric = [h for h in handlers
                 if h["catchability"]["transition"] == "SYMMETRIC_BOTH"]
    neither = [h for h in handlers
               if h["catchability"]["transition"] == "NEITHER"]
    if observing:
        status = "CHANGED_BY_HANDLER"
    elif undecided or record["unresolved"] \
            or record["bootstrap_dependency"]["status"] == "UNKNOWN":
        status = "UNKNOWN"
    elif symmetric:
        status = "SYMMETRIC_CATCH_NO_CLASS_DELTA"
    else:
        status = "UNOBSERVED_NO_REACHING_HANDLER"
    return {"status": status,
            "observing_handlers": observing,
            "undecided_handlers": undecided,
            "symmetric_handlers": symmetric,
            "handlers_catching_neither_side": neither,
            "non_catching_try_sites": [h for h in handlers
                                       if not h["is_catching_handler"]],
            "handled_calls_not_reaching_read": [
                h for h in handlers
                if h["is_catching_handler"] and h["reaches_read_owner"] is False]}


def _blocker_kind(handler: dict) -> str:
    """`LOCAL_HANDLER` for the candidate's own try, `TRANSITIVE_HANDLER` for an
    importer's. The row already carries the distinction in `origin`; this is the
    same fact spelled where a reader of `blockers` alone will see it."""
    return ("LOCAL_HANDLER" if handler["origin"] == "LOCAL_READ"
            else "TRANSITIVE_HANDLER")


def _blockers(record: dict) -> list:
    """Everything standing between this candidate and a READ-only repoint.

    The retained facade symbols are listed here because C8.5V's honest reading
    of its own result says so: "SAFE on the handler criterion" is not "ready to
    repoint", and a record that reported only the handler answer would be read
    as the second thing.
    """
    out = []
    for symbol in record["facade_symbols_after_read_repoint"]:
        out.append({"kind": "RETAINED_FACADE_SYMBOL", "detail": symbol})
    for handler in record["failure_observability"]["observing_handlers"]:
        # NAMED BY WHERE IT LIVES (C8.5X.R2). A candidate-local handler is not a
        # transitive one, and calling it that in the blocker list would hide the
        # very distinction this repair exists to restore.
        out.append({"kind": _blocker_kind(handler),
                    "detail": f"{handler['caller']}:{handler['try_lineno']} "
                              f"catches {'|'.join(handler['catches'])} around "
                              f"{handler['entry']}: "
                              f"{handler['catchability']['transition']}"})
    for handler in record["failure_observability"]["undecided_handlers"]:
        out.append({"kind": f"{_blocker_kind(handler)}_UNKNOWN",
                    "detail": f"{handler['caller']}:{handler['try_lineno']} "
                              f"catches {'|'.join(handler['catches'])} around "
                              f"{handler['entry']}: "
                              f"{handler['catchability']['transition']}, "
                              f"reachability {handler['reaches_read_owner']}"})
    if record["bootstrap_dependency"]["status"] == "UNKNOWN":
        out.append({"kind": "BOOTSTRAP_UNKNOWN",
                    "detail": "; ".join(record["bootstrap_dependency"]["evidence"])})
    for item in record["unresolved"]:
        out.append({"kind": "UNRESOLVED_EVIDENCE",
                    "detail": f"{item['caller']}: {item['reason']}"})
    return sorted(out, key=lambda r: (r["kind"], r["detail"]))


def _consumer_record(candidate: Module, universe: dict,
                     model: dict) -> dict:
    calls: list = []
    handlers: list = []
    static_importers: list = []
    dynamic_sites: list = []
    unresolved: list = []
    inert_dynamic: list = []

    # THE CANDIDATE'S OWN HANDLERS, FIRST AND SEPARATELY (C8.5X.R2). The loop
    # below is the EXTERNAL-caller loop and skips `rel == candidate.rel` for a
    # good reason -- a module is not its own importer, and listing it as one
    # would put it in `static_importers`. But that skip also deleted every
    # handler the candidate has around its own read, which is the shortest
    # reaching path there is. `_local_rows` supplies exactly those, tagged
    # `origin: LOCAL_READ` so a reader can tell them from an importer's.
    handlers += _local_rows(candidate, model)

    for rel, caller in sorted(universe.items()):
        if rel == candidate.rel:
            continue
        bindings = caller.bindings_for(candidate.name)
        if bindings["star"]:
            unresolved.append({"caller": caller.rel.as_posix(),
                               "reason": "star import of the candidate; the "
                                         "bound names cannot be enumerated"})
        if bindings["aliases"] or bindings["symbols"]:
            entries = _entry_calls(caller, set(bindings["aliases"]))
            for node in ast.walk(caller.tree):
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) \
                        and node.func.id in bindings["symbols"]:
                    entries.append((bindings["symbols"][node.func.id], node))
            static_importers.append({"caller": caller.rel.as_posix(),
                                     "aliases": bindings["aliases"],
                                     "symbols": sorted(bindings["symbols"].values()),
                                     "call_count": len(entries)})
            new_calls, new_handlers = _caller_rows(caller, candidate, entries,
                                                   "STATIC_IMPORT", model)
            calls += new_calls
            handlers += new_handlers

        sites, dyn_bindings, dyn_unresolved = _dynamic_sites(caller, candidate)
        for item in dyn_unresolved:
            (unresolved if candidate.import_time_read else inert_dynamic).append(item)
        if sites:
            entries = _entry_calls(caller, set(dyn_bindings))
            dynamic_sites.append({"caller": caller.rel.as_posix(), "sites": sites,
                                  "bindings": dyn_bindings,
                                  "call_count": len(entries)})
            new_calls, new_handlers = _caller_rows(caller, candidate, entries,
                                                   "DYNAMIC_LOAD", model)
            calls += new_calls
            handlers += new_handlers

    if candidate.facade["star"]:
        unresolved.append({"caller": candidate.rel.as_posix(),
                           "reason": "star import of the facade; the read "
                                     "binding cannot be resolved"})

    symbols = facade_symbol_references(candidate.tree, candidate.facade)
    retained = [s for s in symbols if s != READ_SYMBOL]
    record = {
        "module": candidate.rel.as_posix(),
        "facade_bindings": {"aliases": candidate.facade["aliases"],
                            "symbols": dict(sorted(candidate.facade["symbols"].items())),
                            "star": candidate.facade["star"]},
        "read_sites": [{"lineno": n.lineno, "expr": ast.unparse(n.func),
                        "owner": owner_of(candidate.scopes, n),
                        "argument_count": len(n.args) + len(n.keywords)}
                       for n in sorted(candidate.reads, key=lambda n: n.lineno)],
        "read_owner_functions": candidate.read_owners,
        "import_time_read": candidate.import_time_read,
        "static_importers": sorted(static_importers, key=lambda r: r["caller"]),
        "dynamic_loader_sites": sorted(dynamic_sites, key=lambda r: r["caller"]),
        "dynamic_loads_inert_for_this_candidate": sorted(
            inert_dynamic, key=lambda r: (r["caller"], r["lineno"])),
        "reaching_call_paths": sorted(
            calls, key=lambda r: (r["caller"], r["lineno"], r["entry"])),
        "catching_handlers": sorted(
            handlers, key=lambda r: (r["caller"], r["lineno"], r["try_lineno"],
                                     r["handler_origin"])),
        "failure_model_status": model["status"],
        "bootstrap_dependency": bootstrap_dependency(candidate, universe),
        "facade_symbols": symbols,
        "facade_symbols_after_read_repoint": retained,
        "facade_disposition": "SPLIT" if retained else "DROP_AFTER_READ_REPOINT",
        "output_truth_boundary": output_truth_boundary(candidate),
        "unresolved": sorted(unresolved,
                             key=lambda r: (r["caller"], r.get("lineno", 0),
                                            r["reason"])),
    }
    record["failure_observability"] = _observability(record)
    record["blockers"] = _blockers(record)
    record["classification"] = _classify(record)
    return record


# ---------------------------------------------------------------------------
# Entry points
# ---------------------------------------------------------------------------


def _universe(root: Path) -> dict:
    modules = {}
    for rel in python_files(root):
        try:
            modules[rel] = Module(root, rel)
        except SyntaxError as error:
            raise SystemExit(f"STOP — {rel.as_posix()} does not parse: {error}")
    return modules


def _totals(records: list) -> dict:
    totals: dict = {}
    for record in records:
        totals[record["classification"]] = totals.get(record["classification"], 0) + 1
    return dict(sorted(totals.items()))


def _failure_model(universe: dict) -> dict:
    """The derived transition plus the hierarchy every catchability test needs."""
    model = failure_transition(universe)
    model["hierarchy"] = class_hierarchy(universe)
    return model


def analyze_repository(root) -> dict:
    """The whole facade read population, one record per read-owning file."""
    root = Path(root)
    universe = _universe(root)
    model = _failure_model(universe)
    fan_in = sorted(rel.as_posix() for rel, m in universe.items()
                    if m.facade["aliases"] or m.facade["symbols"] or m.facade["star"])
    read_owning = sorted((rel for rel, m in universe.items() if m.reads),
                         key=lambda rel: rel.as_posix())
    records = [_consumer_record(universe[rel], universe, model)
               for rel in read_owning]
    return {
        "schema": SCHEMA,
        "facade": {"module": FACADE_MODULE, "read_symbol": READ_SYMBOL},
        "failure_model": {k: v for k, v in sorted(model.items())
                          if k != "hierarchy"},
        "population": {
            "python_files": len(universe),
            "facade_fan_in_files": len(fan_in),
            "facade_fan_in": fan_in,
            "facade_read_call_sites": sum(len(m.reads) for m in universe.values()),
            "facade_read_owning_files": len(read_owning),
            "read_owning": [rel.as_posix() for rel in read_owning],
        },
        "classification_totals": _totals(records),
        "consumers": records,
    }


def analyze_consumer(root, module_path) -> dict:
    """One consumer record, with the same repository-wide caller evidence."""
    root = Path(root)
    rel = Path(module_path)
    if rel.is_absolute():
        rel = rel.relative_to(root)
    universe = _universe(root)
    if rel not in universe:
        raise SystemExit(f"STOP — {rel.as_posix()} is not in the analysis universe")
    return _consumer_record(universe[rel], universe, _failure_model(universe))


def main(argv=None) -> int:
    """JSON to stdout, and nothing else. No file is written, ever."""
    parser = argparse.ArgumentParser(
        description="Static analysis of the foundry_codebook read consumers.")
    parser.add_argument("--root", default=str(Path(__file__).resolve().parents[2]))
    parser.add_argument("--module", default=None,
                        help="analyze one consumer instead of the repository")
    args = parser.parse_args(argv)
    root = Path(args.root).resolve()
    result = (analyze_consumer(root, args.module) if args.module
              else analyze_repository(root))
    json.dump(result, sys.stdout, indent=2, sort_keys=False)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
