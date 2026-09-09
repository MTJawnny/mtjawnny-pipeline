/* The Path E diagnostic pilot — rendering only.
 *
 * WHAT IS DELIBERATELY ABSENT FROM THIS FILE, and the reason it is absent:
 *
 *   - no comparator, sort key or ordering rule;
 *   - no candidate rule and no set intersection that could stand in for one;
 *   - no feature arithmetic — shared_axis_count and shared_axis_cardinalities
 *     arrive per tie block, already computed;
 *   - no threshold, weight, score or similarity of any kind.
 *
 * `mtj_foundry.pilot` precomputes every candidate list by calling the accepted
 * milestone-2 `retrieval.query`, and `pilot.verify_retrieval_equivalence`
 * re-checks the emitted bytes against that same function for every anchor. So a
 * defect in this file can misdraw a block; it cannot invent a different ranking,
 * because there is no ranking code here to be wrong. That asymmetry is the whole
 * design — the 2026-08-09 wire result records what happens when the thing that
 * orders and the thing that displays are separate code with the same intentions.
 *
 * Everything below reads bundle files by RELATIVE path. There is no absolute
 * URL, no CDN, no font host, no analytics and no API in this bundle. */

"use strict";

const state = {
  meta: null, cards: null, names: null, axes: null, evidence: null,
  normalization: null,          // {strip: Set, fold: Map} from the bundle
  positionById: new Map(),      // oracle_id -> card index
  membershipsByCard: new Map(), // card index -> [[axis index, member], ...]
  nameKeys: [],                 // normalized names, artifact order
  textShards: new Map(),        // shard -> Map(card index -> faces)
  retrievalShards: new Map(),   // shard -> Map(card index -> anchor payload)
  selected: null,
};

const RESULT_LIMIT = 300;

/* ---- small helpers ----------------------------------------------------- */

function el(tag, className, text) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text !== undefined && text !== null) node.textContent = String(text);
  return node;
}

function shardOf(oracleId) { return oracleId.slice(0, 2); }

async function getJSON(path) {
  const response = await fetch(path, { cache: "no-store" });
  if (!response.ok) throw new Error(path + ": HTTP " + response.status);
  return response.json();
}

/* THE ACCEPTED NORMALIZATION, RUN IN THE BROWSER. M3.R1 repair A.
 *
 * The artifact's name index is keyed with Python `str.strip().casefold()`. The
 * first M3 candidate approximated that here as `trim().toLowerCase()` and said
 * in a comment that they differ, which made it a known contract deviation
 * rather than an edge case. Both halves are wrong:
 *
 *   - `toLowerCase()` is not full case folding. U+017F folds to "s", U+00DF to
 *     "ss", U+FB01 to "fi"; toLowerCase leaves all three alone. So `ſol ring`
 *     resolved to Sol Ring in Python and MISSED in the browser -- a real query
 *     against the real bundle, not a hypothetical.
 *   - `trim()` is not `str.strip()`. Python strips U+001C-001F and U+0085,
 *     which trim keeps; trim removes U+FEFF, which Python keeps. Neither set
 *     contains the other, so no amount of care with toLowerCase fixes it.
 *
 * The table in `data/normalization.json` is DERIVED by `mtj_foundry.pilot`
 * asking Python about every Unicode code point, and is proven against
 * `str.strip().casefold()` at build time over every card name in the index,
 * every code point the table mentions, and fixed synthetic witnesses. Nothing
 * is hardcoded here and no character is special-cased.
 *
 * Full case folding is context-free, so folding a string is exactly folding
 * each code point and concatenating -- which is why a table is faithful here
 * and would NOT be for lowercasing.
 *
 * THIS IS NOT A SEARCH FEATURE. It turns a typed query into a KEY. Every lookup
 * downstream is still exact, prefix or substring against the artifact's own key
 * list: no fuzzy matching, no similarity, no scoring, no ranking, no threshold.
 * A card's own key is never re-derived -- those come from the artifact. */
function normalizeQuery(text) {
  const table = state.normalization;
  const chars = Array.from(text);          // code points, not UTF-16 units
  let start = 0;
  let end = chars.length;
  while (start < end && table.strip.has(chars[start])) start += 1;
  while (end > start && table.strip.has(chars[end - 1])) end -= 1;
  let out = "";
  for (let i = start; i < end; i += 1) {
    const folded = table.fold.get(chars[i]);
    out += folded === undefined ? chars[i] : folded;
  }
  return out;
}

function cardCount() { return state.cards.count; }
function nameOf(i) { return state.cards.name[i]; }
function idOf(i) { return state.cards.oracle_id[i]; }
function isEligible(i) { return state.cards.gate0_eligible[i] === 1; }
function isAssigned(i) { return state.cards.assigned[i] === 1; }

/* ---- boot -------------------------------------------------------------- */

async function boot() {
  try {
    const [meta, cards, names, axes, evidence, normalization] = await Promise.all([
      getJSON("data/meta.json"), getJSON("data/cards.json"),
      getJSON("data/names.json"), getJSON("data/axes.json"),
      getJSON("data/evidence.json"), getJSON("data/normalization.json"),
    ]);
    state.meta = meta; state.cards = cards; state.names = names;
    state.axes = axes; state.evidence = evidence;
    state.normalization = {
      strip: new Set(normalization.strip),
      fold: new Map(Object.entries(normalization.fold)),
    };
    for (let i = 0; i < cards.count; i += 1) state.positionById.set(cards.oracle_id[i], i);
    for (const [cardIndex, rows] of evidence.rows) state.membershipsByCard.set(cardIndex, rows);
    state.nameKeys = Object.keys(names.names);
    renderDisclosure();
    wireControls();
    renderResults("");
    window.addEventListener("hashchange", applyHash);
    applyHash();
  } catch (error) {
    document.querySelector("#card-pane").replaceChildren(
      el("div", "error",
        "This bundle's data files could not be loaded (" + error.message + "). " +
        "The pilot reads its data by relative path, so it must be served over " +
        "HTTP by any plain static file server — for example: " +
        "python3 -m http.server --directory <bundle> 8000. Opening index.html " +
        "directly from the filesystem will not work."));
    document.querySelector("#status-badge").textContent = "DATA NOT LOADED";
  }
}

/* ---- disclosure -------------------------------------------------------- */

function renderDisclosure() {
  const d = state.meta.disclosure;
  document.querySelector("#status-badge").textContent = d.status;
  document.querySelector("#disclosure-headline").textContent = d.headline;
  const points = document.querySelector("#disclosure-points");
  points.replaceChildren(...d.points.map((p) => el("li", null, p)));

  document.querySelector("#does-not-prove").replaceChildren(
    ...d.what_this_does_not_prove.map((p) => el("li", null, p)));

  document.querySelector("#ordering-keys").replaceChildren(
    ...d.ordering.keys.map((k) => el("li", "mono", k)));
  document.querySelector("#ordering-note").textContent =
    d.ordering.is + " Constants: " + d.ordering.constants + " " + d.tie_blocks_are;

  const semantics = d.evidence_state_semantics;
  document.querySelector("#unassigned-means").textContent =
    semantics.UNASSIGNED_NO_ACTIVE_EVIDENCE + ". " + semantics.absent_membership_is + ".";
  document.querySelector("#unassigned-is-not").replaceChildren(
    ...semantics.UNASSIGNED_IS_NOT.map((p) => el("li", null, p)));

  const dl = document.querySelector("#source-identities");
  const rows = [
    ["evidence index", state.meta.source_artifacts.index.sha256],
    ["index bytes", state.meta.source_artifacts.index.byte_size.toLocaleString()],
    ["evaluation report", state.meta.source_artifacts.evaluation.sha256],
    ["selected codebook", state.meta.selected_inputs.codebook.measured_sha256],
    ["selected corpus", state.meta.selected_inputs.corpus.measured_sha256],
    ["corpus identity status", state.meta.selected_inputs.corpus.identity_status],
  ];
  dl.replaceChildren();
  for (const [label, value] of rows) {
    dl.append(el("dt", null, label), el("dd", null, value));
  }

  const pop = state.meta.population;
  document.querySelector("#footer-note").textContent =
    state.meta.schema + " · built by " + state.meta.generator.package + " " +
    state.meta.generator.version + " · " + state.meta.bundle_is + " · " +
    pop.coverage.corpus_ids_total.toLocaleString() + " cards, " +
    pop.coverage.corpus_ids_covered.toLocaleString() + " with active evidence, " +
    state.axes.count + " active axes. This bundle reads " + state.meta.runtime.reads + ".";

  const toggle = document.querySelector("#disclosure-toggle");
  toggle.addEventListener("click", () => {
    const panel = document.querySelector("#disclosure");
    const hidden = panel.hasAttribute("hidden");
    if (hidden) panel.removeAttribute("hidden"); else panel.setAttribute("hidden", "");
    toggle.setAttribute("aria-expanded", String(hidden));
    toggle.textContent = hidden ? "hide notice" : "show notice";
  });
}

/* ---- deep links --------------------------------------------------------
 *
 * `#card=<oracle_id>` and `#q=<query>`. A card is addressed by ORACLE_ID and
 * never by name, for the same reason the retrieval layer refuses an ambiguous
 * name: 216 normalized names in this corpus belong to more than one card, and a
 * link that named one of them would silently resolve to whichever identity
 * happened to sort first. */

function applyHash() {
  const hash = window.location.hash.replace(/^#/, "");
  if (!hash) return;
  const params = new URLSearchParams(hash);
  const query = params.get("q");
  if (query !== null) {
    document.querySelector("#query").value = query;
    renderResults(query);
  }
  const oracleId = params.get("card");
  if (oracleId === null) return;
  const cardIndex = state.positionById.get(oracleId);
  if (cardIndex === undefined) {
    document.querySelector("#card-pane").replaceChildren(el("div", "error",
      "oracle_id " + oracleId + " is not a card of the selected corpus. That is " +
      "NOT the same as a card with no active evidence."));
    return;
  }
  if (state.selected !== cardIndex) selectCard(cardIndex);
}

/* ---- finding a card ---------------------------------------------------- */

function wireControls() {
  const input = document.querySelector("#query");
  input.addEventListener("input", () => renderResults(input.value));
  for (const id of ["#filter-eligible", "#filter-assigned"]) {
    document.querySelector(id).addEventListener("change", () => renderResults(input.value));
  }
  document.querySelector("#finder-hint").textContent =
    cardCount().toLocaleString() + " cards, all selectable. " +
    state.names.ambiguous_names.toLocaleString() +
    " normalized names are shared by more than one card; those are never " +
    "collapsed — pick the oracle_id you mean.";
}

function passesFilters(i) {
  if (document.querySelector("#filter-eligible").checked && !isEligible(i)) return false;
  if (document.querySelector("#filter-assigned").checked && !isAssigned(i)) return false;
  return true;
}

/* Matching is a LOOKUP, never a similarity. Exact normalized name first, then
 * prefix, then substring, then a direct oracle_id hit. Nothing is scored. */
function stripOnly(text) {
  const table = state.normalization;
  const chars = Array.from(text);
  let start = 0;
  let end = chars.length;
  while (start < end && table.strip.has(chars[start])) start += 1;
  while (end > start && table.strip.has(chars[end - 1])) end -= 1;
  return chars.slice(start, end).join("");
}

function findMatches(raw) {
  const query = normalizeQuery(raw);
  if (!query) return { groups: [], total: 0 };
  const groups = [];
  const seen = new Set();

  /* An oracle_id is matched EXACTLY, after only the accepted strip -- an id is
   * a key, not a name, and case-folding one would be inventing an identity
   * rule the artifact does not have. `stripOnly` uses the same derived set as
   * the normalizer so the two cannot disagree about what whitespace is. */
  const bare = stripOnly(raw);
  const direct = state.positionById.get(bare);
  if (direct !== undefined) {
    groups.push({ label: "oracle_id", key: bare, indices: [direct] });
    seen.add(direct);
  }

  const exact = state.names.names[query];
  if (exact) {
    groups.push({ label: "exact name", key: query, indices: exact.slice() });
    for (const i of exact) seen.add(i);
  }

  const prefix = [];
  const substring = [];
  for (const key of state.nameKeys) {
    if (key === query) continue;
    if (key.startsWith(query)) prefix.push(key);
    else if (key.includes(query)) substring.push(key);
  }
  for (const [label, keys] of [["name starts with", prefix], ["name contains", substring]]) {
    for (const key of keys) {
      const indices = state.names.names[key].filter((i) => !seen.has(i));
      if (indices.length) {
        groups.push({ label, key, indices });
        for (const i of indices) seen.add(i);
      }
    }
  }
  return { groups, total: seen.size };
}

function renderResults(raw) {
  const list = document.querySelector("#results");
  const count = document.querySelector("#result-count");
  list.replaceChildren();
  if (!stripOnly(raw)) {
    count.textContent = "Type a card name or a full oracle_id.";
    return;
  }
  const { groups } = findMatches(raw);
  let shown = 0, matched = 0, hiddenByFilter = 0;
  for (const group of groups) {
    const visible = group.indices.filter((i) => {
      if (passesFilters(i)) return true;
      hiddenByFilter += 1;
      return false;
    });
    matched += visible.length;
    if (!visible.length) continue;
    /* AMBIGUITY IS NEVER RESOLVED HERE. A normalized name carrying more than one
     * identity is announced as such and every identity is listed; the reader
     * picks the oracle_id. `oracle_id` is the only card key. */
    if (group.label !== "oracle_id" && group.indices.length > 1) {
      const box = el("li");
      const warn = el("div", "ambiguity");
      warn.append(
        el("h3", null, "ambiguous name — " + group.indices.length + " identities"),
        el("p", null, "“" + group.key + "” matches " + group.indices.length +
          " distinct cards. They are not merged. Choose one by oracle_id."));
      box.append(warn);
      list.append(box);
    }
    for (const i of visible) {
      if (shown >= RESULT_LIMIT) break;
      list.append(resultRow(i, group.label));
      shown += 1;
    }
  }
  const parts = [matched.toLocaleString() + " card" + (matched === 1 ? "" : "s") + " matched"];
  if (shown < matched) parts.push("showing the first " + shown.toLocaleString());
  if (hiddenByFilter) {
    parts.push(hiddenByFilter.toLocaleString() +
      " hidden by YOUR view filters — still in the bundle, still selectable with the filters off");
  }
  count.textContent = parts.join(" · ");
}

function resultRow(i, how) {
  const item = el("li");
  const button = el("button");
  button.type = "button";
  const name = el("span", "rname", nameOf(i));
  const badges = [];
  if (!isEligible(i)) badges.push("gate0-ineligible");
  badges.push(isAssigned(i) ? "evidence" : "unassigned");
  const meta = el("span", "rid", idOf(i) + "  ·  " + badges.join(" · ") + "  ·  " + how);
  button.append(name, meta);
  button.addEventListener("click", () => selectCard(i));
  item.append(button);
  return item;
}

/* ---- shard loading ----------------------------------------------------- */

async function faceRows(cardIndex) {
  const shard = shardOf(idOf(cardIndex));
  if (!state.textShards.has(shard)) {
    const payload = await getJSON("data/text/" + shard + ".json");
    state.textShards.set(shard, new Map(payload.rows));
  }
  return state.textShards.get(shard).get(cardIndex);
}

async function anchorRows(cardIndex) {
  const shard = shardOf(idOf(cardIndex));
  if (!state.retrievalShards.has(shard)) {
    const payload = await getJSON("data/retrieval/" + shard + ".json");
    state.retrievalShards.set(shard, new Map(payload.rows));
  }
  return state.retrievalShards.get(shard).get(cardIndex);
}

/* ---- rendering one card ------------------------------------------------ */

async function selectCard(cardIndex) {
  state.selected = cardIndex;
  const link = "#card=" + idOf(cardIndex);
  if (window.location.hash !== link) window.history.replaceState(null, "", link);
  const pane = document.querySelector("#card-pane");
  pane.replaceChildren(el("p", "empty", "loading " + nameOf(cardIndex) + "…"));
  try {
    const faces = await faceRows(cardIndex);
    const anchor = isAssigned(cardIndex) ? await anchorRows(cardIndex) : null;
    if (state.selected !== cardIndex) return;
    const nodes = [cardHead(cardIndex), facePanel(faces), membershipPanel(cardIndex)];
    nodes.push(anchor ? await candidatePanel(cardIndex, anchor) : absencePanel());
    pane.replaceChildren(...nodes.filter(Boolean));
    pane.scrollIntoView({ block: "start" });
  } catch (error) {
    pane.replaceChildren(el("div", "error", "could not load this card: " + error.message));
  }
}

function cardHead(i) {
  const head = el("div", "card-head");
  head.append(el("h2", null, nameOf(i)));
  head.append(el("p", "card-ids",
    "oracle_id " + idOf(i) + "   ·   normalized “" + state.cards.normalized_name[i] + "”"));
  const badges = el("div", "badges");
  badges.append(el("span", isEligible(i) ? "badge" : "badge warn",
    isEligible(i) ? "GATE#0 ELIGIBLE" : "GATE#0 INELIGIBLE"));
  badges.append(el("span", isAssigned(i) ? "badge" : "badge absent",
    isAssigned(i) ? state.cards.evidence_state_codes["1"]
                  : state.cards.evidence_state_codes["0"]));
  badges.append(el("span", "badge", state.cards.face_count[i] + " face" +
    (state.cards.face_count[i] === 1 ? "" : "s")));
  const shared = state.names.names[state.cards.normalized_name[i]] || [];
  if (shared.length > 1) {
    badges.append(el("span", "badge warn",
      "NAME SHARED BY " + shared.length + " CARDS"));
  }
  head.append(badges);
  if (!isEligible(i)) {
    head.append(el("p", "muted",
      "Gate #0 is a dataset-scope ruling about whether a card is a valid pipeline " +
      "target — legal or restricted in at least one format. It says nothing about " +
      "similarity, and this card is in the bundle in full."));
  }
  return head;
}

function facePanel(faces) {
  const panel = el("section", "panel");
  panel.append(el("h3", null, faces.length > 1 ? "Card text — all faces" : "Card text"));
  for (const face of faces) {
    const block = el("div", "face");
    const head = el("div", "face-head");
    head.append(el("strong", null, face.name));
    const bits = [face.mana_cost, face.type_line].filter(Boolean);
    if (face.power !== null && face.power !== undefined) {
      bits.push(face.power + "/" + face.toughness);
    }
    if (bits.length) head.append(el("span", "face-meta", bits.join("   ·   ")));
    block.append(head);
    block.append(face.oracle_text
      ? el("p", "oracle", face.oracle_text)
      : el("p", "oracle blank", "(no oracle text on this face)"));
    panel.append(block);
  }
  return panel;
}

function axisAt(axisIndex) {
  return state.axes.axes[state.axes.order[axisIndex]];
}

/* Renders a codebook member object WITHOUT enumerating the keys it expects.
 *
 * The index copies member objects WHOLE so that a field a later codebook schema
 * adds still arrives; a renderer with a fixed field list would drop it again at
 * the last step, which is the same loss with a longer delay. So this walks
 * whatever keys are present, at whatever depth, and the ONE key it treats
 * specially is `quote` — set as a block rather than a line, because it is the
 * evidence a reader came here to read. On the selected codebook every member is
 * {oracle_id, assertions[]} and every assertion carries class, source_ref,
 * quote, corpus_ref, evidence_status and usually locality. None of that shape
 * is assumed by the code below. */
function valueNode(value) {
  if (Array.isArray(value)) {
    if (value.every((v) => typeof v !== "object" || v === null)) {
      return el("span", null, "[" + value.join(", ") + "]");
    }
    const stack = el("div");
    value.forEach((entry, i) => stack.append(keyValues(entry, "#" + (i + 1))));
    return stack;
  }
  if (typeof value === "object" && value !== null) return keyValues(value, null);
  return el("span", null, String(value));
}

function keyValues(record, label) {
  const box = el("div", "side");
  if (label) box.append(el("div", "side-label", label));
  const dl = el("dl", "kv");
  for (const key of Object.keys(record)) {
    dl.append(el("dt", null, key));
    const dd = el("dd");
    if (key === "quote" && typeof record[key] === "string") {
      dd.append(el("div", "quote", record[key]));
    } else {
      dd.append(valueNode(record[key]));
    }
    dl.append(dd);
  }
  box.append(dl);
  return box;
}

function memberObject(member, label) {
  const box = el("div", "side");
  box.append(el("div", "side-label", label));
  box.append(valueNode(member));
  return box;
}

function membershipPanel(cardIndex) {
  const rows = state.membershipsByCard.get(cardIndex);
  const panel = el("section", "panel");
  if (!rows || !rows.length) {
    panel.append(el("h3", null, "Active memberships"));
    panel.append(el("p", "muted",
      "None. The selected codebook records no membership for this card on any " +
      "axis whose status is active."));
    return panel;
  }
  panel.append(el("h3", null, "Active memberships — " + rows.length +
    " axis membership" + (rows.length === 1 ? "" : "s") +
    ", copied from the selected codebook"));
  for (const [axisIndex, member] of rows) {
    const axis = axisAt(axisIndex);
    const row = el("div", "axis-row");
    row.append(el("div", "axis-id", axis.axis_id));
    row.append(el("p", "axis-meta",
      (axis.definition || "(no definition recorded)") +
      "  ·  " + axis.active_member_count.toLocaleString() + " active members" +
      (axis.scope ? "  ·  scope: " + axis.scope : "") +
      (axis.source ? "  ·  source: " + axis.source : "")));
    row.append(memberObject(member, "this card's stored assertion"));
    panel.append(row);
  }
  return panel;
}

function absencePanel() {
  const semantics = state.meta.disclosure.evidence_state_semantics;
  const box = el("section", "absence");
  box.append(el("h3", null, state.cards.evidence_state_codes["0"]));
  box.append(el("p", null, semantics.UNASSIGNED_NO_ACTIVE_EVIDENCE + "."));
  box.append(el("p", "loud",
    "This is an ABSENCE OF EVIDENCE. It is NOT a finding that this card has no " +
    "similar cards. No neighbour has been fabricated to fill it, and nothing " +
    "here has judged this card."));
  box.append(el("p", null, "0 evidence-discoverable candidates, because the " +
    "candidate rule needs a shared active axis and this card is on none."));
  const list = el("ul");
  for (const line of semantics.UNASSIGNED_IS_NOT) list.append(el("li", null, line));
  box.append(el("p", "muted", "In particular, it is:"), list);
  box.append(el("p", "muted", semantics.absent_membership_is + "."));
  return box;
}

/* ---- candidates, as tie blocks ----------------------------------------- */

async function candidatePanel(cardIndex, anchor) {
  const panel = el("section", "panel");
  const blocks = anchor.blocks;
  const nonSingleton = blocks.filter((b) => b.size > 1).length;
  panel.append(el("h3", null, "Evidence connections — " +
    anchor.candidate_count.toLocaleString() + " candidate" +
    (anchor.candidate_count === 1 ? "" : "s") + " in " +
    blocks.length.toLocaleString() + " tie block" + (blocks.length === 1 ? "" : "s")));
  panel.append(el("p", "muted",
    "A candidate is a card that shares at least one ACTIVE axis with this one in " +
    "the selected codebook. That is the entire rule: no text similarity, no " +
    "embedding, no model, no score. A card sharing nothing is simply not listed — " +
    "which says nothing about it."));
  if (nonSingleton) {
    panel.append(el("p", "muted",
      nonSingleton.toLocaleString() + " of these " + blocks.length.toLocaleString() +
      " blocks hold more than one card. Inside such a block the accepted ordering " +
      "found NO difference at all, so the sequence you see there is arbitrary and " +
      "no member is ranked above another."));
  }
  const host = el("div");
  let drawn = 0;
  const drawMore = () => {
    const stop = Math.min(blocks.length, drawn + 25);
    for (; drawn < stop; drawn += 1) host.append(tieBlock(cardIndex, blocks[drawn], drawn));
    more.textContent = "show more tie blocks (" +
      (blocks.length - drawn).toLocaleString() + " left)";
    more.hidden = drawn >= blocks.length;
  };
  const more = el("button", "ghost");
  more.type = "button";
  more.addEventListener("click", drawMore);
  panel.append(host);
  const wrap = el("p", "more");
  wrap.append(more);
  panel.append(wrap);
  drawMore();
  return panel;
}

function tieBlock(anchorIndex, block, ordinal) {
  const box = el("div", block.size > 1 ? "tie-block" : "tie-block singleton");
  const head = el("div", "tie-head");
  const last = block.first_rank + block.size - 1;
  head.append(el("div", "tie-title",
    "tie block " + (ordinal + 1) + " · " + block.size + " card" +
    (block.size === 1 ? "" : "s") + " · positions " + block.first_rank +
    (block.size === 1 ? "" : "–" + last) +
    " · shared axes " + block.shared_axis_count +
    " · cardinalities [" + block.shared_axis_cardinalities.join(", ") + "]"));
  head.append(el("p", "tie-arbitrary", block.size > 1
    ? "EVIDENCE-EQUIVALENT GROUP — the order of the " + block.size +
      " cards below is arbitrary and carries no meaning"
    : "one card, separated from every other by the recorded evidence"));
  box.append(head);

  const list = el("ul", "tie-members");
  for (const [candidateIndex, sharedAxisIndices] of block.members) {
    list.append(candidateRow(anchorIndex, candidateIndex, sharedAxisIndices));
  }
  box.append(list);
  return box;
}

function candidateRow(anchorIndex, candidateIndex, sharedAxisIndices) {
  const item = el("li");
  const details = el("details");
  const summary = el("summary");
  summary.append(el("span", "cand-name", nameOf(candidateIndex)));
  summary.append(el("span", "cand-id", idOf(candidateIndex)));
  summary.append(el("span", "cand-axes",
    sharedAxisIndices.map((a) => state.axes.order[a]).join("  ")));
  if (!isEligible(candidateIndex)) summary.append(el("span", "badge warn", "GATE#0 INELIGIBLE"));
  details.append(summary);

  const body = el("div", "evidence-pair");
  for (const axisIndex of sharedAxisIndices) {
    const axis = axisAt(axisIndex);
    body.append(el("h4", null, "why: " + axis.axis_id));
    body.append(el("p", "axis-meta",
      (axis.definition || "(no definition recorded)") + "  ·  " +
      axis.active_member_count.toLocaleString() + " active members" +
      (axis.scope ? "  ·  scope: " + axis.scope : "") +
      (axis.source ? "  ·  source: " + axis.source : "")));
    body.append(memberObject(memberOn(anchorIndex, axisIndex),
      nameOf(anchorIndex) + " — stored assertion"));
    body.append(memberObject(memberOn(candidateIndex, axisIndex),
      nameOf(candidateIndex) + " — stored assertion"));
  }
  body.append(el("p", "muted",
    "Both assertions above were copied from the selected codebook. They are the " +
    "whole of the recorded reason these two cards are connected here; nothing " +
    "else was consulted and no similarity was computed."));
  details.append(body);
  item.append(details);
  return item;
}

function memberOn(cardIndex, axisIndex) {
  const rows = state.membershipsByCard.get(cardIndex) || [];
  for (const [candidateAxis, member] of rows) {
    if (candidateAxis === axisIndex) return member;
  }
  /* Unreachable against a conserved bundle: a candidate is only listed because
   * the accepted retrieval found a SHARED membership, so both sides must carry
   * one. Reported rather than silently blanked, because a blank would look like
   * a card whose codebook entry has no evidence, which is a different fact. */
  return { ERROR: "this bundle's evidence layer records no membership for this " +
                  "card on this axis, though the precomputed retrieval says it " +
                  "shares it. that is a defect in the bundle, not a fact about " +
                  "the card." };
}

boot();
