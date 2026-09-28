"""Trusted-host Git finalization: a provider edits and tests, the host commits.

Every provider -- Codex in its workspace-write sandbox, Claude, any other -- is
held to one Git law: it never writes Git metadata. After a successful response
the host extracts the Worker evidence, proves the provider left HEAD, the branch,
every ref and the index untouched, proves scope BEFORE staging, stages exactly
the measured paths, makes one trailered commit, pushes it non-force to the
commanded branch, verifies the unit, publishes durable evidence, and only then
reports progress and PASS.

Every refusal below happens before PASS, and none of them tidies the tree.
No network, no model, no real repository: the git model is the extended
`EvidenceRepo`, driven through the same supervisor path production uses.
"""

from __future__ import annotations

import json
import re
import unittest
from unittest import mock

from tests.refoundation.agent_bus_fixtures import REPO_ROOT, WAVE, comment_body, unit
from tests.refoundation.test_agent_bus_provider_failover import (
    COMMAND, REPO_PATH, Step, armed, claude_quota, ok, repo, stream,
)
from tests.refoundation.test_agent_bus_provider_failover import ProviderRepo

from agent_bus import errors as E
from agent_bus import finalize as F
from agent_bus import providers as P
from agent_bus import worker_evidence as W
from agent_bus.errors import BusError
from agent_bus.git_evidence import units_in_message
from agent_bus.transport import worker_brief

GIT_VERBS = ("add", "commit", "push")


def posts(fake):
    """Every GitHub write, in order, as (target, body)."""
    out = []
    for call in fake.calls:
        if call[0] == "gh" and any(a.startswith("body=") for a in call):
            out.append((call[2], next(a[5:] for a in call if a.startswith("body="))))
    return out


def position(fake, predicate) -> int:
    for index, call in enumerate(fake.calls):
        if predicate(call):
            return index
    return -1


def git_verb(call, verb) -> bool:
    return call[0] == "git" and verb in call


def host_git_calls(fake):
    """Git calls with the provider-chosen bits stripped, to compare across providers."""
    return [c for c in fake.calls if c[0] == "git"]


def with_units(*units) -> ProviderRepo:
    body = {"branch": "infra/agent-bus-v1", "review_boundary": "end", "units": list(units)}
    return ProviderRepo(stream(comment_body(body=body, **COMMAND)), script=[])


# ---------------------------------------------------------------------------
# 1. The positive path, for either provider
# ---------------------------------------------------------------------------

class TestHostFinalizesTheUnit(unittest.TestCase):
    def run_one(self, provider: str, **step):
        fake = repo(Step(provider, **step) if step else ok(provider))
        report = armed(fake, order=(provider,), max_units=1).poll_once(execute=True)
        return fake, report

    def test_codex_in_workspace_write_edits_and_the_host_commits_and_pushes(self):
        fake, report = self.run_one("codex")
        self.assertEqual(report["action"], "WAVE_RAN")
        codex_argv = fake.provider_calls[0]
        self.assertEqual(codex_argv[codex_argv.index("--sandbox") + 1], "workspace-write")
        self.assertEqual(len(fake.host_commits), 1)
        sha = fake.host_commits[0]
        self.assertEqual(fake.head, sha)
        self.assertEqual(fake.remote_head, sha)
        message = fake.commits[-1][1]
        self.assertEqual(units_in_message(message, WAVE), ["U1"])
        self.assertTrue(message.rstrip("\n").endswith(
            f"Agent-Bus-Wave: {WAVE}\nAgent-Bus-Unit: U1"))
        self.assertEqual(fake.commits[-1][2], ("agent_bus/x.py",))
        self.assertEqual(fake.entries(), [])
        final = fake.posted_messages()[-1]
        self.assertEqual(final.body["status"], "P")
        self.assertEqual(final.body["units"], [{"id": "U1", "status": "DONE", "commit": sha}])

    def test_claude_takes_the_identical_host_path(self):
        runs = {}
        for provider in ("claude", "codex"):
            fake, report = self.run_one(provider)
            self.assertEqual(report["action"], "WAVE_RAN", provider)
            runs[provider] = fake
        claude, codex_ = runs["claude"], runs["codex"]
        # Provider identity changes nothing about Git: the same commands, the same
        # tree, the same trailers. Only the message's `Provider:` line names who.
        self.assertEqual(host_git_calls(claude), host_git_calls(codex_))
        self.assertEqual(claude.commits[-1][2], codex_.commits[-1][2])
        self.assertEqual(claude.commits[-1][1].replace("Provider: claude", "Provider: codex"),
                         codex_.commits[-1][1])

    def test_the_commit_message_is_deterministic(self):
        first, _ = self.run_one("claude")
        second, _ = self.run_one("claude")
        self.assertEqual(first.commits[-1][1], second.commits[-1][1])

    def test_additions_modifications_and_deletions_are_staged_exactly(self):
        fake, report = self.run_one("claude", dirty=("agent_bus/a.py",),
                                    untracked=("agent_bus/new/b.py",),
                                    deleted=("agent_bus/gone.py",))
        self.assertEqual(report["action"], "WAVE_RAN")
        self.assertEqual(fake.commits[-1][2],
                         ("agent_bus/a.py", "agent_bus/gone.py", "agent_bus/new/b.py"))
        add = next(c for c in fake.calls if git_verb(c, "add"))
        self.assertIn("--literal-pathspecs", add)
        self.assertEqual(add[add.index("--") + 1:],
                         ("agent_bus/a.py", "agent_bus/gone.py", "agent_bus/new/b.py"))
        self.assertEqual(fake.entries(), [])

    def test_the_push_is_non_force_to_the_commanded_branch_with_hooks_off(self):
        fake, _ = self.run_one("codex")
        push = fake.pushes[0]
        self.assertEqual(push[-1], f"{fake.host_commits[0]}:refs/heads/infra/agent-bus-v1")
        self.assertEqual(push[-2], fake.remote_url)
        self.assertFalse(any(a in ("--force", "-f", "--force-with-lease", "--mirror")
                             or a.startswith("+") or a.startswith("--force") for a in push))
        for verb in ("commit", "push"):
            call = next(c for c in fake.calls if git_verb(c, verb))
            self.assertIn("core.hooksPath=/dev/null", call)
            self.assertIn("--no-verify", call)

    def test_the_order_is_evidence_then_git_then_evidence_post_then_progress(self):
        fake, _ = self.run_one("codex")
        snap = position(fake, lambda c: git_verb(c, "for-each-ref"))
        provider = position(fake, lambda c: c[0] == "codex")
        status = position(fake, lambda c: git_verb(c, "-z") and "status" in c)
        add = position(fake, lambda c: git_verb(c, "add"))
        commit = position(fake, lambda c: git_verb(c, "commit"))
        push = position(fake, lambda c: git_verb(c, "push"))
        landed = position(fake, lambda c: git_verb(c, "ls-remote"))
        written = [i for i, c in enumerate(fake.calls)
                   if c[0] == "gh" and any(a.startswith("body=") for a in c)]
        self.assertEqual(sorted([snap, provider, status, add, commit, push, landed] + written),
                         [snap, provider, status, add, commit, push, landed] + written)
        kinds = [(t, b.startswith(W.PREFIX)) for t, b in posts(fake)]
        self.assertTrue(kinds[0][1])                    # evidence first, on Issue #1
        self.assertIn("/issues/1/comments", kinds[0][0])
        self.assertEqual(fake.posted_kinds(), ["WAVE_PROGRESS", "WAVE_RESULT"])
        payload = json.loads(fake.posted[0][len(W.PREFIX):-len(W.SUFFIX)])
        self.assertEqual(payload["head"], fake.host_commits[0])

    def test_a_two_unit_wave_is_two_host_commits_each_pushed(self):
        fake = repo(ok("codex", "U1", "agent_bus/a.py"), ok("codex", "U2", "agent_bus/b.py"))
        report = armed(fake, order=("codex",)).poll_once(execute=True)
        self.assertEqual(report["action"], "WAVE_RAN")
        self.assertEqual(len(fake.host_commits), 2)
        self.assertEqual([units_in_message(m, WAVE) for _, m, _ in fake.commits],
                         [["U1"], ["U2"]])
        self.assertEqual(fake.remote_head, fake.host_commits[-1])

    def test_failover_then_host_finalization(self):
        fake = repo(claude_quota(), ok("codex", "U1"))
        report = armed(fake, max_units=1).poll_once(execute=True)
        self.assertEqual(report["action"], "WAVE_RAN")
        self.assertEqual(fake.providers_invoked, ["claude", "codex"])
        self.assertIn("Provider: codex", fake.commits[-1][1])


# ---------------------------------------------------------------------------
# 2. Read-only units never commit
# ---------------------------------------------------------------------------

class TestReadOnlyUnits(unittest.TestCase):
    def test_a_read_only_unit_passes_without_any_staging_commit_or_push(self):
        fake = with_units(unit("R1", mutating=False, allow=()))
        fake.script = [Step("claude")]
        report = armed(fake, order=("claude",)).poll_once(execute=True)
        self.assertEqual(report["action"], "WAVE_RAN")
        self.assertEqual((fake.host_commits, fake.pushes), ([], []))
        self.assertFalse(any(git_verb(c, v) for c in fake.calls for v in GIT_VERBS))
        self.assertEqual(fake.posted_messages()[-1].body["status"], "P")

    def test_NC_a_read_only_unit_that_edited_is_refused_and_not_committed(self):
        fake = with_units(unit("R1", mutating=False, allow=()))
        fake.script = [Step("claude", dirty=("agent_bus/x.py",))]
        report = armed(fake, order=("claude",)).poll_once(execute=True)
        self.assertEqual(report["reason"], E.READONLY_UNIT_MUTATED)
        self.assertEqual(fake.host_commits, [])
        self.assertEqual(fake.dirty, ("agent_bus/x.py",))


# ---------------------------------------------------------------------------
# 3. Fail closed before PASS
# ---------------------------------------------------------------------------

class TestFailsClosed(unittest.TestCase):
    def stopped(self, fake, code, **kw):
        report = armed(fake, max_units=1, **kw).poll_once(execute=True)
        self.assertEqual(report["action"], "WAVE_STOPPED")
        self.assertEqual(report["reason"], code, report["units"])
        self.assertFalse(any(b.startswith(W.PREFIX) for b in fake.posted))
        self.assertEqual(fake.posted_messages()[-1].body["status"], "F")
        self.assertEqual([m.body["status"] for m in fake.posted_messages()
                          if m.kind == "WAVE_PROGRESS"], ["FAILED"])
        return report

    def assert_nothing_staged_or_committed(self, fake):
        self.assertEqual((fake.host_commits, fake.pushes), ([], []))
        self.assertFalse(any(git_verb(c, v) for c in fake.calls for v in GIT_VERBS))

    def test_NC_a_provider_commit_is_refused(self):
        for provider in ("claude", "codex"):
            with self.subTest(provider=provider):
                fake = repo(Step(provider, message="U1\n\nAgent-Bus-Wave: " + WAVE
                                 + "\nAgent-Bus-Unit: U1", paths=("agent_bus/x.py",)))
                self.stopped(fake, E.PROVIDER_GIT_MUTATION, order=(provider,))
                self.assert_nothing_staged_or_committed(fake)

    def test_NC_a_provider_ref_move_or_new_ref_is_refused(self):
        rigs = {
            "tag": lambda r: r.extra_refs.update({"refs/tags/x": r.head}),
            "stash": lambda r: r.extra_refs.update({"refs/stash": "e" * 40}),
            "remote-tracking": lambda r: setattr(r, "remote_head", "e" * 40),
        }
        for name, rig in rigs.items():
            with self.subTest(ref=name):
                fake = repo(Step("codex", dirty=("agent_bus/x.py",), then=rig))
                report = self.stopped(fake, E.PROVIDER_GIT_MUTATION, order=("codex",))
                self.assertIn("refs changed", report["units"][0]["problems"][0]["detail"])
                self.assert_nothing_staged_or_committed(fake)
                self.assertEqual(fake.dirty, ("agent_bus/x.py",))

    def test_NC_a_detached_head_with_every_ref_unchanged_is_refused(self):
        # `git checkout <sha>` moves HEAD without moving any ref.
        before = F.Snapshot("a" * 40, "infra/agent-bus-v1", ("a" * 40 + " refs/heads/x",))
        after = F.Snapshot("b" * 40, "infra/agent-bus-v1", before.refs)
        problems = F.git_mutations(before, after, [])
        self.assertEqual(len(problems), 1)
        self.assertIn("HEAD moved", problems[0])
        self.assertEqual(F.git_mutations(before, before, [(" M", "x"), ("??", "y"),
                                                          (" D", "z")]), [])

    def test_NC_a_provider_config_change_is_refused_before_git_status_runs(self):
        planted = lambda r: setattr(r, "local_config", r.local_config + "core.fsmonitor=/x\n")
        fake = repo(Step("claude", dirty=("agent_bus/x.py",), then=planted))
        report = self.stopped(fake, E.PROVIDER_GIT_MUTATION, order=("claude",))
        self.assertIn("config", report["units"][0]["problems"][0]["detail"])
        after_provider = position(fake, lambda c: c[0] == "claude")
        self.assertFalse(any("status" in c for c in fake.calls[after_provider:]))
        self.assert_nothing_staged_or_committed(fake)

    def test_NC_a_provider_branch_change_is_refused(self):
        fake = repo(Step("claude", dirty=("agent_bus/x.py",),
                         then=lambda r: setattr(r, "branch", "elsewhere")))
        report = armed(fake, order=("claude",), max_units=1).poll_once(execute=True)
        self.assertEqual(report["reason"], E.PROVIDER_GIT_MUTATION)
        self.assert_nothing_staged_or_committed(fake)

    def test_NC_provider_staging_is_a_git_mutation(self):
        fake = repo(Step("claude", dirty=("agent_bus/x.py",),
                         then=lambda r: setattr(r, "staged", ("agent_bus/x.py",))))
        report = self.stopped(fake, E.PROVIDER_GIT_MUTATION, order=("claude",))
        self.assertIn("index", report["units"][0]["problems"][0]["detail"])
        self.assert_nothing_staged_or_committed(fake)

    def test_NC_a_mutating_unit_that_changed_nothing_is_refused(self):
        fake = repo(Step("codex"))
        report = self.stopped(fake, E.UNIT_NO_COMMIT, order=("codex",))
        self.assertIn("changed nothing for the host to commit",
                      report["units"][0]["problems"][0]["detail"])
        self.assert_nothing_staged_or_committed(fake)

    def test_NC_a_scope_escape_is_refused_before_staging_and_left_as_evidence(self):
        cases = {
            "modified": dict(dirty=("agent_bus/x.py", "pipeline/build_db.py")),
            "untracked": dict(dirty=("agent_bus/x.py",), untracked=("data/cards.jsonl",)),
            "deleted": dict(deleted=("CLAUDE.md",)),
        }
        for name, edits in cases.items():
            with self.subTest(escape=name):
                fake = repo(Step("claude", **edits))
                report = self.stopped(fake, E.UNIT_SCOPE_ESCAPE, order=("claude",))
                self.assert_nothing_staged_or_committed(fake)
                self.assertIn("nothing staged", report["units"][0]["problems"][0]["detail"])
                self.assertEqual({p for _, p in fake.entries()},
                                 {p for group in edits.values() for p in group})

    def test_NC_a_denied_path_is_a_scope_escape_before_staging(self):
        fake = with_units(unit("U1", deny_paths=["agent_bus/secret.py"]))
        fake.script = [Step("claude", dirty=("agent_bus/secret.py",))]
        self.stopped(fake, E.UNIT_SCOPE_ESCAPE, order=("claude",))
        self.assert_nothing_staged_or_committed(fake)

    def test_NC_evidence_extraction_failure_creates_no_commit(self):
        for provider, stdout in (("claude", "{}"), ("codex", '{"type":"turn.completed"}'),
                                 ("claude", "not json")):
            with self.subTest(provider=provider, stdout=stdout):
                fake = repo(Step(provider, dirty=("agent_bus/x.py",), stdout=stdout))
                with self.assertRaises(BusError) as caught:
                    armed(fake, order=(provider,)).poll_once(execute=True)
                self.assertEqual(caught.exception.code, E.WORKER_EVIDENCE_INVALID)
                self.assert_nothing_staged_or_committed(fake)
                self.assertEqual(fake.posted, [])
                self.assertEqual(fake.dirty, ("agent_bus/x.py",))

    def test_NC_a_commit_failure_prevents_progress_and_pass(self):
        fake = repo(ok("claude"))
        fake.fail_commit = "error: gpg failed to sign the data"
        self.stopped(fake, E.HOST_COMMIT_FAILED, order=("claude",))
        self.assertEqual((fake.host_commits, fake.pushes), ([], []))

    def test_NC_a_staging_mismatch_prevents_the_commit(self):
        fake = repo(ok("claude"))
        original = fake._git

        def lossy(argv):
            result = original(argv)
            if "add" in argv:             # the index took more than was asked
                fake.staged = fake.staged + ("agent_bus/unasked.py",)
            return result
        fake._git = lossy
        report = self.stopped(fake, E.HOST_COMMIT_FAILED, order=("claude",))
        self.assertIn("is not exactly the measured", report["units"][0]["problems"][0]["detail"])
        self.assertEqual(fake.host_commits, [])

    def test_NC_a_push_failure_prevents_progress_and_pass(self):
        fake = repo(ok("claude"))
        fake.fail_push = "fatal: could not read from remote repository"
        self.stopped(fake, E.HOST_PUSH_FAILED, order=("claude",))
        self.assertEqual(len(fake.host_commits), 1)     # kept as evidence, not reset
        self.assertEqual(fake.remote_head, fake.base)

    def test_NC_a_remote_that_moved_rejects_the_non_force_push(self):
        fake = repo(ok("codex"))
        fake.remote_head = "f" * 40      # somebody else pushed before the provider ran
        self.stopped(fake, E.HOST_PUSH_FAILED, order=("codex",))
        self.assertEqual(fake.remote_head, "f" * 40)

    def test_NC_a_race_after_the_push_is_caught_by_re_reading_the_remote(self):
        fake = repo(ok("codex"))
        fake.race_sha = "d" * 40
        self.stopped(fake, E.HOST_PUSH_FAILED, order=("codex",))

    def test_NC_failover_still_needs_the_failed_provider_to_leave_git_alone(self):
        fake = repo(claude_quota(dirty=("agent_bus/half.py",)), ok("codex"))
        with self.assertRaises(BusError) as caught:
            armed(fake).poll_once(execute=True)
        self.assertEqual(caught.exception.code, E.FAILOVER_REFUSED)
        self.assertEqual(fake.providers_invoked, ["claude"])
        self.assert_nothing_staged_or_committed(fake)


# ---------------------------------------------------------------------------
# 4. WE4: durable evidence after a durable commit
# ---------------------------------------------------------------------------

class TestEvidenceAfterTheHostCommit(unittest.TestCase):
    def test_NC_an_evidence_post_failure_after_the_push_is_fail_closed(self):
        from agent_bus.shell import Completed
        fake = repo(ok("claude"))
        sup = armed(fake, order=("claude",), max_units=1)

        def refuse_posts(argv, **kwargs):
            if argv[0] == "gh" and any(a.startswith("body=") for a in argv):
                return Completed(tuple(argv), 1, "", "HTTP 502")
            return fake(argv, **kwargs)
        sup.run = refuse_posts
        sup.transport.run = refuse_posts
        with self.assertRaises(BusError) as caught:
            sup.poll_once(execute=True)
        self.assertEqual(caught.exception.code, E.WORKER_EVIDENCE_POST_FAILED)
        self.assertEqual(fake.remote_head, fake.host_commits[0])    # durable commit
        self.assertEqual(fake.posted, [])                            # no progress, no PASS

        # The response is lost. Git proves U1's scope, not what the model said, so
        # a resume refuses instead of reconstructing evidence from the commit.
        fake.script.append(ok("claude", "U2"))
        with self.assertRaises(BusError) as caught:
            armed(fake, order=("claude",)).poll_once(execute=True, resume=True)
        self.assertEqual(caught.exception.code, E.WORKER_EVIDENCE_INVALID)
        self.assertEqual(fake.providers_invoked, ["claude"])


# ---------------------------------------------------------------------------
# 5. The provider boundary, the brief and the contracts
# ---------------------------------------------------------------------------

AGENT_BUS = REPO_ROOT / "agent_bus"
CONTRACTS = (REPO_ROOT / "CLAUDE.md", REPO_ROOT / "refoundation" / "AGENT-BUS.md")


class TestProviderBoundary(unittest.TestCase):
    def test_codex_stays_exactly_workspace_write(self):
        self.assertEqual(P.CodexProvider.sandbox, "workspace-write")
        argv = P.CodexProvider(REPO_PATH).argv("b", P.SessionRef("codex", None, False))
        self.assertEqual(argv.count("--sandbox"), 1)
        self.assertEqual(argv[argv.index("--sandbox") + 1], "workspace-write")

    def test_headless_claude_loads_no_ambient_settings_and_is_sandboxed(self):
        from agent_bus.transport import HEADLESS_CLAUDE_SETTINGS
        argv = P.ClaudeProvider(REPO_PATH).argv("b", P.SessionRef("claude", "s", False))
        flag = lambda name: argv[argv.index(name) + 1]
        self.assertEqual(argv.count("--setting-sources"), 1)
        self.assertEqual(flag("--setting-sources"), "")
        self.assertEqual(flag("--permission-prompts"), "none")
        settings = json.loads(flag("--settings"))
        self.assertEqual(settings, HEADLESS_CLAUDE_SETTINGS)
        self.assertIs(settings["sandbox"]["enabled"], True)
        self.assertIs(settings["sandbox"]["allowUnsandboxedCommands"], False)
        denied = set(settings["permissions"]["deny"])
        for verb in ("add", "commit", "push", "stash", "reset", "checkout", "rebase",
                     "clean", "fetch", "config", "update-ref"):
            with self.subTest(verb=verb):
                self.assertIn(f"Bash(git {verb}:*)", denied)
        for allowed in settings["permissions"]["allow"]:
            with self.subTest(allowed=allowed):
                self.assertNotIn(allowed.split("(")[1].split(":")[0].split(" ")[-1],
                                 {"add", "commit", "push", "config"})

    def test_NC_resuming_claude_keeps_the_same_least_privilege(self):
        fresh = P.ClaudeProvider(REPO_PATH).argv("b", P.SessionRef("claude", "s", False))
        resumed = P.ClaudeProvider(REPO_PATH).argv("b", P.SessionRef("claude", "s", True))
        tail = lambda a: a[a.index("--setting-sources"):a.index("--settings") + 2]
        self.assertEqual(tail(fresh), tail(resumed))

    def test_no_danger_full_access_path_exists_in_the_bus(self):
        for path in sorted(AGENT_BUS.rglob("*.py")):
            text = path.read_text(encoding="utf-8")
            for word in ("danger-full-access", "dangerously-bypass", "--yolo",
                         "bypassPermissions", "dangerously-skip-permissions"):
                with self.subTest(path=path.name, word=word):
                    self.assertNotIn(word, text)

    def test_the_brief_forbids_every_git_mutation_and_names_the_host(self):
        sup = armed(repo())
        observation = sup.observe()
        envelope = observation.state.pending_for("WORKER")[0]
        brief = worker_brief(envelope, observation.state.waves[WAVE].plan, ["U1"], REPO_PATH)
        rules = brief.split("Rules for this wave:")[1].split("The authorizing command")[0]
        flat = re.sub(r"\s+", " ", rules)
        self.assertIn("Edit and test files only", flat)
        for verb in ("commit", "push", "reset", "stash", "clean", "checkout", "rebase",
                     "stage", "otherwise mutate Git metadata"):
            with self.subTest(verb=verb):
                self.assertIn(verb, flat.split("Never ")[1].split(".")[0])
        self.assertIn("trusted Agent Bus host", flat)
        self.assertNotIn("Commit each mutating unit", brief)

    def test_the_contracts_no_longer_tell_a_model_to_commit_or_push(self):
        for path in CONTRACTS:
            flat = re.sub(r"\s+", " ", path.read_text(encoding="utf-8"))
            with self.subTest(contract=path.name):
                self.assertNotIn("Commit each mutating unit separately", flat)
                self.assertNotIn("Commit per unit with trailers", flat)
                self.assertIn("edits and tests files only", flat)
                self.assertIn("never commits, pushes", flat)

    def test_the_bus_contract_names_every_host_finalization_code(self):
        doc = (REPO_ROOT / "refoundation" / "AGENT-BUS.md").read_text(encoding="utf-8")
        for code in (E.PROVIDER_GIT_MUTATION, E.HOST_COMMIT_FAILED, E.HOST_PUSH_FAILED,
                     E.UNIT_SCOPE_ESCAPE, E.UNIT_NO_COMMIT, E.WORKER_EVIDENCE_INVALID,
                     E.WORKER_EVIDENCE_POST_FAILED):
            with self.subTest(code=code):
                self.assertIn(code, doc)


# ---------------------------------------------------------------------------
# 6. Real git: the same argv against a real clone and a real bare remote
# ---------------------------------------------------------------------------

class TestAgainstRealGit(unittest.TestCase):
    BRANCH = "infra/agent-bus-v1"

    def setUp(self):
        import shutil
        import subprocess
        import tempfile
        from pathlib import Path
        from agent_bus.protocol import parse_comment
        from agent_bus.shell import Runner
        if shutil.which("git") is None:
            self.skipTest("git is not installed")
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        self.remote, self.repo = str(root / "remote.git"), str(root / "work")
        self.sh = lambda *a, cwd=None: subprocess.run(
            ["git", *a], cwd=cwd, capture_output=True, text=True, check=True).stdout
        self.sh("init", "-q", "--bare", self.remote)
        self.sh("init", "-q", "-b", self.BRANCH, self.repo)
        for key, value in (("user.name", "host"), ("user.email", "host@example.invalid"),
                           ("commit.gpgsign", "false")):
            self.sh("config", key, value, cwd=self.repo)
        (Path(self.repo) / "agent_bus").mkdir()
        for name in ("keep.py", "gone.py"):
            (Path(self.repo) / "agent_bus" / name).write_text("x\n", encoding="utf-8")
        self.sh("add", "-A", cwd=self.repo)
        self.sh("commit", "-q", "-m", "base", cwd=self.repo)
        self.sh("remote", "add", "origin", self.remote, cwd=self.repo)
        self.sh("push", "-q", "origin", self.BRANCH, cwd=self.repo)
        self.root = Path(self.repo)
        self.run_ = Runner()
        self.command = parse_comment(comment_body(**COMMAND))
        self.unit = __import__("agent_bus.wave", fromlist=["Unit"]).Unit(
            id="U1", objective="o", depends_on=(), allow_paths=("agent_bus/**",),
            validation=("v",), mutating=True)

    def tearDown(self):
        self.tmp.cleanup()

    def edit(self):
        (self.root / "agent_bus" / "keep.py").write_text("changed\n", encoding="utf-8")
        (self.root / "agent_bus" / "gone.py").unlink()
        (self.root / "agent_bus" / "new[1]*.py").write_text("new\n", encoding="utf-8")

    def finalize(self, before):
        return F.finalize(self.repo, "origin", self.BRANCH, self.command, self.unit,
                          "codex", before, self.run_)

    def test_edits_become_one_trailered_commit_on_the_real_remote(self):
        before = F.snapshot(self.repo, self.run_)
        self.edit()
        result = self.finalize(before)
        self.assertTrue(result.ok, result.problems)
        self.assertEqual(result.paths, ("agent_bus/gone.py", "agent_bus/keep.py",
                                        "agent_bus/new[1]*.py"))
        head = self.sh("rev-parse", "HEAD", cwd=self.repo).strip()
        self.assertEqual(result.commit, head)
        self.assertEqual(self.sh("rev-parse", self.BRANCH, cwd=self.remote).strip(), head)
        self.assertEqual(self.sh("rev-parse", "HEAD~1", cwd=self.repo).strip(), before.head)
        message = self.sh("log", "-1", "--format=%B", cwd=self.repo)
        self.assertEqual(units_in_message(message, WAVE), ["U1"])
        self.assertEqual(message.rstrip("\n"),
                         F.commit_message(self.command, self.unit, "codex").rstrip("\n"))
        self.assertEqual(self.sh("status", "--porcelain", cwd=self.repo), "")

    def test_NC_a_real_provider_commit_is_refused_before_staging(self):
        before = F.snapshot(self.repo, self.run_)
        self.edit()
        self.sh("add", "-A", cwd=self.repo)
        self.sh("commit", "-q", "-m", "provider did this", cwd=self.repo)
        result = self.finalize(before)
        self.assertEqual(result.problems[0][0], E.PROVIDER_GIT_MUTATION)
        self.assertEqual(self.sh("rev-parse", self.BRANCH, cwd=self.remote).strip(), before.head)

    def test_NC_a_real_remote_that_moved_rejects_the_non_force_push(self):
        from pathlib import Path
        other = str(Path(self.tmp.name) / "other")
        self.sh("clone", "-q", "-b", self.BRANCH, self.remote, other)
        for key, value in (("user.name", "x"), ("user.email", "x@example.invalid"),
                           ("commit.gpgsign", "false")):
            self.sh("config", key, value, cwd=other)
        self.sh("commit", "-q", "--allow-empty", "-m", "raced", cwd=other)
        self.sh("push", "-q", "origin", self.BRANCH, cwd=other)
        raced = self.sh("rev-parse", "HEAD", cwd=other).strip()

        before = F.snapshot(self.repo, self.run_)
        self.edit()
        result = self.finalize(before)
        self.assertEqual(result.problems[0][0], E.HOST_PUSH_FAILED)
        self.assertEqual(self.sh("rev-parse", self.BRANCH, cwd=self.remote).strip(), raced)

    def test_NC_a_planted_hook_does_not_run_in_the_host(self):
        # `--no-verify` skips pre-commit and pre-push only; post-commit and
        # reference-transaction run anyway unless hooks are disabled outright.
        marker = self.root.parent / "hook-ran"
        for name in ("pre-commit", "post-commit", "reference-transaction", "pre-push"):
            hook = self.root / ".git" / "hooks" / name
            hook.write_text(f"#!/bin/sh\ntouch {marker}\n", encoding="utf-8")
            hook.chmod(0o755)
        before = F.snapshot(self.repo, self.run_)
        self.edit()
        result = self.finalize(before)
        self.assertTrue(result.ok, result.problems)
        self.assertFalse(marker.exists())


# ---------------------------------------------------------------------------
# 6b. Real git, hostile config OUTSIDE the checkout
# ---------------------------------------------------------------------------

class _AmbientRunner:
    """The pre-R3 host: real git, but with whatever config the environment has.
    Used only as the RED side of a negative control."""

    def __call__(self, argv, stdin=None, timeout=None):
        import subprocess
        from agent_bus.shell import Completed
        proc = subprocess.run(list(argv), input=stdin, capture_output=True, text=True,
                              stdin=None if stdin is not None else subprocess.DEVNULL,
                              timeout=60)
        return Completed(tuple(argv), proc.returncode, proc.stdout, proc.stderr)


class TestHostGitIgnoresConfigOutsideTheCheckout(TestAgainstRealGit):
    """A provider with broad filesystem rights can write the user's global or the
    system git config; the host must not obey either. Each hostile file lives in
    the test's temp dir and reaches git only through GIT_CONFIG_GLOBAL /
    GIT_CONFIG_SYSTEM on this process, never the real ~/.gitconfig. Each case is
    shown RED against the ambient-config host and GREEN against `Runner`."""

    def setUp(self):
        super().setUp()
        self.tmp_root = self.root.parent
        self.hostile = self.tmp_root / "hostile.gitconfig"
        self.hostile.write_text("", encoding="utf-8")
        self.marker = self.tmp_root / "host-ran-it"
        self.script = self.tmp_root / "payload.sh"
        self.script.write_text(f"#!/bin/sh\ntouch {self.marker}\nexit 1\n",
                               encoding="utf-8")
        self.script.chmod(0o755)
        env = {"GIT_CONFIG_GLOBAL": str(self.hostile), "GIT_CONFIG_SYSTEM": str(self.hostile)}
        patcher = mock.patch.dict("os.environ", env)
        patcher.start()
        self.addCleanup(patcher.stop)

    def plant(self, text: str) -> None:
        """What the provider does: write hostile config after the snapshot."""
        self.hostile.write_text(text, encoding="utf-8")

    def attempt(self, run):
        before = F.snapshot(self.repo, run)
        self.edit()
        return before, F.finalize(self.repo, "origin", self.BRANCH, self.command, self.unit,
                                  "claude", before, run)

    def reset_checkout(self):
        self.sh("reset", "-q", "--hard", "HEAD", cwd=self.repo)
        self.sh("clean", "-qfd", cwd=self.repo)

    def remote_head(self):
        return self.sh("rev-parse", self.BRANCH, cwd=self.remote).strip()

    # -- fsmonitor: code execution on `git status` ---------------------------
    def test_NC_global_fsmonitor_runs_in_an_ambient_host_but_not_in_the_bus(self):
        before = F.snapshot(self.repo, self.run_)
        self.edit()
        self.plant(f"[core]\n\tfsmonitor = {self.script}\n")
        # RED: the host's first post-provider git command runs the planted program.
        F.worktree_changes(self.repo, _AmbientRunner())
        self.assertTrue(self.marker.exists(), "RED side did not reproduce the attack")
        self.marker.unlink()
        result = F.finalize(self.repo, "origin", self.BRANCH, self.command, self.unit,
                            "claude", before, self.run_)
        self.assertTrue(result.ok, result.problems)
        self.assertFalse(self.marker.exists())

    # -- insteadOf: the push and its proof both go to the attacker -----------
    def test_NC_global_insteadof_is_a_false_pass_in_an_ambient_host_but_not_in_the_bus(self):
        attacker = str(self.tmp_root / "attacker.git")
        self.sh("init", "-q", "--bare", attacker)
        self.plant(f'[url "{attacker}"]\n\tinsteadOf = {self.remote}\n')
        base = self.remote_head()
        _, red = self.attempt(_AmbientRunner())
        # RED: finalize reports success, yet the real remote never moved.
        self.assertTrue(red.ok, red.problems)
        self.assertEqual(self.remote_head(), base)
        self.assertEqual(self.sh("rev-parse", self.BRANCH, cwd=attacker).strip(), red.commit)

        self.sh("reset", "-q", "--hard", base, cwd=self.repo)
        _, green = self.attempt(self.run_)
        self.assertTrue(green.ok, green.problems)
        self.assertEqual(self.remote_head(), green.commit)

    # -- gpg.program: code execution on the host commit ----------------------
    def test_NC_global_gpg_program_runs_in_an_ambient_host_but_not_in_the_bus(self):
        self.sh("config", "--unset", "commit.gpgsign", cwd=self.repo)
        self.plant(f"[commit]\n\tgpgsign = true\n[gpg]\n\tprogram = {self.script}\n")
        self.attempt(_AmbientRunner())
        self.assertTrue(self.marker.exists(), "RED side did not reproduce the attack")
        self.marker.unlink()
        self.reset_checkout()
        _, result = self.attempt(self.run_)
        self.assertTrue(result.ok, result.problems)
        self.assertFalse(self.marker.exists())

    # -- include: config that changes without .git/config changing -----------
    def test_NC_an_included_config_file_change_is_a_git_mutation(self):
        included = self.tmp_root / "included.gitconfig"
        included.write_text("[user]\n\tname = host\n", encoding="utf-8")
        self.sh("config", "include.path", str(included), cwd=self.repo)
        before = F.snapshot(self.repo, self.run_)
        plain = self.sh("config", "--local", "--list", cwd=self.repo)
        included.write_text(f'[url "/elsewhere"]\n\tinsteadOf = {self.remote}\n',
                            encoding="utf-8")
        # RED: the pre-R3 snapshot text cannot see the change at all.
        self.assertEqual(self.sh("config", "--local", "--list", cwd=self.repo), plain)
        self.edit()
        result = F.finalize(self.repo, "origin", self.BRANCH, self.command, self.unit,
                            "claude", before, self.run_)
        self.assertEqual(result.problems[0][0], E.PROVIDER_GIT_MUTATION)

    # -- metadata files: exclude hides a path from the measured change set ---
    def test_NC_a_provider_edit_to_info_exclude_is_a_git_mutation(self):
        before = F.snapshot(self.repo, self.run_)
        self.edit()
        exclude = self.root / ".git" / "info" / "exclude"
        exclude.parent.mkdir(exist_ok=True)
        exclude.write_text("agent_bus/hidden.py\n", encoding="utf-8")
        (self.root / "agent_bus" / "hidden.py").write_text("x\n", encoding="utf-8")
        result = F.finalize(self.repo, "origin", self.BRANCH, self.command, self.unit,
                            "claude", before, self.run_)
        self.assertEqual(result.problems[0][0], E.PROVIDER_GIT_MUTATION)
        self.assertIn("info/exclude", result.problems[0][1])
        self.assertEqual(self.remote_head(), before.head)


class TestHostGitEnvironment(unittest.TestCase):
    def test_host_git_env_drops_ambient_git_and_pins_the_executing_keys(self):
        from agent_bus.shell import HOST_GIT_CONFIG, host_git_env
        env = host_git_env({"PATH": "/bin", "GIT_DIR": "/evil", "GIT_CONFIG_PARAMETERS": "x",
                            "HOME": "/h"})
        self.assertNotIn("GIT_DIR", env)
        self.assertNotIn("GIT_CONFIG_PARAMETERS", env)
        self.assertEqual((env["PATH"], env["HOME"]), ("/bin", "/h"))
        self.assertEqual(env["GIT_CONFIG_NOSYSTEM"], "1")
        self.assertEqual(env["GIT_CONFIG_GLOBAL"], __import__("os").devnull)
        self.assertEqual(env["GIT_TERMINAL_PROMPT"], "0")
        pinned = [(env[f"GIT_CONFIG_KEY_{i}"], env[f"GIT_CONFIG_VALUE_{i}"])
                  for i in range(int(env["GIT_CONFIG_COUNT"]))]
        self.assertEqual(tuple(pinned), HOST_GIT_CONFIG)
        keys = dict(pinned)
        for key, value in (("core.fsmonitor", "false"), ("commit.gpgsign", "false"),
                           ("protocol.ext.allow", "never")):
            self.assertEqual(keys[key], value)
        # The ambient credential helper is cleared before the pinned one is set.
        helpers = [v for k, v in pinned if k == "credential.helper"]
        self.assertEqual(helpers[0], "")
        self.assertEqual(len(helpers), 2)

    def test_only_git_gets_the_host_git_environment(self):
        from agent_bus.shell import Runner
        seen = []
        def fake_run(argv, **kw):
            seen.append((argv[0], kw.get("env")))
            return mock.Mock(returncode=0, stdout="", stderr="")
        with mock.patch("subprocess.run", fake_run):
            Runner()(["git", "status"])
            Runner()(["gh", "api", "x"])
        self.assertEqual(seen[0][1]["GIT_CONFIG_NOSYSTEM"], "1")
        self.assertIsNone(seen[1][1])


# ---------------------------------------------------------------------------
# 7. Rigs: each guard, disabled on purpose, lets its failure through (RED)
# ---------------------------------------------------------------------------

class TestRiggedGuards(unittest.TestCase):
    def test_rig_scope_guard_off_the_host_would_commit_an_escape(self):
        fake = repo(ok("claude", "U1", "pipeline/build_db.py"))
        with mock.patch.object(F, "scope_violations", lambda *a, **k: []):
            armed(fake, order=("claude",), max_units=1).poll_once(execute=True)
        # Red: the escaped path reached the index and a commit. (The ordinary
        # post-commit verification still catches it, which is why the pre-staging
        # guard is the one that keeps the escape out of history.)
        self.assertEqual(fake.commits[-1][2], ("pipeline/build_db.py",))

    def test_rig_mutation_guard_off_a_provider_ref_move_would_reach_pass(self):
        fake = repo(Step("codex", dirty=("agent_bus/x.py",),
                         then=lambda r: r.extra_refs.update({"refs/tags/x": r.head})))
        with mock.patch.object(F, "git_mutations", lambda *a: []):
            report = armed(fake, order=("codex",), max_units=1).poll_once(execute=True)
        self.assertEqual(report["action"], "WAVE_RAN")   # red: the mutation got through


if __name__ == "__main__":
    unittest.main()
