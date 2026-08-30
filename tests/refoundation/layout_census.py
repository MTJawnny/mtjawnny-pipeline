"""C8 step-5 layout / delegation census — the repaired measurement surface.

Stdlib only, fully static, and read-only. Nothing here imports or executes a
legacy module, and nothing here reads a path by asking a running module for it.

WHY THIS MODULE EXISTS
----------------------
The P0.4-era census (issue:1#issuecomment-5470371439) discovered a module's
layout PROVIDERS by following a module-level ``Path(__file__)`` chain: a name
counted as a provider only if its value was, transitively, a join off a locally
derived root. That rule was true of `foundry_common` for the whole P0.4 arc.

C8.5A ended it. The compatibility boundary now reads

    _PATHS = ProjectPaths.for_root(_BOOTSTRAP_ROOT)
    REPO_ROOT       = _PATHS.root
    FOUNDRY_OUT_DIR = _PATHS.legacy_foundry_out
    REVIEW_DIR      = _PATHS.legacy_foundry_review

so none of the three public providers is a ``Path(__file__)`` join any more, and
a chain-only rule stops seeing them. The downstream expressions did not move —
GitHub verifies C8.5A changed no consumer — but the census that counts them
collapses. That is a MEASUREMENT defect, and the Manager blocked further
census-driven Step-5 selection on repairing it
(issue:1#issuecomment-5471350993, `STEP5_MEASUREMENT_SURFACE_STALE_AFTER_C8_5A`).

`legacy_chain_provider_layout()` below is a reimplementation of the OLD rule,
kept deliberately so the defect stays demonstrable in a committed test rather
than surviving as a claim in a result comment.

WHAT IS MEASURED, AS FIVE SEPARATE THINGS
-----------------------------------------
These are different questions with different answers and the arc has already
paid for conflating two of them, so each has its own function and its own name:

1. RAW TEXTUAL OCCURRENCE — the literal substring `fc.FOUNDRY_OUT_DIR` in a
   file's bytes. Counts comments, docstrings and shell commands.
2. DELEGATION REFERENCE — an AST attribute load of a resolved provider name
   through a verified import alias, classified by what the reference DOES.
3. INDEPENDENT LOCAL-LAYOUT SITE — a repository-relative path stated locally
   rather than obtained from a provider.
4. REAL sys.path CALL SITE — an AST call node, which is not the same set as the
   lines carrying the text `sys.path.insert`.
5. COMPATIBILITY-BOUNDARY STATEMENT — what `foundry_common` itself still states.

RESOLUTION IS TO A REPOSITORY-RELATIVE TUPLE, NOT TO A BOOLEAN
--------------------------------------------------------------
Every provider resolves to a tuple of path components under the repository root
(`()` is the root itself). A provider that resolves to the WRONG tuple is
therefore a red guard rather than an unnoticed pass — which is what makes an
intentionally wrong `ProjectPaths` property detectable at all. A census that
only asked "is this a provider?" would score a wrong mapping as healthy.
"""

from __future__ import annotations

import ast
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path

# The provider modules whose exported layout names other legacy modules consume.
# Aliases are DERIVED from each file's own import statements, never assumed:
# `fc` and `fcb` are what the corpus happens to use today, and a census that
# hardcoded them would silently miss a third.
PROVIDER_MODULES = ("foundry_common", "foundry_codebook")

LEGACY_PRODUCTION = ("experiments", "experiments_measure")

_SYS_PATH_TEXT = re.compile(r"sys\.path\.(?:insert|append)")


# ---------------------------------------------------------------------------
# Universe and scope
# ---------------------------------------------------------------------------


def tracked_python(root: Path) -> list[Path]:
    """Every tracked `.py` file, repository-relative, sorted.

    `git ls-files` is a read-only query about the repository, not project code.
    `walked_python()` is the independent cross-check: a census silently narrowed
    by an ignore rule would report a smaller universe and look healthy.
    """
    out = subprocess.run(["git", "-C", str(root), "ls-files", "*.py"],
                         capture_output=True, text=True, check=True).stdout
    return sorted(Path(line) for line in out.splitlines() if line)


def walked_python(root: Path) -> list[Path]:
    """The same universe derived from the filesystem, for cross-checking."""
    found = []
    for base in ("experiments", "pipeline", "src", "tests"):
        for path in (root / base).rglob("*.py"):
            if "__pycache__" in path.parts:
                continue
            found.append(path.relative_to(root))
    return sorted(found)


def scope_of(rel: Path) -> str:
    """Which measurement bucket a file belongs to.

    AQ4 is PAUSED and is therefore excluded from every legacy-production count.
    It lives in two places — the `experiments/aq4_benchmark/` package and
    `experiments/foundry_aq4_probes.py` — so a directory test alone would leave
    one AQ4 file inside the production scope.
    """
    posix = rel.as_posix()
    if posix.startswith("experiments/aq4_benchmark/") or "aq4" in rel.name:
        return "aq4_PAUSED"
    if posix.startswith("experiments/measure/"):
        return "experiments_measure"
    if posix.startswith("experiments/"):
        return "experiments"
    if posix.startswith("pipeline/"):
        return "pipeline"
    if posix.startswith("tests/"):
        return "tests"
    if posix.startswith("src/"):
        return "src"
    return "other"


# ---------------------------------------------------------------------------
# Static resolution of `mtj_foundry.paths.ProjectPaths`
# ---------------------------------------------------------------------------


def project_paths_layout(paths_source: str) -> dict[str, tuple[str, ...]]:
    """Resolve every `ProjectPaths` property to repository-relative components.

    Parsed from `src/mtj_foundry/paths.py` rather than imported. Importing the
    package would be executing project code to learn a layout fact, which is the
    habit this whole arc is removing; parsing also means an intentionally wrong
    property body is visible as a wrong TUPLE.

    Each property body is `return self.<other> / "<literal>"` or `return
    self.root`, so resolution is a small fixpoint over the property graph.
    """
    bodies: dict[str, ast.expr] = {}
    for node in ast.walk(ast.parse(paths_source)):
        if not isinstance(node, ast.FunctionDef):
            continue
        if not any(isinstance(d, ast.Name) and d.id == "property"
                   for d in node.decorator_list):
            continue
        returns = [n for n in node.body if isinstance(n, ast.Return) and n.value]
        if len(returns) == 1:
            bodies[node.name] = returns[0].value

    resolved: dict[str, tuple[str, ...]] = {"root": ()}

    def evaluate(expr: ast.expr) -> tuple[str, ...] | None:
        if isinstance(expr, ast.Attribute) and isinstance(expr.value, ast.Name) \
                and expr.value.id == "self":
            return resolved.get(expr.attr)
        if isinstance(expr, ast.BinOp) and isinstance(expr.op, ast.Div):
            left = evaluate(expr.left)
            right = expr.right
            if left is None or not (isinstance(right, ast.Constant)
                                    and isinstance(right.value, str)):
                return None
            return left + (right.value,)
        return None

    changed = True
    while changed:
        changed = False
        for name, body in bodies.items():
            if name in resolved:
                continue
            value = evaluate(body)
            if value is not None:
                resolved[name] = value
                changed = True
    return resolved


# ---------------------------------------------------------------------------
# Static resolution of a module's own layout names
# ---------------------------------------------------------------------------


def _file_chain_hops(expr: ast.expr) -> int | None:
    """How many parent-directory hops a `__file__` chain takes FROM THE FILE.

    None when the expression is not rooted at `__file__` at all.

    THE UNIT IS HOPS FROM THE FILE, NOT FROM ITS DIRECTORY, and that choice is
    what makes the two pathlib spellings agree. `pathlib` numbers `parents`
    from 1: `p.parents[0]` IS `p.parent`, so `parents[N]` costs **N + 1** hops,
    not N. Counting it as N while counting `.parent` as 1 makes these pairs
    disagree, and they denote the same directory:

        Path(__file__).resolve().parent        == ....parents[0]
        Path(__file__).resolve().parent.parent == ....parents[1]
        ....parent.parent.parent               == ....parents[2]

    C8.5B shipped exactly that inconsistency (`.parent` -> 1 while
    `parents[0]` -> 0, and a docstring that contradicted its own code). It moved
    no accepted count, because the only chain-backed providers in the corpus are
    spelled `parents[1]` and the local-site scan only asks whether a chain
    EXISTS. It was still a live wrong answer waiting for a provider spelled the
    other way: `.parent` resolved to the repository ROOT when it means the
    module's own directory — a WRONG tuple, not a missing one, which is the
    failure mode that passes quietly. Repaired under C8.5B.R1
    (issue:1#issuecomment-5471544666).
    """
    if not any(isinstance(n, ast.Name) and n.id == "__file__"
               for n in ast.walk(expr)):
        return None
    hops = 0
    node = expr
    while True:
        if isinstance(node, ast.Subscript) and isinstance(node.value, ast.Attribute) \
                and node.value.attr == "parents" \
                and isinstance(node.slice, ast.Constant) \
                and isinstance(node.slice.value, int):
            hops += node.slice.value + 1
            node = node.value.value
            continue
        if isinstance(node, ast.Attribute) and node.attr == "parent":
            hops += 1
            node = node.value
            continue
        if isinstance(node, ast.Attribute) and node.attr == "resolve":
            node = node.value
            continue
        if isinstance(node, ast.Call):
            node = node.func
            continue
        if isinstance(node, ast.Attribute):
            node = node.value
            continue
        break
    return hops


def _root_relative(rel: Path, hops: int) -> tuple[str, ...] | None:
    """Turn a hop count into repository-relative components, or None.

    Measured from the FILE's own path, so the arithmetic is one subtraction and
    needs no special case: `experiments/foundry_common.py` has 2 components, so
    2 hops (`parents[1]` or `.parent.parent`) leaves `()`, the repository root,
    and 1 hop (`parents[0]` or `.parent`) leaves `("experiments",)`.

    None means the chain ascends ABOVE the repository root, which no
    repository-relative tuple can express. That is a real answer, not a failure:
    `experiments/foo.py` with `parents[2]` genuinely names the root's parent.
    """
    keep = len(rel.parts) - hops
    if keep < 0:
        return None
    return rel.parts[:keep]


def _join_literals(expr: ast.expr) -> tuple[ast.expr, tuple[str, ...]] | None:
    """Split a `/`-join into its base expression and its string components."""
    parts: list[str] = []
    node = expr
    while isinstance(node, ast.BinOp) and isinstance(node.op, ast.Div):
        if not (isinstance(node.right, ast.Constant)
                and isinstance(node.right.value, str)):
            return None
        parts.insert(0, node.right.value)
        node = node.left
    return node, tuple(parts)


def provider_layout(source: str, rel: Path,
                    paths_layout: dict[str, tuple[str, ...]]
                    ) -> dict[str, tuple[str, ...]]:
    """Repository-relative layout names a module EXPORTS, resolved to components.

    THIS IS THE REPAIR. Three provider shapes are understood, and the second is
    the one the P0.4-era rule could not see:

    1. a `Path(__file__)` ascent, optionally joined with string literals —
       `REPO_ROOT = Path(__file__).resolve().parents[1]` (the pre-C8.5A shape,
       and still the shape of `foundry_codebook`, which has NOT been migrated);
    2. a `ProjectPaths` property read through a locally constructed instance —
       `FOUNDRY_OUT_DIR = _PATHS.legacy_foundry_out` (the C8.5A shape);
    3. a join off a name already resolved by 1 or 2 — the old
       `REVIEW_DIR = FOUNDRY_OUT_DIR / "review"` hop.

    Module scope only: a provider is a name an importer can read, and a
    function-local binding is not one.
    """
    tree = ast.parse(source)
    instances: set[str] = set()
    resolved: dict[str, tuple[str, ...]] = {}

    def evaluate(expr: ast.expr) -> tuple[str, ...] | None:
        # 2. a ProjectPaths property through a local instance.
        if isinstance(expr, ast.Attribute) and isinstance(expr.value, ast.Name) \
                and expr.value.id in instances:
            return paths_layout.get(expr.attr)
        # 1. a bare `Path(__file__)` ascent.
        hops = _file_chain_hops(expr)
        if hops is not None:
            return _root_relative(rel, hops)
        split = _join_literals(expr)
        if split is not None and split[1]:
            base, parts = split
            head = evaluate(base)
            if head is not None:
                return head + parts
        # 3. a name already resolved in this module.
        if isinstance(expr, ast.Name) and expr.id in resolved:
            return resolved[expr.id]
        return None

    for _ in range(len(tree.body)):
        changed = False
        for statement in tree.body:
            if not isinstance(statement, ast.Assign):
                continue
            names = [t.id for t in statement.targets if isinstance(t, ast.Name)]
            if not names:
                continue
            value = statement.value
            if isinstance(value, ast.Call) and isinstance(value.func, ast.Attribute) \
                    and value.func.attr == "for_root" \
                    and isinstance(value.func.value, ast.Name) \
                    and value.func.value.id == "ProjectPaths":
                for name in names:
                    if name not in instances:
                        instances.add(name)
                        changed = True
                continue
            components = evaluate(value)
            if components is None:
                continue
            for name in names:
                if resolved.get(name) != components:
                    resolved[name] = components
                    changed = True
        if not changed:
            break
    return resolved


def legacy_chain_provider_layout(source: str, rel: Path) -> dict[str, tuple[str, ...]]:
    """The PRE-REPAIR rule, reimplemented so the defect stays demonstrable.

    Follows only shape 1 and shape 3 above — a module-level `Path(__file__)`
    chain and joins off it. Reimplemented here from its description in the P0.4P
    result; the original scanner was worker-local and never committed, so this is
    a reconstruction of the rule, not a copy of the code. What it demonstrates is
    structural and does not depend on that distinction: a chain-only rule cannot
    see a `ProjectPaths`-backed provider.
    """
    return provider_layout(source, rel, paths_layout={})


def provider_aliases(source: str) -> dict[str, str]:
    """`{alias: provider module}` from this file's OWN import statements."""
    aliases = {}
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.Import):
            for name in node.names:
                if name.name in PROVIDER_MODULES:
                    aliases[name.asname or name.name] = name.name
        elif isinstance(node, ast.ImportFrom) and node.module in PROVIDER_MODULES:
            for name in node.names:
                aliases[name.asname or name.name] = node.module
    return aliases


# ---------------------------------------------------------------------------
# The five measurements
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Reference:
    """One AST load of a provider layout name, classified by what it does."""
    path: str
    lineno: int
    alias: str
    module: str
    name: str
    form: str
    expr: str


@dataclass(frozen=True)
class Site:
    """One repository-relative layout fact stated locally by a module."""
    path: str
    lineno: int
    origin: str      # hop1 | hop2 | inline
    scope: str       # module | <function name>
    bootstrap: bool  # consumed by a real sys.path call
    expr: str


def _parents(tree: ast.AST) -> dict[int, ast.AST]:
    links = {}
    for node in ast.walk(tree):
        for child in ast.iter_child_nodes(node):
            links[id(child)] = node
    return links


def _function_scopes(tree: ast.AST) -> dict[int, str]:
    scopes = {}
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for inner in ast.walk(node):
                scopes.setdefault(id(inner), node.name)
    return scopes


def sys_path_call_nodes(tree: ast.AST) -> list[ast.Call]:
    """REAL `sys.path.insert/append` call nodes.

    Anchored to the CALL, which is what separates this module's own bootstrap
    from the literal text `sys.path.insert` appearing inside an f-string that
    builds a shell command. P0.4N classified that site by a text match and got it
    wrong; the correction is preserved here as structure, not as a comment.
    """
    calls = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        if (isinstance(func, ast.Attribute) and func.attr in ("insert", "append")
                and isinstance(func.value, ast.Attribute)
                and func.value.attr == "path"
                and isinstance(func.value.value, ast.Name)
                and func.value.value.id == "sys"):
            calls.append(node)
    return calls


def sys_path_text_lines(source: str) -> list[int]:
    """Every line carrying the TEXT `sys.path.insert`/`append`, call or not."""
    return [i for i, line in enumerate(source.splitlines(), 1)
            if _SYS_PATH_TEXT.search(line)]


def delegation_references(source: str, rel: Path,
                          provider_names: dict[str, dict[str, tuple[str, ...]]]
                          ) -> list[Reference]:
    """Provider layout names consumed by this file, one row per AST load.

    Classified by FORM, because "how many delegations are there" and "how many
    times does this text appear" are different questions and the arc has already
    been warned not to equate them:

    * `PATH_JOIN` — the provider is the base of a `/` join. A repository-relative
      path is BUILT from it. This is the delegation a migration inherits.
    * `DIRECT_BIND` — the provider value is bound to a local name unchanged. No
      new layout is stated; the local name is an alias for the provider.
    * `ATTRIBUTE_NAV` — the provider is navigated with `.parent`, which states a
      layout fact the provider's own vocabulary does not contain.
    * `CALL_ARG` — the value is passed to a call (`relative_to(...)`). It is a
      use of the root, not a construction of a path.
    """
    tree = ast.parse(source)
    aliases = provider_aliases(source)
    links = _parents(tree)
    found = []
    for node in ast.walk(tree):
        if not (isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name)):
            continue
        module = aliases.get(node.value.id)
        if module is None or node.attr not in provider_names.get(module, {}):
            continue
        parent = links.get(id(node))
        if isinstance(parent, ast.BinOp) and isinstance(parent.op, ast.Div) \
                and parent.left is node:
            form = "PATH_JOIN"
        elif isinstance(parent, ast.Attribute):
            form = "ATTRIBUTE_NAV"
        elif isinstance(parent, ast.Call):
            form = "CALL_ARG"
        elif isinstance(parent, ast.Assign):
            form = "DIRECT_BIND"
        else:
            form = "OTHER"
        found.append(Reference(rel.as_posix(), node.lineno, node.value.id,
                               module, node.attr, form, ast.unparse(node)))
    return found


def local_layout_sites(source: str, rel: Path) -> list[Site]:
    """Repository-relative layout stated locally rather than obtained.

    A site is an OUTERMOST `/` join carrying at least one string literal whose
    base is a locally derived root. The three shapes the negative controls
    require are all reachable: a module-level hop-1 constant, a hop-2 constant
    derived from it, and an inline `Path(__file__)` chain with no named root —
    at module scope or inside a function.

    Outermost only. `ROOT / "a" / "b"` is left-nested, so counting every matching
    BinOp scores one site up to three times; that double count is recorded four
    times in this arc and is fixed here rather than absorbed into an expectation.

    EVERY component must be a string literal. `ROOT / relative_name` joins a
    RUNTIME value and states no layout fact of its own, so it is not a site —
    the same rule the ratified checkers already apply. And a root used with no
    join at all (`sys.path.insert(0, str(REPO_ROOT))`) is not a site either: it
    re-adds a directory the module is already in. 53 modules bind `REPO_ROOT` to
    `experiments` rather than to the repository root, so counting those would
    fill the census with non-facts.

    (The literal test lives in `_join_literals`, which returns None as soon as a
    component is not a string. An earlier draft ALSO tested `not split[1]` here;
    a mutation drill showed that branch was unreachable and it was removed rather
    than left as a guard that cannot fail.)
    """
    tree = ast.parse(source)
    scopes = _function_scopes(tree)

    origins: dict[str, str] = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and _file_chain_hops(node.value) is not None:
            for target in node.targets:
                if isinstance(target, ast.Name):
                    origins[target.id] = "hop1"
    for _ in range(len(tree.body)):
        changed = False
        for node in ast.walk(tree):
            if not (isinstance(node, ast.Assign)
                    and isinstance(node.value, ast.BinOp)
                    and isinstance(node.value.op, ast.Div)):
                continue
            split = _join_literals(node.value)
            if split is None:
                continue
            base = split[0]
            if isinstance(base, ast.Attribute):
                base = base.value
            if not (isinstance(base, ast.Name) and base.id in origins):
                continue
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id not in origins:
                    origins[target.id] = "hop2"
                    changed = True
        if not changed:
            break

    bootstrap_nodes = {id(inner) for call in sys_path_call_nodes(tree)
                       for inner in ast.walk(call)}

    matches: list[tuple[ast.BinOp, str]] = []
    for node in ast.walk(tree):
        if not (isinstance(node, ast.BinOp) and isinstance(node.op, ast.Div)):
            continue
        split = _join_literals(node)
        if split is None:
            continue
        base = split[0]
        if _file_chain_hops(base) is not None:
            origin = "inline"
        else:
            named = base.value if isinstance(base, ast.Attribute) else base
            if not (isinstance(named, ast.Name) and named.id in origins):
                continue
            origin = origins[named.id]
        matches.append((node, origin))

    nested = {id(inner) for node, _ in matches
              for inner in ast.walk(node) if inner is not node}
    return [Site(rel.as_posix(), node.lineno, origin,
                 scopes.get(id(node), "module"),
                 id(node) in bootstrap_nodes, ast.unparse(node))
            for node, origin in matches if id(node) not in nested]


def raw_textual_occurrences(source: str, expression: str) -> int:
    """Literal substring count, comments and shell commands included."""
    return len(re.findall(re.escape(expression), source))
