"""Repository layout and root resolution — the ONE owner of both.

## Why this module exists

Measured in P0.1 and confirmed by the P0.2 Manager review: the legacy shared
foundation derives the repository root itself, mutates `sys.path`, and imports an
engine module at import time, so the foundation depends upward on the engine.
Roughly 97 sites derive a root or hardcode layout independently.

## What this module is NOT

P0.2 correction C1 rejected the stronger P0.1 proposal that one module may touch
the filesystem and that importing it asserts a repository is present. Both are
refused here, deliberately:

- **No global `ROOT`.** There is no module-level root constant to import.
- **No import-time discovery.** Importing this module runs no git search, reads
  no filesystem, and raises nothing. An installed package, a test fixture, a
  detached worktree, an archive, or an arbitrary root must all stay usable.
- **Ordinary libraries are not banned from I/O.** They receive an explicit
  `ProjectPaths` (or a plain `Path`) from the composition boundary; they simply
  do not rediscover the repository or restate its layout.

The invariant this module carries is therefore: *exactly one component defines
repository-relative layout and default root resolution.*

`discover_root()` exists for the CLI/composition boundary and is EXPLICITLY
CALLED. It halts loudly when it cannot find a root, which is house style for an
explicit request — the refused behavior is halting merely because someone
imported a library.
"""

from __future__ import annotations

import dataclasses
import os
from pathlib import Path

__all__ = ["ProjectPaths", "RootNotFound", "discover_root"]

# The marker that identifies a repository root when discovery is explicitly asked
# for. Kept here because layout knowledge lives in exactly one module.
_ROOT_MARKERS: tuple[str, ...] = (".git",)


class RootNotFound(RuntimeError):
    """Explicit root discovery failed. Never raised at import time."""


def _absolute_lexical(root: str | os.PathLike[str]) -> Path:
    """Make a root absolute and lexically stable. Touches no filesystem.

    `os.getcwd()` is read only to anchor a relative root at construction time, which
    is the whole point: after this returns, no later `chdir` can change what the
    object derives. It is not a probe of the root — nothing is stat-ed, opened,
    resolved, or searched for.
    """
    raw = os.fspath(root)
    absolute = raw if os.path.isabs(raw) else os.path.join(os.getcwd(), raw)
    return Path(os.path.normpath(absolute))


@dataclasses.dataclass(frozen=True)
class ProjectPaths:
    """An immutable, explicit view of repository layout rooted at `root`.

    Construction touches NO filesystem: no existence check, no stat, no
    `Path.resolve()`, no discovery. A caller may build one for a root that does not
    exist — a test fixture, a planned destination, a remote checkout — and every
    derived path is a pure string join.

    The root is normalized to an absolute lexical path once, at construction, so the
    object is stable: changing the process working directory afterwards cannot change
    any path it derives.

    That normalization lives in `__post_init__`, NOT in the `for_root` classmethod,
    which is what makes it an invariant rather than a convention. A dataclass is
    directly constructible — `ProjectPaths(root=Path("rel"))` — so a rule enforced
    only by an alternative constructor is enforced only for callers who happen to use
    it. Every supported construction path now yields an absolute, lexically stable
    root, including `dataclasses.replace`.
    """

    root: Path

    def __post_init__(self) -> None:
        object.__setattr__(self, "root", _absolute_lexical(self.root))

    # ---- construction ---------------------------------------------------
    @classmethod
    def for_root(cls, root: str | os.PathLike[str]) -> "ProjectPaths":
        """Build paths for an EXPLICIT root. The only supported constructor.

        The root is made **absolute lexically, once, at construction**. Storing a
        relative root verbatim left the object cwd-dependent: two calls to the same
        property from different working directories returned different files, so the
        object was not the stable description of a layout it claims to be. A caller
        passing `.` means "the directory I am in now", not "wherever anyone happens
        to chdir to later".

        Lexical means lexical. This does NOT verify the root exists, does not stat
        it, does not call `Path.resolve()` (which would touch the filesystem and
        follow symlinks), and does not search for a repository. `..` is collapsed
        textually. An arbitrary or nonexistent root therefore stays valid, which is
        what C1 requires.

        Normalization itself happens in `__post_init__`, so this classmethod is a
        named entry point rather than the thing that enforces the invariant.
        """
        return cls(root=Path(os.fspath(root)))

    # ---- refoundation layout (current) ----------------------------------
    @property
    def src(self) -> Path:
        return self.root / "src"

    @property
    def tests(self) -> Path:
        return self.root / "tests"

    @property
    def config(self) -> Path:
        return self.root / "config"

    @property
    def baselines(self) -> Path:
        """Tracked ratchet/control baselines.

        P0.2 accepted that control inputs which govern acceptance must be tracked
        and reviewable; the legacy ratchet baseline was ignored by git and so a
        change to it was not naturally visible in a diff.
        """
        return self.config / "baselines"

    @property
    def foundry_audit_baseline(self) -> Path:
        """The ONE tracked ratchet control input the standing audits compare against.

        Named here because eight tools consume it and the alternative is eight
        restatements of the same repository-relative fact. Before C8.5J each of
        them reached it through a module-level constant inside
        `experiments/foundry_audit_baseline.py`, which derived a repository root
        of its own — layout knowledge stated outside the layout owner, and the
        seam that made the file a mutable process-global.

        NAMING IS NOT MOVING. The file stays exactly where P0.3A tracked it, and
        no value or byte of it changes here.
        """
        return self.baselines / "foundry-audit-baseline.json"

    @property
    def refoundation(self) -> Path:
        return self.root / "refoundation"

    @property
    def decisions(self) -> Path:
        return self.refoundation / "decisions"

    @property
    def conservation(self) -> Path:
        return self.refoundation / "conservation"

    # ---- accepted destination layout (NAMED, NOT CREATED) ----------------
    # Migration slice 1. The accepted experiments-migration master plan
    # (R2/R3/R4/R5 as corrected by R6) relocates configuration, generated
    # output, frozen benchmark evidence and history into destinations that do
    # not exist at this commit. Naming them HERE, before anything physically
    # moves, is what stops each later slice from restating a repository-relative
    # fact this module already owns -- the same reason every `legacy_` sibling
    # below exists, pointed forward instead of backward.
    #
    # NAMING IS NOT MOVING, CREATING, CLASSIFYING, SELECTING OR AUTHORIZING.
    # None of these directories exists yet, no slice-1 change creates one, and a
    # property here confers no disposition on any file that may later land in
    # it. Every value is a pure lexical join, so a root that will never exist
    # stays valid -- which is the whole point of naming a destination early.
    #
    # Intermediates (`var`, `var_mtg`, `benchmarks`, `archive_research`, ...) are
    # deliberate: a child derives from its owner rather than restating a segment,
    # so a group can be re-pointed in exactly one place.

    # config/ -- the plan distinguishes four kinds of tracked input, and
    # conflating them is how a generated registry starts being read as ratified
    # law. `config` and `baselines` above are UNCHANGED; these sit beside them.
    @property
    def config_selectors(self) -> Path:
        """Tracked authority selectors / governance records.

        Kept apart from `config_semantic` on purpose: a selector NAMES which
        snapshot is authoritative, it is not itself ratified configuration.
        """
        return self.config / "selectors"

    @property
    def config_semantic(self) -> Path:
        """Ratified semantic configuration -- Captain-ratified law as data."""
        return self.config / "semantic"

    @property
    def config_generated(self) -> Path:
        """Derived-but-pinned registries. Regenerable, never hand-edited.

        The distinction is load-bearing rather than tidy: a post-refresh routing
        diff once read clean because a CR-derived list under this kind of path
        had not been regenerated. A generated artifact is not the CR, and filing
        it beside ratified configuration is what made that easy to forget.
        """
        return self.config / "generated"

    @property
    def config_registers(self) -> Path:
        """Declared-debt / exception registers.

        A register records a divergence that is KNOWN and accepted. It is not
        ratified law and it is not generated output, so it gets its own group.
        """
        return self.config / "registers"

    @property
    def config_cr(self) -> Path:
        """The Comprehensive Rules edition the pipeline reads."""
        return self.config / "cr"

    @property
    def config_thesaurus(self) -> Path:
        """Tracked thesaurus INPUTS.

        An input that happens to live under a code path is still an input; the
        accepted plan moves it here so that stops being ambiguous.
        """
        return self.config / "thesaurus"

    # var/ -- one ignored root for generated output, with OWNERSHIP visible
    # beneath it and no cross-owner catch-alls. The `.gitignore` change and the
    # physical relocation are separate later slices, deliberately: an ignore
    # edit that orphans a declared conservation source is a silent-loss event.
    @property
    def var(self) -> Path:
        """The generated-output ownership root. Nothing tracked lives here."""
        return self.root / "var"

    @property
    def var_codebook(self) -> Path:
        return self.var / "codebook"

    @property
    def var_mtg(self) -> Path:
        return self.var / "mtg"

    @property
    def var_mtg_cr(self) -> Path:
        return self.var_mtg / "cr"

    @property
    def var_evidence(self) -> Path:
        return self.var / "evidence"

    @property
    def var_thesaurus(self) -> Path:
        """Retrieval outputs. Distinct from `config_thesaurus`, which is INPUT."""
        return self.var / "thesaurus"

    @property
    def var_ops(self) -> Path:
        return self.var / "ops"

    @property
    def var_ops_axis_review(self) -> Path:
        return self.var_ops / "axis_review"

    @property
    def var_guards(self) -> Path:
        """Gate reports and regression corpora written by the guards."""
        return self.var / "guards"

    @property
    def var_benchmarks(self) -> Path:
        return self.var / "benchmarks"

    @property
    def var_benchmarks_aq4(self) -> Path:
        """Where AQ4 run outputs WOULD land. AQ4 is PAUSED and produces none.

        Naming an output destination is not scheduling a run: this property
        exists so that if AQ4 is ever resumed its outputs have an owner, and it
        authorizes nothing. Its frozen tracked evidence is `benchmarks_aq4`,
        which is a different place for a different kind of thing.
        """
        return self.var_benchmarks / "aq4"

    @property
    def var_archive(self) -> Path:
        return self.var / "archive"

    @property
    def var_archive_engine(self) -> Path:
        """Generated output of the ARCHIVED legacy engine -- caches, reports.

        Separate from `archive_engine`, which holds the engine's tracked source
        as history. Output and source are different artifact classes and the
        plan keeps them in different roots.
        """
        return self.var_archive / "engine"

    # benchmarks/ -- FROZEN research evidence, tracked and byte-pinned. This is
    # not generated output and not history: it is pre-registered material that
    # must survive the migration with its bytes and hashes intact.
    @property
    def benchmarks(self) -> Path:
        return self.root / "benchmarks"

    @property
    def benchmarks_aq4(self) -> Path:
        """Frozen AQ4 benchmark evidence -- relocated verbatim, never re-run.

        The accepted plan preserves these bytes under a digest manifest and
        explicitly does NOT claim executable equivalence: changing a
        pre-registered benchmark's import boundary is a ruling, not a fix.
        """
        return self.benchmarks / "aq4"

    @property
    def benchmarks_path_e(self) -> Path:
        return self.benchmarks / "path_e"

    # archive/ -- INERT history, kept as evidence and digest-pinned. An archived
    # file is retained BECAUSE it is historical; nothing here is a live path.
    @property
    def archive(self) -> Path:
        return self.root / "archive"

    @property
    def archive_config(self) -> Path:
        """Superseded configuration, kept so a prior result stays explicable."""
        return self.archive / "config"

    @property
    def archive_engine(self) -> Path:
        """The legacy tier engine and its consumers, as tracked history."""
        return self.archive / "engine"

    @property
    def archive_reports(self) -> Path:
        return self.archive / "reports"

    @property
    def archive_research(self) -> Path:
        return self.archive / "research"

    @property
    def archive_research_triage(self) -> Path:
        return self.archive_research / "triage"

    @property
    def archive_research_consolidation(self) -> Path:
        return self.archive_research / "consolidation"

    @property
    def archive_research_mutations(self) -> Path:
        """One-off codebook executors, archived as a group.

        The plan keeps a mutator and its verifier together: the verifier is the
        migration's only proof, so archiving them apart would retain the record
        of a change without the evidence that it was correct.
        """
        return self.archive_research / "mutations"

    @property
    def archive_research_batch8(self) -> Path:
        return self.archive_research / "batch8"

    @property
    def archive_research_thesaurus_measurement(self) -> Path:
        return self.archive_research / "thesaurus-measurement"

    # ---- legacy layout (READ-ONLY KNOWLEDGE, nothing here moves it) ------
    # Recorded so that later phases have ONE place that knows where legacy state
    # lives, rather than re-deriving `experiments/out/...` at ~97 more sites.
    # Naming these does not move, read, or change anything.
    @property
    def legacy_docs(self) -> Path:
        return self.root / "docs"

    @property
    def legacy_experiments(self) -> Path:
        return self.root / "experiments"

    @property
    def legacy_experiments_out(self) -> Path:
        return self.legacy_experiments / "out"

    @property
    def legacy_foundry_out(self) -> Path:
        return self.legacy_experiments_out / "foundry"

    @property
    def legacy_ruling_registry_json(self) -> Path:
        """The ruling registry's GENERATED machine-readable output, where it is.

        Named here for the same reason as its siblings: `foundry_ruling_registry`
        was appending `"experiments" / "out" / "foundry" / "ruling_registry.json"`
        to a root of its own, which is a repository-relative layout fact stated
        outside the one component that owns layout. Deriving it from
        `legacy_foundry_out` is what lets that restatement go away.

        NAMING IS NOT CLASSIFYING. This does not relocate the file, create it,
        assert it exists, make it authoritative, or decide its artifact class --
        the `legacy_` prefix says exactly that and carries no future ruling. The
        registry's two `docs/` paths are deliberately NOT named here; they are
        Step-6 knowledge and are out of this slice.
        """
        return self.legacy_foundry_out / "ruling_registry.json"

    @property
    def codebook_authority_selector(self) -> Path:
        """The TRACKED selector naming the codebook snapshot that is authoritative.

        Same shape and same reason as its siblings: without a layout owner naming
        this file, a composition boundary that wants to resolve the selected
        codebook has to append the literal `"codebook-authority.json"` to a
        directory this module already owns -- a repository-relative layout fact
        stated outside the one component that owns layout.

        It carries no `legacy_` prefix ON PURPOSE, and the distinction is a fact
        about the file rather than a decision made here: the selector is a
        tracked governance record that the refoundation reads and keeps, not
        generated output pending a disposition. Where it currently SITS is still
        `legacy_docs`, which is why the location is derived from that sibling
        instead of restated.

        NAMING IS NOT SELECTING. This does not read the file, assert it exists,
        verify a digest, or choose a snapshot; a reader does all of that with the
        path in hand.
        """
        return self.legacy_docs / "codebook-authority.json"

    @property
    def legacy_codebook_json(self) -> Path:
        """The operational codebook, where it is.

        Same shape and same reason as `legacy_ruling_registry_json`. C8.5P adds
        it because `mtj_foundry.codebook_store.read` takes an EXPLICIT path and
        has no default: without a layout owner naming this file, the only source
        of the default is the legacy facade's own `CODEBOOK_PATH`, and no
        consumer could ever stop importing the facade. Measured at C8.5O: five
        of the six unblockable consumers call `load_codebook()` with no argument.

        NAMING IS NOT CLASSIFYING. This does not relocate the file, create it,
        assert it exists, read or write it, make it authoritative, or decide its
        artifact class -- the `legacy_` prefix says exactly that and carries no
        future ruling. `foundry_codebook.CODEBOOK_PATH` is UNCHANGED and remains
        the facade's default; repointing consumers at this property is a later
        slice, not this one.
        """
        return self.legacy_foundry_out / "codebook.json"

    @property
    def legacy_foundry_review(self) -> Path:
        """The legacy foundry review directory.

        Named here for the same reason as its siblings: the alternative is for a
        legacy consumer to keep appending the literal `"review"` to a path this
        module already owns, which is a repository-relative layout fact stated
        outside the one component that owns layout. Adding the name is what lets
        `foundry_common.REVIEW_DIR` delegate instead of restating.
        """
        return self.legacy_foundry_out / "review"

    @property
    def legacy_oracle_cards(self) -> Path:
        """The legacy card corpus, exactly where the pipeline already writes it.

        Named here for the same reason as its siblings, and for one more: the
        legacy engine states this path as `Path("data/raw/oracle-cards.jsonl.gz")`
        — RELATIVE, so it resolves against the working directory rather than the
        repository. Naming it in the layout owner is what lets a consumer stop
        being cwd-dependent without restating the layout fact.

        NAMING IS NOT MOVING OR CLASSIFYING. Nothing here relocates the corpus,
        creates it, asserts it exists, or decides its artifact class.
        """
        return self.root / "data" / "raw" / "oracle-cards.jsonl.gz"

    @property
    def legacy_data_artifacts(self) -> Path:
        """The legacy pipeline-artifact directory, exactly where it already is.

        Named here because the alternative is for a legacy consumer to append
        `"data" / "artifacts"` to a root this module already owns, which is a
        repository-relative layout fact stated outside the one component that
        owns layout. C8.5A settled that: `fc.REPO_ROOT / "data" / "artifacts"`
        would still be a second layout statement, merely a shorter one.

        NAMING IS NOT MOVING. Nothing here relocates the directory, creates it,
        or asserts it exists; `data/` is gitignored card data and stays exactly
        where the pipeline already writes it.
        """
        return self.root / "data" / "artifacts"

    @property
    def legacy_pipeline(self) -> Path:
        return self.root / "pipeline"

    # ---- generic ---------------------------------------------------------
    def resolve(self, *parts: str) -> Path:
        """Join repository-relative parts onto the root. No filesystem access."""
        return self.root.joinpath(*parts)


def discover_root(start: str | os.PathLike[str], *,
                  markers: tuple[str, ...] = _ROOT_MARKERS) -> Path:
    """Walk upward from `start` to the nearest directory carrying a root marker.

    EXPLICIT CALL ONLY. Nothing in this package calls it at import time, and no
    library should call it to recover a root it was not given — that is the
    rediscovery habit this module replaces. Intended for a CLI/composition
    boundary that must turn a working directory into a `ProjectPaths`.

    Halts loudly rather than guessing: an unfound root is an error the caller
    asked for, not a silent fallback to the current directory.
    """
    current = Path(start).absolute()
    for candidate in (current, *current.parents):
        if any((candidate / marker).exists() for marker in markers):
            return candidate
    raise RootNotFound(
        f"no repository root found at or above {current}: none of {list(markers)} "
        "is present. Pass an explicit root to ProjectPaths.for_root() instead."
    )
