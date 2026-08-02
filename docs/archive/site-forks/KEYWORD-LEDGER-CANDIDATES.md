# Keyword Ledger Candidates

Standing doc for keyword mechanics killed out of the T3 axis foundry's
derived-tag layer (`rule:` namespace) because the signal belongs to the
Tagger/keyword layer, not a derived tag — per
`~/Projects/mtjawnny.github.io/docs/SUP-TRIAGE-PROTOCOL.md`: "Bare keywords
/ reminder text / procedural riders are never axes; killed keyword
mechanics go to `docs/KEYWORD-LEDGER-CANDIDATES.md` in the same commit
set." This is a holding pen, not a spec — Phase B (the ratified keyword
ledger, per `DERIVED-TAG-LAYER-SPEC.md`) is the governed home for these
once it exists. Nothing here is load-bearing.

Lives in THIS repo (mtjawnny-pipeline), not the site repo — unlike the rest
of the strategy docs referenced by the SUP-triage protocol, this one must
be durably version-controlled: the lane-1b keyword kills in batch 1 are
conditional on this doc existing and staying tracked.

Each entry: the keyword/mechanic, why it surfaced in triage, representative
cards + quotes, and any kinship note worth carrying into Phase B design.

## Batch 1 (2026-07-18)

### Convoke
- **Killed axis:** `rule:convoke-cost-reduction` (DF 100, lane 1b)
- **Representative cards:** Chord of Calling, Clever Concealment —
  "Convoke (Your creatures can help cast this spell. Each creature you tap
  while casting this spell pays for {1} or one mana of that creature's
  color.)"
- **Note:** Cost-alternative-payment keyword; equipment-ness/type-line-style
  fact, not a derived kinship axis.

### Exploit
- **Killed axis:** `rule:exploit-sacrifice-trigger` (DF 24, lane 1b)
- **Representative cards:** Rakshasa Gravecaller, Minister of Pain —
  "Exploit (When this creature enters, you may sacrifice a creature.)"
- **Note (SUP, carried forward for Phase B design):** exploit-as-functional-
  sac-outlet kinship to non-keyword free-sacrifice-outlet cards (Ashnod's
  Altar, Phyrexian Altar — see codebook `rule:free-sacrifice-outlet`) is a
  genuinely good ledger entry; worth a cross-reference at Phase B design
  time rather than a derived axis now.

### Cascade
- **Not promoted** from OTHER lane (excluded from `rule:free-cast`, P7).
- **Representative card:** Bloodbraid Elf — "Cascade (When you cast this
  spell, exile cards from the top of your library until you exile a
  nonland card that costs less. You may cast it without paying its mana
  cost. Put the exiled cards on the bottom of your library in a random
  order.)"
- **Note:** free-cast-shaped effect, but the *keyword* Cascade is the
  Tagger's territory; the non-keyword free-cast family (Omniscience, Fires
  of Invention, Etali) is what `rule:free-cast` covers.

### Delve
- **Not promoted** from OTHER lane (excluded from `rule:cost-reduction`,
  P6).
- **Representative card:** Dead Drop — "Delve (Each card you exile from
  your graveyard while casting this spell pays for {1}.)"
- **Note:** alternative-cost-payment keyword, same shape as Convoke/
  Affinity; cost-reduction axis stays non-keyword (tribal/type/color/
  chosen-type/condition filters).

### Affinity
- **Not promoted** from OTHER lane (excluded from `rule:cost-reduction`,
  P6).
- **Representative card:** Sky-Blessed Samurai — "Affinity for enchantments
  (This spell costs {1} less to cast for each enchantment you control.)"
- **Note:** same alternative-cost-payment shape as Convoke/Delve.

### Ward
- **Not promoted** from OTHER lane (P12: "Ward rows: do NOT promote... same
  KILL logic as lane 1a").
- **Representative cards:** Roaming Throne — "Ward {2}"; Rimeshield Frost
  Giant — "Ward {3} (Whenever this creature becomes the target of a spell
  or ability an opponent controls, counter it unless that player pays
  {3}.)"
- **Note:** bare keyword + reminder text, Tagger-covered; no distinct
  kinship signal beyond the keyword itself.

## Batch 2 (2026-07-19)

### Kicker
- **Killed axes:** `rule:kicked-conditional-etb-bonus`,
  `rule:kicker-scales-effect`, `rule:kicker-scales-effect-magnitude` (3
  free-lane candidates, all the same keyword)
- **Representative cards:** All-Star Kicker — "Then if All-Star Kicker was
  kicked, creatures your team controls get +1/+1 and gain haste..."; Shell
  Shield — "If this spell was kicked, that creature also gains hexproof
  until end of turn."; Burst Lightning — "If this spell was kicked, it
  deals 4 damage instead."
- **Note:** Kicker (optional additional cost, conditional payoff) is a
  CR-defined keyword; the "if kicked" branching is the keyword's own
  rules text, not a derived functional pattern. Three separately-worded
  free-lane clusters collapsed to one ledger entry.

### Venture into the Dungeon
- **Killed axis:** `rule:venture-into-dungeon`
- **Representative cards:** Undercity // The Initiative — "You can't enter
  this dungeon unless you 'venture into Undercity.'"; Lost Mine of
  Phandelver — "Cave Entrance — Scry 1. (Leads to: Goblin Lair, Mine
  Tunnels)"
- **Note:** Venture into the Dungeon is a CR-defined keyword action
  (Adventures in the Forgotten Realms).

### Daybound/Nightbound (werewolf transform)
- **Killed axis:** `rule:werewolf-daybound-transform-trigger`
- **Representative card:** Lambholt Pacifist // Lambholt Butcher — "At the
  beginning of each upkeep, if no spells were cast last turn, transform
  this creature." / "...if a player cast two or more spells last turn,
  transform..."
- **Note:** Daybound/Nightbound is a CR-defined keyword pair. Also flagged
  as single-card evidence (both instances trace to the same card) —
  doubly disqualified as a derived axis.

### Saga-chapter-transform templating
- **Killed axis:** `rule:saga-transform-into-creature`
- **Representative cards:** The Legend of Kuruk // Avatar Kuruk, Azusa's
  Many Journeys // Likeness of the Seeker — both: "Exile this Saga, then
  return it to the battlefield transformed under your control."
- **Note:** Standard Saga-template boilerplate for chapter-final
  transformation, same standing as batch-1-killed
  `rule:saga-chapter-progression` — a layout/template fact, not a
  functional kinship signal.

### Spellbook
- **Killed axis:** `rule:draft-from-spellbook` (Q3, Captain-ratified
  kill-and-ledger)
- **Representative cards:** Key to the Archive — "When this artifact
  enters, draft a card from this artifact's spellbook, then discard a
  card..."; March Toward Perfection — "Draft a card from March Toward
  Perfection's spellbook."
- **Note:** "Spellbook" drafting is a defined, recurring game-rules
  concept tied to specific cards (not a CR keyword with its own reminder
  text, but functions the same way for ledger purposes per Captain's
  ruling) — real mechanic, but the shared surface is the spellbook
  mechanism itself, not a derived functional pattern.
