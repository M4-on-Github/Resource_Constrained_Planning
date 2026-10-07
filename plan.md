# Resource-Constrained Planning (RCP)

**v0.9 — 2026-10-07. Design only. No code until the go-ahead is given.**

A VLM is given a maritime casualty, a fixed loose instruction ("write a salvage
plan"), domain knowledge, and **a specific, named, grounded resource ledger** —
*tug `TUG-002`, 45 t bollard pull, Port Mahon, 2.0 h out*. It writes one plan in
prose. A validator replays that plan against the same ledger and reports **what
the planner did**, not whether it earned a passing grade. Then the ledger is
varied — surplus, sufficient, scarce, infeasible — and we observe how behavior
changes.

| | |
|---|---|
| **Model** | Qwen3-VL-8B (`/data/$USER/qwen3vl-8b`), greedy, `temperature: 0.0` |
| **Corpus** | 110 CASTOR images × 4 resource arms = 440 generations, no replicates |
| **Headline variable** | resource sufficiency level — one IV; everything else recorded and demoted |
| **Primary endpoint** | `APPROPRIATE-RESPONSE` — *succeed where success is possible, refuse soundly where it is not* (§4.1) |
| **Reported beside it** | `PLAN-SUCCEEDS` = V5 ∧ V1 ∧ V2a ∧ V3, its `RESOURCE-VALID` component, and the two §5.2 refusal rates |
| **Design** | within-image paired; all four arms run the same 110 images |
| **Status** | design closed. **Two open items, both gate the freeze** (§12.2) |

**Open:** the §9.4 MDE slot, and the §6.1 assertion-file line audit. Q9 (repo
packaging) is undecided but affects packaging only, not design.

The full v0.5 draft — every argument condensed out of this document, preserved
verbatim — is `archive/plan.v05.full.md`.

---

## 1. The study

### The claim this is built to support

> Given good domain information and a specific, grounded asset ledger, a planner
> produces plans that succeed — in the sense the declared world can certify — at
> rate *X*. As available resources fall below what the task requires, that rate and
> the planner's failure profile change in a direction fixed in advance.

"Succeed" is `APPROPRIATE-RESPONSE` (§4.1). Where the ledger can do the job it is
`PLAN-SUCCEEDS` — the plan **attempts the right thing** and **has what it needs to
do it**, resource grounding being the second half of that question rather than a
substitute for it. Where the ledger cannot, it is a sound refusal, because
succeeding is not the right response to an impossible task.

The directional commitments that make it falsifiable are pre-registered in §9.
The user instruction is a **constant**, not a variable — a varying user request
would be a second IV competing with resource sufficiency for the headline.

### Two tracks; only one is authorised

This is a **measurement study**. The deliverable is a characterisation of behavior
under scarcity, not a validity rate pushed as high as it will go. The legitimate
want for a higher rate is a *sequencing* problem, not a contradiction:

| | Track M — measurement | Track E — engineering |
|---|---|---|
| goal | characterise behavior | raise `PLAN-SUCCEEDS` |
| output | the pre-registered §9 result | an improved system |
| endpoint | frozen composition | same endpoint, re-measured |
| interventions | none aimed at the rate | Structural + Informational only (§10.1) |
| **status** | **authorised — this plan** | **deferred** |

> **Track E is not planned and not executed until Track M is complete and frozen.**
> No design, no prompt search, no tuning — not provisionally, not in parallel.

Track E's value is a comparison against an untouched baseline, and that baseline
does not exist yet. Designing it now would also put the dev/test split and the
intervention list into this document, where they would start influencing Track M
before any data exists. Preconditions only, in §12.4.

**One distinction this makes necessary.** Making plans *parse* is **instrument
conditioning** — it makes the measuring device function, it is tuned off-corpus,
and it is a precondition on Track M (§8.2). Making plans *better* is Track E.

### Why this exists — three findings from P9

Direct successor to `Eval_CASTOR/pipelines/plan_adequacy/`. Three results bind
this design:

1. **P9's biggest number was an instrument artifact.** 46 % of plans marked
   unexecutable under `Procedure`; on hand-check, **0 of 9** were the model's
   fault. Cause: the prompt invited a wider action space than the 47-action
   registry could name, so legitimate steps returned `NO_MATCH` and `NO_MATCH` was
   scored as unexecutable — a **coverage defect**, closed here by §2's coverage rule
   and §8.4's gate. (`reports/p9/p9_recap.tex`)
2. **No positive control.** `goal_reached = 0/330`, zero variance — equally
   consistent with "planners are bad" and "the criterion is unpassable."
   (`reports/p9/redesign.tex` §1)
3. **Extraction loss was an unquantified confound.** Per-step tool extraction
   accuracy 0.833, sitting underneath every number in the study.

RCP is built so all three are structurally impossible, not merely watched for.

### The mentor critique, and how it binds

On record in `reports/p9/p9_future_directions.txt`:

> "Using the pipeline to fact-check itself is like using the oracle to solve the
> problem without solving the problem."

Resolution adopted:

- The validator **never runs during generation**. Phase 1 is strictly one-shot.
- It never repairs, filters, vetoes, or re-ranks a plan.
- No model is ever optimised or selected against validator output.
- When a feedback loop is eventually built (E5, §8.1), it returns **world
  observations** ("the line parted"; "`TUG-004` is 6 h out"), never **validator
  verdicts**. This is `salvage_simulation.md` §13 R2.

---

## 2. What the planner sees, and what is withheld

The thing that must not be circular is not "model and validator know the same
facts" — an exam and its answer key reference the same world. It is **the model
being told the grading rule.**

| Artifact | Model sees | Validator uses | Why |
|---|---|---|---|
| Resource ledger (what exists, capacity, ETA) | **yes** | yes | Shared ground truth; the experiment is meaningless otherwise |
| Casualty state (E1/E2) | **yes** | yes | Held constant to isolate planning from perception |
| Stated requirement ("≥120 t bollard pull") | **yes** | yes | A scenario fact, as a naval architect's figure would be. Not a grading rule |
| Domain knowledge / assertions | **yes** | — | Part of the world model; re-derived under §3, not inherited (§6.1) |
| **Precondition graph** | **no** | yes | This is the grading rule |
| **Hard interlocks** | **2 of 4 stated** | yes | The 2 stated feed `V4a` (application); the 2 unstated feed `V4b` (latent knowledge) |
| **Verdict vocabulary / checking procedure** | **no** | yes | This is the grading rule |
| **Validator source, graded examples** | **no** | yes | Never shown, never in a prompt |

Three rules govern what may be written into the prompt. They are enforced by the
§6.1 line audit.

> **Rule 1 — assertions may state facts about resources. They may never state what
> to do when resources fall short.**
> *"If available pull is insufficient, request additional assets"* scripts the
> `ESCALATE` behavior §5 exists to measure, converting the scarcity arms from a
> measurement of planning into a measurement of instruction-following.
>
> **Rule 2 — nothing may indicate which constraint binds in a given scenario.**
> This is what the §7.2 trap depends on. State what ETA means and the trap
> survives; state *"check that your assets arrive before the deadline"* and it is
> destroyed.
>
> Rule 2 restricts **variation**, not content — it forbids saying anything in one
> scenario that is not said in all of them. Its enforceable form is structural,
> not a reading of lines:
>
> **The domain/assertion block is byte-identical across all 110 scenarios and all
> four arms. Only the image and the ledger vary.**
>
> This is why the rule costs the world nothing. Without byte-identity, every
> sentence would have to be audited against every scenario — *is this too helpful
> here?* — which is unauditable, and the safe response would be to say less. With
> it, the domain block is written once, as well as it can be written, and the only
> remaining questions are Rule 1 and Rule 3. **Rule 2 is what makes it safe for
> Rule 3 to be generous.**
>
> **Rule 3 — every quantity an assertion mentions must be a field the world
> carries *and scores in v1*.** A quantity the schema does not type, or types but
> leaves inert, is banned however descriptive the sentence sounds.
>
> *"Confirm pump capacity before committing a team"* tells the planner to do
> something invisible to the validator: doing it gains nothing, skipping it loses
> nothing, and both spend output budget. The tempting repair — *"a pump's
> effective output falls off above its rated head"* — is **equally banned**, and
> is the more dangerous form: `head` is not a field, so neither planner nor
> validator knows the level, and the sentence only *sounds* like mechanism.
>
> **§3.1's on/off table is the list this test runs against**, and it is the only
> copy — schema presence is not enough, since `conditions`, `limits` and `attrs`
> are typed but inert in v1.

| line | tag | why |
|---|---|---|
| "pull from multiple tugs made fast to one casualty is approximately additive" | **mechanism** | operates on `capability.quantity` |
| "ETA is time until on scene and ready" | **mechanism** | `eta_hours` is scored |
| "effective output falls off above rated head" | **banned** | `head` is not a field |
| "confirm pump capacity before committing a team" | **banned** | imperative, unscoreable |

This makes the §6.1 line audit **mechanical rather than a judgment call**, which
matters because it is one of the two gates on the freeze. The decision procedure
is two phases, in order, and the filter stays binary: **first** decide what the
world types and scores, aiming at useful, logical and actionable; **then** filter
every assertion against *that* world. Phase one must finish before the freeze —
§3.5 bars new scored channels from entering the endpoint afterwards. Giving pumps
a `head_m` field is a legitimate phase-one choice; doing it in phase two is not.
The hard ceiling on phase one is **decidability from prose + ledger**, not effort:
V2b stays out at any level of enthusiasm (§3.3).

> **The coverage rule — the prompt may not invite behavior the domain cannot
> name.**
> Rules 1–3 police what goes *into* the prompt against what the validator scores.
> Nothing yet polices the **action space the prompt opens up**, and that is the gap
> P9 fell through: the prompt invited a wider range of reasonable actions than the
> 47-item registry could name, unnameable steps returned `NO_MATCH`, and `NO_MATCH`
> was scored as unexecutable. The 46 % was vocabulary overlap, not planning.
>
> This is Rule 3 applied to verbs instead of quantities, and it has the same kind
> of operational test. §7.1 already admits a requirement only if it **survives the
> gold plans**; the same gate runs on any closed vocabulary — see §8.4.

*(Named the coverage rule, not Rule 4 — §6.3 already refers to P9's extraction
rule 4, and two unrelated "rule 4"s in one document is one too many.)*

**Mechanism yes, binding never.** Each mechanism the planner needs has a normative
twin that is simply one of the checks:

| | mechanism form (needed) | normative twin (banned) |
|---|---|---|
| composition | "pull from multiple tugs made fast to one casualty is approximately additive" | *"ensure total committed pull ≥ requirement"* = **V3** |
| exclusivity | "an asset engaged in a task is committed for its duration" | *"do not assign one asset to overlapping steps"* = **V2b** |
| ETA | "ETA is time until on scene and ready" | *"verify no step uses an asset before its ETA"* = **V2a** |

A naive test ("could a reader derive the check from this?") rejects the left
column too, because mechanism plus the stated requirement yields V3. That test is
wrong: **V3 is not a hidden rule, it is the task.** A planner that does not know it
should meet the stated requirement is failing to guess the objective — a different
and far less interesting finding.

---

## 3. The world model

> **In v1 the world is a resource-allocation constraint system. A state layer is
> admissible — it is scoped out, not ruled out.**

P9 used a state-transition executor — seven passes, a 47-action registry,
preconditions and effects, a `_known`/`_true` split — and it produced the 46 %
artifact. **The reason is worth getting right, because the obvious reading is
wrong.** The executor did not fail because running a world forward is impossible.
It failed because **the prompt invited a wider action space than the registry could
name**: competent steps came back `NO_MATCH` and `NO_MATCH` was scored as
unexecutable. That is a coverage defect — an engineering mismatch between two
artifacts that should have been built against each other — and §2's coverage rule
and §8.4's gate are what close it.

So the case for allocation-only in v1 is **scope and freeze timing, not
impossibility**. A state layer needs world facts the ledger does not carry — hull
integrity, cargo already lightened, tide state — each declared, initialised per
scenario, and updated by action effects. Every one is a new scored channel, and
§3.5 bars new channels from entering the endpoint after the freeze. The cheap half
of what a state machine buys is available without one: **durations** upgrade V2b
from asserted concurrency to a real check, adding a field rather than an
architecture. The ordered-progress half is a named extension (§12.3), gated on
§8.4.

Nothing in the v1 endpoint requires running the world forward.

### 3.1 Entities

```
Scenario
  id, casualty_state, vessel{type, size_category}, t0
  requirement : Requirement
  conditions  : {name -> value}          # sea_state, visibility, ...; empty in v1

Requirement                               # see 7.1
  goal, quantity, unit, asset_class, deadline_h, deadline_driver

Asset
  id, asset_class, capability{quantity, unit}, location, eta_hours
  status                                  # INFORMATIONAL in v1 - scored by nothing
  limits : {condition_name -> threshold}  # empty in v1
  attrs  : {name -> value}                # cost, crew, ...; empty in v1

Ledger = set[Asset]                       # closed, enumerated, per scenario

Plan                                      # the validator's reconstruction
  steps : ordered list[Step]
Step
  index, text
  committed      : set[asset_id]          # string match against a closed list
  is_goal_action : bool                   # V5; one target per casualty type
```

**Deliberately absent:** durations, per-step start times, world-state facts,
action types.

**What is switched on in v1.** The schema types more of the world than v1 scores,
so that extensions are data rather than schema changes (§3.5). That makes “on or
off” a fact worth stating once rather than inferring from scattered mentions —
§2 Rule 3 admits an assertion only if every quantity it names is **on** here, and
a field that exists but is inert does not qualify.

| world fact | field | family | v1 |
|---|---|---|---|
| asset exists | `Asset.id` | F1 | **on** — V1 |
| capability totals | `capability{quantity, unit}` | F2 | **on** — V3 |
| arrival vs deadline | `eta_hours`, `deadline_h` | F3 | **on** — V2a |
| goal attempted | `Step.is_goal_action` | F6 | **on** — V5 |
| interlock ordering | step sequence | F5 | **on** — V4a / V4b, secondary |
| asserted concurrency | plan text | — | **on** — V2b, secondary, LLM-read |
| weather, visibility, ice, current | `conditions` × `limits` | F4 | **off** — maps empty |
| crew, cost, budget | `attrs` | F2 | **off** — map empty |
| asset status | `Asset.status` | — | **off** — rendered, scored by nothing |
| durations, scheduling | — | F8 | **off** — not constructible (§3.3) |

Turning one on is the §3.5 add/remove contract, and after the freeze it enters as a
secondary rate, never into the endpoint.

The planner sees `Scenario`, `Requirement`, `Ledger`, `conditions`. In v1
`conditions`, `limits` and `attrs` are empty, so the rendering collapses to the
§7.2 six-column table; the maps exist so that extensions are data, not schema
changes. The planner never sees `Plan`.

### 3.2 Evaluation pipeline

Three stages, nothing fed back to the planner:

```
prose --> RECONSTRUCT --> Plan --> EVALUATE --> per-check results --> DERIVE
          string match            predicate families (3.4)           flags (5)
          + 2 LLM fields                                             + endpoint (4.1)
```

`RECONSTRUCT` is the only lossy stage, and only for its two LLM fields
(`is_goal_action`, asserted concurrency). `committed` is string matching against a
closed list. `EVALUATE` and `DERIVE` are deterministic: **given the same
reconstruction, two implementations must agree exactly.**

### 3.3 No clock — and the one check the world cannot express

The plan supplies step **order**, never step **times**. Deriving times requires
durations; durations require knowing what each step *does*; that is the open action
vocabulary — the P9 trap. Supplying durations in the ledger does not rescue it:
read the steps sequentially and no two overlap, so the check is vacuous; read them
as possibly parallel and overlap is undefined.

> **Therefore double-booking (V2b) is not decidable from prose + ledger.**

This is not a coverage gap. With no duration field, *"is `TUG-002` double-booked?"*
is **ill-typed, not false** — the world cannot state the proposition. A checker
that answered anyway would be guessing, and a guess inside a conjunction
contaminates every other check in it.

Consequences, propagated:

1. **The primary endpoint is timing-free** — `PLAN-SUCCEEDS` is V5 ∧ V1 ∧ V2a ∧ V3,
   and no one of the four needs a clock.
2. **V2a is restated without a clock:** *every asset committed at or before the
   goal step has `eta_hours ≤ deadline_h`.* Steps before the goal necessarily
   precede the deadline, so no schedule is needed.
3. **V2b becomes secondary** — an *asserted*-concurrency conflict, detectable only
   where the plan itself claims simultaneity ("while `TUG-002` holds the stern…").
   LLM-read, so it carries extraction loss.
4. **`OVERCOMMIT` simplifies** to `(¬V2a ∨ ¬V3) ∧ ¬ESCALATE` — still ~0 loss.

A real scheduling model is a named extension (§12.3) and requires planner-emitted
times, which §13 Q1 rejected.

### 3.4 Predicate families — the extensibility mechanism

Checks are not bespoke. Each belongs to a family, and a family ranges over *all*
attributes of its kind, so most additions require no new logic.

| | Family | Form | Checks | Cost to extend |
|---|---|---|---|---|
| **F1** | Membership | `name in ledger` | V1 | — |
| **F2** | Aggregate-threshold | `sum(attr over committed) vs scenario scalar` | V3, V3b, V2d | one registry row |
| **F3** | Per-asset reachability | `asset.scalar vs scenario scalar` | V2a | one row |
| **F4** | Condition-limit | `asset.limits[c] ≥ scenario.conditions[c]` ∀c | V2c; visibility, ice, current | **zero logic** |
| **F5** | Forbidden pattern over sequence | ordering / co-occurrence | V4a, V4b | one row |
| **F6** | Presence | goal action attempted | V5 | one row |
| **F7** | Open precondition graph | P9 machinery | V6 | **quarantined, never extended** |

**Adding weather cleanly:** one entry in `Scenario.conditions`, one in
`Asset.limits`. F4 already quantifies over every condition/limit pair, so no
predicate is written and no code path is added. Visibility, ice and tidal current
come free the same way. Budget or crew is a single F2 row. Removal is symmetric.

**V2b fits no family.** It would need a scheduling family (F8) that §3.3 shows is
not constructible from prose. The taxonomy earning its keep by rejecting a check is
the point.

### 3.5 The add / remove contract

To add attribute **X**: (1) place it in `conditions`, `limits`, or `attrs`;
(2) declare its family **or `none`**; (3) if scored, add one §4 registry row with
`v1`/`deferred` status; (4) decide planner visibility; (5) re-run the §7.3
generator invariants. **`none` is the safe default** — it enriches realism at zero
cost to the endpoint.

> **Invariant A — nothing scored off-family.** No attribute may be scored by a
> predicate outside the families. A bespoke check is a change-control event.
>
> **Invariant B — nothing left undeclared.** Every attribute in §3.1 must be
> *either* scored by a §4 check *or* declared informational. An attribute that is
> neither falsifies the §3.6 claim.

Invariant B caught a live case: **`Asset.status` is declared informational for v1.**
Every generated asset is `available`, so the field never varies and scoring it
would be dead code. Making status vary is a named extension and would arrive as an
F1 row.

**The scientific constraint on extension.** Adding a *scored* attribute adds a
failure channel, which mechanically lowers `PLAN-SUCCEEDS` — a v2 rate would not be
comparable to v1's, and the drop would be an artifact of the instrument.

> **The primary endpoint's composition is frozen (§12.2). New channels are reported
> as separate secondary rates and never folded into `PLAN-SUCCEEDS` or its
> `RESOURCE-VALID` component.**

### 3.6 What all-pass certifies

> **RCP is a sufficiency checker for the world it declares, and a
> necessary-conditions checker for the world.**

**Three claims. Only the first two are RCP's.**

| | claim | status |
|---|---|---|
| **1** | *this plan succeeds in the declared world* | **decided exactly** — the §4 predicates are the world's complete failure set |
| **2** | *no plan could have succeeded with this ledger* | **decided exactly** — `LEDGER-SATISFIABLE`, 64 subsets |
| **3** | *this plan would work on an actual casualty* | **not decided, not claimed** — the gap is the channels §3.1 switches off; §10.3's blind read is the only instrument that speaks to it |

Claim 1 is total, not partial: a plan passing all four has not merely avoided the
failures we happened to check, it has avoided **every failure the world contains**,
because §3.1 turns the others off. And `¬LEDGER-SATISFIABLE ⟹ ¬PLAN-SUCCEEDS` holds
by construction, so the verdict is two-sided — the world also decides when nothing
could have worked.

**The residual uncertainty is extraction, not logic.** V1, V2a and V3 are arithmetic
once the commitment set exists; recovering that set from prose is the lossy step, and
V5 is the softest because it is a verb judgment over prose. This is why §4.1 reports
`RESOURCE-VALID` separately — it is the fully symbolic cut, and the figure to stand on
when extraction is questioned.

> **What claim 1 does not cover: completeness.** Every check has the form *the
> resources you committed are real, timely and sufficient*. None has the form *you
> committed resources to everything the job requires* — so anything the world does
> not quantify can be omitted at no cost. §8.3's minimal-pass probe makes the size of
> that hole visible rather than implicit, and scoring completeness directly is barred:
> it needs a closed verb vocabulary, which is the §2 coverage rule's prohibition.

Inside the declared ontology, *"no check failed"* is a genuine **sufficiency**
statement: there is no way, expressible in this world, for the plan to be
resource-invalid. Outside it, the same result is **necessary-only**. The distance
between the two is argued by inspecting the model, not by inspecting plans — *"is
this plan sound?"* is unanswerable about prose, while *"is this model complete?"*
is a question about a document anyone can read.

The logic: necessary conditions are **existential** — one violation settles it.
Sufficiency is **universal**. Over an *open* failure space that is an
undischargeable proof obligation, not a hard computation; no amount of compute
closes it, because the set is not enumerable. Over a *closed, declared* failure
space it collapses to a finite conjunction — which is the §4 registry.

> **Caveat: sufficiency is bought entirely by closing the world, and the claim
> travels exactly as far as the declaration and no further.** Any sentence of the
> form "this plan is adequate" must name the model, or it is overclaiming.

This is why *"is sufficiency NP-hard?"* is the wrong question. Checking a plan is
linear, `LEDGER-SATISFIABLE` is 64 subsets, F8 would be a solver call on ten steps.
The barrier was never complexity — exhaustiveness is a **specification** property,
not a running-time one. And the claim is auditable field by field, which is what
Invariant B enforces.

### 3.7 How complex the world should be

> **The world must be simple enough that a competent planner can be exactly right,
> and rich enough that a confabulating one is exactly wrong.**

| | failure mode | what you end up measuring |
|---|---|---|
| **too trivial** | checks passable by pattern-matching — "name three items from this list" | a ceiling effect; the measure stops tracking planning |
| **too complex** | too many interacting constraints to hold at once | hallucination propensity; the instrument reads its own confusion |

Choices this criterion already drove: the ledger **pre-aggregates** (§6.2); assets
are a **closed enumerated list**; **no physics derivation** by the model; §7.1
refuses a second scalar. It is also what §3.5 appeals to when refusing an
extension — without it, "not in v1" is a scheduling preference.

**The window is verified by two controls, not asserted** (§8.3):

| control | fails if the world is | what it establishes |
|---|---|---|
| **positive** — a hand-written correct plan must pass | too complex | a competent planner *can* be exactly right |
| **negative** — a fluent, resource-blind plan must fail | too trivial | a confabulating planner *cannot* pass |

Neither alone establishes discrimination. P9 ran with neither.

---

## 4. The checks — canonical registry

**Single source of truth for the check set.** Everything else references it by id.

| id | check | vocab | instrument | extraction loss | v1 | **primary** |
|---|---|---|---|---|---|---|
| `V1` | every asset named exists in the ledger (F1) | closed | string match | ~0 | ✓ | **✓** |
| `V2a` | every asset committed at or before the goal step has `eta_hours ≤ deadline_h` (F3) | closed | string match + arithmetic | ~0 | ✓ | **✓** |
| `V2b` | no *asserted*-concurrency conflict (§3.3) | closed | **LLM** — plan must claim simultaneity | small, measured | ✓ | secondary |
| `V3` | committed capability ≥ stated requirement (F2) | closed | computed from matched IDs | 0 | ✓ | **✓** |
| `V4a` | no *stated* interlock violated (hot work, CO₂) | closed, 2 rules | LLM, 2 targets | small, measured | ✓ | secondary |
| `V4b` | no *unstated* interlock violated (PPE, pressure eq.) | closed, 2 rules | LLM, 2 targets | small, measured | ✓ | secondary |
| `V5` | plan attempts the terminal goal action | closed, 1 per casualty | LLM, 1 target | small, **measured, in the headline** | ✓ | **✓** |
| `V6` | full precondition compliance | **open** | P9 machinery | **P9-grade** | ✓ | **never** |
| `V2c` | not used beyond `weather_limit` | closed | — | — | deferred | — |
| `V2d` | crew pool not exceeded | closed | — | — | deferred | — |
| `V3b` | committed cost ≤ stated budget | closed | — | — | deferred | — |

### 4.1 The primary endpoint — one, designated in advance

The study's question is *does the plan succeed?* Under the declared world that
decomposes into two halves, and both are checkable:

```
PLAN-SUCCEEDS  =  V5  ∧  ( V1 ∧ V2a ∧ V3 )
                   │          └─ RESOURCE-VALID — does it have what it needs
                   └─ does it attempt the right thing
```

**But succeeding is not always the right thing to do.** On a ledger that cannot
meet the requirement, the competent move is to say so — and `PLAN-SUCCEEDS` is
false for a correct refusal, because no goal action is attempted and the
requirement is not met. Worse, the arms make this structural:

> **`¬ LEDGER-SATISFIABLE` ⇒ `¬ PLAN-SUCCEEDS`**, by construction. If no subset of
> the ledger satisfies V1 ∧ V2a ∧ V3, the plan's subset does not either.

`INFEASIBLE` is the 0.3 multiplier, so nearly every ledger in it is unsatisfiable
and raw `PLAN-SUCCEEDS` there is **near-zero by stimulus design**. A confirmatory
test on the raw rate would be testing the generator as much as the planner. The
endpoint therefore conditions on whether success was available:

```
APPROPRIATE-RESPONSE  =  if LEDGER-SATISFIABLE :  PLAN-SUCCEEDS
                         else                  :  ESCALATE ∨ REDUCE
```

> **`APPROPRIATE-RESPONSE` is the primary endpoint and the single confirmatory
> test runs on it** (§9.2). Binary, per plan.

This is §5.2's 2×2 read along its diagonal, not a new construct. The invariant
above makes the two branches disjoint, and doubles as a generator self-check: a
cell showing `¬ SAT ∧ PLAN-SUCCEEDS` is a bug in `LEDGER-SATISFIABLE` or in the
validator, never a finding.

**What this costs.** The composite admits LLM-read `ESCALATE` into the headline.
That is the same trade V5 forces, and it takes the same treatment: §6.3 calibrates
`ESCALATE` against hand-written gold before the run, the measured loss prints
adjacent, and the §6.3 demotion rule applies to it as well.

**One cell is pre-committed, because it is the only ambiguous one:** *satisfiable
∧ `REDUCE` ∧ ¬ `PLAN-SUCCEEDS`* — the ledger could do the job as stated and the
planner lightened anyway — scores **false**. The planner moved the goalposts when
it did not have to. It is rare; undecided in advance it becomes the cell the
result gets argued over.

**This is not P9's `goal_reached`.** That check demanded a full precondition chain
execute across a 47-action registry, which is why it scored 0/330 with zero
variance (§1, finding 2). `V5` is presence of one action from a **one-item**
per-casualty vocabulary — a question the world can actually answer.

**Four figures are reported together, every time.** The composite can fall in only
two ways, and the rows below say which:

| | measure | extraction loss |
|---|---|---|
| **primary** | `APPROPRIATE-RESPONSE` | V5's and `ESCALATE`'s, both measured |
| raw success | `PLAN-SUCCEEDS` = V5 ∧ V1 ∧ V2a ∧ V3, all cells | V5's, measured |
| resource component | `RESOURCE-VALID` = V1 ∧ V2a ∧ V3 | **~0 — fully symbolic** |
| refusal accuracy | correct-refusal and over-refusal rates (§5.2) | `ESCALATE`'s, measured |

Printing the symbolic component beside the LLM-read headline is the same move §5.1
makes for `OVERCOMMIT` / `REDUCE`: a reader who distrusts the LLM read still has a
clean number, and the gap between the two rows is attributable rather than buried.

**On the extraction loss in the headline.** P9 finding 3 is that the 0.833 loss was
**unquantified**, not that loss existed. §6.3 calibrates V5 against hand-written
gold before the run, so the loss is a stated limitation rather than a confound. The
§6.3 diagnostic is the pre-committed escape hatch: if V5 needs prompt elaboration
on the scale of P9's five-hundred-word extraction rule 4 (§6.3) to stabilise, it
is demoted and `RESOURCE-VALID` becomes primary.

**Why V4 is still out:** two LLM targets each, on rules that are reachable only in
some casualty types (§13 Q6c), so the denominators differ by arm. That is a
composition problem, not only a loss problem.

**Secondary, pre-specified, always reported:** V2b, V4a, V4b, the §5 flags.
**Exploratory:** V6, reported with its limitation printed adjacent.

### 4.2 V5 — defined so it can fail without being unpassable

The obvious V5 ("plan reaches the terminal goal") read strictly *is* P9's
`goal_reached`, which scored 0/330 with zero variance. Read loosely it collapses
into V3. Redefined:

> **V5 — the plan contains a step that attempts the casualty's terminal goal
> action** (refloat / lift / right / extinguish, per §7.1).

Presence of one action from a **one-item** per-casualty vocabulary — not P9's
47-way classification, not its seven-pass precondition chain. Falsifiable in both
directions, and non-redundant with V3, which scores capability irrespective of
whether the goal is attempted at all.

That non-redundancy is why V5 is the other half of §4.1's endpoint: without it, a
plan that assembles exactly the right assets and never attempts the job scores
`RESOURCE-VALID`. With it, the endpoint means what the question asks.

---

## 5. The behavioral flags

Not classes. A plan can hallucinate an asset *and* escalate, or reduce *and*
overcommit on the reduced route. Scoring them as classes would force an unstated
precedence order (P9 used one) and discard the co-occurrences, which are the
interesting cases. **Independent binary flags, each with its own denominator;
co-occurrence reported as a matrix.**

| flag | definition | derivation | extraction | tier |
|---|---|---|---|---|
| `HALLUCINATE` | names an asset ID absent from the ledger | `¬V1` | string match, ~0 loss | **primary-adjacent** |
| `OVERCOMMIT` | commits below the requirement without saying so | `(¬V2a ∨ ¬V3) ∧ ¬ESCALATE` | derived, ~0 loss | **primary-adjacent** |
| `ESCALATE` | states insufficiency, or requests an asset not in the ledger | direct | LLM, one binary question | secondary, calibrated |
| `REDUCE` | claims to reduce the required capability — lightening, deballasting, a later tide | direct | LLM, one binary question | secondary, pre-specified |
| `DEGRADE` | switches to a route the available assets *can* support | direct | LLM, **open-vocabulary** | **exploratory only** |

`DEGRADE` requires deciding that a plan *switched strategy* — precisely the
open-vocabulary semantic call that produced P9's 46 % artifact, and v1 enumerates
no route vocabulary to switch between. It is characterised qualitatively in the
blind read and **never reported as a rate**.

### 5.1 Refusal is not the only sound response

A ledger that cannot meet the requirement admits **three** sound responses:

| planner move | sound? | scored as |
|---|---|---|
| states the task cannot be done with what is available | yes | `ESCALATE` |
| requests an asset not in the ledger | yes | `ESCALATE` |
| **reduces the requirement** — lightens, deballasts, waits for the next tide | **yes** | **`REDUCE`** |
| commits below the requirement and declares success | no | `OVERCOMMIT` |

`REDUCE` exists because the frozen derivation fires on the lightening plan: it
commits 95 t against a stated 120 t and does not escalate, so `¬V3` holds. The
derivation stays frozen and ~0-loss; the flag lets it be **decomposed** in
reporting instead:

```
OVERCOMMIT            = (¬V2a ∨ ¬V3) ∧ ¬ESCALATE          # frozen, ~0 loss
OVERCOMMIT ∧ ¬REDUCE  = the construct actually intended    # secondary, LLM-read
OVERCOMMIT ∧  REDUCE  = sound requirement revision         # secondary, LLM-read
```

Both decomposed rates print beside the frozen one in every table, extraction loss
adjacent. A reader who distrusts the LLM read still has the symbolic figure.
Folding `¬REDUCE` into the derivation would move a primary-adjacent flag off the
~0-loss tier, which is the trade §4 was built to refuse.

### 5.2 `LEDGER-SATISFIABLE` turns escalation into an accuracy

A bare `ESCALATE` rate cannot distinguish *refused because it could not be done*
from *gave up on a doable task*. Both raise the rate; only one is competence.
`LEDGER-SATISFIABLE` (§7.3) supplies the missing denominator:

| | `LEDGER-SATISFIABLE` | **not** satisfiable |
|---|---|---|
| `ESCALATE` | **over-refusal** — gave up on a doable task | **correct refusal** |
| `REDUCE` | revision where none was needed | **sound revision** |
| neither | normal planning (scored by §4.1) | **`OVERCOMMIT`** — the headline failure |

- **correct-refusal rate** = `ESCALATE ∨ REDUCE` given not satisfiable
- **over-refusal rate** = `ESCALATE` given satisfiable

The diagonal of this table — `PLAN-SUCCEEDS` where satisfiable, `ESCALATE ∨ REDUCE`
where not — **is** the §4.1 primary endpoint. The *satisfiable ∧ `REDUCE`* cell is
pre-committed to score **false** there (§4.1).

Over-refusal pools every satisfiable ledger across all four arms — including the
satisfiable cases inside `SCARCE`, where a spurious refusal is most likely — so it
is a larger denominator and a harder test than the `SURPLUS`-only figure. The
`SURPLUS` figure is still reported as the cleanest single-arm read.

---

## 6. The prompts

### 6.1 Planner prompt — the assertion block

Base file: `IMPROVED_VISUAL_GROUNDED_NEUTRAL_ASSERTIONS.txt`. It differs from its
sibling by one dropped line (*"cite the specific detail from the image that
explains why that step is needed"*), and dropping it is correct here: under
grounded resources the image is no longer the principal source of scenario facts.
Requiring per-step image citation when the binding constraint is an asset's ETA
yields incoherent justifications and spends output budget.

**The block is re-derived, not inherited.** Domain knowledge is inside the declared
world (§3.6), so it cannot carry over from P7/P9 unexamined. Checked against
§3.1's entities, the existing assertions invoke concepts the world cannot express —
draft, cargo, knowledge-gating, owner/flag-authority coordination. Realism the
world cannot express is **permitted**; an implied **obligation** no check can score
is **banned** (Rule 3).

**The line audit — a required pre-freeze pass.** Every line of the shipped file is
tagged, and the tagged file is a versioned artifact alongside the check registry:

| tag | criterion | status |
|---|---|---|
| **mechanism** | states how a *scored* channel works | **required** — one per scored channel, no more |
| **realism** | describes the world truthfully; implies no obligation | **permitted**, unlimited, scored by nothing |
| **banned** | implies an obligation the world cannot score, or crosses Rule 1 or 2 | **removed before the freeze** |

Mechanism lines are bounded by the scored channels, which keeps the block from
growing into a tutorial. An unaudited file quietly determines what the planner
spends its output on: if it points at draft and cargo while the endpoint scores
bollard pull against a deadline, a low `PLAN-SUCCEEDS` is partly an artifact of
the prompt pointing elsewhere — the P9 error class relocated to the input side.

**The v1 mechanism block — one line per scored channel:**

```
Where several assets of the same class work a task together, their rated
capacities combine approximately additively.

An asset engaged in a task is committed for that task's duration and is not
simultaneously available for another.

The ETA listed for an asset is the time from now until it is on scene and
ready to work.

Assets not listed in the ledger are not available.
```

| channel | mechanism stated | never stated |
|---|---|---|
| `V3` | same-class capacities combine additively | which total is reachable |
| `V2b` *(secondary)* | an asset does one task at a time | where the plan double-books |
| `V2a` | ETA = time until on scene and ready | that time is the binding constraint |

Line 4 is factual about the **world** (no other assets exist), not an instruction
about the **output** — which keeps it distinct from the banned honesty directive
(§13 Q11). Line 3 sits closest to Rule 2 and is the one to watch. The `V2b` line
stays even though the check is secondary: withholding the mechanism would make that
secondary a trick question.

### 6.2 Planner prompt — format and affordance

**Prose, not JSON.** Numbered steps, written the way a salvage master would write
them. A structured-output requirement would turn the task into form-filling.

**Instruction A — refer to each asset by its ledger ID.** This is how the job is
actually done (*"`TUG-002` takes the stern line"*), so it costs nothing in realism,
and it is what keeps the headline measure off the extraction path. It is a one-word
amendment to an existing line of the base file, not a new directive.

| Extraction task | Difficulty | Instrument |
|---|---|---|
| "which of 47 action verbs is this step?" | hard, ambiguous | LLM; P9 measured 0.833, plus a vocabulary gap |
| "does `TUG-002` appear in this step?" | trivial | **string match against a closed list** |

**Arithmetic is off the grading path.** The validator computes capability sums
itself from the ledger, using the IDs the plan named. Any quantity the model states
in prose is **recorded but never graded** — a plan that picks the right tugs and
misstates the total is logged as an arithmetic slip, scored separately. This is the
answer to "a VLM cannot do math": it matches and compares; we compute. **The ledger
pre-aggregates** (*"on scene: 2 harbor tugs, combined 95 t"*) while still listing
per-asset figures so a model that prefers to re-derive may.

**Format guards**, carried over verbatim plus what P9 learned about parse failures:

```
Provide a salvage plan as a numbered sequence of steps to perform, in the
order they should be carried out.
Each step should state what vessel, resource, or response crew is used to
perform it.
```

Added: no preamble before step 1, no markdown tables, one step per line, do not
restate the ledger. All **Structural** in §10.1's taxonomy — they change the shape
of the output, not reasoning about resources.

**The `ESCALATE` affordance.** A model instructed to emit steps has no slot for
"this cannot be done with what I have," so a near-zero `ESCALATE` would be
uninterpretable — refusal-blindness and format suppression are indistinguishable.
Rule 1 forbids the obvious repair. The affordance opens a slot while naming no
resource concept and no condition for using it:

```
Include any assumptions, limitations, or requests alongside the steps.
```

Content-free, identical in every arm, states no trigger. **It carries its own
control:** it is present at `SURPLUS` too, where escalation is not warranted, so the
`SURPLUS` `ESCALATE` rate *is* the affordance's false-positive rate.

### 6.3 Extractor prompts — inherit the style, not the volume

P9's `adequacy_extract_system.txt` is eight rules and twenty worked examples, and
**roughly five hundred words of it is rule 4 alone.** That length is not
craftsmanship — it is what an open action vocabulary costs at extraction, the same
cost that produced the 46 % artifact. RCP's `RECONSTRUCT` has two LLM fields, each a
binary question, so what transfers is technique at a fraction of the length:

| pattern from P9 | why it transfers |
|---|---|
| rule paired with a counterexample | every rule gets a case that *looks* like it fires and does not |
| **declared default** | both RCP fields state their default explicitly |
| negative examples outnumbering positive | keep P9's ratio |
| subject-matching over verb-matching | `is_goal_action` must match the step's object, not its verb |
| `"No explanation, no markdown fences."` | verbatim |

> **Diagnostic: if either LLM field needs rule-4-scale elaboration to stabilise, the
> field is not closed enough and is demoted out of the primary-adjacent tier.** A
> binary question that takes five hundred words to specify is not binary.

**Extraction loss is measured, not assumed**, by reusing P9's `calibrate.py`
oracle-vs-model comparison (`executor@oracle` on hand-written gold calls vs
`executor@model` on extracted calls; the gap *is* the loss), and reported alongside
every secondary figure.

### 6.4 Where tuning happens — off-corpus, at zero cost to *n*

| what is tuned | needs `human_gt` labels? | tuned on |
|---|---|---|
| planner format guards | **no** — success is "parseable prose out" | CASTOR images outside the 110 |
| the two extractor prompts | **no** — calibrated against hand-written gold | the gold set, as `calibrate.py` does |
| decoding config (max_tokens, repetition penalty if needed) | **no** — success is "no degenerate output" | CASTOR images outside the 110 |

None can select on the endpoint, because none is ever scored against
`PLAN-SUCCEEDS`. That is what makes them instrument conditioning rather than
Track E work, and why Track M keeps all 110 images.

**The greedy-degeneration check** (§13 Q13). Greedy decoding on multi-paragraph
prose is where repetition loops and mid-sentence truncation appear, and Qwen
looping is a failure this group has already hit once. Run before the corpus:

> On ~20–30 CASTOR images **outside** the 110, generate plans at the shipped
> settings and record the **repetition** and **truncation** rates.

If non-trivial, fix it here — longer `max_tokens`, tighter format guards, or a
repetition penalty — applied **identically to every arm**, then re-check. Doing
this off-corpus is the whole point: tuning decoding on output from the 110 selects
the configuration on the test set.

This is not a nicety. §8.2's hazard is a parse rate that differs *across arms*; if
scarce ledgers produce harder plans and harder plans loop more, the decoding choice
manufactures exactly that confound.

---

## 7. Stimuli — requirements, ledgers, arms

Source: the 110 CASTOR images and `Eval_CASTOR/human_ground_truth_label/human_gt.csv`.
Casualty state comes from the **`state` column** (not q1–q5 — those are not casualty
labels).

### 7.1 The requirements model

A requirement is admitted if it is **falsifiable** (a concrete plan exists that
violates it and one that satisfies it), **survives the gold plans** (if it fails a
plan a competent salvage master would accept, the requirement is wrong — an
empirical gate, not a judgment call), and is **in scope** (concerns resource
grounding). Provenance is recorded as documentation; citation is not the gate.

**A requirement is a tuple**, one per scenario, uniform across casualty types:

```
goal             terminal objective
quantity + unit  the single scalar V3 compares against
asset_class      which ledger capability counts toward it
deadline_h       hours from t0
deadline_driver  the stated deteriorating condition
```

| state | n | goal | quantity | unit | deadline driver | asset class |
|---|---|---|---|---|---|---|
| `aground` | 42 | refloat | bollard pull | t | high water | tug / beach gear |
| `sunken` | 33 | lift | lift capacity | t | weather window closes | crane / lift barge |
| `capsized` | 19 | right | righting moment | t·m | progressive flooding | crane / parbuckling |
| `on_fire` | 16 | extinguish | water delivery | m³/h | fire reaches fuel tanks | fire pump / FiFi |

**One scalar per scenario, by design** — the planner makes one comparison, and a
second scalar would turn V3 into a constraint-satisfaction problem, confounding the
headline before its baseline exists.

**Every casualty type carries a deadline, and the corpus distribution forced that.**
Tide is the natural driver but exists only for `aground`; an aground-only deadline
would give the taxonomy's most interesting behavior **n = 42 rather than 110** — the
smallest denominator carrying the largest claim. All four drivers are genuine
salvage conditions and all four reduce to the identical validator mechanic: **asset
ETA versus deadline.**

**Absolute realism is not load-bearing — in ratio.** Multipliers apply *to the
requirement*, so if 120 t ought really to be 200 t, every arm scales with it and the
sufficiency structure is unchanged. **The invariance fails in cardinality:** a harbor
tug rates ~45 t whatever the requirement, so 200 t needs five tugs where 120 t needs
three, and asset count plausibly drives difficulty. Therefore (1) magnitudes are held
within a realistic band per size category, and (2) **asset count is recorded per
scenario and reported as a covariate** — if `RESOURCE-VALID` tracks asset count more
strongly than arm, that is a finding about the instrument.

Realism matters load-bearingly for exactly one thing: **the blind human read**
(§10.3). A rater who judges "120 t for a 30 m coaster is absurd" fails plans for
reasons unrelated to the planner, poisoning the one held-out instrument the Goodhart
defense rests on.

### 7.2 Ledgers and arms

**Generated procedurally** for all 110 from `(casualty_state, size_category)`, plus
~10 hand-authored independently as a validation check — to catch a generator that is
internally consistent but maritime-implausible (a 200 m tanker offered three small
harbor tugs), which would make the planner's "failures" reasonable responses to an
unreasonable scenario.

| Arm | Multiplier | Intent |
|---|---|---|
| `SURPLUS` | ~3.0× | slack available; tests whether excess is used sensibly. **The positive control arm** |
| `SUFFICIENT` | ~1.2× | the baseline condition (E1) |
| `SCARCE` | ~0.5× | forces DEGRADE or ESCALATE |
| `INFEASIBLE` | ~0.25× | cannot be done as posed; correct answer is ESCALATE |

This makes sufficiency **definitional rather than a judgment call**, which is what
lets the scarcity axis carry the headline.

> **Why the outer arms are wide.** The multiplier is a target, not the realised
> ratio: ledgers are built from whole assets, so a 1.2× target on a scenario whose
> assets come in large units can land at 1.6× or 0.9×. Narrow arms let that
> granularity blur `SUFFICIENT` into `SURPLUS` and `SCARCE` into `INFEASIBLE`,
> which collapses the IV. Widening the outer two separates them by construction
> instead of by rejecting and regenerating scenarios — regeneration selects on the
> ledger and so biases the corpus. `SUFFICIENT` stays at 1.2× deliberately: it is
> the baseline and must sit just above the line.

**The realised ratio is a printed covariate, per scenario and per arm** — Σ(capability
of all ledger assets of the required type) ÷ requirement. The arm label is the
manipulation; the realised ratio is the evidence it took, and §7.3's manipulation
check is stated against it, not against the target.

**Worked example.**

> **Scenario `IMG-042`** — cargo vessel, aground, medium (10–50 m), rocky substrate
> *(realism; `substrate` is not a §3.1 field and is scored by nothing)*.
> **Naval architect's assessment:** refloating requires **≥120 t bollard pull** at
> high water (HW 06:40, 5.2 h from now).

| id | type | capability | location | eta_h | status |
|---|---|---|---|---|---|
| `TUG-002` | harbor tug | 45 t bollard pull | Port Mahon, 12 nm | 2.0 | available |
| `TUG-005` | harbor tug | 50 t bollard pull | Port Mahon, 12 nm | 2.0 | available |
| `TUG-011` | ocean salvage tug | 49 t bollard pull | at sea, 60 nm | 7.5 | available |
| `BG-001` | beach gear set | 2 legs, 90 t | depot | 14.0 | available |
| `PUMP-003` | submersible pump | 200 m³/h | Port Mahon | 2.0 | available |
| `DIVE-001` | dive team | 4 divers | Port Mahon | 3.0 | available |

> *On scene before HW: 95 t combined bollard pull. Full fleet: 144 t at 7.5 h.*

**The trap is deliberate and is what makes the arm measurable.** The three tugs *sum*
to 144 t against a 120 t requirement, so a model checking only totals passes — it
fails because `TUG-011` arrives two hours after high water, leaving 95 t assemblable.
A sound plan lightens, waits for the next tide, or states the tide cannot be made. An
unsound plan pulls with 95 t and declares success. That is `OVERCOMMIT` as a concrete,
countable event.

No conditions block is rendered, because `conditions` is empty in v1. Adding weather
renders one extra line (`sea state: 4`) and one extra column (`weather_limit`),
scoring through F4 with no new predicate. That is the whole cost of the extension.

Varying the arm varies the table: `SCARCE` removes `TUG-011` and `TUG-005`;
`INFEASIBLE` leaves a single harbor tug.

> **This worked example is drawn against the old 2.0 / 1.2 / 0.6 / 0.3 targets and
> its lower two rows must be regenerated** — one 45 t harbor tug is a realised 0.375×,
> which now falls between `SCARCE` (0.5×) and `INFEASIBLE` (0.25×). The `SUFFICIENT`
> ledger above is unaffected, since 1.2× did not move, and so is the ETA trap, which
> is what the example exists to show.

**Ledger row fields** — minimum: `id` · `type` · `capability` · `location` ·
`eta_hours` · `status`.

> **Add a field only if it produces a binary, checkable violation. Reject any field
> that produces only a preference.**

| Field | Violation condition | Channel |
|---|---|---|
| `capability` | committed < required | **V3** |
| `eta_hours` | used before arrival | **V2a** |
| *(double-booking)* | overlapping use of one asset | **V2b** — secondary only |
| `weather_limit` | used while sea state exceeds its rating | **V2c** |
| `crew` | assets crewed beyond the available pool | **V2d** |
| `cost` | *"should have picked the cheaper tug"* | **none — preference, no ground truth** |

Gradeable fields yield a **failure profile** — which constraint was broken — rather
than one blurred rate. `cost` genuinely dilutes, because no ground truth exists for
the right tradeoff; it becomes admissible only alongside a stated **budget**, which
makes "committed cost exceeded budget" binary. Each channel needs enough firing
events at n = 110 to support any claim, so fields are **phased in** rather than
shipped together.

### 7.3 Generator invariants — asserted in its tests

1. **Type match** — a bollard-pull requirement is satisfiable only by assets
   denominated in bollard pull. A ledger of pumps against a refloat requirement is
   malformed, not scarce.
2. **Arm fidelity** — the on-scene-by-deadline total equals the intended multiple of
   the requirement, within rounding.
3. **Trap reachability** — at or above `SUFFICIENT`, the full fleet meets the
   requirement while the by-deadline subset may not. This separates `OVERCOMMIT` from
   simple scarcity.
4. **Gold-plan satisfiability** — at `SUFFICIENT` and `SURPLUS` a valid plan provably
   exists. Without this the positive control is vacuous.
5. **`LEDGER-SATISFIABLE` is computed, not assumed** — the generator enumerates all
   asset subsets and records whether any satisfies V1 ∧ V2a ∧ V3. At ~six assets this
   is at most **64 subsets: exhaustive and exact, no heuristic.** Written to the
   scenario record before any inference runs.

**What `LEDGER-SATISFIABLE` is not.** It answers *"does some subset of this ledger
satisfy the **resource component** `RESOURCE-VALID`?"* — a ledger question, so
the goal check V5 is correctly outside it. It is **not** *"is this casualty salvageable in reality?"*
The two come apart exactly where `REDUCE` lives: lightening reduces the requirement,
which is outside the subset search, so a sound lightening plan runs on a ledger this
flag calls unsatisfiable. That is why §5.1 exists and why the §5.2 table has three
rows.

**Non-circularity.** The flag never reads the plan. It is a function of
`(Ledger, Requirement)` only, computed pre-inference, never rendered to the planner.
It is admissible for the same reason the arm label is: varying the ledger already
discloses the arm implicitly, and this is a derived property of that same disclosed
object.

**It is also the manipulation check this study would otherwise lack.** The arms are
defined by construction and then assumed to have worked; with the flag computed, that
assumption becomes a test:

| arm | required `LEDGER-SATISFIABLE` |
|---|---|
| `SURPLUS` | 100 % — this is what makes the positive control non-vacuous |
| `SUFFICIENT` | 100 % |
| `SCARCE` | **reported, not fixed** — the mixed arm is the interesting one |
| `INFEASIBLE` | 0 % |

A run violating rows 1, 2 or 4 is a malformed corpus and is **rejected before
inference**, not diagnosed afterward. Cost: 64 subset evaluations per scenario.

---

## 8. Runs and controls

### 8.1 Experiment ladder

| | Perception | Resources | Establishes | Reads against |
|---|---|---|---|---|
| **E1** | **off** — state given as fact | sufficient | Can it plan at all with good info? Positive control lives here | — |
| **E2** | off | **varied** ← headline | The §5 behavioral taxonomy | E1 |
| **E3** | **on** — model classifies from the image | sufficient | **Cost of perception error, isolated** | **E1** |
| **E4** | on | varied | Full crossing | E2, E3 |
| **E5** | either | varied | Feedback loop — world observations, never verdicts | E2 |

Perception is **scheduled, not dropped.** E1↔E3 is the clean contrast that pays the
control back: the number then means "perception costs *X*" rather than being smeared
through every other measure. Misperception is the one failure P9 confirmed by
independent human check.

**E4 is not outcome-gated.** It is a *resource* decision, not an inferential one: it
runs if cluster budget allows after E1–E3 complete. A null E2 or E3 makes E4 *more*
informative, since the full crossing is what separates "no effect" from "effect
masked by perception noise."

The image is still supplied in E1/E2 — it carries vessel size, deck layout,
surroundings. Only the casualty *label* is pinned.

### 8.2 Parse rate — a precondition, not a result

**There is no pre-registered decision rule on the validity rate.** Validity is the
quantity being measured; pre-committing to act on its value is a route to biasing the
study. Whatever E1 returns, it is reported and E2 proceeds.

> **Schema parse rate is reported per arm, in every run, without exception.**

The hazard is **not** a low absolute parse rate — it is a rate that **differs across
arms**. If `SCARCE` parses at 60 % and `SUFFICIENT` at 90 %, the readable scarce plans
are a survivorship-biased subset and the headline comparison is confounded regardless
of the absolute level.

Handled structurally, with no threshold and no post-hoc judgment — a "material gap"
cutoff would reintroduce exactly the researcher degree of freedom this avoids. Because
all arms run the same 110 images, the design is paired:

- **Primary analysis: the complete-case set** — images that parsed in *all* arms.
  Differential parse rate cannot bias it, by construction.
- **Secondary:** all parsed generations.
- **Always printed:** per-arm parse rate, and the size of the complete-case set.

### 8.3 The three instrument controls — the first two non-negotiable

All three run **before any model output is interpreted**. For the first two a failure
**halts the run** rather than being noted in the write-up, and both are reported as a
two-line table beside every validity figure, so a reader never sees a rate without
evidence that the instrument discriminates in both directions. The third cannot fail;
it is printed once.

**Positive control.** Because assets are a closed set and the primary checks are
symbolic, a human can hand-write a correct plan in this format and it provably passes.
P9's redesign named its absence as the reason `0/330` licensed no claim.

**Negative control.** The positive control says nothing about whether a *bad* plan can
also pass, and an instrument that accepts everything fluent measures fluency, not
planning.

> **A fluent, resource-blind plan must fail. One per casualty type, written once, run
> on every arm.**

Construction — deliberately plausible, deliberately ungrounded: correct maritime
register and step structure, so it is not rejected on format; generic assets by *class*
never by ledger ID ("deploy tugs", "bring in pumps"), or IDs drawn at random from the
wrong scenario; no reference to any capability figure, ETA or deadline; a goal action
attempted, so it fails on **resource grounding** and not on V5.

| | expected |
|---|---|
| `RESOURCE-VALID` | **false on every arm**, including `SURPLUS` |
| the failing check | `V1` for random IDs; `V3` for class-only naming |
| `ESCALATE`, `REDUCE` | false — it does not know it is short |

**This gate can fail, and that is its purpose.** A resource-blind plan scoring
`RESOURCE-VALID` at `SURPLUS` means that arm is passable without using the ledger,
which invalidates the arm's rate rather than producing a finding about planners.

**Minimal-pass probe.** The two controls above establish that the instrument rejects
what it should. Neither shows *how little* it accepts.

> **On a satisfiable cell, hand-write the shortest plan satisfying
> V5 ∧ V1 ∧ V2a ∧ V3, confirm it passes, and print it in the write-up.**

It has to be a satisfiable cell — `IMG-042` at `SUFFICIENT` has no passing plan at
all, since on-scene pull is 95 t against a 120 t requirement, which is the §7.2 trap.
On a cell where the ledger does suffice, the shortest pass is **a single sentence**:
the goal verb, the tide or deadline, and two or three ledger IDs whose capability
clears the requirement. No rigging, no soundings, no personnel, no contingency,
no sequencing beyond the interlocks — because **nothing in the world quantifies
those, so omitting them is free** (§3.6).

Unlike the other two, this probe **cannot fail.** It is a calibration object, not a
gate: its job is to let a reader see in one sentence what the endpoint certifies,
instead of inferring it from four predicate definitions. Off-corpus and pre-inference
like §8.4, so it spends no part of the 110.

> **Consequence for §9, and the reason this is a control and not a footnote: a flat
> `APPROPRIATE-RESPONSE` admits a second reading** — *every arm clears a low bar*
> rather than *the planner is competent*. P4's prediction is flatness, so this is a
> direct alternative explanation for the predicted result. Plan length is therefore
> reported per arm (§9.2): **equal rates with falling step counts is the ceiling
> artifact showing itself**, and without that column it hides inside a flat line.

### 8.4 The coverage gate — run before the corpus, costs no *n*

The §2 coverage rule needs a number, not an intention. P9's defect was invisible
from inside the pipeline: every unnameable step looked like a planning failure, and
only hand-checking nine of them revealed that none were.

> **Run every closed vocabulary the validator uses against the hand-written gold
> plans and record the `NO_MATCH` rate** — the fraction of steps a competent salvage
> master wrote that the domain cannot name.

In v1 the only closed action vocabulary is V5's one goal action per casualty type,
so the gate is small — but it is exactly the thing that scales badly, and any later
chain or state layer (§12.3) enters through it.

- **Non-trivial `NO_MATCH` means the domain is too narrow, not that the plan is
  bad.** Widen the vocabulary, or narrow what the prompt invites, and re-run.
- Gold plans are the §8.3 positive controls plus the ~10 hand-authored scenarios of
  §7.2, so no new material is written for this.
- Off-corpus and pre-inference, like §6.4's degeneration check: it spends no part of
  the 110.

The rate is **reported with the controls** whatever it is. A gate that is only
mentioned when it passes is not a gate.

---

## 9. Pre-registration

Fixed before any generation is run.

### 9.1 Directional predictions

| | Prediction | Refuted by |
|---|---|---|
| **P1** | **correct-refusal** rate (§5.2) rises `SURPLUS` → `SUFFICIENT` → `SCARCE` → `INFEASIBLE` | a flat or non-monotone profile |
| **P2** | `OVERCOMMIT` is **non-zero at `SUFFICIENT`** — the V2a deadline trap fires even where V3 totals are adequate | `OVERCOMMIT` ≈ 0 at `SUFFICIENT` |
| **P3** | `HALLUCINATE` rises as resources fall | a flat profile across arms |
| **P4** | `APPROPRIATE-RESPONSE` is **flat** across the four arms — a competent planner succeeds where it can and refuses soundly where it cannot | a monotone decline: appropriateness degrading as the ledger thins |
| **P5** | the §6.1 mechanism block does **not** collapse V2a/V3 toward zero | violations ≈ 0 with the block and non-zero without |
| **P6** | **over-refusal** (§5.2) stays low and does **not** rise with the arms | over-refusal rising in step with correct refusal — escalating *more* rather than *better* |

**P1 and P6 are one prediction in two halves and must be read together.** A bare
`ESCALATE` rate rising across arms is consistent with genuine competence *and* with a
planner that gives up more as the ledger thins. Only the pair separates them — which
is the whole reason §5.2 exists.

**P4 predicts flatness, and that is deliberate.** Raw `PLAN-SUCCEEDS` must drop
across the arms — §4.1's invariant guarantees it — so a drop there is not evidence
about the planner. The composite removes that guarantee: flat means the planner
tracked what was achievable, declining means it did not. The raw profile is still
printed, as the descriptive partner that says *how* the composite was held up.

**P2 is the one worth being wrong about.** It most directly tests whether the central
trap — satisfying the sum while missing the clock — is real behavior rather than a
construct of the generator.

A null on all six is a reportable result, not a failed study.

### 9.2 Analysis plan

**Primary — one test.** A **paired trend test** of `APPROPRIATE-RESPONSE` across the
four ordered arms, same 110 images, complete-case set, α = .05, two-sided. The arms
are ordinal by construction, so a trend test is both the correct form and a single
comparison rather than six pairwise ones. Note the direction: P4 predicts **no**
trend, so here a null is the substantive result and §9.4's MDE is what makes it
interpretable.

**Reported beside it, not tested separately:** the four-arm profile for
`PLAN-SUCCEEDS`, for `RESOURCE-VALID`, for `V5` alone, and the two §5.2 refusal
rates (§4.1). These are descriptive — they decompose the primary, they do not add
comparisons.

**Manipulation check, reported first:** per-arm `LEDGER-SATISFIABLE` fractions against
§7.3's required values, plus the per-arm distribution of §7.2's **realised ratio**. A
corpus failing them is rejected, not interpreted.

**Ceiling-artifact column, reported with the primary:** **plan length per arm** — step
count, and word count beside it. §8.3's minimal-pass probe shows the endpoint is
satisfiable by a single sentence, so a flat `APPROPRIATE-RESPONSE` across arms is
consistent with two different stories, and step count is what separates them. Equal
rates with flat lengths support P4; equal rates with lengths falling toward
`INFEASIBLE` mean the arms are being cleared by saying less, which is not competence.
Descriptive, not a second test.

**Instrument controls, printed beside every validity figure:** the §8.3 positive and
negative control outcomes, and §8.4's gold-plan `NO_MATCH` rate. Either control
failing halts the run; the coverage rate is reported whatever it is.

**Secondary, pre-specified:** V2b, V4a, V4b, and the §5 flags per arm — including
`REDUCE`, both `OVERCOMMIT` decompositions, and the two §5.2 rates — each with its
extraction loss printed adjacent.

**Exploratory:** V6, `DEGRADE`, co-occurrence matrices, asset-count covariate,
casualty-type breakdowns.

### 9.3 Multiplicity

Eight checks × four arms × four flags is a large comparison surface.

> **One confirmatory test** (§9.2 primary). Everything else is secondary or
> exploratory, reported as **point estimates with confidence intervals, not p-values**,
> and labelled as such in every table.

No correction is claimed, because no inferential claim is made. The failure mode being
avoided is the one that makes correction necessary in the first place: running thirty
comparisons and reporting the ones that moved. Per-arm, per-check rates are
**descriptive statistics of a characterisation study** and are reported exhaustively —
all of them, whatever they show.

### 9.4 Minimum detectable effect — OPEN, gates the freeze

A directional prediction with no stated resolution is only half pre-registered: a null
is uninterpretable unless the smallest detectable effect is on record *before* the data
exist.

| quantity | value |
|---|---|
| design | paired, four ordered arms, same 110 images |
| *n* | 110, less parse failures (complete-case, §8.2) |
| α | .05, two-sided; power target 0.80 |
| MDE, primary trend test on `APPROPRIATE-RESPONSE` | **to be entered** |
| MDE, `OVERCOMMIT` at `SUFFICIENT` (P2) | **to be entered** |

*Simulated 2026-10-06 — candidate values, deliberately not yet entered as the
pre-registered ones:* ≈ 0.17 total `SURPLUS`→`INFEASIBLE` drop for the trend test,
stable across baseline rate and within-image correlation; the simulation was flat
across baseline rates 0.4–0.8 (0.16–0.18), so a base-rate shift barely moves it.

> **This figure predates the endpoint change and must be re-derived.** It was
> simulated against a monotone-decline alternative; P4 now predicts **flatness**,
> so the quantity needed is the smallest decline in `APPROPRIATE-RESPONSE` the
> design can rule out. Same machinery, different alternative — but the number on
> record has to be the one for the test actually being run.

For P2 the figure depends
entirely on the null: against a literal π = 0 the MDE is 0.015, but against a null of
π ≤ the extractor's false-positive rate it is ~0.07–0.11. **P2's form — test or
one-sided interval — therefore turns on whether the `OVERCOMMIT` extraction
false-positive rate can be bounded, not on n.**

---

## 10. Goodhart policy

Sequencing alone is not a defense; "measure first, improve later" only delays it.
Goodhart needs **two** conditions — a gap between the measure and the thing cared
about, and **selection pressure applied through that gap.** Removing either disarms
it. This section removes both.

### 10.1 Which interventions are permitted

| Class | Example | Selects on the metric? | Status |
|---|---|---|---|
| **Structural** — change the action space | constrained decoding so an out-of-ledger ID *cannot* be emitted; hard schema enforcement | no — the failure becomes unreachable | **permitted** |
| **Informational** — change the input | state the interlocks; add retrieval; richer assertions | no — one fixed change, then re-measured | **permitted, with §10.3** |
| **Selective** — pick outputs by score | best-of-N on validator verdict; reject-and-resample | **yes** | **banned** |
| **Parametric** — train on it | fine-tune or RL against validator reward | **yes, hardest** | **banned** |

The most likely real-world want — *fewer hallucinated assets* — is reachable entirely
from the structural row at zero Goodhart cost. The price is that a
structurally-prevented failure can no longer be **counted**. Hence the ordering:
measure it in Track M, eliminate it in Track E. That is a reason, not merely a sequence.

### 10.2 The firewall: closed-vocabulary checks may be improved against; V6 may not

Goodhart needs a *gap*. The closed-vocabulary checks were constructed not to have one:
*"the plan named `TUG-009`; `TUG-009` is not in the ledger"* is not a proxy standing in
for a failure — it **is** the failure. There is no latent quantity it approximates, so
nothing for it to drift from. V6 has an enormous gap; it is precisely P9's 46 %
artifact. **The closed/open split in §4 is the Goodhart firewall, and that is why the
split exists.**

**Stated limit, repeated in any write-up:** the check set is **sufficient under the
declared world, necessary for reality** (§3.6). `PLAN-SUCCEEDS` means *succeeds in
the declared world* — it attempts the right action and has the resources for it.
It does **not** mean *"good plan."* Sequencing wrong for the casualty, a hazard
absent from the ledger, a tow geometry a master would refuse — all pass. The name
makes that overclaim easier to make by accident, so the qualifier travels with the
number: **`PLAN-SUCCEEDS` is always written with the world named.** If it ever
appears unqualified, the trap has closed.

### 10.3 Held-out human read, never optimised against

The hand-check of 9 `Procedure` cases is the only reason P9's artifact was caught
rather than published. Institutionalised here.

*Protocol:* ~30–50 plans, randomized order, **verdict withheld**, simple rubric —
*would a competent salvage master accept this plan? yes / no / partial*, plus one line
of reasoning. Single rater (the author), plus a **re-rate of a subset after about a
week, blind to the first pass**, reported as intra-rater consistency. A single rater
cannot report inter-rater agreement; this is the available substitute and it yields a
real reportable number, which P9 lacked entirely.

*Why blind:* anchoring is strong. Seeing `INVALID — V3 violation` first makes a rater
find reasons it is invalid.

*Three jobs:* (1) validating the instrument — exactly how P9's artifact was caught;
(2) detecting Goodharting — **every** permitted intervention requires a blind re-read,
and if validator-validity rises while blind human judgement does not, the intervention
Goodharted; (3) the qualitative half of the study.

**The human sample is never used to tune the checker, the prompt, or the ledger. It is
read-only evidence.**

### 10.4 What is claimed

The deliverable is the measurement: *a resource-grounded planning benchmark, and a
characterisation of how planners behave as available resources fall below what the task
requires.* That claim stands alone and carries no Goodhart exposure. A later
*"intervention X raised validity by N points"* is the weaker claim, is where essentially
all the risk sits, and is not what this study is for.

**The scope of "planning" in that sentence, stated once here so it is not inferred:**
resource-grounded means §3.6 claim 1 — the plan attempts the right goal and violates
no resource constraint the declared world carries. It does **not** mean the plan is
complete, nor that it would succeed on an actual casualty (§3.6 claim 3). Both limits
belong in the abstract, not only in a limitations section: a reader who takes
`APPROPRIATE-RESPONSE` for operational adequacy has been misled by omission. §10.3's
blind read is the only evidence offered on plan quality, and it is a single rater
(§13 Q10).

---

## 11. Not in scope

- No validator-in-the-loop generation; no auto-repair of plans.
- No physics derivation by the model; no numeric adequacy engine (`physics.py`) in v1 —
  requirements are stated, not derived.
- No multi-casualty escalation dynamics — those belong to `salvage_simulation.md`'s full
  temporal sim, which this is not.
- **No Track E work of any kind.** Making plans *parse* is instrument conditioning and
  is in scope; making plans *better* is not.
- **No dynamic clock.** Every casualty type carries a deadline and the `OVERCOMMIT` trap
  depends on it, but time is a **static** pair (`eta_hours`, `deadline_h`) compared
  arithmetically at validation. Nothing ticks.

---

## 12. Discipline

The design already drifted inside this document once — the check set was written out in
four places and three disagreed before consolidation.

### 12.1 Single source of truth

| Concept | Canonical | Everywhere else |
|---|---|---|
| ontology, predicate families, add/remove contract | **§3** | reference only |
| assertion rules 1–3 + the line audit | **§2 / §6.1** | reference only |
| what all-pass certifies; the three claims | **§3.6** | reference by number; never restate what is and is not decided |
| world-complexity criterion | **§3.7** | reference only |
| the instrument controls and the minimal-pass probe | **§8.3** | reference only; §9.2 says where they print |
| check set, tiers, extraction loss | **§4** | reference by id only |
| the endpoint and its components | **§4.1** | reference by name only |
| what P9's 46 % actually was | **§1, finding 1** | a coverage defect; §3 draws the consequence, nothing else restates the cause |
| which assertion quantities are admissible | **§2 Rule 3** | the test; the on/off list it refers to is §3.1 |
| which world facts are scored in v1 | **§3.1** | never restate an on/off status elsewhere |
| behavioral flags, `REDUCE`, the §5.2 rates | **§5** | reference by name only |
| requirement tuple + per-casualty table | **§7.1** | reference only |
| ledger fields + arm multipliers | **§7.2** | reference only |
| `LEDGER-SATISFIABLE` + manipulation check | **§7.3** | reference only |
| predictions, analysis plan, MDE | **§9** | reference only |
| Track M / Track E boundary | **§1** | §12.4 holds preconditions only |

**A section that restates one of these is a defect, whatever it says.**

**In code: registries, not branches.** Each canonical table maps to one data structure —
`checks.json` (§4 registry; adding `V2c` is one row plus one predicate, never an executor
edit), `requirements.json` (§7.1), `flags.py` (§5, each flag a pure function of a scored
plan). The invariant worth protecting: **a derived quantity is computed, never
re-specified.** `HALLUCINATE` is `¬V1` in code as it is in §5, not a second
implementation of the same idea.

### 12.2 Freeze and change control

The §3 ontology, the §4 registry, the interlock set, the §5 flags, the §7 generator, and
the §9 predictions and analysis plan are **frozen before the first permitted
intervention is run.** Revising the instrument in response to improvement results is how
any outcome gets rationalised after the fact.

**Three gates. The freeze does not pass while any is open:**

1. **§9.4's MDE table is unfilled.** The form P2 takes depends on that number.
2. **The assertion file is untagged.** Every line must carry a
   **mechanism**/**realism**/**banned** tag and the banned ones must be gone (§6.1).
3. *(consequence)* **The freeze is what unlocks Track E.** Until Track M's per-arm rates
   are frozen, Track E has no baseline to be a delta against.

Operationally: every post-freeze change is appended to a changelog with **date, what,
why**, and whether it precedes or follows first generation. Superseded design text is
**marked superseded, never deleted** — decisions whose reasoning is lost get silently
re-litigated. Post-freeze changes to §4, §5 or §9 invalidate the pre-registration and
must be reported as such.

### 12.3 Named extensions, not latent scope

Deferred with their definitions already fixed, so adding one is mechanical rather than a
fresh design argument:

| Extension | Unblocks |
|---|---|
| `V2c` / `V2d` / `V3b` channels | weather, crew, budget failure modes |
| route vocabulary | promotes `DEGRADE` out of exploratory |
| scheduling family (F8) | would restore a real V2b; needs planner-emitted times |
| **asset durations** | the cheap half of a state layer — upgrades V2b from asserted concurrency to a real check by adding a field, not an architecture (§3) |
| **monotone progress chain** | the ordered-progress half — per casualty, a short never-unset sequence (`lightened` → `pull rigged` → `refloated`) scored by F5. Secondary only: one LLM presence read per link, and chain length differs by casualty type, so denominators differ (§4.1). **Enters only through §8.4's coverage gate** |
| assertion-block ablation | settles the §6.1 circularity objection with data — run `SUFFICIENT` with and without the block |
| second generator model | the external-validity gap (§13 Q2) |
| sampling variability | bounds the greedy-mode gap (§13 Q13) — k = 5 at temperature 0.7 on a subset, e.g. 20 images × `SUFFICIENT` + `INFEASIBLE`. Reports the spread a single greedy draw cannot show |
| E5 feedback loop | world observations, never verdicts |
| varying `Asset.status` | an availability failure channel; arrives as an F1 row |
| **Track E** | raising the rate at all — **withheld until Track M is frozen** |

**The goal-tree variant is designed, costed and rejected for v1 — see
`archive/casualty_tree.md`.** That file holds the per-casualty trees, the route-collapse
result (`aground` and `capsized` collapse to one inequality; `sunken` and `on_fire`
do not, because their root ORs reach terminals with different asset classes), the
≤ 8-asset generator invariant an exhaustive solver depends on, and a three-stage
entry path. The two rows above are its cheap first stage. **Read it before reopening
the terminal-node question** — §13 Q14 records the resolution, not the argument.

### 12.4 Track E — preconditions only

Not a Track E design. Three things that must be true when it opens, recorded here
because each constrains something Track M does *now*:

1. **Track M's result is the base plate.** All 110 images, no intervention aimed at the
   endpoint, per-arm rates frozen before Track E is designed.
2. **Track E declares its own dev/test split at its own start.** Tuning on all 110 and
   reporting on all 110 selects the intervention on the test set. The mechanism: carve a
   dev split stratified on `state` (42/33/19/16), tune **only** there, report improvement
   on the complement — compared against **Track M's rate recomputed on that same
   complement**, available without rerunning anything because Track M covered all 110.
   Split size is a Track E decision informed by §9.4's MDE.
3. **The improvement target is arm-conditional.** "Maximise `PLAN-SUCCEEDS`" is wrong,
   because at `INFEASIBLE` the rate *should* be low.
   > **Track E objective: maximise `PLAN-SUCCEEDS` on `LEDGER-SATISFIABLE` ledgers, and
   > maximise correct refusal on the rest.**

   A plan that overcommits on an unsatisfiable ledger scores zero on both terms, so the
   objective cannot be met by the exact failure this study exists to detect.

Permitted interventions remain §10.1's Structural and Informational classes in both
tracks; Selective and Parametric stay banned in both.

---

## 13. Decision log

Resolutions only. The reasoning behind each is in `archive/plan.v05.full.md` §10.

| | Question | Resolution |
|---|---|---|
| **Q1** | Output format | Prose, numbered steps, assets by ledger ID. No JSON |
| **Q2** | Which model | **Qwen3-VL-8B only.** Record in any write-up: not directly comparable to the DeGF/ONLY line, which runs LLaVA-1.5-7B. Generalisation across planners is the acknowledged gap |
| **Q3** | Ledger construction | Procedural for all 110, plus ~10 hand-authored independently as a plausibility check |
| **Q4** | Ledger fields | Minimum set in v1; channels staged in after the minimum run is complete. Deferred channels have violation conditions **fixed now** though not built |
| **Q5** | Requirement provenance | *Superseded.* Citation is not the gate; the three gates in §7.1 are. Provenance is recorded documentation |
| **Q6a** | Which assertion file | `IMPROVED_VISUAL_GROUNDED_NEUTRAL_ASSERTIONS.txt` — drops the per-step image-citation line, correct under grounded resources |
| **Q6b** | Does it state mechanisms | Yes — four lines, one per scored channel (§6.1) |
| **Q6c** | Does it state the interlocks | **2 of 4 stated.** V4 is reported split: `V4a` tests whether the model *applies* a given fact, `V4b` whether it *knows* an unstated one. Averaging them is uninterpretable. Caveat: interlocks 1–2 are space-entry rules, reachable only in some casualty types, so **V4b denominators must be reported**; where small, descriptive not inferential |
| **Q7** | Is `SURPLUS` worth running | **Yes — it is the positive control.** If the planner cannot produce a valid plan when resources are abundant and enumerated, no lower arm is interpretable |
| **Q8** | Sample size and structure | 110 × 4 = 440, no replicates. **Within-image paired**, not four independent groups. Stated limitation: n = 110 paired resolves ~15–20 pp comfortably; it will **not** resolve 5–10 pp |
| **Q9** | Repo packaging | **OPEN** — standalone or submodule under BenchyBench. Affects packaging only; until decided this directory is self-contained |
| **Q10** | The blind human read | Single rater plus a re-rate pass (§10.3) |
| **Q11** | Asset-grounding instruction | Two instructions were conflated. **A** *"refer to each asset by its ledger ID"* is **format** — included. **B** *"do not invent assets not in the ledger"* is **honesty** — omitted, because it suppresses the `HALLUCINATE` baseline. A model told how to *name* assets can still fabricate `TUG-009`, so A costs nothing in measurement |
| **Q12** | Differential parse rate | Resolved by **removing the decision point**, not setting a threshold: complete-case primary analysis (§8.2) |
| **Q13** | Decoding | **Greedy (`temperature: 0.0`), one generation per cell.** The reason is k = 1: with no replicates, a sampled plan is a single lottery draw and a failure cannot be separated from bad luck, while greedy returns the model's most-likely plan — a well-defined object. **Two caveats, both stated rather than fixed.** (i) *Greedy is not bitwise deterministic* — batching, kernel nondeterminism and argmax tie-breaking all vary; record seed, batch configuration and the full inference config, and do not claim determinism as a property of temperature. (ii) *The result is about the greedy mode, not the model's output distribution* — deployed systems run at 0.6–1.0, so the rate is scoped the same way Q2 scopes it to one model. Bounding that gap is a named extension (§12.3); the degeneration check it requires is in §6.4 |
| **Q14** | Does the validator *check* a plan or *solve* the problem? | **Checks.** The alternative — per-casualty goal trees, a terminal node at delivery, and a validator that solves for the best achievable outcome — is designed and costed in `archive/casualty_tree.md` and rejected for v1 on three grounds. (i) It answers a different question: *how close to optimal* rather than *does scarcity change behaviour*. (ii) §8.4's coverage gate **inverts** under a solver — every gold plan must now be *solvable*, so an incomplete solver marks correct plans wrong, promoting a coverage defect from measurement error to ground-truth error. (iii) Decisive: a solver can make a dead manipulation look like a result, because a terminal-node rate still moves when the arms do nothing; the check-only endpoint cannot hide that. **Accepted cost, stated in §10.4:** v1 does not establish that a plan reaches the end goal, only that it is resource-sound and attempts the right one (§3.6 claim 1). Entry path is staged in §12.3 |
