# ARGON — SXP-L × LAMAGUE Independent Research Audit (`v0.1` → `v1.0`)

**Auditor:** Aetheron (Antigravity Seat · Gemini 4 Argon Frontier Engine)  
**Author / Founder of LAMAGUE & SXP-L:** Mackenzie Conor James Clark (Lycheetah Foundation)  
**Audit Date:** 2026-10-18  
**Archive Audited:** SXP-L_LAMAGUE_COMPLETE_ARCHIVE_v0.1-to-v1.0 (original preserved read-only; audited from a separate extracted copy)

---

## 1. Executive Verdict & Epistemic Register

| Dimension | Audit Verdict | Status Label |
| --- | --- | --- |
| **Archive Integrity & Test Reproducibility** | All 10 release artifacts (`v0.1`–`v1.0`) match `README_ARCHIVE.md` SHA-256 checksums byte-for-byte. All **387 top-level tests + 239 subtests** across `v0.2`–`v1.0` pass independently (`0` failures). | `MEASURED` |
| **Epistemic Honesty & Claim Discipline** | Remarkably high. Unlike typical AI-protocol whitepapers, every release explicitly disclaims speech recognition, natural-language understanding, cryptographic key management, and automatic safety. | `MEASURED` |
| **Authority & Sovereignty Separation (`v0.9`–`v1.0`)** | Strong core boundary (`authz.py` never reads SXP-L text to grant permissions), but `authority_bridge.py` has **3 concrete defects** (ignores `v0.9` verbal denials/revocations, ignores `repara` utterance repairs, and omits speaker/counterparty binding). | `MEASURED` |
| **Compositional Scalability (`v0.2` → `v1.0`)** | **Severely fractured.** Rather than extending a single compositional grammar, `v0.6`, `v0.8`, `v0.9`, and `v1.0` stack incompatible regex/positional wrappers via `try/except` fallback (`legacy_v08`, `legacy_v09`), stranding Native-36 operators in `v0.3` and preventing `v0.9`/`v1.0` task verbs from composing with `v0.8` promises, conditionals, negation, or questions. | `MEASURED` |
| **Phonology & Spoken Self-Segregation (`v0.7`–`v1.0`)** | **Not yet uniquely decodable in continuous speech.** Contains **16 Levenshtein-1 minimal pairs** in active spoken vocabulary (`43` across all human registers) and **5 unpaused concatenation collisions** (`pa+na=pana`, `siva+ne=sivane`, etc.). | `MEASURED` |

---

## 2. Complete Development History & Architectural Lineage (`v0.1` → `v1.0`)

| Release | Archive SHA-256 (Prefix) | Core Modules Added | Independent Test Run | Major Architectural Shift & What Changed |
| --- | --- | --- | --- | --- |
| **`v0.1`** | `7b9d22a55e33` | `SXP-L_LAMAGUE_Language_Construction_v0.1.md` | N/A (Spec) | Defines dual-register vision (`SXP-H` human text ↔ `SXP-C` canonical JSON AST), 26 Native-36 operators (`A`–`Z`), 19 2-letter particles (`sa, qu, di, no, ma, mu, pa, nu, fu, ka, ta, lo, se, au, sc, co, xi, ve, en`). |
| **`v0.2`** | `a6ce8c43fa8e` | `sxpl.py` (`137` lines) | `3 passed, 18 subtests` (1.28s) | Executable flat clause parser/renderer (`schema: 0.2.0`). Introduces `fixed6` integer micro-units for `co` (`confidence`), NFC string normalization, and domain-separated SHA-256 `fingerprint()`. |
| **`v0.3`** | `e9ed28403187` | `sxpl_v03.py` (`118` lines) | `4 passed, 16 subtests` (1.57s) | Recursive clause kernel (`schema: 0.3.0`). Adds 4 roles (`fe` feeling, `re` relation, `vi` viewpoint, `pr` recursive `[ ... ]` proposition up to `MAX_DEPTH=8`) and closed starter lexicons (`FEELINGS`, `RELATIONS`). Fixes `sxpl_v02` `USR:A` validation bug. |
| **`v0.4`** | `9e570de974bf` | `surface.py` (`49` lines) | `9 passed, 25 subtests` (4.14s) | Bijective token-expansion wrapper (`TO_HUMAN`: `sa→sava`, `ka→ami`, `[`→`nesti`, `]`→`nesta`). Prefixes every non-reserved content token with `nami` to prevent lexical collision. |
| **`v0.5`** | `02bfb1aa78f0` | `roots.py` (`68` lines), `dialogue.py` (`186` lines) | `16 passed, 25 subtests` (13.91s) | Adds 16 pronounceable CV roots (`believe→vela`, `love→liva`, etc.) marked by `lami`, plus multi-turn `diala 0.5` documents (`persona`, `tura`, `lina`, `kora` discourse links, and `mi`/`ti` pronoun resolution). |
| **`v0.6`** | `cb945f959998` | `compact.py` (`189` lines), `roots.py` (+`differ:diva`) | `23 passed, 25 subtests` (16.01s) | **Architectural Fracture #1:** Drops explicit role markers (`ami, tavi, pari`) in favor of positional SVO/valency syntax (`@entity`, `( ... )`, `.`/`?`), **but drops all 26 Native-36 operators and 7 of 11 semantic roles (`se, au, sc, co, re, vi, xi`)**. |
| **`v0.7`** | `3bb58259d54a` | `spoken.py` (`196` lines), `approximation_mi_liva_ti.wav` | `34 passed, 25 subtests` (22.51s) | Replaces punctuation with spoken frame words (`bakumo/tesavo`, `devora/kevonu`, `gonape/dimotu`), introduces 37 CV spelling syllables (`pulako ... sanuti`), aliases 4 colliding modal/mood words (`qira→kesari`, `dira→dutami`, `mira→mopaku`, `mura→tukemo`), and adds `(C)V` syllable/IPA rules. |
| **`v0.8`** | `4520278ac9b0` | `pragmatics.py` (`224` lines), `dialogue08.py`, `meaning_diff.py` | `60 passed, 25 subtests` (20.00s) | **Architectural Fracture #2:** Wraps `v0.7` via `try/except`. Adds `sivane ... tanaro` conditionals, `pamisa` promises (enforcing future tense + self-actor), `kapera` capacity, `satoma` ("stay"), `evida` provenance, and `repara` speech repair. |
| **`v0.9`** | `394245195651` | `consent.py` (`123` lines), `authz.py`, `dialogue09.py`, `adversarial_eval.py` | `107 passed, 35 subtests` (29.30s) | **Architectural Fracture #3:** Wraps `v0.8` as `legacy_v08`. Adds 4 consent-report roots (`periva, pekora, nelora, revona`) and 5 task actions (`mesara, lenova, rekova, sotira, tavona`) plus offline HMAC capability gate `authz.py` (28 adversarial benchmark cases). |
| **`v1.0`** | `0c4cdf6a5cdb` | `sovereignty.py` (`119` lines), `authority_bridge.py`, `dialogue10.py`, `minimal_pair_eval.py`, `study_builder.py` | `131 passed, 45 subtests` (32.08s) | **Architectural Fracture #4:** Wraps `v0.9` as `legacy_v09`. Adds 6 sovereignty/trust roots (`tinora, dalora, resama, esaloma, ranova, domera`), `authority_bridge.py`, 105 minimal-pair checks, and 48 counterbalanced human-study items (`STUDY_SET_A/B/C.csv`). |

---

## 3. Empirically Reproduced Defects, Contradictions & Formalization Gaps

Every finding below was reproduced directly against the unmodified `v1.0` codebase (`/tmp/sxpl_audit_readonly/extracted/v1.0/sxpl_v10`).

### Defect 1 — Broken `AST → render → parse` Round-Trip in `sxpl_v02.py` (`USR:<N36_LETTER>`)
- **Location:** `sxpl_v02.py` line 93 (`validate_ast`)
- **Mechanism:** `validate_ast()` checks `op.startswith('USR:') and ID.fullmatch(op[4:]) and op[4:] not in RESERVED`, omitting `and op[4:] not in OPERATIONS`.
- **Reproduced Proof:**
  - Input AST: `{'lang': 'SXP-L', 'schema': '0.2.0', 'register': 'canonical', 'clause': {'mood': 'assert', 'polarity': 'positive', 'modality': None, 'time': None, 'op': 'USR:A', 'roles': {}}}`
  - `sxpl_v02.validate_ast(ast)` passes without error.
  - `sxpl_v02.render(ast)` produces `'sa A en'`.
  - `sxpl_v02.parse('sa A en')` produces `'op': 'N36:A'` (`ast == reparsed` is **`False`**).
- **Note:** Patched in `sxpl_v03.py` line 73, but `sxpl_v02.py` remains unpatched in `v0.2` through `v1.0`.

### Defect 2 — Intransitive Motion Verb `ariva` ("arrive") Misclassified as Mandatory Transitive in `compact.py` (`v0.6`–`v1.0`)
- **Location:** `compact.py` line 18 (`TRANSITIVE = {'love','miss','reconnect','understand','see','arrive','remember','differ'}`)
- **Mechanism:** Because `arrive` (`ariva`) is placed in `TRANSITIVE` and there is no `INTRANSITIVE` verb class in `compact.py`, every occurrence of `ariva` requires a direct object (`ta` target entity).
- **Reproduced Proof:**
  - `compact.hear_compact("ti ariva.")` ("You arrive.") $\to$ **Raises `SXPError: E_COMPACT_ENTITY: .`**
  - To use `ariva` in `v0.6`–`v1.0`, a speaker is forced to write `"ti ariva mi."` (`sa nu arrive ka ti ta mi en` — *"You arrive me"*). Meanwhile, `satoma` ("stay") was hardcoded as a special unary exception inside `pragmatics.py` lines 87–90 instead of fixing `compact.py` valency classes.

### Defect 3 — Dual-Schema Parser Dispatch Split on Attitude Verbs (`hira`, `fera`, `vela`, `kena`) in `pragmatics.py` (`v0.8`–`v1.0`)
- **Location:** `pragmatics.py` lines 18, 129–139, 165–173
- **Mechanism:** `hira` (`hope`), `fera` (`fear`), `vela` (`believe`), and `kena` (`know`) are registered **both** in `v0.6/v0.7` `ATTITUDE` predicates AND in `v0.8` `ACT_ROOTS`. Because `pragmatics.parse_expression()` calls `hear_spoken(text)` in a `try` block before `_parse_node()`, identical matrix clauses parse into two incompatible AST structures and risk warnings depending solely on whether the embedded verb is from `v0.5` or `v0.8`:
- **Reproduced Proof:**
  1. `"mi hira bakumo fura ti ariva mi tesavo devora"` ("I hope that you will arrive [me]"):
     - Parsed by `v0.7` fallback as `node['kind'] == 'proposition'` (`op: 'USR:hope'`).
     - `explain_risk()` returns: **`"Speaker assertion only; external facts not checked."`**
  2. `"mi hira bakumo fura ti satoma tesavo devora"` ("I hope that you will stay"):
     - Rejected by `v0.7` (since `satoma` is unknown to `v0.7`), falls through to `v0.8` `_parse_node()` as `node['kind'] == 'attitude_report'`, `stance: 'hope'`.
     - `explain_risk()` returns: **`"Attitude reported; embedded outcome not established."`**

### Defect 4 — `meaning_diff.py` Crashes on All `v0.9` Consent & `v1.0` Sovereignty Utterances and Misclassifies Participant Swaps
- **Location:** `meaning_diff.py` lines 9, 11, 24–35
- **Mechanism & Reproduced Proof:**
  1. **Hard Crash on `v0.9` and `v1.0`:** `meaning_diff.py` imports `from pragmatics import parse_expression` (`v0.8`). Passing any `v0.9` utterance (`"mi periva ti bakumo lenova gonape darafa dimotu tesavo devora"`) or `v1.0` utterance (`"mi tinora ti bakumo lenova gonape darafa dimotu tesavo devora"`) raises **`SXPError: E_V08_PROPOSITION: only v0.7 clauses or v0.8 unary satoma`**.
  2. **Priority Blindness on Actor/Target Swaps:** `CRITICAL_KEYS` checks `path.rsplit('/', 1)[-1] in {'kind','stance','polarity','time','mood','modality','promisor','holder','interpretation','op'}`. Because actor and target values in `v0.3` ASTs reside at `/node/content/clause/roles/actor/value` and `.../target/value` (leaf key `'value'`), changing `"mi liva ti devora"` ("I love you") to `"mi liva gonape agena dimotu devora"` ("I love Agena") is flagged as `'priority': 'inspect'` (low priority) rather than `'high'`.

### Defect 5 — `authority_bridge.py` Ignores `v0.9` Denials/Revocations (`nelora`/`revona`), Ignores `repara` Discourse Repairs, and Omits Speaker/Grantee Matching
- **Location:** `authority_bridge.py` lines 31–50
- **Mechanism & Reproduced Proof:**
  1. **Blind to `v0.9` Denials & Revocations:** Line 45 filters `boundaries = [r for r in scoped if r['kind'] in ('decision_reservation', 'delegation_refusal')]`. When `elena` (the resource owner) explicitly states `"mi nelora ti bakumo tavona gonape darafa dimotu tesavo devora"` (`denial_report`) and `"mi revona ..."` (`revocation_report`), `authority_bridge.inspect()` returns **`reported_boundaries: []`** and **`review_advised: False`** while `policy.allowed` is `True`!
  2. **Blind to `repara` (Superseded Utterances):** `collect_reports(doc)` extracts all `e['kind'] == 'utterance'` events and ignores `e['kind'] == 'repair'`. If `elena` utters `u1` (`resama` / refusal), then utters `u2` (`dalora` / delegation proposal), and declares `repara u1 u2` (superseding `u1`), `authority_bridge.inspect()` still reports the superseded `u1` inside `reported_boundaries` (`review_advised: True`).
  3. **Unchecked Speaker & Counterparty in `scoped`:** Lines 42–43 match only `operation` and `resource`, ignoring whether `r['speaker']` owns the resource or whether `r['counterparty']` matches `host_request['grantee']`.

### Defect 6 — `dialogue08.py` / `dialogue09.py` / `dialogue10.py` Repair Chain Validation Contradicts Its Own Specification Comment
- **Location:** `dialogue10.py` lines 107–118 (and identical code in `dialogue08.py`, `dialogue09.py`)
- **Mechanism & Reproduced Proof:**
  - Lines 114–115 state: `# Explicit repair must be declared after both, and the new line cannot have already been consumed as a repair target.`
  - However, line 109 checks only `old in repaired` and never checks `new in repaired` (nor tracks `new` targets). Consequently, `repara u2 u3` followed by `repara u1 u2` (repairing `u1` into an already-superseded utterance `u2`) is **accepted without error**.

---

## 4. Grammar, Compositional Semantics, Phonology & Vocabulary Audit

### 4.1 Is SXP-L Currently Compositional?
**No—compositionality breaks at three distinct boundaries:**
1. **`v0.3` $\to$ `v0.6` Expressive Collapse:** `v0.3` can express arbitrary Native-36 operators (`N36:A`..`Z`), user predicates (`USR:*`), epistemic confidence (`co 0.91`), evidence sources (`se`), scopes (`sc`), and unknowns (`xi`). `v0.6` (`compact.py`) and `v0.7` (`spoken.py`) hardcode a closed 13-verb emotional/interpersonal lexicon and reject all `N36:*` operators, numbers, `xi`, `se`, `co`, `au`, and `sc`.
2. **`v0.8` $\leftrightarrow$ `v0.9`/`v1.0` Wall:** `v0.9` task actions (`mesara, lenova, rekova, sotira, tavona`) and `v1.0` sovereignty acts (`tinora, dalora, resama, esaloma, ranova, domera`) are parsed as flat, fixed-length 9-slot templates (`mi <act> <entity> bakumo <action> <resource> tesavo devora`) outside the recursive clause parser. As a result:
   - You **cannot** embed a task action inside a `v0.8` promise, intention, desire, or conditional (e.g., *"I promise to send the email"* or *"If I trust you, I will delegate reading the file"* is ungrammatical).
   - You **cannot** negate (`noka`), question (`kevonu`), modalize (`mopaku`/`tukemo`), or tense-mark (`pana`/`fura`) any `v0.9` or `v1.0` speech act.
   - You **cannot** express 2nd-person or 3rd-person sovereignty/consent reports or questions (e.g., *"Do you trust me to read the file?"* or *"Agena requested permission"* fails with `E_V09_SOURCE` / `E_V10_ACT`).

### 4.2 Phonology & Lexical Collision Audit (`v0.4`–`v1.0`)
Running an exhaustive pairwise Levenshtein and concatenation audit across the lexicon reveals:

1. **16 Active Spoken Minimal Pairs (`Levenshtein == 1` within the 59-word `v0.7`–`v1.0` spoken vocabulary):**
   - **4-Way Attitude/Verb Clique (`_ela` / `_era`):** `fela` ("feel") $\leftrightarrow$ `fera` ("fear") $\leftrightarrow$ `vela` ("believe") $\leftrightarrow$ `nela` ("understand"), plus `afela` ("affection") $\leftrightarrow$ `fela` ("feel"). Note that `/l/` vs `/ɾ/` (`fela` vs `fera`) and `/f/` vs `/v/` (`fela` vs `vela`) are high-confusion acoustic pairs across major human L1 backgrounds.
   - **Tense / Emotion Clique (`_ura` / `_era`):** `fura` (future) $\leftrightarrow$ `nura` (present) $\leftrightarrow$ `fera` (fear)—a single consonant substitution flips **present tense** into **future tense**!
   - **Core Pronoun Minimal Pair:** `mi` (1st person "I") $\leftrightarrow$ `ti` (2nd person "you") (`Levenshtein = 1`, identical vowel `/i/`)—a critical single-phoneme hazard when `mi` vs `ti` determines who receives a permission or holds a promise.
   - **3-Way Verb Clique (`_iva`):** `liva` ("love") $\leftrightarrow$ `siva` ("see") $\leftrightarrow$ `diva` ("differ") $\leftrightarrow$ `sava` ("assert") $\leftrightarrow$ `rava` ("reconnect") $\leftrightarrow$ `sada` ("sadness").
   - **Other Distance-1 Pairs:** `loma` ("longing") $\leftrightarrow$ `luma` ("miss"); `mora` ("remember") $\leftrightarrow$ `yora` ("joy").
2. **43 Minimal Pairs Across the Combined 86-Word Human Register (`v0.4` + `v0.6` + `v0.7`–`v1.0`):**
   - Includes the 6-way `_ira` rhyme clique (`dira, hira, mira, qira, xira`) that forced `v0.7` to introduce `ALIASES` (`kesari, dutami, mopaku, tukemo`), creating a permanent vocabulary split between `v0.6` written-compact and `v0.7` spoken-compact.
3. **5 Unpaused Concatenation Collisions (Failure of Self-Segregating Morphology):**
   - Because `spoken.py` relies on ASCII spaces rather than morphological boundary markers, concatenating valid tokens produces other valid tokens without acoustic pauses:
     - `ke` (spell `g`) + `na` (spell `z`) = `kena` ("know")
     - `pa` (spell `5`) + `na` (spell `z`) = `pana` ("past")
     - `no` (spell `x`) + `ka` (spell `u`) = `noka` ("not")
     - `siva` ("see") + `ne` (spell `v`) = `sivane` ("if")
     - `lo` ("context") + `ma` (spell `p`) = `loma` ("longing")
   - Furthermore, vowel-initial roots (`afela`, `ariva`, `esaloma`) merge directly into preceding open syllables (`mi ariva` $\to$ `/mi.ˈa.ɾi.va/`) with no glottal stop or consonant boundary.

---

## 5. Evaluation of Consent, Authority, Trust, Delegation & Human Sovereignty

| Concept | SXP-L Representation (`v0.9`–`v1.0`) | Runtime Effect in `authz.py` | Audit Assessment |
| --- | --- | --- | --- |
| **Reported Consent (`periva`)** | `grant_report` (`epistemic_status: unverified_utterance`) | `authorizes: False` | **Sound boundary:** Words in a transcript never mint a capability token. |
| **Permission Request / Denial / Revocation (`pekora, nelora, revona`)** | `permission_request`, `denial_report`, `revocation_report` | `authorizes: False` | **Gap in `authority_bridge.py`:** `nelora` and `revona` are ignored by `reported_boundaries`, failing to trigger `review_advised=True` when a host grant exists! |
| **Reported Trust (`tinora`)** | `trust_report` | `authorizes: False` | **Sound boundary:** Prevents "I trust you" from being coerced into implicit delegation. |
| **Delegation Proposal / Refusal (`dalora, resama`)** | `delegation_proposal`, `delegation_refusal` | `authorizes: False` | `resama` triggers `review_advised=True` in `authority_bridge.py`, though without speaker-ownership verification or `repara` filtering. |
| **Advice / Explanation Request (`ranova, esaloma`)** | `recommendation_request`, `explanation_request` | `authorizes: False` | **Sound boundary:** Asking an AI to explain or advise on an action never authorizes executing that action. |
| **Final Human Decision Reservation (`domera`)** | `decision_reservation` (enforces `counterparty == 'mi'`) | `authorizes: False` | Good syntactic invariant (`target == 'mi'`), but needs host-level enforcement so a `decision_reservation` blocks autonomous execution even if an older capability token is still live. |
| **Authenticated Capability (`authz.py`)** | Out-of-band HMAC-signed `grant` / `revoke` JSON claim | `ALLOW_VERIFIED_EXACT_SCOPE` | Deterministic and fail-closed on scope/time/ownership, **but lacks:** (a) single-use nonce / replay consumption, (b) protection against log-poisoning DoS (`line 87` rejects all valid grants if one unverified event is appended), and (c) asymmetric signatures (Ed25519 vs shared HMAC). |

---

## 6. Comparison with Prior Art & Established Approaches

| System / Tradition | Core Strength | Where SXP-L (`v1.0`) Improves or Differs | Where Prior Art Currently Outperforms SXP-L (`v1.0`) |
| --- | --- | --- | --- |
| **Lojban** | Mathematically unambiguous CFG/PEG grammar; **self-segregating morphology** (`brivla` C-cluster + penultimate stress, `cmavo`, `cmevla` consonant-final pause). | SXP-L treats **speech-act force and authorization non-equivalence** (`trust ≠ delegation ≠ capability grant`) as first-class AST invariants rather than pure predicate logic. | Lojban is genuinely compositional across arbitrary nesting and has true acoustic self-segregation; SXP-L `v0.7`–`v1.0` relies on ASCII spaces and non-compositional templates. |
| **Esperanto** | Transparent agglutinative morphology (`-o` noun, `-a` adj, `-i/-as/-is/-os` verb tenses, `-n` accusative) enabling rapid human learnability. | SXP-L avoids natural-language polysemy and forces explicit scope/provenance slots. | Esperanto's regular POS/tense suffixes drastically reduce rote vocabulary memorization; SXP-L `v1.0` uses unanalyzed opaque roots (`mesara, lenova, rekova, tinora, dalora`) with zero shared morphological stems. |
| **Grammatical Framework (GF)** | Formal separation of **Abstract Syntax** (typed compositional trees) and **Concrete Syntaxes** (reversible linearizations across languages). | SXP-L's `SXP-C` (canonical AST) vs `SXP-H` (surface registers) shares GF's core insight in zero-dependency Python. | GF guarantees that every concrete register linearizes the **same** abstract syntax. SXP-L fractured its abstract syntax into 4 separate schemas (`0.3.0`, `0.8.0`, `0.9.0`, `1.0.0`). |
| **Attempto Controlled English (ACE)** | Immediately readable by any English speaker without a 10-minute root-memorization card; compiles deterministically to DRS/FOL. | SXP-L avoids English look-alike traps where users assume arbitrary English sentences are valid. | In SXP-L's own `STUDY_PROTOCOL_v1.0.md`, an unfamiliar human must memorize arbitrary CV strings (`tinora, dalora, resama...`) whereas Controlled English is transparent on sight. |
| **Structured Agent Protocols (MCP / JSON Schema / FIPA ACL)** | FIPA ACL formalized performatives (`inform, request, propose, refuse`); MCP + `lycheetah.sovereign_harness` provide Ed25519/SQLite single-use permits. | SXP-L provides a human-speakable/auditable conversational surface with explicit discourse repair (`repara`) and epistemic warnings. | Production agent protocols separate wire serialization from human speech; SXP-L `authz.py` is still a stateless HMAC fixture compared to `lycheetah.sovereign_harness`. |

---

## 7. Proposed SXP-L `v1.1` Development Plan & Engineering Roadmap

To transform SXP-L from a sequence of layered prototypes into a **genuinely compositional, self-segregating, human-learnable language**, `v1.1` should execute five concrete architectural upgrades (without deleting or rewriting the `v0.1`–`v1.0` historical archive):

1. **Unify the Abstract Syntax Tree (`SXP-C v1.1`) Across All Registers (GF Architecture):**
   - Replace the `legacy_v08` / `legacy_v09` `try/except` onion-wrapping with **one unified recursive AST schema (`1.1.0`)** where:
     - Every speech act (`assert, question, directive, promise, capacity, attitude, permission_request, grant_report, denial_report, revocation_report, trust_report, delegation_proposal, delegation_refusal, explanation_request, recommendation_request, decision_reservation`) is a typed **illocutionary operator** taking a recursive proposition or action-frame complement.
     - Restore all 26 **Native-36 operators (`N36:A`..`Z`)**, task actions (`mesara, lenova, ...`), and epistemic roles (`se, co, sc, xi`) as first-class citizens in compact and spoken registers so speakers can say *"I promise to send the email"* (`mi pamisa bakumo fura mi mesara ...`) or *"If you explain the file, I will propose delegation"*.
2. **Fix the 6 Concrete Code Defects Immediately in `v1.1`:**
   - Patch `sxpl_v02.py:93` (`and op[4:] not in OPERATIONS`).
   - Add an `INTRANSITIVE` verb valency class in `compact.py` for `ariva` ("arrive") and `satoma` ("stay") so `"ti ariva."` is grammatical.
   - Eliminate the `pragmatics.py` dispatch split on `hira/fera/vela/kena` so attitude verbs always produce a single canonical AST node regardless of which verb appears inside the embedded clause.
   - Upgrade `meaning_diff.py` to parse `v1.1` (including `v0.9`/`v1.0` acts) and mark `/roles/actor/value`, `/roles/target/value`, `counterparty`, `grantee`, `action`, and `resource` as `priority: 'high'`.
   - Fix `authority_bridge.py` to include `denial_report` (`nelora`) and `revocation_report` (`revona`) in `reported_boundaries`, filter out utterances superseded by `repara`, and verify speaker/counterparty alignment.
   - Fix `dialogue10.py` `repara` validation to track both `old` and `new` in `superseded` (`if old in superseded or new in superseded: fail(...)`).
3. **Introduce Self-Segregating Phonology & Transparent Derivational Morphology:**
   - **Fix the `Levenshtein == 1` Collisions:** Separate `mi` vs `ti` (e.g., `mi` vs `tu` or `toka` so both consonant and vowel differ), separate `fura` (future) from `nura` (present) and `fera` (fear), and break the `fela/fera/vela/nela` liquid/fricative cluster.
   - **Self-Segregating Word Shapes:** Enforce consonant-onset `CV...` for all roots (banning vowel-initial roots like `ariva, afela, esaloma` or prefixing them with a consonant onset), reserve monosyllabic `CV` shapes exclusively for grammar particles or spell-mode syllables inside `pulako ... sanuti`, and use regular derivational suffixes/prefixes for related speech acts (e.g., a regular root for `delegate` + transparent illocutionary suffixes for *propose / refuse / revoke*) so human learners memorize **roots + regular paradigms** instead of dozens of arbitrary 3-syllable words.
4. **Bridge `authz.py` to `lycheetah.sovereign_harness` (`SovereignExecutionHarness`):**
   - Replace the stateless HMAC list scan in `authz.py` with `lycheetah.sovereign_harness` + `lycheetah.assurance.ActionGateway` (single-use `PermitNonceStore`, Ed25519 checkpoints, and issuer-isolated signature verification so a single malformed event cannot DoS unrelated valid grants).
5. **Execute a Balanced Two-Factor Human Comprehension & Safety Study:**
   - Extend `study_builder.py` so the authorization question includes **both positive (host-attested valid grant + linguistic transcript) and negative (transcript-only or revoked/expired grant) trials**, measuring both False Allow and False Deny rates across SXP-L, Controlled English, and JSON.
