"""Guard the cold-start control plane against stale routing.

Task selection has one owner: GitHub Issue #1 latest K -> active T.
The root README is the generic LLM router; CLAUDE.md is the Claude Worker law;
SESSION-PROTOCOL keeps durable Manager/Worker semantics; WORKER-START is only a
compact role pointer. Historical phase/bootstrap paths are inert tombstones.
"""
from __future__ import annotations
import re
import unittest
from tests.refoundation.helpers import REPO_ROOT

README = REPO_ROOT / 'README.md'
CLAUDE = REPO_ROOT / 'CLAUDE.md'
WORKER = REPO_ROOT / 'refoundation' / 'WORKER-START.md'
PROTOCOL = REPO_ROOT / 'refoundation' / 'SESSION-PROTOCOL.md'
ACTIVE_TOMBSTONE = REPO_ROOT / 'refoundation' / 'ACTIVE-PHASE.yaml'
BOOTSTRAP_TOMBSTONE = REPO_ROOT / 'refoundation' / 'BOOTSTRAP-STATE.yaml'
CURRENT_ROUTING = {
    'README.md': README,
    'CLAUDE.md': CLAUDE,
    'refoundation/WORKER-START.md': WORKER,
    'refoundation/SESSION-PROTOCOL.md': PROTOCOL,
}
ARCHIVED_ROUTING = (
    REPO_ROOT / 'archive/routing/refoundation/ACTIVE-PHASE.yaml',
    REPO_ROOT / 'archive/routing/refoundation/BOOTSTRAP-STATE.yaml',
    REPO_ROOT / 'archive/routing/refoundation/MANAGER-START.md',
    REPO_ROOT / 'archive/routing/refoundation/README.md',
    REPO_ROOT / 'archive/routing/refoundation/ROADMAP.md',
)
K_SELECTOR = 'latest K -> active T'
PROTOCOL_FORM = 'M:T -> W:X -> M:V -> M:T|K'
EXACT_HUMAN_CONTRACT = 'Claude done'
IMPORT_RE = re.compile(r'@([A-Za-z0-9_.\-]+(?:/[A-Za-z0-9_.\-]+)+)')
SHA40_RE = re.compile(r'\b[0-9a-f]{40}\b')
PR_STATE_RE = re.compile(r'(?i)\b(?:PR|pull[\s_-]?request)[\s_-]*#?\s*\d+')
STALE_SELECTOR_RE = re.compile(r'latest\s+accepted\s+K', re.I)
HISTORICAL_ROUTING = (
    r'docs/SESSION-HANDOFF[A-Za-z0-9-]*\.md', r'docs/PICK-UP-HERE\.md',
    r'docs/SESSION-START-PROCEDURE\.md', r'docs/NEXT-SESSION-[A-Za-z0-9-]*\.md',
    r'refoundation/ACTIVE-PHASE\.yaml', r'refoundation/BOOTSTRAP-STATE\.yaml',
    r'refoundation/MANAGER-START\.md', r'refoundation/ROADMAP\.md',
    r'refoundation-manager-bootstrap-\d{4}-\d{2}-\d{2}',
)
EVERY_SESSION_INVARIANTS = (
    'PRESERVE TRUTH, NOT PLUMBING','Issue #1','self-authorized successor',
    'Never merge','STOP','transitive','Negative-control','No card data in git',
    'oracle_id','Halt loudly','Determinism','Captain','Manager','Worker',
)
AUTHORITY_LAW_PHRASES = ('evidence, not authority','never self-authorizes','STOP and report the conflict')
RANK_RULE='Rank buries, never excludes'
RANK_LAW='Rank buries, never excludes (sole exception: corroboration gate).'

def flat(text: str) -> str:
    return re.sub(r'\s+',' ',text.replace('*','').replace('`',''))
def selector_problems(text: str):
    f=flat(text); out=[]
    if K_SELECTOR not in f: out.append('missing canonical selector')
    if STALE_SELECTOR_RE.search(f): out.append('stale selector spelling')
    return out
def historical_routing_problems(text: str):
    return [m.group(0) for p in HISTORICAL_ROUTING for m in re.finditer(p,text)]
def startup_import_problems(text: str):
    imports=IMPORT_RE.findall(text)
    return [] if not imports else [f'startup imports are {imports}; expected none']
def authority_problems(text: str):
    f=flat(text); return [p for p in AUTHORITY_LAW_PHRASES if p not in f]
def rank_problems(text: str):
    f=flat(text)
    return [] if RANK_RULE not in f or RANK_LAW in f else ['rank exception lost']
def protocol_problems(text: str):
    out=[]
    if PROTOCOL_FORM not in text: out.append('branching protocol missing')
    if re.search(r'M:V\s*->\s*M:K',text): out.append('mandatory K')
    return out
def checkpoint_problems(text: str):
    f=flat(text); out=[]
    for phrase in ('K is a CHECKPOINT','accepted_head','active_task'):
        if phrase not in f: out.append(f'missing {phrase}')
    if K_SELECTOR not in f: out.append('missing selector')
    if re.search(r'K\s*=\s*acceptance|K is the acceptance arm|records? acceptance \(K\)',f):
        out.append('K equated with acceptance')
    return out
def tombstone_problems(text: str, archive_path: str):
    out=[]
    for required in ('ARCHIVED_DO_NOT_FOLLOW', archive_path, 'GitHub Issue #1', 'latest K -> active T'):
        if required not in flat(text): out.append(f'missing {required}')
    if re.search(r'(?mi)^\s*(?:next|phase|goal|current_strategy)\s*:',text): out.append('carries task/phase state')
    return out
def generic_router_problems(text: str):
    out=selector_problems(text)+historical_routing_problems(text)
    if SHA40_RE.search(text): out.append('mirrors a SHA')
    if PR_STATE_RE.search(text): out.append('mirrors PR state')
    if 'archive/' not in text or 'inert history' not in text: out.append('archive boundary missing')
    return out

class TestColdStartContract(unittest.TestCase):
    def setUp(self):
        self.text={n:p.read_text(encoding='utf-8') for n,p in CURRENT_ROUTING.items()}
        self.claude=self.text['CLAUDE.md']; self.protocol=self.text['refoundation/SESSION-PROTOCOL.md']
    def test_current_routing_files_exist_and_archived_bodies_are_retained(self):
        for p in CURRENT_ROUTING.values(): self.assertTrue(p.is_file(),p)
        for p in ARCHIVED_ROUTING: self.assertTrue(p.is_file(),p)
    def test_generic_root_router_points_only_to_durable_authority(self):
        self.assertEqual(generic_router_problems(self.text['README.md']),[])
    def test_no_current_routing_document_routes_through_superseded_state(self):
        for n,t in self.text.items():
            with self.subTest(n=n): self.assertEqual(historical_routing_problems(t),[])
    def test_every_current_router_carries_the_one_selector(self):
        for n,t in self.text.items():
            with self.subTest(n=n): self.assertEqual(selector_problems(t),[])
    def test_root_contract_imports_no_repository_state_file(self):
        self.assertEqual(startup_import_problems(self.claude),[])
    def test_exact_human_contract_and_every_session_rules_survive(self):
        self.assertIn(EXACT_HUMAN_CONTRACT,self.claude)
        for rule in EVERY_SESSION_INVARIANTS: self.assertIn(rule,self.claude,rule)
    def test_measurement_remains_evidence_not_authority(self):
        self.assertEqual(authority_problems(self.claude),[])
    def test_rank_exception_survives_if_rank_rule_survives(self):
        self.assertEqual(rank_problems(self.claude),[])
    def test_protocol_branching_and_checkpoint_semantics_survive(self):
        self.assertEqual(protocol_problems(self.protocol),[])
        self.assertEqual(checkpoint_problems(self.protocol),[])
        self.assertEqual(checkpoint_problems(self.claude),[])
    def test_phase_and_bootstrap_paths_are_inert_tombstones(self):
        self.assertEqual(tombstone_problems(ACTIVE_TOMBSTONE.read_text(), 'archive/routing/refoundation/ACTIVE-PHASE.yaml'),[])
        self.assertEqual(tombstone_problems(BOOTSTRAP_TOMBSTONE.read_text(), 'archive/routing/refoundation/BOOTSTRAP-STATE.yaml'),[])
    def test_control_plane_is_compact(self):
        self.assertLessEqual(len(self.claude.splitlines()),180)
        self.assertLessEqual(len(self.claude.encode()),8000)
        self.assertLessEqual(len(self.text['README.md'].splitlines()),40)
        self.assertLessEqual(len(self.text['refoundation/WORKER-START.md'].splitlines()),25)
        self.assertLessEqual(len(self.protocol.splitlines()),140)

class TestColdStartNegativeControls(unittest.TestCase):
    def setUp(self):
        self.claude=CLAUDE.read_text(); self.protocol=PROTOCOL.read_text(); self.readme=README.read_text()
    def test_NC1_dated_handoff_route_is_red(self):
        self.assertTrue(historical_routing_problems(self.readme+'\nRead docs/SESSION-HANDOFF-2026-08-09.md'))
    def test_NC2_phase_import_is_red(self):
        self.assertTrue(startup_import_problems(self.claude+'\n@refoundation/ACTIVE-PHASE.yaml'))
    def test_NC3_stale_selector_is_red(self):
        rig=self.readme.replace('latest `K` -> active `T`','latest accepted `K` -> active `T`')
        self.assertTrue(selector_problems(rig))
    def test_NC4_missing_selector_is_red(self):
        rig=self.readme.replace('latest `K` -> active `T`','whichever task looks current')
        self.assertTrue(selector_problems(rig))
    def test_NC5_K_as_acceptance_is_red(self):
        self.assertTrue(checkpoint_problems(self.claude+'\nK = acceptance\n'))
    def test_NC6_mandatory_K_protocol_is_red(self):
        rig=self.protocol.replace(PROTOCOL_FORM,'M:T -> W:X -> M:V -> M:K')
        self.assertTrue(protocol_problems(rig))
    def test_NC7_dropping_authority_law_is_red(self):
        rig=self.claude.replace('**A measurement is evidence, not authority, and it never self-authorizes.**','Believe the measurement.')
        self.assertTrue(authority_problems(rig))
    def test_NC8_dropping_rank_exception_is_red(self):
        rig=self.claude.replace('Rank buries, never excludes (sole exception:\n  corroboration gate).','Rank buries, never excludes.')
        self.assertTrue(rank_problems(rig))
    def test_NC9_current_SHA_in_generic_router_is_red(self):
        self.assertTrue(generic_router_problems(self.readme+'\naccepted: 9412e9e6236dd6509941b668f0951fdbfc213d29'))
    def test_NC10_reactivating_tombstone_is_red(self):
        t=ACTIVE_TOMBSTONE.read_text()+'\nphase: DO_THIS_NEXT\n'
        self.assertTrue(tombstone_problems(t,'archive/routing/refoundation/ACTIVE-PHASE.yaml'))

if __name__=='__main__': unittest.main()
