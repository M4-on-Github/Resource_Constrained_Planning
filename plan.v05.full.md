# Resource-Constrained Planning (RCP)

Design plan — v0.5, 2026-10-05. **Design only. No code is to be written until
the go-ahead is given.** The design is closed (§10: eleven of twelve items
resolved; Q9 is packaging, not design). §13 is pre-registered and §14 governs
changes to it. Domain knowledge is **part of the declared world**, so the
assertion block is re-derived and line-audited, not inherited (§3.2). **Only Track M is authorised; Track E is withheld until Track M
is frozen (§1, §14.5).** One open item remains: §13.4's MDE table, which gates
the freeze.

---

## 1. What this is

A VLM is given a maritime casualty, a loose user spec ("write a salvage
plan"), real domain knowledge, and **a specific, named, grounded resource
ledger** — *tug `TUG-002`, 55 t bollard pull, Pier 3, on scene*. It writes a
one-shot plan. A validator then replays that plan against the same ledger and
reports **what the planner did**, not whether it earned a passing grade.

Then the ledger is varied — surplus, sufficient, scarce, infeasible — and we
observe how planner behavior changes.

### The claim this is built to support

> Given good domain information and a specific, grounded asset ledger, a
> planner produces plans that are resource-valid at rate *X*. As available
> resources fall below what the task requires, that rate and the planner's
> failure profile change in a direction fixed in advance.

*"Shifts in a measurable way" was the earlier wording and admits every possible
outcome, so nothing could refute it.* The directional commitments that make it
falsifiable are **pre-registered in §13**; the estimand is `RESOURCE-VALID`
(§5.1).

### Headline variable

**Resource sufficiency level.** One independent variable. Everything else
(prompt variant, knowledge arm, model) is recorded and reported, but demoted.

The **user spec is a constant**, not a variable — one fixed loose instruction
("write a salvage plan for this casualty"), identical across every arm. The
user in this setup is the *reader* of the plan, not a party whose request
varies. This is deliberate: a varying user request would be a second
independent variable competing with resource sufficiency for the headline.

### Study type — two tracks, only one of which is authorised

This is a **measurement study**, not an engineering effort. The deliverable is
a characterisation of planner behavior under resource scarcity, not a validity
rate pushed as high as it will go. See §12 for why that distinction is load-
bearing and what it permits later.

That is the honest framing, and it sits in tension with a legitimate want —
this is engineering-flavored research, and a higher validity rate is worth
having. The tension is a **sequencing** problem, not a contradiction, and it is
resolved by naming two tracks and authorising exactly one of them:

| | Track M — measurement | Track E — engineering |
|---|---|---|
| goal | characterise behavior | raise `RESOURCE-VALID` |
| output | the pre-registered §13 result | an improved system |
| endpoint | frozen composition (§4.6, §11.4) | same endpoint, re-measured |
| interventions | none aimed at the rate | Structural + Informational only (§11.1) |
| **status** | **authorised — this plan** | **deferred; see below** |

> **Track E is not planned and not executed until Track M is complete.**
> No Track E design work, no prompt search, no tuning — not even
> provisionally, and not in parallel.

The reason is the base plate. Track E's entire value is a *comparison against
an untouched baseline*, and that baseline does not exist until Track M has run
and been frozen. Designing Track E first would also put the dev/test split,
the intervention list, and the improvement target into this document, where
they would start influencing Track M's choices long before any data exists —
which is precisely the selection pressure §11 is built to prevent. Track E's
preconditions are recorded in §14.5 so that the deferral costs nothing later;
nothing beyond those preconditions is specified here.

**One distinction this makes necessary.** Making the plans *parse* is not
Track E work. Getting a model to emit a numbered list of steps is **instrument
conditioning** — it makes the measuring device function — and §8.1 makes it a
precondition on Track M rather than a result. Making the plans *better* is
Track E. The dividing line: instrument conditioning is tuned off-corpus and
never on the 110 (§7), so it cannot select on the endpoint; Track E
interventions move the endpoint by construction, which is why they wait.

---

## 2. Why this exists — what P9 established

This is a direct successor to `Eval_CASTOR/pipelines/plan_adequacy/` (P9).
Three findings from that study are load-bearing here:

1. **P9's biggest number was an instrument artifact.** 46 % of plans were
   marked unexecutable under `Procedure`; on hand-check, **0 of 9** were the
   model's fault. The cause was P9's own 47-action registry not recognising
   legitimate steps ("set up a safety perimeter"). See `reports/p9/p9_recap.tex`.
2. **P9 had no positive control.** `goal_reached = 0/330` with zero variance.
   Nothing that *should* pass was ever run through it, so the result was
   equally consistent with "planners are bad" and "the criterion is
   unpassable." See `reports/p9/redesign.tex` §1.
3. **Extraction loss was an unquantified confound.** Per-step tool extraction
   accuracy was 0.833, sitting underneath every number in the study.

RCP is designed so that all three are structurally impossible, not merely
watched for. See §5 and §7.

### The mentor critique, and how it binds this design

On record in `reports/p9/p9_future_directions.txt`:

> "Using the pipeline to fact-check itself is like using the oracle to solve
> the problem without solving the problem."

Resolution adopted here: **the validator tells us WHERE TO LOOK, never WHAT IS
CORRECT.** Concretely, in this project that means:

- The validator never runs during generation. Phase 1 is strictly one-shot.
- The validator never repairs, filters, vetoes, or re-ranks a plan.
- No model is ever optimised or selected against validator output.
- When a feedback loop is eventually built (E5, §8), it returns **world
  observations** ("the line parted"; "`TUG-004` is 6 h out"), never **validator
  verdicts** ("you violated precondition X"). This is `salvage_simulation.md`
  §13 R2 — already written, never implemented.

---

## 3. The non-circularity contract

The thing that must not be circular is not "the model and the validator know
the same facts" — an exam and its answer key reference the same world. It is
**the model being told the grading rule**.

| Artifact | Model sees it | Validator uses it | Rationale |
|---|---|---|---|
| Resource ledger (what exists, where, capacity, ETA) | **yes** | **yes** | Shared ground truth. The experiment is meaningless otherwise. |
| Casualty state (E1/E2 only) | **yes** | yes | Held constant to isolate planning from perception. |
| Stated requirement ("≥120 t bollard pull") | **yes** | yes | A scenario fact, as a naval architect's figure would be. Not a grading rule. |
| Domain knowledge / safety assertions | **yes** | — | **Part of M, re-derived under §4 — not inherited.** The P7/P9 files are a source to audit, not a carry-over: §3.2. |
| **Precondition graph (what must precede what)** | **no** | yes | This is the grading rule. |
| **Hard interlocks** | **2 of 4 — stated** | yes | Resolved §Q6c: the 2 stated feed `V4a` (application), the 2 unstated feed `V4b` (latent knowledge). |
| **Verdict vocabulary / checking procedure** | **no** | yes | This is the grading rule. |
| **Validator source, or examples of graded output** | **no** | yes | Never shown, never in a prompt. |

### 3.1 The assertion block: mechanism, never binding

The existing assertion files (`all_maritime_prompts/assertions_planning/`)
cover maritime *domain* concepts and say nothing about resource logistics, so
an RCP-specific block is needed — ETAs, capability ratings, availability
semantics.

**This is a re-derivation, not an addition.** The block is written against
§4.2's entities and every line of the shipped file is audited against them
(§3.2). Treating the existing files as inherited content would import a world
richer than the one the validator certifies, which §3.2 shows is already the
case. There are two lines in the block that must not be crossed — Rules 1 and
2 below — and a third, in §3.2, that follows from §4.

| | Example | Status |
|---|---|---|
| **Factual** | "Bollard pull is rated in tonnes." / "An asset with a stated ETA is not on scene before that time." | **allowed** |
| **Normative** | "If available pull is insufficient, request additional assets rather than proceeding." | **banned** |

The normative example **scripts the `ESCALATE` behavior that §6 exists to
measure.** Writing it into the prompt converts the scarcity arms from a
measurement of planning into a measurement of instruction-following.

**Rule 1: assertions may state facts about resources. They may never state
what to do when resources fall short.**

#### The sharper criterion — mechanism yes, binding never

Rule 1 alone is too blunt, and applying it to resource logistics shows why.
Each mechanism the planner needs has a normative twin that is simply one of the
validator's checks:

| | mechanism form (needed) | normative twin (banned) |
|---|---|---|
| composition | "pull from multiple tugs made fast to one casualty is approximately additive" | *"ensure total committed pull ≥ requirement"* = **V3** |
| exclusivity | "an asset engaged in a task is committed for its duration" | *"do not assign one asset to overlapping steps"* = **V2b** |
| ETA | "ETA is time until on scene and ready" | *"verify no step uses an asset before its ETA"* = **V2a** |

A naive reconstruction test ("could a reader derive the check from this?")
rejects the left column too, since mechanism plus the scenario's stated
requirement yields V3. That test is wrong, because it mistakes V3 for a hidden
grading rule. **V3 is not a rule, it is the task.** §3 puts the requirement in
front of the model deliberately; a planner that does not know it should meet
the stated requirement is failing to guess the objective, not failing at
resource grounding — a different and far less interesting finding.

What must stay hidden is narrower:

> **Rule 2: nothing may indicate which constraint binds in a given scenario.**

This is what the §9 trap depends on. `TUG-002 + TUG-005 + TUG-011` **sum** to
144 t against a 120 t requirement, so a model checking only totals passes; it
fails because `TUG-011` arrives two hours after high water, leaving 95 t
assemblable. `OVERCOMMIT` *is* satisfying the sum while missing the clock.
State what ETA means and the trap survives. State *"check that your assets
arrive before the deadline"* and the trap is destroyed.

#### The resulting v1 block — one mechanism per scored channel

| v1 channel | mechanism stated | never stated |
|---|---|---|
| `V3` | same-class capacities combine additively | which total is reachable |
| `V2b` *(secondary)* | an asset does one task at a time | where the plan double-books |
| `V2a` | ETA = time until on scene and ready | that time is the binding constraint |

```
Where several assets of the same class work a task together, their rated
capacities combine approximately additively.

An asset engaged in a task is committed for that task's duration and is not
simultaneously available for another.

The ETA listed for an asset is the time from now until it is on scene and
ready to work.

Assets not listed in the ledger are not available.
```

The `V2b` row stays in the block even though §4.4 demoted the check to a
secondary: the mechanism is what makes an *asserted* concurrency claim
interpretable, and withholding it would make that secondary a trick question.

Line 4 is factual about the **world** (no other assets exist), not an
instruction about the **output**, which keeps it distinct from Instruction B —
the honesty directive §Q11 rejects for suppressing `HALLUCINATE`. Line 3 sits
closest to Rule 2 and is the one to watch.

#### The circularity objection, and how to settle it empirically

A reader may object that the block mirrors the channel registry. The argument
in reply: mirroring the **mechanism** is mandatory, since scoring a channel the
model cannot reason about is a trick question rather than a measurement, while
mirroring the **threshold or the binding** would be circular.

That is an argument, and it is cheap to replace with a measurement: run
`SUFFICIENT` with and without the block. If the mechanism statements were doing
the grading work, the primary channels V2a/V3 collapse toward zero. *Prediction: they
will not*, because the trap concerns which constraint binds, not whether pull
adds. Per §Q4's staging rule this is an extension, not v1 — but it is the clean
way to settle the point.

**Requirement provenance.** *Superseded by §Q5 and §9.1* — citation is no
longer the admission gate. Provenance is still recorded per requirement as
documentation, and the authored count is still printed as a stated limitation.

### 3.2 Rule 3 — the assertion block is part of M, so it is re-derived, not inherited

§4.7 makes the declared world the thing the validator certifies against. The
domain knowledge handed to the planner is **inside that world**, not an
external input condition, so it cannot be carried over from P7/P9 unexamined.
The existing files are a **source to audit**, not an inheritance.

**The mismatch is real, and specific.** Checked against §4.2's entities, the
existing assertions invoke concepts the declared world cannot express:

| assertion line | concept | in §4.2? |
|---|---|---|
| *"the vessel's size and draft may scale the resources needed"* | draft | **no** |
| *"any cargo or hazardous material present may be reason for added caution"* | cargo | **no** |
| *"the emergency fire pump's capacity may need confirming before committing a team"* | knowledge-gating | **no** — §4.1 removed the `_known`/`_true` split |
| *"coordination may involve the vessel owner, local or flag authorities"* | — | not expressible at all |

Not all of that is a problem, and the distinction is exactly §4.6's. Realism
the world cannot express is **permitted** — it costs the endpoint nothing and
makes the task read like the job. What is not permitted is an assertion that
implies an **obligation** no check can score: *"confirm pump capacity before
committing a team"* tells the planner to do something invisible to the
validator, so a plan that does it gains nothing, a plan that skips it loses
nothing, and both spent output budget on it. That is §4.8's *too complex* edge
arriving through the prompt instead of through the ontology — the same
output-budget argument that selected `IMPROVED` in §10 Q6(a).

> **Rule 3: an assertion may describe anything the world can express, and may
> add realism it cannot — but it may never imply an obligation the validator
> cannot score.**

#### The audit — a required pre-freeze pass

Every line of the shipped assertion file is tagged, and the tagged file is a
versioned artifact alongside the check registry:

| tag | criterion | status |
|---|---|---|
| **mechanism** | states how a *scored* channel works (§3.1's table) | **required** — one per scored channel, no more |
| **realism** | describes the world truthfully; implies no obligation | **permitted**, unlimited, scored by nothing |
| **banned** | implies an obligation M cannot score (Rule 3), or crosses Rule 1 or Rule 2 | **removed before the freeze** |

Mechanism lines are bounded by the scored channels, which is what keeps §3.1
from growing into a tutorial. Realism lines are not bounded, because they carry
no measurement consequence — but a realism line that a reader could mistake for
an instruction is a banned line wearing realism's tag, and the audit is where
that gets caught.

**Why this matters beyond tidiness.** An unaudited assertion file quietly
determines what the planner spends its output on. If it directs attention at
draft, cargo and inter-agency coordination while the endpoint scores bollard
pull against a deadline, a low `RESOURCE-VALID` is partly an artifact of the
prompt pointing elsewhere — which is the P9 error class (an instrument
artifact reported as a finding) relocated from the validator to the input.

---

## 4. The world model

Everything §5 checks is a predicate over the objects defined here. This section
is canonical for the ontology (§14.1).

### 4.1 What kind of world this is — allocation, not simulation

> **The world is a resource-allocation constraint system, not a state machine.**

P9 used a state-transition executor: seven passes, a 47-action registry,
preconditions and effects, and a `_known` / `_true` split over world facts.
**That architecture is what produced the 46 % artifact.** A state machine must
know what every action *does*, which forces an open action vocabulary, which is
where the artifact came from.

The primary endpoint here needs none of it. It needs to know which assets a
plan commits and whether those commitments satisfy constraints. **Nothing in
the primary requires running the world forward.** There are no effects, no
precondition firing, and no knowledge/truth split outside V6, where P9's
machinery is deliberately quarantined.

### 4.2 Entities

```
Scenario
  id, casualty_state, vessel{type, size_category}, t0
  requirement : Requirement
  conditions  : {name -> value}          # sea_state, visibility, ... extensible; may be empty

Requirement                               # see 9.1
  goal, quantity, unit, asset_class, deadline_h, deadline_driver

Asset
  id, asset_class, capability{quantity, unit}, location, eta_hours
  status                                  # INFORMATIONAL in v1 - scored by nothing (4.6)
  limits : {condition_name -> threshold}  # extensible; may be empty
  attrs  : {name -> value}                # cost, crew, ... extensible; may be empty

Ledger = set[Asset]                       # closed, enumerated, per scenario

Plan                                      # what the validator reconstructs from prose
  steps : ordered list[Step]
Step
  index, text
  committed      : set[asset_id]          # string match against a closed list
  is_goal_action : bool                   # V5; one target per casualty type
```

**What is deliberately absent:** durations, per-step start times, world-state
facts, action types. §4.4 states what each absence costs.

The planner sees `Scenario`, `Requirement`, `Ledger` and `conditions`, rendered
as in §9's worked example. **In v1 `conditions`, `limits` and `attrs` are all
empty**, so the rendering collapses to the worked example's six columns; the
maps exist in the ontology so that §4.6 additions are data, not schema
changes. It never sees `Plan` — that is the validator's
reconstruction of its prose. The full contract is §3; it is not restated here.

### 4.3 How a plan is evaluated

Three stages, in order, with nothing fed back to the planner:

```
prose --> RECONSTRUCT --> Plan --> EVALUATE --> per-check results --> DERIVE
          string match            predicate families (4.5)           flags (6)
          + 2 LLM fields                                             + endpoint (5.1)
```

`RECONSTRUCT` is the only lossy stage, and only for its two LLM fields
(`is_goal_action`, and the secondary concurrency read). `committed` is string
matching against a closed list. `EVALUATE` and `DERIVE` are deterministic
functions of `Plan` and `Scenario` — **given the same reconstruction, two
implementations must agree exactly**, which is what makes the primary endpoint
reproducible rather than merely stable.

### 4.4 No clock, no durations — and the one check the world cannot express

*Read this with §4.7:* what follows is not a gap in coverage. A world with no
duration field cannot state the proposition "this asset is double-booked" at
all, so declining to score it is what sufficiency-under-M **requires** — a
checker that answered anyway would be guessing, and a guess inside a
conjunction contaminates every other check in it.

The plan is prose: it supplies step **order**, never step **times**. Deriving
times requires durations; durations require knowing what each step *does*;
that is the open action vocabulary — the P9 trap. Supplying durations in the
ledger does not rescue it either: read the steps **sequentially** and no two
overlap, so the check is vacuous; read them as **possibly parallel** and
overlap is undefined.

> **Therefore double-booking (V2b) is not decidable from prose + ledger.**

This was caught while modelling, not after implementing. V2b had been inside
the primary endpoint since §5.1 was written, because `(derived) | overlapping
use` *reads* like arithmetic — but its derivation needs information this design
deliberately refuses to collect.

**Consequences, propagated:**

1. **Primary endpoint becomes `V1 and V2a and V3`** (§5.1). Three checks, all
   genuinely timing-free.
2. **V2a is restated without a clock:** *every asset committed at or before the
   goal step has `eta_hours <= deadline_h`.* Steps before the goal necessarily
   precede the deadline, so no schedule is needed.
3. **V2b becomes secondary** — an *asserted*-concurrency conflict, detectable
   only where the plan itself claims simultaneity ("while `TUG-002` holds the
   stern..."). LLM-read, so it carries extraction loss and cannot sit in the
   primary.
4. **`OVERCOMMIT` simplifies** to `(not V2a or not V3) and not ESCALATE` —
   still ~0 loss.

A real scheduling model is a named extension (§14.4), and it requires the
planner to emit times, which Q1 rejected for good reasons.

### 4.5 Predicate families — the extensibility mechanism

Checks are not bespoke. Each belongs to a **family**, and a family ranges over
*all* attributes of its kind, so most additions require no new logic at all.

| | Family | Form | Checks | Cost to extend |
|---|---|---|---|---|
| **F1** | Membership | `name in ledger` | V1 | — |
| **F2** | Aggregate-threshold | `sum(attr over committed) vs scenario scalar` | V3, V3b (budget), V2d (crew) | **one registry row** |
| **F3** | Per-asset reachability | `asset.scalar vs scenario scalar` | V2a | one row |
| **F4** | Condition-limit | `asset.limits[c] >= scenario.conditions[c]` for all c | V2c (weather); visibility, ice, current | **zero logic** |
| **F5** | Forbidden pattern over sequence | ordering / co-occurrence | V4a, V4b | one row |
| **F6** | Presence | goal action attempted | V5 | one row |
| **F7** | Open precondition graph | P9 machinery | V6 | **quarantined, never extended** |

**Why this answers "add or remove weather cleanly."** Weather is one entry in
`Scenario.conditions` plus one entry in `Asset.limits` on affected assets. **F4
already quantifies over every condition/limit pair**, so no predicate is
written and no code path is added. Visibility, ice and tidal current come free
by the same route. Budget or crew is a single F2 row. Removal is symmetric:
delete the column and the registry row; nothing else references it.

Note that V2b fits **no** family — it would need a scheduling family (F8) that
§4.4 shows is not constructible from prose. The taxonomy earning its keep by
rejecting a check is the point.

### 4.6 The add / remove contract

To add attribute **X**:

1. Place it — `Scenario.conditions`, `Asset.limits`, or `Asset.attrs`.
2. Declare its family, **or `none`**: an attribute may be purely informational,
   visible to the planner and scored by nothing. **`none` is the safe default**
   — it enriches realism at zero cost to the endpoint.
3. If scored, add one row to the §5 registry with `v1` / `deferred` status.
4. Decide planner visibility: rendered in the ledger, or validator-only.
5. Re-run the generator invariants (§9.1).

> **Invariant A — nothing scored off-family.** No attribute may be scored by a
> predicate outside the families. A bespoke check is a design smell and a
> §14.3 change-control event.
>
> **Invariant B — nothing left undeclared.** Every attribute in §4.2 must be
> *either* scored by a check in §5 *or* declared informational. An attribute
> that is neither **falsifies sufficiency-under-M** (§4.7), because it names a
> fact the world can express and the validator cannot see.

Invariant B is the auditable half of the §4.7 claim, and applying it caught a
live case:

> **`Asset.status` is declared informational for v1.** It is in the ontology and
> no check in §5 can fail on it; in v1 every generated asset is `available`, so
> the field never varies and scoring it would be dead code. It is rendered to
> the planner as realism and scored by nothing. Making status vary — an asset
> listed as committed elsewhere or under repair — is a named extension, and it
> would arrive as an F1-family row, not as a new predicate.

**The scientific constraint on extension, which matters more than the
engineering one.** Adding a *scored* attribute adds a failure channel, which
mechanically lowers `RESOURCE-VALID` — a v2 validity rate would not be
comparable to v1's, and the drop would be an artifact of the instrument rather
than a fact about planners. Therefore:

> **The primary endpoint's composition is frozen (§11.4). New channels are
> reported as separate secondary rates and are never folded into
> `RESOURCE-VALID`.**

This is why `none` is the default, and why §10 Q4 stages fields in rather than
shipping them all together.

### 4.7 What the validator certifies — sufficiency under M, necessity for reality

> **RCP is a sufficiency checker for the world it declares, and a
> necessary-conditions checker for the world.**

Both halves are load-bearing. Inside the declared ontology of §4.2 — assets,
capability, ETA, requirement, deadline, goal action — *"no check failed"* is a
genuine **sufficiency** statement: there is no way, expressible in this world,
for the plan to be resource-invalid. Outside it the same result is
**necessary-only**, and the distance between the two is the M-to-reality gap,
which is argued by inspecting M rather than by inspecting plans. That
relocation is the point: *"is this plan sound?"* is unanswerable about prose,
while *"is this model complete?"* is a question about a document anyone can
read.

#### The logic, and the caveat it carries

Necessary conditions are **existential**: exhibit one violation and the
question is settled. That is why they are cheap, and why a single
counterexample is decisive. Sufficiency is **universal**: *no* violation
exists, quantified over the whole failure space.

- Over an **open** failure space, that is not a hard computation — it is an
  **undischargeable proof obligation**. No amount of compute closes it, because
  the set being quantified over is not enumerable. Real salvage fails in ways
  nobody wrote down.
- Over a **closed, declared** failure space it collapses to a finite
  conjunction — which is precisely the §5 check registry.

> **The caveat: sufficiency is bought entirely by closing the world, and the
> price is that the claim travels exactly as far as the declaration does and no
> further.** Any sentence of the form "this plan is adequate" must therefore
> name M, or it is overclaiming. §11.5 is worded accordingly.

This is also why *"is sufficiency NP-hard?"* is the wrong question. At RCP's
scale nothing here is computationally hard — checking a plan is linear,
`LEDGER-SATISFIABLE` is 64 subsets, and even a scheduling extension (F8) is a
solver call on ten steps. The barrier was never complexity. It is that
exhaustiveness is a **specification** property, not a running-time one.

#### Why V2b reads better under this framing

§4.4 demotes V2b because durations are not in the ontology. Stated as coverage,
that sounds like a hole. Stated correctly, it is not: with no duration field,
*"is `TUG-002` double-booked?"* is not a proposition this world can express at
all — it is ill-typed, not false. **The model is declining to make a claim it
has no vocabulary for, which is the behavior sufficiency-under-M requires.** A
checker that answered anyway would be guessing, and a guess inside a
sufficiency claim contaminates every other check in the conjunction.

The asserted-concurrency secondary (§6) is then an explicit, labelled reach
*past* the model's edge — which is exactly why it is LLM-read, secondary, and
excluded from the primary.

#### The claim is auditable, which is the real gain

Because M is declared, sufficiency-under-M is not a slogan — it is a property
that can be **checked field by field**: every attribute in §4.2 must either be
scored by some check in §5, or be declared informational. §4.6 carries that
invariant, and applying it is what caught `Asset.status`.

### 4.8 How complex the world should be — the discriminability criterion

The ontology's size is itself a design variable, and it has a window rather
than a direction:

> **The world must be simple enough that a competent planner can be exactly
> right, and rich enough that a confabulating one is exactly wrong.**

Both edges degrade the measurement, in opposite ways:

| | failure mode | what you end up measuring |
|---|---|---|
| **too trivial** | the checks are passable by pattern-matching — "name three items from this list" | a ceiling effect; all-pass is cheap, so the measure stops tracking planning at all |
| **too complex** | too many interacting constraints to hold at once | hallucination propensity rather than planning; output becomes noise and the instrument reads its own confusion |

The plan already makes this trade in several places; naming the criterion is
what makes those choices consistent rather than incidental:

- the ledger **pre-aggregates** (§7), so the model faces one comparison
  instead of arithmetic
- assets are a **closed, enumerated list** (§4.2)
- **no physics derivation** by the model (§12)
- §9.1's refusal of a second scalar states the right-hand column almost
  outright — *"a second scalar turns V3 from one comparison into a
  constraint-satisfaction problem and would confound the headline before its
  baseline exists."*

**This criterion is what §4.6 appeals to when it refuses an extension.**
Without it, "not in v1" is a scheduling preference; with it, there is a stated
reason that an addition can be argued against on the merits.

#### The window is verified by two controls, not asserted

The criterion would be unfalsifiable rhetoric if nothing tested it. The two
§7 controls are what close it, one per edge:

| control | fails if the world is | what it establishes |
|---|---|---|
| **positive** — a hand-written correct plan must pass | **too complex** (or the checks are unpassable) | a competent planner *can* be exactly right |
| **negative** — a fluent, resource-blind plan must fail | **too trivial** | a confabulating planner *cannot* pass |

Neither control alone establishes discrimination. P9 ran with neither, which is
why `0/330` was consistent with both "planners are bad" and "the criterion is
unpassable" (§2).

---

## 5. The check registry — canonical

**This table is the single source of truth for the check set.** §6, §7, §9 and
§11 *reference* it and must not restate it. Any change is made here and nowhere
else; see §14 for why that rule exists.

| id | check | vocab | instrument | extraction loss | v1 | **primary** |
|---|---|---|---|---|---|---|
| `V1` | every asset named exists in the ledger (F1) | closed | string match | ~0 | ✓ | **✓** |
| `V2a` | every asset committed at or before the goal step has `eta_hours ≤ deadline_h` (F3) | closed | string match + arithmetic | ~0 | ✓ | **✓** |
| `V2b` | no *asserted*-concurrency conflict (§4.4) | closed | **LLM** — plan must claim simultaneity | small, measured | ✓ | secondary |
| `V3` | committed capability ≥ stated requirement (F2) | closed | computed from matched IDs | 0 | ✓ | **✓** |
| `V4a` | no *stated* interlock violated (hot work, CO₂) | closed, 2 rules | LLM, 2 targets | small, measured | ✓ | secondary |
| `V4b` | no *unstated* interlock violated (PPE, pressure eq.) | closed, 2 rules | LLM, 2 targets | small, measured | ✓ | secondary |
| `V5` | plan attempts the terminal goal action (§5.2) | closed, 1 per casualty | LLM, 1 target | small, measured | ✓ | secondary |
| `V6` | full precondition compliance | **open** | P9 machinery | **P9-grade** | ✓ | **never** |
| `V2c` | not used beyond `weather_limit` | closed | — | — | deferred | — |
| `V2d` | crew pool not exceeded | closed | — | — | deferred | — |
| `V3b` | committed cost ≤ stated budget | closed | — | — | deferred | — |

### 5.1 The primary endpoint — one, designated in advance

Earlier drafts designated two: §5 said "V1–V5 is the operational definition of
valid", §7 said "V1–V3 — the headline". **Plural primary endpoints are a
researcher degree of freedom** — whichever moves can be named the headline
afterwards. Resolved by designating one, before any data exists:

> **Primary endpoint: `RESOURCE-VALID` = V1 ∧ V2a ∧ V3.**
> Binary, per plan.

All three are symbolic with ~0 extraction loss, and all three are *about
resource grounding* — the construct the study names. Nothing else enters the
primary.

**V2b was removed from the primary during the §4 modelling pass.** It is not
decidable from prose plus ledger: detecting overlap needs a schedule, a
schedule needs durations, and durations need action semantics — the open
vocabulary this design exists to avoid. Full reasoning in §4.4. It survives as
a secondary check over concurrency the plan *itself asserts*, which is
LLM-read and therefore disqualified from a ~0-loss primary.

**Secondary, pre-specified, always reported:** V2b, V4a, V4b, V5, and the §6
flags.
These carry measured extraction loss, so they inform but never define the
headline. **Exploratory:** V6, reported with its limitation printed adjacent —
it is the direct descendant of P9's 46 % artifact and is never a verdict.

**Why V4/V5 are out of the primary.** Not because safety or goal-reaching
matter less, but because they require LLM extraction and the primary was
constructed specifically to have none. Mixing a ~0-loss check with a lossy one
puts the loss back into the headline, which is the exact confound §2 finding 3
exists to prevent.

### 5.2 V5, redefined so that it can fail without being unpassable

The earlier V5 ("plan reaches the casualty's terminal goal") does not pass
**§Q5 gate 1**, the gate written citing P9's `goal_reached` as the cautionary
case — an oversight, since V5 was never run through it. Read strictly it *is*
`goal_reached`: P9 scored `0/330` with zero variance and plans completing <1 of
6 steps. Read loosely it collapses into V3.

Redefined:

> **V5 — the plan contains a step that attempts the casualty's terminal goal
> action** (refloat / lift / right / extinguish, per §9.1).

This is presence of one action, from a **one-item** per-casualty vocabulary —
not P9's 47-way classification, and not P9's seven-pass precondition chain. It
is falsifiable in both directions, since P9 established that plans frequently
never reach the goal action at all, and it is non-redundant with V3, which
scores capability irrespective of whether the goal is ever attempted.

---

## 6. The behavioral taxonomy — independent flags, not classes

Earlier drafts called these "exactly four options", each "symbolically
countable from the structured output". Both were wrong: Q1 removed the
structured output, and the four are **not mutually exclusive** — a plan can
hallucinate an asset *and* escalate, or degrade *and* overcommit on the
degraded route. Scoring them as classes would force an unstated precedence
order (P9 used one) and discard the co-occurrences, which are the interesting
cases.

**They are therefore independent binary flags, each with its own denominator.**
Co-occurrence is reported as a matrix, not collapsed.

| flag | definition | derivation | extraction | tier |
|---|---|---|---|---|
| `HALLUCINATE` | names an asset ID absent from the ledger | `¬V1` | **string match, ~0 loss** | **primary-adjacent** |
| `OVERCOMMIT` | commits below the requirement without saying so — **decomposed by `REDUCE`, §6.3** | `(¬V2a ∨ ¬V3) ∧ ¬ESCALATE` | **derived, ~0 loss** | **primary-adjacent** |
| `ESCALATE` | states insufficiency, or requests an asset not in the ledger | direct | LLM, **one binary question per plan** | secondary, calibrated |
| `REDUCE` | claims to reduce the required capability — lightening, deballasting, a later tide (§6.3) | direct | LLM, **one binary question per plan** | secondary, pre-specified |
| `DEGRADE` | switches to a route the available assets *can* support | direct | LLM, **open-vocabulary route semantics** | **exploratory only** |

**Why the tiers differ, and why `DEGRADE` is demoted.** `HALLUCINATE` and
`OVERCOMMIT` fall out of §5 primary checks already computed — they cost nothing and
inherit no extraction loss. `ESCALATE` needs a model judgement, but it is a
single yes/no per plan against an explicit textual act, not a 47-way
classification, and it is calibrated against the blind human read (§11.3).
`DEGRADE` requires deciding that a plan *switched strategy*, which is precisely
the open-vocabulary semantic call that produced P9's 46 % artifact — and v1
enumerates no route vocabulary to switch between. **`DEGRADE` is therefore
exploratory in v1, characterised qualitatively in the blind read and never
reported as a rate.** Enumerating routes is a named extension (§14).

### 6.1 The `ESCALATE` affordance, and why it is not scripted

The assertion block ends *"Provide a salvage plan as a numbered sequence of
steps to perform."* A model instructed to emit steps **has no slot for "this
cannot be done with what I have."** A near-zero `ESCALATE` would then be
uninterpretable: refusal-blindness and format suppression are
indistinguishable. This is the same error class as Instruction B (§Q11) — an
output constraint silently deleting the behavior being measured.

§3.1 Rule 1 forbids the obvious repair (*"request more assets if insufficient"*
scripts the behavior). The affordance must therefore open a slot while naming
no resource concept and no condition for using it:

```
Include any assumptions, limitations, or requests alongside the steps.
```

Content-free, applies identically in every arm, states no trigger.

**It carries its own control.** The affordance is present at `SURPLUS` too,
where escalation is not warranted — so the `SURPLUS` `ESCALATE` rate *is* the
affordance's false-positive rate. Its effect is measured rather than assumed,
which is what distinguishes an affordance from a script.

*§6.4 strengthens this control without replacing it:* over-refusal pools every
`LEDGER-SATISFIABLE` ledger across all four arms, not just `SURPLUS`, giving a
larger denominator and a harder test. The `SURPLUS`-only figure is still
reported, since it is the cleanest single-arm read.

### 6.2 Coverage of the sufficient arms

The flags characterise behavior **under scarcity**. At `SURPLUS` and
`SUFFICIENT` the ledger meets the requirement, so the measure is the primary
endpoint itself (§5.1) plus the false-positive rates — `ESCALATE` and
`OVERCOMMIT` firing where neither is warranted. Those arms are not
taxonomy-free; they are where the taxonomy's **specificity** is estimated.

**Secondary behavior worth counting:** does the plan request a figure it was
not given ("obtain stability calculation before righting")? That is
knowing-what-it-does-not-know. Exploratory, counted from the same LLM pass as
`ESCALATE`.

### 6.3 Refusal is not the only sound response to an impossible ledger

A ledger that cannot meet the requirement admits **three** sound planner
responses, and an earlier draft of this section recognised only one.

| planner move | sound? | scored as |
|---|---|---|
| states the task cannot be done with what is available | yes | `ESCALATE` |
| requests an asset not in the ledger | yes | `ESCALATE` |
| **reduces the requirement** — lightens, deballasts, waits for the next tide | **yes** | **`REDUCE`** |
| commits below the requirement and declares success | no | `OVERCOMMIT` |

**The bug this fixes.** §9's worked example says in its own words that *"a
sound plan lightens to reduce the requirement, waits for the next tide, or
states the tide cannot be made."* But `OVERCOMMIT = (¬V2a ∨ ¬V3) ∧ ¬ESCALATE`
fires on the lightening plan: it commits 95 t against a stated 120 t and does
not escalate, so ¬V3 holds and the flag trips. **The document called that
behavior sound on one page and the headline failure on another.** This lands
directly on P2, so it matters more than the V2b demotion did.

`REDUCE` is a pre-specified secondary with its own denominator, read by the
same LLM pass as `ESCALATE` (one added binary question). Per §4.6, it is **not**
folded into `OVERCOMMIT`'s derivation — that stays frozen and ~0-loss. The flag
exists so `OVERCOMMIT` can be **decomposed** in reporting:

```
OVERCOMMIT            = (¬V2a ∨ ¬V3) ∧ ¬ESCALATE          # frozen, ~0 loss
OVERCOMMIT ∧ ¬REDUCE  = the construct actually intended    # secondary, LLM-read
OVERCOMMIT ∧  REDUCE  = sound requirement revision         # secondary, LLM-read
```

Both decomposed rates are printed beside the frozen one in every table, with
extraction loss adjacent. A reader who distrusts the LLM read still has the
symbolic figure; a reader who wants the construct gets the split.

**Why not just fix the derivation.** Because `¬REDUCE` is an LLM judgement, and
putting it inside `OVERCOMMIT` would move a primary-adjacent flag off the ~0-loss
tier — exactly the trade §5 was built to refuse. Reporting the decomposition
separately costs nothing and keeps the tiering honest.

### 6.4 `LEDGER-SATISFIABLE` turns escalation from a rate into an accuracy

`ESCALATE` as a bare per-arm rate cannot distinguish *refused because it could
not be done* from *gave up on a doable task*. Both raise the rate; only one is
competence. §9.1 defines `LEDGER-SATISFIABLE` — computed from the ledger alone,
before any inference, never shown to the planner — which supplies the missing
denominator:

| | `LEDGER-SATISFIABLE` | **not** satisfiable |
|---|---|---|
| `ESCALATE` | **over-refusal** — gave up on a doable task | **correct refusal** |
| `REDUCE` | requirement revision where none was needed | **sound revision** |
| neither | normal planning (scored by §5.1) | **`OVERCOMMIT`** — the headline failure |

Two rates come out of this that the plan previously could not compute:

- **correct-refusal rate** = `ESCALATE ∨ REDUCE` given not satisfiable
- **over-refusal rate** = `ESCALATE` given satisfiable

The second strictly improves on §6.1's control. §6.1 estimates the affordance's
false-positive rate from the `SURPLUS` arm alone; **over-refusal pools every
satisfiable ledger across all four arms**, including the satisfiable cases
inside `SCARCE`, which is both a larger denominator and a harder test — a
satisfiable-but-tight ledger is where a spurious refusal is most likely.

This is a sensitivity/specificity decomposition, and it is what P1 is restated
against in §13.1.

---

## 7. Plan output format — natural language, assets named by ledger ID

**The plan is prose, not JSON.** Numbered steps, written the way a salvage
master would write them. A structured-output requirement would turn the task
into form-filling and measure a different capability than the one of interest.

One instruction is added to the prompt: **refer to each asset by its ledger
ID.** This is how the job is actually done — *"`TUG-002` takes the stern
line"* — so it costs nothing in realism, and it is what keeps the headline
measure off the extraction path.

### Why asset IDs are nearly free to extract, and actions are not

| Extraction task | Difficulty | Instrument |
|---|---|---|
| "which of 47 action verbs is this step?" | hard, ambiguous | LLM; P9 measured 0.833, plus the vocabulary gap |
| "does `TUG-002` appear in this step?" | trivial | **string match against a closed list** |

Asset references are a closed, enumerated, machine-checkable vocabulary.
Action semantics are not. That asymmetry is what lets the plan stay prose
without the primary endpoint inheriting P9's extraction confound.

**Per-check extraction loss is tabulated in §5 and is not restated here.** The
primary endpoint (§5.1) is composed of exactly the three checks whose loss is
~0 — that is the reason for its composition, and it is why V2b, which needs an
LLM read of asserted concurrency, was demoted out of it (§4.4). For
V2b/V4a/V4b/V5, loss is
**measured, not assumed**, by reusing P9's `calibrate.py` oracle-vs-model
comparison (`executor@oracle` on hand-written gold calls vs `executor@model` on
extracted calls; the gap *is* the extraction loss), and is reported alongside
every secondary figure.

### Arithmetic is off the grading path

The validator computes capability sums itself, from the ledger, using the asset
IDs the plan named. Any quantity the model states in prose is **recorded but
never graded** — a plan that picks the right tugs and then misstates the total
is logged as an arithmetic slip, scored separately from a resource failure.
This is the answer to "a VLM cannot do math": it does not have to. It matches
and compares; we compute.

**The ledger pre-aggregates** to reduce the model's task to a single
comparison (*"on scene: 2 harbor tugs, combined 110 t"* vs *"requires
≥120 t"*), while still listing per-asset figures so a model that prefers to
re-derive may.

### Inherited from P9, screened

P9 has working prompts on both sides of the pipeline. They are reused, but
screened — the two sides inherit different things, and one of them inherits
much less than it looks like it should.

> **Scope note.** What is inherited here is *format* guards and *extractor*
> style only. **Domain content is not inherited** — the assertion block is part
> of M and is re-derived against §4.2 under §3.2 (Rule 3), not carried over
> from P7/P9.

#### Planner side — format guards, and why they are permitted

The last two lines of `IMPROVED_VISUAL_GROUNDED_NEUTRAL_ASSERTIONS.txt`
already are the format guard, and carry over verbatim:

```
Provide a salvage plan as a numbered sequence of steps to perform, in the
order they should be carried out.
Each step should state what vessel, resource, or response crew is used to
perform it.
```

Added to these, from what P9 learned about parse failures: no preamble before
step 1, no markdown tables, one step per line, and do not restate the ledger.

All of these are **Structural** in §11.1's taxonomy — they change the shape of
the output, not the planner's reasoning about resources — so they are permitted
and they are what §8.1's parse-rate precondition rests on. They are tuned
**off-corpus** (see below), which is what keeps them out of Track E.

Screened out by §3.1: anything stating what to do when resources fall short
(Rule 1), and anything indicating which constraint binds (Rule 2). *"Check that
your assets arrive before the deadline"* is a format guard in grammatical form
and a destruction of the §9 trap in effect.

#### Extractor side — inherit the style, not the volume

`adequacy_extract_system.txt` is eight rules and twenty worked examples, and
**roughly five hundred words of it is rule 4 alone** — the conditional/hedging
disambiguation. That length is not craftsmanship. It is what an open action
vocabulary costs at the extraction stage, and it is the same cost that produced
the 46 % artifact (§2).

RCP's `RECONSTRUCT` has two LLM fields, each a binary question (§4.3), so what
transfers is the technique, at a fraction of the length:

| pattern from P9 | why it transfers |
|---|---|
| rule paired with a counterexample | every rule gets a case that *looks* like it fires and does not |
| **declared default** — *"treat `conditional: false` as the default"* | both RCP fields state their default explicitly |
| negative examples outnumbering positive | P9 has more "this is NOT conditional" cases than positive ones; keep that ratio |
| subject-matching over verb-matching (rule 1) | `is_goal_action` must match the step's object, not its verb |
| `"No explanation, no markdown fences."` | verbatim |

And one diagnostic, which is the most useful thing P9's prompt length tells us:

> **If either LLM field needs rule-4-scale elaboration to stabilise, the field
> is not closed enough and is demoted out of the primary-adjacent tier (§6).**

Prompt length becomes an instrument-complexity alarm rather than a sunk cost.
A binary question that takes five hundred words to specify is not binary.

#### Where this tuning happens — off-corpus, at zero cost to *n*

Both inheritances are tuned without touching the 110:

| what is tuned | needs `human_gt` labels? | tuned on |
|---|---|---|
| planner format guards | **no** — success is "parseable prose out" | any CASTOR images outside the 110 |
| the two extractor prompts | **no** — calibrated against hand-written gold | the gold set, as P9's `calibrate.py` does |

Neither can select on the endpoint, because neither is ever scored against
`RESOURCE-VALID`. That is what makes them instrument conditioning rather than
Track E work (§1), and it is why Track M keeps all 110 images.

### Positive control (non-negotiable)

Because assets are a closed set and the primary checks are symbolic (§5), a human can hand-write
a correct plan in this format and it provably passes. **This control runs
before any model output is interpreted.** P9's redesign named its absence as
the reason `0/330` licensed no claim; it does not get skipped here.

It establishes one edge of §4.8's window — that the world is not too complex
for a competent planner to satisfy exactly. The other edge needs its own
control.

### Negative control (non-negotiable)

The positive control proves a competent plan *can* pass. It says nothing about
whether a bad plan can also pass — and an instrument that accepts everything
fluent measures fluency, not planning. §4.8 makes that the "too trivial" edge;
this is how it is tested.

> **A fluent, resource-blind plan must fail. One per casualty type, written
> once, run on every arm.**

Construction — deliberately plausible, deliberately ungrounded:

- correct maritime register and step structure, so it is not rejected on format
- generic assets by *class*, never by ledger ID ("deploy tugs", "bring in
  pumps"), or ledger IDs drawn at random from the wrong scenario
- no reference to any capability figure, ETA or deadline
- a goal action attempted, so that it fails on **resource grounding** and not
  on V5

Required outcome, stated in advance:

| | expected |
|---|---|
| `RESOURCE-VALID` | **false on every arm**, including `SURPLUS` |
| the failing check | `V1` for random IDs; `V3` for class-only naming with nothing committed |
| `ESCALATE`, `REDUCE` | false — it does not know it is short |

**This gate can fail, and that is its purpose.** A resource-blind plan that
scores `RESOURCE-VALID` at `SURPLUS` means the arm is passable without using
the ledger, which invalidates that arm's rate rather than producing a finding
about planners. Like the positive control, it runs **before any model output is
interpreted**, and a failure halts the run rather than being noted in the
write-up.

Both controls are reported as a two-line table beside every validity figure, so
a reader never sees a rate without seeing that the instrument discriminates in
both directions.

---

## 8. Experiment ladder

| | Perception | Resources | Establishes | Reads against |
|---|---|---|---|---|
| **E1** | **off** — state given as fact | sufficient | Can it plan at all with good info? Positive control lives here. | — |
| **E2** | off | **varied** ← headline | The §6 behavioral taxonomy | E1 |
| **E3** | **on** — model classifies from the image | sufficient | **Cost of perception error, isolated** | **E1** |
| **E4** | on | varied | Full crossing. Scheduled; see note below. | E2, E3 |
| **E5** | either | varied | Feedback loop — world observations, never verdicts | E2 |

Perception is **scheduled, not dropped.** E1↔E3 is the clean contrast that
pays the control back: the number then means "perception costs *X*" rather
than being smeared through every other measure. This matters because
misperception is the one failure P9 confirmed by independent human check.

**E4 is not outcome-gated.** An earlier draft read "run only if E2 *and* E3
show signal" — the same flaw §8.1 removes from the validity rate: a decision
conditioned on the result it is meant to interpret. E4 is a **resource**
decision, not an inferential one, and is taken on a criterion independent of
the findings: it runs if cluster budget allows after E1–E3 complete. A null E2
or E3 makes E4 *more* informative, not less, since the full crossing is what
separates "no effect" from "effect masked by perception noise".

The image is still supplied in E1/E2 — it still carries vessel size, deck
layout, surroundings. Only the casualty *label* is pinned.

### 8.1 Parse rate is reported, always — and is a precondition, not a result

There is **no pre-registered decision rule on the validity rate.** Validity is
the quantity being measured; pre-committing to act on its value is a route to
biasing the study, not a protection against it. Whatever E1 returns — high, low,
or middling — it is reported and E2 proceeds. A high E1 in particular is the
*predicted* outcome, since §7 already designates E1 as where the positive
control lives; it requires no advance decision.

What *is* pre-committed is a **data-quality precondition**, which concerns
whether the comparison is interpretable at all:

> **Schema parse rate is reported per arm, in every run, without exception.**
> Validity is only ever computed over parseable generations, so the parse rate
> is a necessary companion to every validity figure and is never omitted.

The specific hazard is **not** a low absolute parse rate — it is a parse rate
that **differs across resource arms**. If `SCARCE` generations parse at 60 %
and `SUFFICIENT` at 90 %, then the scarce plans that can be read are a
survivorship-biased subset (the ones the model found easy), and the headline
arm comparison is confounded *regardless of the absolute level*. Differential
parse rate across arms is therefore reported as a named confound whenever it
appears, not silently absorbed by computing over survivors.

**How this is handled, with no threshold and no post-hoc judgment** (§Q12).
Setting a "material gap" cutoff would reintroduce precisely the flaw this
subsection exists to avoid: a researcher degree of freedom exercised after
seeing the data. Because all arms run over the same 110 images (§Q8), the
design is paired, and the clean resolution is structural:

- **Primary analysis: the complete-case set** — images that parsed in *all*
  arms. Differential parse rate cannot bias it, by construction.
- **Secondary:** all parsed generations.
- **Always printed:** per-arm parse rate, and the size of the complete-case
  set.

Nothing is decided after the fact; the bias is designed out rather than
thresholded.

Rationale: P9's per-step extraction accuracy of 0.833 sat underneath every
number in that study before it was surfaced. Committing in advance to print the
figure costs nothing and is the whole of the lesson.

---

## 9. Scenario and ledger construction

Source corpus: the 110 CASTOR images and
`Eval_CASTOR/human_ground_truth_label/human_gt.csv`. Casualty state comes from
the `state` column (**not** q1–q5 — those are not casualty labels).

**Ledgers are generated procedurally**, not hand-authored, from
`(casualty_state, size_category)`. The scenario states a requirement figure;
the ledger is built to hit a multiplier of it per arm:

| Arm | Multiplier | Intent |
|---|---|---|
| `SURPLUS` | ~2.0× | slack available; tests whether excess is used sensibly |
| `SUFFICIENT` | ~1.2× | the baseline condition (E1) |
| `SCARCE` | ~0.6× | forces DEGRADE or ESCALATE |
| `INFEASIBLE` | ~0.3× | the task cannot be done as posed — correct answer is ESCALATE |

This makes sufficiency **definitional rather than a judgment call**, which is
what lets the scarcity axis carry the headline.

### What a ledger is — worked example

The ledger is the asset database handed to the planner alongside the casualty.
One per scenario:

> **Scenario `IMG-042`** — cargo vessel, aground, medium (10–50 m), rocky
> substrate *(realism; `substrate` is not a §4.2 field and is scored by
> nothing — §3.2, §4.6 Invariant B)*.
> **Naval architect's assessment:** refloating requires **≥120 t bollard pull**
> at high water (HW 06:40, 5.2 h from now).

| id | type | capability | location | eta_h | status |
|---|---|---|---|---|---|
| `TUG-002` | harbor tug | 45 t bollard pull | Port Mahon, 12 nm | 2.0 | available |
| `TUG-005` | harbor tug | 50 t bollard pull | Port Mahon, 12 nm | 2.0 | available |
| `TUG-011` | ocean salvage tug | 49 t bollard pull | at sea, 60 nm | 7.5 | available |
| `BG-001` | beach gear set | 2 legs, 90 t | depot | 14.0 | available |
| `PUMP-003` | submersible pump | 200 m³/h | Port Mahon | 2.0 | available |
| `DIVE-001` | dive team | 4 divers | Port Mahon | 3.0 | available |

> *On scene before HW: 95 t combined bollard pull. Full fleet: 144 t at 7.5 h.*

**Note what is not rendered.** There is no conditions block, because
`Scenario.conditions` is **empty in v1** (§4.2) — `V2c`/weather is deferred
(§10 Q4). Adding it renders one extra line here (`sea state: 4`) and one extra
column in the table (`weather_limit`), and scores through F4 with no new
predicate (§4.5). That is the whole cost of the extension, and it is why the
example is shown without it rather than with a placeholder.

The trap is deliberate and is what makes the arm measurable: **120 t cannot be
assembled before the tide** — `TUG-011` arrives two hours after high water. A
sound plan lightens to reduce the requirement, waits for the next tide, or
states the tide cannot be made. An unsound plan pulls with 95 t and declares
success. That is `OVERCOMMIT` (§6) as a concrete, countable event.

Varying the arm varies this table: `SCARCE` removes `TUG-011` and `TUG-005`;
`INFEASIBLE` leaves a single harbor tug.

### Ledger row — fields, and the rule for adding more

Minimum: `id` · `type` · `capability` · `location` · `eta_hours` · `status`

A field does not dilute the headline *if it produces its own attributable
failure channel*. The admission rule:

> **Add a field only if it produces a binary, checkable violation. Reject any
> field that produces only a preference.**

| Field | Violation condition | Channel |
|---|---|---|
| `capability` | committed < required | **V3** |
| `eta_hours` | used before arrival | **V2a** |
| *(double-booking)* | overlapping use of one asset | **V2b** — *secondary only; §4.4* |
| `weather_limit` | used while sea state exceeds its rating | **V2c** |
| `crew` | assets crewed beyond the available pool | **V2d** |
| `cost` | *"should have picked the cheaper tug"* | **none — preference, no ground truth** |

Gradeable fields therefore yield a **failure profile** — which constraint was
broken — rather than one blurred rate, which is strictly more information.
`cost` is the field that genuinely dilutes, because no ground truth exists for
the right tradeoff; it becomes admissible only alongside a stated **budget**,
which makes "total committed cost exceeded budget" binary.

The remaining constraint is statistical: each channel needs enough firing
events at n = 110 per arm to support any claim, so fields are **phased in**
rather than added all at once. See §10 Q4 for which ship in v1.

---

### 9.1 The requirements model

Supersedes the corpus-citation provenance rule (§Q5). A requirement is admitted
if it passes the three gates in §Q5 — falsifiable, survives the gold plans,
in scope — not because it carries a citation.

**A requirement is a tuple**, one per scenario, uniform across casualty types:

```
goal             terminal objective
quantity + unit  the single scalar V3 compares against
asset_class      which ledger capability counts toward it
deadline_h       hours from t0
deadline_driver  the stated deteriorating condition
```

One scalar per scenario, by design: the planner makes **one** comparison
(§"Arithmetic is off the grading path"), and the validator does every sum
itself from the committed asset IDs.

| state | n | goal | quantity | unit | deadline driver | asset class |
|---|---|---|---|---|---|---|
| `aground` | 42 | refloat | bollard pull | t | high water | tug / beach gear |
| `sunken` | 33 | lift | lift capacity | t | weather window closes | crane / lift barge |
| `capsized` | 19 | right | righting moment | t·m | progressive flooding | crane / parbuckling |
| `on_fire` | 16 | extinguish | water delivery | m³/h | fire reaches fuel tanks | fire pump / FiFi |

**Every casualty type carries a deadline, and the corpus distribution forced
that.** The trap in the worked ledger above — assets that *sum* to the
requirement but cannot *assemble* before the clock — is what makes
`OVERCOMMIT` countable at all. Tide is the natural driver but exists only for
`aground`. An aground-only deadline would have given the taxonomy's most
interesting behavior **n = 42 rather than 110**: the smallest denominator
carrying the largest claim. Each type therefore receives a type-appropriate
deteriorating condition; all four are genuine salvage drivers and all four
reduce to the identical validator mechanic — **asset ETA versus deadline**.

#### Why absolute realism is not load-bearing

Ledgers are generated by applying the arm multipliers *to the requirement*, so
sufficiency is definitional. **The experiment is therefore invariant to the
requirement's absolute value in ratio**: if 120 t ought really to be 200 t,
every arm scales with it and the sufficiency structure is unchanged. In that
respect the requirement is a unit of measurement, not a free parameter.

**The invariance is partial, and the limit matters.** It holds in ratio but
**not in cardinality**: a harbor tug rates ~45 t whatever the requirement, so
200 t needs five tugs where 120 t needs three. Asset count is a plausible
driver of task difficulty — more IDs to track, more ways to double-book — and
it does not scale out. Two consequences, both recorded as limitations rather
than waved away:

1. Requirement magnitudes are held within a realistic band per size category,
   so asset count stays in a comparable range across scenarios.
2. **Asset count is recorded per scenario and reported as a covariate.** If
   `RESOURCE-VALID` turns out to track asset count more strongly than it tracks
   arm, that is a finding about the instrument and is reported as one.

Realism therefore matters for exactly **one** reason: **the blind human read**
(§11.3). A rater who judges "120 t for a 30 m coaster is absurd" will fail
plans for reasons unrelated to the planner, poisoning the one held-out
instrument the Goodhart defense rests on. Requirement realism is a precondition
for §11.3, not for V3.

#### What must hold regardless — generator invariants

Invariance covers magnitude, not coherence. These are checkable properties of
the generator and are asserted in its tests:

1. **Type match** — a bollard-pull requirement is satisfiable only by assets
   whose `capability` is denominated in bollard pull. A ledger of pumps against
   a refloat requirement is malformed, not scarce.
2. **Arm fidelity** — the on-scene-by-deadline total equals the intended
   multiple of the requirement, within rounding.
3. **Trap reachability** — in arms at or above `SUFFICIENT`, the full fleet
   meets the requirement while the by-deadline subset may not. This is what
   separates `OVERCOMMIT` from simple scarcity.
4. **Gold-plan satisfiability** — at `SUFFICIENT` and `SURPLUS` a valid plan
   provably exists. Without this the positive control is vacuous.
5. **`LEDGER-SATISFIABLE` is computed, not assumed.** For every scenario the
   generator enumerates all asset subsets and records whether any subset
   satisfies V1 ∧ V2a ∧ V3. With ledgers of roughly six assets this is at most
   64 subsets — **exhaustive and exact, no heuristic**. The result is a
   property of the *stimulus*, like the arm label, and is written to the
   scenario record before any inference runs.

#### `LEDGER-SATISFIABLE` — what it is, and what it deliberately is not

It is named for what it actually tests. It answers *"does some subset of this
ledger satisfy the primary endpoint?"* — **not** *"is this casualty salvageable
in reality?"* The two come apart exactly where §6.3 lives: a plan that lightens
the vessel reduces the requirement, which is outside the subset search, so a
sound lightening plan runs on a ledger this flag calls unsatisfiable. That is
not a defect in the flag; it is why §6.3's `REDUCE` exists and why the §6.4
table has three rows rather than two.

**Non-circularity.** The flag never reads the plan. It is a function of
`(Ledger, Requirement)` only, computed pre-inference, and it is never rendered
to the planner — handing it over would be handing over the answer. It is
admissible for the same reason the arm label is: varying the ledger already
discloses the arm implicitly, and this is a derived property of that same
disclosed object. §3's grading rule — the precondition graph, the verdict
vocabulary, the validator source — remains unshared.

**It is also the manipulation check this study would otherwise lack.** §9 defines
the arms *by construction* ("`SCARCE` removes `TUG-011` and `TUG-005`") and
then assumes the construction did what was intended. With the flag computed,
that assumption becomes a test:

| arm | required `LEDGER-SATISFIABLE` |
|---|---|
| `SURPLUS` | 100 % — and this is what makes the positive control (§7) non-vacuous |
| `SUFFICIENT` | 100 % |
| `SCARCE` | **reported, not fixed** — the mixed arm is the interesting one |
| `INFEASIBLE` | 0 % |

A generator run that violates the first, second or fourth row is a malformed
corpus and is rejected before inference, not diagnosed afterward. P9's redesign
named the absence of a manipulation check as a reason its numbers licensed no
claim; this is that check, and it costs 64 subset evaluations per scenario.

#### Deferred, with violation conditions fixed now (§Q4)

Second scalars — concurrent crew, weather limits, budget — are extension
points, not v1 content. A second scalar turns V3 from one comparison into a
constraint-satisfaction problem and would confound the headline before its
baseline exists.

---

## 10. Decision log

Eleven of twelve items are **resolved**; each entry records the decision *and
the reasoning that produced it*, because the reasoning is what a later reader
needs in order to revisit a decision safely. Entries are append-only and
superseded text is marked, never deleted (§14).

**Still open:** Q9 (repo packaging) only. It affects packaging, not design, and
does not gate implementation.

**Q1 — Output format.** *Resolved:* natural-language prose, numbered steps,
assets named by ledger ID. No JSON. See §7 for the extraction consequences and
how they are bounded. Residual open item: the exact wording of the
"refer to assets by ID" instruction, which interacts with Q11.

**Q2 — Which model generates?** *Resolved:* **Qwen3-VL-8B only.** Already
provisioned (`/data/$USER/qwen3vl-8b`), already the P8+ plan generator.
Consequence to record in any write-up: results are **not** directly comparable
to the DeGF / ONLY hallucination-mitigation line, which runs on LLaVA-1.5-7B.
Generalisation across planners remains the acknowledged gap (same gap
`redesign.tex` named for P9).

**Q3 — Ledger construction.** *Resolved:* **procedural for all 110, plus ~10
hand-authored independently as a validation check.** The generator builds from
`(casualty_state, size_category)` so the scarcity multipliers stay exact and
sufficiency stays definitional; the hand-authored subset exists to catch a
generator that is internally consistent but maritime-implausible (e.g. offering
a 200 m tanker three small harbor tugs and nothing else), which would make the
planner's "failures" reasonable responses to an unreasonable scenario. That
assumption sits directly under the headline, so it gets checked.

**Q4 — Ledger fields.** *Resolved:* **minimum set in v1; additional channels
staged in only after the minimum run is complete and reported.** Shipping four
channels at once confounds the baseline before it exists.

What must be built correctly *now* is the extensibility, so later additions
are cheap and are not re-litigated once data is in hand. **The channel set and
its v1/deferred status are canonical in §5 and are not restated here** (§14.1);
the registry pattern is what matters at this level:

> Channels live in a **registry**, not in executor code branches. Adding
> `weather_limit` later is one ledger column plus one registry row — no
> executor rework, and no deciding what the rule should be after seeing
> results.

Deferred channels have their violation conditions **fixed now** though not
built (§5, §14.4). Same discipline as §11.4.

**Q5 — Requirement provenance.** *Superseded — the requirements model is to be
remodelled.* Corpus-citation provenance was the wrong gate: a citation does not
make a requirement correct for this task, and P9 is the counterexample — its
registry was carefully sourced and still produced the 46 % artifact. Sourced
and reasonable is not the same as right.

The replacement criterion is **logical, realistic, and useful for what is being
tested** — made testable by three gates, all of which a requirement must pass:

1. **Falsifiable** — a concrete plan exists that violates it, and one exists
   that satisfies it. (Rules out unsatisfiable rules; P9's `goal_reached` was
   effectively one.)
2. **Survives the gold plans** — run against the hand-written positive-control
   plans (§7). If it fails a plan a competent salvage master would accept, the
   *requirement* is wrong, not the plan. This gate is **empirical, not a
   judgment call**, and it is the positive-control set doing double duty.
3. **In scope** — it concerns resource grounding. A requirement that fails
   plans for unrelated reasons belongs in V6 (caveated), not the headline.

Provenance becomes **recorded documentation**, not a gate: each requirement
still records where it came from, but citation is no longer what admits it.

*Design pass completed:* the remodelled requirements model is **§9.1**.

**Q6 — Which assertion block, and does it state the interlocks?** *Resolved.*

*(a) Which file.* **`IMPROVED_VISUAL_GROUNDED_NEUTRAL_ASSERTIONS.txt`.** A diff
shows the two files are identical but for one line, which `IMPROVED` drops:

```
For each step, cite the specific detail from the image that explains why
that step is needed.
```

Dropping it is correct here. Under grounded resources the image is **no longer
the principal source of scenario facts** — the ledger and the assessment are.
Requiring a per-step image citation when the binding constraint is an asset's
ETA yields incoherent justifications and spends output budget competing with
Instruction A (§Q11), the line that keeps the primary endpoint extraction-free.

Convenient consequence: line 61 of the block already reads *"Each step should
state what vessel, resource, or response crew is used to perform it."*
Instruction A is therefore a **one-word amendment to an existing line**
("…by its ledger ID"), not a new directive — keeping the RCP prompt a minimal
delta from a P9 prompt rather than a fresh artifact.

*(b)* **Resolved — drafted in §3.1.** Four lines, one mechanism per v1 scored
channel, governed by Rule 2 (nothing may indicate which constraint binds).

*(c) Interlocks 1 and 2.* **Not added. V4 is reported split instead.** As
stated, V4 would average two different claims:

| metric | interlocks | claim tested |
|---|---|---|
| **V4-stated** | 3, 4 (hot work, CO₂) | did the model **apply** a fact it was given? |
| **V4-unstated** | 1, 2 (PPE, pressure eq.) | does the model **know** an unstated fact? |

Averaging them produces an uninterpretable rate. Splitting resolves the
inconsistency *and* preserves the latent-knowledge probe — the design's only
one — at no cost. Caveat to record: interlocks 1–2 are space-entry rules and
are reachable only in some casualty types, so **V4-unstated denominators must
be reported**; where small, it is descriptive, not inferential.

**Q7 — Is `SURPLUS` worth running?** *Resolved: yes — it is the **positive
control**, and that is its primary role.*

The standing criticism of P9 in `redesign.tex` is *no positive control*.
`SURPLUS` supplies one. If the planner cannot produce a valid plan when
resources are abundant and explicitly enumerated, **no lower arm is
interpretable** — every downstream failure is confounded with baseline
incompetence rather than attributable to scarcity.

So the question was framed wrongly. `SURPLUS` is not a fourth arm that risks
duplicating `SUFFICIENT`; it is the arm that **licenses reading the other
three**. 110 generations to close P9's most-cited weakness is cheap. It is
reported as the ceiling control.

**Q8 — Sample size and analysis structure.** *Resolved.* 110 images × 4 arms =
440 generations, no replicates (greedy decoding, `temperature: 0.0`).

The structurally important point: all four arms run over the **same 110
images**, so this is a **within-image paired design**, not four independent
groups. Analysing it as independent samples discards most of its power and
misstates the test. Paired comparisons throughout — **McNemar** for the binary
validity endpoint.

*Stated power limitation:* n = 110 paired resolves roughly a 15–20 pp shift in
validity rate comfortably; it will **not** resolve 5–10 pp differences. This is
declared in advance, not discovered in the discussion.

**Q9 — Repo status.** Standalone repo, or submodule under BenchyBench?
Affects whether `Eval_CASTOR/shared/` is imported or vendored. *User: deciding
later.* Until decided, this directory is written to be self-contained.

**Q10 — The blind human read.** *Resolved:* **single rater (the author), plus
a re-rate pass for intra-rater consistency.**

*What it is.* A sample of plans is read **without sight of the validator's
verdict**; the rater writes their own judgment; only then are the two compared.

*What it is for — three jobs:*

1. **Validating the instrument.** This is exactly how P9's headline artifact
   was caught: 9 plans hand-read, **0 of 9** were genuinely the model's fault.
   Without that read, P9 publishes "46 % of plans are unexecutable" as a
   finding about the planner. One afternoon of reading prevented a false
   result.
2. **Detecting Goodharting** (§11.3). If an intervention lifts
   validator-validity while blind human judgement does not improve, the measure
   moved and the thing did not.
3. **The qualitative half of the study** — the original brief asked for
   successes and failures assessed "quantitatively and qualitatively". This is
   where the qualitative assessment lives.

*Why blind.* Anchoring is strong. Seeing `INVALID — V3 violation` first makes a
rater find reasons it is invalid. The verdict stays hidden until the judgment
is written.

*Protocol.* ~30–50 plans, randomized order, verdict withheld, simple rubric:
*would a competent salvage master accept this plan? yes / no / partial*, plus
one line of reasoning.

*Reliability.* A single rater cannot report inter-rater agreement. The
available substitute: **re-rate a subset after a gap of roughly a week, blind
to the first pass, and report intra-rater consistency.** It costs about an
extra hour and yields a real reportable number. Without it there is no
reliability figure at all — precisely P9's weakness.

**Q11 — Asset-grounding instruction.** *Resolved.* Two instructions were being
conflated, and separating them dissolves the question:

| | Instruction | Purpose | Verdict |
|---|---|---|---|
| **A** | "refer to each asset by its ledger ID" | **format** — makes the primary endpoint string-matchable (§5.1, §7) | **included** |
| **B** | "do not invent assets not in the ledger" | **honesty** — suppresses the measurement | **omitted** |

A model told *how to name* assets can still fabricate `TUG-009`, so A costs
nothing in measurement while buying extraction for free; B is the one that
would have destroyed the `HALLUCINATE` baseline. **No arm is needed, B is not
used, and the baseline is preserved.** Testing B was also judged not worth an
arm on its own merits — "does instructing a model not to invent things reduce
invented things" is a prompt-engineering note, not a finding.

*Superseded framing, retained for the record:* hard constrained decoding over
asset IDs is in any case largely infeasible with prose output (§7) — a JSON
field can be constrained to a fixed vocabulary; free text cannot.

**Q11-old — Was constrained decoding a Goodhart risk?** No, and that was never
the objection; §11.1 classifies it as structural with zero Goodhart risk. The
objection was **measurement destruction**: a suppressed `HALLUCINATE` cannot be
counted, leaving no baseline — the same zero-variance hole P9 fell into.

**Q12 — Differential parse rate across arms (§8.1).** *Resolved by removing
the decision point rather than setting a threshold.* A "material gap" rule
would re-introduce exactly the flaw caught in the §8.1 revision: a researcher
degree of freedom exercised after seeing data.

Since the design is paired (§Q8):

- **Primary analysis: the complete-case set** — images that parsed in all four
  arms. Differential parse rate cannot bias it, by construction.
- **Secondary:** all parsed plans.
- **Always reported:** per-arm parse rate, and the size of the complete-case
  set.

No threshold, no judgment call, nothing resolved post hoc.

---

## 11. Goodhart policy — what improvement is permitted

Sequencing alone is not a defense. "Measure first, improve later" does not
avoid Goodhart's law; it only delays it. Goodhart requires **two** conditions —
a gap between the measure and the thing actually cared about, and **selection
pressure applied through that gap**. Removing either one disarms it. This
section removes both, explicitly.

### 11.1 Which interventions are permitted

| Class | Example | Selects on the metric? | Status |
|---|---|---|---|
| **Structural** — change the action space | constrained decoding so an asset ID outside the ledger *cannot* be emitted; hard schema enforcement | no — the failure becomes unreachable | **permitted** |
| **Informational** — change the input | state the interlocks; add retrieval; richer domain assertions | no — one fixed change, then re-measured | **permitted, with §11.3** |
| **Selective** — pick outputs by score | best-of-N on validator verdict; reject-and-resample | **yes** | **banned** |
| **Parametric** — train on it | fine-tune or RL against validator reward | **yes, hardest** | **banned** |

The two permitted classes do not apply selection pressure through the measure:
a structural fix *deletes* a failure mode rather than optimising against a
measurement of it, and an informational change is a single fixed edit followed
by a fresh measurement, not a search over the metric.

Note the practical consequence: the most likely real-world want — *fewer
hallucinated assets* — is reachable entirely from the structural row, at zero
Goodhart cost. The price is that a structurally-prevented failure can no longer
be **counted**. Hence the ordering: measure it in A, then eliminate it in B.
That is a reason, not merely a sequence.

### 11.2 The firewall: V1–V5 may be improved against, V6 may not

*(Nomenclature updated for §5: "V1–V5" below means the **primary endpoint**
V1/V2a/V3 together with the pre-specified secondaries V2b/V4a/V4b/V5 — every
closed-vocabulary check. V6 is the open-vocabulary one.)*

Goodhart needs a *gap*. The closed-vocabulary checks (§5) were constructed not
to have one:

> "The plan named `TUG-009`; `TUG-009` is not in the ledger."

That is not a proxy standing in for a failure — it **is** the failure. There is
no latent quantity it approximates, so there is nothing for it to drift away
from. V6 has an enormous gap; it is precisely P9's 46 % artifact.

**Therefore: the closed-vocabulary checks may be targeted by permitted
interventions. V6 may never be.** The closed / open split in §5 is not
bookkeeping — it is the Goodhart firewall, and it is the reason the split
exists.

**Stated limit, to be repeated in any write-up:** the check set is
**sufficient under M, necessary for reality** (§4.7, §11.5). A plan can satisfy
every check and still be operationally poor, because soundness depends on facts
the declared world cannot express. Saturating the checks licenses the claim
*"no resource use that is invalid in M"*. It never licenses *"good plan"*. If
that second claim ever starts being made, the trap has closed.

### 11.3 Held-out human read, never optimised against

The hand-check of 9 `Procedure` cases is the only reason P9's 46 % artifact was
caught rather than published as a planner finding. That mechanism is
institutionalised here:

- **Every** permitted intervention in §11.1 requires a **blind human re-read**
  of a held-out sample, judged without sight of the validator verdict.
- If validator-validity rises and blind human judgement does not, the
  intervention Goodharted — and this is how that becomes *detectable* rather
  than invisible.
- The human sample is **never** used to tune the checker, the prompt, or the
  ledger. It is read-only evidence.

### 11.4 The checker is frozen before any improvement work

The §4 ontology and family set, the §5 check registry, the interlock set, the
§6 flags, the ledger generator (§9/§9.1), and the §13 predictions and analysis
plan are **frozen** before the first permitted intervention is run.
Revising the instrument in response to improvement results is how any outcome
gets rationalised after the fact. Instrument revision belongs to the
measurement phase only, and every revision is logged with its date and reason.

### 11.5 What is claimed

The deliverable is the measurement: *a resource-grounded planning benchmark,
and a characterisation of how planners behave as available resources fall below
what the task requires.* That claim stands alone and carries no Goodhart
exposure.

**What an all-pass result means, stated exactly.** Earlier wording here —
"a necessary-conditions checker, not a sufficiency checker" — is superseded by
§4.7, which is sharper in both directions:

> **Sufficient under M, necessary for reality.** `RESOURCE-VALID` true means
> there is no way, *expressible in the declared world of §4.2*, for this plan
> to be resource-invalid. It does **not** mean the plan is operationally sound.
> Sequencing wrong for the casualty, a hazard absent from the ledger, a tow
> geometry a master would refuse — all pass.

The gap is not a defect to be apologised for; it is the declared scope, and
§4.7 explains why closing the world is the only thing that buys a sufficiency
claim at all. Every reported figure names M by reference, and no sentence in
the write-up asserts plan adequacy without it. A later *"and intervention X raised validity by N points"* is the
weaker claim and is where essentially all of the risk sits — it is permitted
only under §11.1–§11.4, and it is not what this study is for.

---

## 12. What is NOT in scope

- No validator-in-the-loop generation. (§2)
- No auto-repair of plans. (§2)
- No physics derivation by the model. (§7)
- No numeric adequacy engine (`physics.py`) in v1 — requirements are stated,
  not derived. Deferred, as in P9.
- No multi-casualty escalation dynamics. Those belong to
  `salvage_simulation.md`'s full temporal sim, which this is not.
- **No Track E work of any kind** — no intervention aimed at raising
  `RESOURCE-VALID`, no prompt search, no dev/test split, not even provisional
  design. Withheld until Track M is complete and frozen (§1); preconditions
  only in §14.5. Making plans *parse* is instrument conditioning and is in
  scope (§7, §8.1); making plans *better* is not.
- **No dynamic clock.** Note the earlier wording here ("no clock, no tide") is
  withdrawn: §9.1 makes a deadline universal across casualty types and the
  `OVERCOMMIT` trap depends on it. What is out of scope is a *simulated
  advancing* clock — time in RCP is a **static** pair (`eta_hours`,
  `deadline_h`) compared arithmetically at validation. Nothing ticks.

---

## 13. Pre-registered predictions and analysis plan

Fixed before any generation is run. This section exists because §1's claim, as
originally worded, could not be refuted by any outcome.

### 13.1 Directional predictions

Each is stated so that a specific result would refute it.

| | Prediction | Refuted by |
|---|---|---|
| **P1** | **correct-refusal** rate (§6.4 — `ESCALATE ∨ REDUCE` given not `LEDGER-SATISFIABLE`) rises `SURPLUS` → `SUFFICIENT` → `SCARCE` → `INFEASIBLE` | a flat or non-monotone profile |
| **P2** | `OVERCOMMIT` is **non-zero at `SUFFICIENT`** — the V2a deadline trap fires even where V3 totals are adequate | `OVERCOMMIT` ≈ 0 at `SUFFICIENT` |
| **P3** | `HALLUCINATE` rises as resources fall | a flat profile across arms |
| **P4** | `RESOURCE-VALID` at `SURPLUS` is substantially above `INFEASIBLE` | comparable rates, which would indicate the arms are not doing what they are built to do |
| **P5** | the §3.1 mechanism block does **not** collapse the primary channels V2a/V3 toward zero | violations ≈ 0 with the block and non-zero without |
| **P6** | **over-refusal** (§6.4 — `ESCALATE` given `LEDGER-SATISFIABLE`) stays low and does **not** rise with the arms | over-refusal rising in step with correct refusal, which would mean the planner escalates *more* rather than *better* |

**P1 and P6 are one prediction in two halves, and must be read together.** A
bare `ESCALATE` rate rising across arms is consistent with genuine competence
*and* with a planner that simply gives up more as the ledger thins. Only the
pair separates them — which is the whole reason §6.4 exists.

**P2 is the one worth being wrong about.** It is the prediction that most
directly tests whether the design's central trap — satisfying the sum while
missing the clock — is real behavior rather than a construct of the ledger
generator.

A null on all five is a reportable result, not a failed study: §1 designates
this a **measurement study**, so the estimands stand whatever direction they
take.

### 13.2 Analysis plan

**Primary.** One test: a **paired trend test** of `RESOURCE-VALID` across the
four ordered arms (same 110 images, §Q8), on the complete-case set (§8.1),
α = .05, two-sided. The arms are ordinal by construction, so a trend test is
both the correct form and a single comparison rather than six pairwise ones.

**Secondary, pre-specified:** V2b, V4a, V4b, V5, and the §6 flags per arm —
including `REDUCE` and both `OVERCOMMIT` decompositions (§6.3) and the two §6.4
rates — each with its extraction loss printed adjacent (§5).

**Manipulation check, reported before any of the above:** per-arm
`LEDGER-SATISFIABLE` fractions against §9.1's required values. A corpus failing
them is rejected, not interpreted.

**Instrument controls, printed beside every validity figure:** the §7 positive
and negative control outcomes, two lines, so no rate is ever read without
evidence that the instrument discriminates in both directions (§4.8). Either
control failing halts the run.

**Exploratory:** V6, `DEGRADE`, co-occurrence matrices, asset-count covariate
analysis, casualty-type breakdowns.

### 13.3 Multiplicity

Eight checks × four arms × four flags is a large comparison surface, and
nothing in earlier drafts said how it would be handled.

> **One confirmatory test** (§13.2 primary). Everything else is secondary or
> exploratory, reported as **point estimates with confidence intervals, not
> p-values**, and labelled as such in every table.

No correction is claimed, because no correction is needed where no inferential
claim is made. The failure mode being avoided is the one that makes a
multiplicity correction necessary in the first place: running thirty
comparisons and reporting the ones that moved. Per-arm, per-check rates are
**descriptive statistics of a characterisation study** and are reported
exhaustively — all of them, whatever they show.

### 13.4 Minimum detectable effect — a required pre-registration slot

A directional prediction with no stated resolution is only half
pre-registered: a null result is uninterpretable unless the design's smallest
detectable effect is on record *before* the data exist. Earlier drafts
committed to the direction of every prediction and to none of their
magnitudes.

> **The MDE for the §13.2 primary test is computed and written here before the
> §14.3 freeze. The freeze does not pass with this slot empty.**

| quantity | value |
|---|---|
| design | paired, four ordered arms, same 110 images (§Q8) |
| *n* | 110, less parse failures (complete-case, §8.1) |
| α | .05, two-sided; power target 0.80 |
| MDE, primary trend test | **to be computed** |
| MDE, `OVERCOMMIT` at `SUFFICIENT` (P2) | **to be computed** |

**P2 is the binding case, not P4.** P4 predicts a large `SURPLUS`-vs-
`INFEASIBLE` gap, for which 110 paired observations are comfortable. P2
predicts a rate that is merely *non-zero*, and if the true rate is small, 110
may not separate it from zero — in which case the honest pre-registration is
a one-sided interval on the rate rather than a test, decided now and not after
seeing it. Computing both numbers is what settles which form P2 takes.

This is the one open item in §13. Everything else in this section is fixed.

---

## 14. Maintaining this plan and the system it specifies

The design has already drifted inside this document — the check set was written
out in four places and three of them disagreed before consolidation. These
rules exist so that does not recur, and so the eventual implementation inherits
the same discipline.

### 14.1 Single source of truth

| Concept | Canonical location | Everywhere else |
|---|---|---|
| **ontology, predicate families, add/remove contract** | **§4** | reference only |
| assertion-block rules (1-3) + the tagged-line audit | **§3.1 / §3.2** | §7 and §11.1 reference only |
| what all-pass certifies; world-complexity criterion | **§4.7 / §4.8** | §11.2 and §11.5 reference only |
| check set, tiers, extraction loss | **§5** | reference by id only |
| behavioral flags, `REDUCE`, the §6.4 rates | **§6** | reference by name only |
| requirement tuple + per-casualty table | **§9.1** | reference only |
| ledger fields + arm multipliers | **§9** | reference only |
| `LEDGER-SATISFIABLE` + arm manipulation check | **§9.1** | reference only |
| predictions, analysis plan, MDE | **§13** | reference only |
| Track M / Track E boundary | **§1** | §14.5 holds preconditions only |

A section that restates one of these is a defect, whatever it says.

### 14.2 In code: registries, not branches

Each canonical table above maps to **one data structure**, not to scattered
conditionals:

- `checks.json` — the §5 registry. Adding `V2c` is one row plus one predicate,
  never an executor edit (§Q4).
- `requirements.json` — the §9.1 per-casualty tuple table.
- `flags.py` — §6, each flag a pure function of a scored plan, so the derived
  flags (`HALLUCINATE`, `OVERCOMMIT`) cannot drift from the checks they are
  defined by.

The invariant worth protecting: **a derived quantity is computed, never
re-specified.** `HALLUCINATE` is `¬V1` in code as it is in §6, not a second
implementation of the same idea.

### 14.3 Freeze and change control

§11.4 freezes the instrument before any improvement work. Operationally:

- Every change after the freeze is appended to a changelog with **date, what,
  why**, and whether it precedes or follows first generation.
- Superseded design text is **marked superseded, never deleted** — §Q5 and
  §Q11-old are the pattern. Decisions whose reasoning is lost get silently
  re-litigated.
- Post-freeze changes to §5, §6 or §13 invalidate the pre-registration and
  must be reported as such.
- **The freeze does not pass while §13.4's MDE table is unfilled.** A
  directional prediction with no stated resolution is only half
  pre-registered, and the form P2 takes (test or one-sided interval) depends on
  that number.
- **The freeze does not pass while the assertion file is untagged.** Every
  line must carry a **mechanism** / **realism** / **banned** tag and the banned
  ones must be gone (§3.2). An unaudited block puts the planner's output budget
  somewhere the endpoint does not score, which is the P9 artifact class moved
  to the input side.
- **The freeze is also what unlocks Track E** (§1, §14.5). Until Track M's
  per-arm rates are frozen, Track E has no baseline to be a delta against, so
  it is not designed.

### 14.4 Named extensions, not latent scope

Deferred with their definitions already fixed, so adding one is mechanical
rather than a fresh design argument:

| Extension | Unblocks | Fixed in |
|---|---|---|
| `V2c` / `V2d` / `V3b` channels | weather, crew, budget failure modes | §Q4 |
| route vocabulary | promotes `DEGRADE` out of exploratory | §6 |
| scheduling family (F8) | would restore a real V2b; needs planner-emitted times | §4.4 |
| assertion-block ablation | settles the §3.1 circularity objection with data | §3.1 |
| second generator model | the external-validity gap named in §Q2 | §Q2 |
| E5 feedback loop | world observations, never verdicts | §2, §8 |
| varying `Asset.status` | an availability failure channel; arrives as an F1 row | §4.6 |
| **Track E** | raising the rate at all | **§1, §14.5 — withheld until Track M is frozen** |

### 14.5 Track E — preconditions only, recorded so the deferral is free

§1 defers Track E in full: no design, no prompt search, no tuning until Track M
is complete and frozen. This subsection is **not** a Track E design. It records
the three things that must be true when Track E opens, because each of them
constrains something Track M does *now*, and discovering them later would mean
rerunning Track M.

**1. Track M's result is the base plate.** Track M runs on all 110 images with
no intervention aimed at the endpoint, and its per-arm rates are frozen under
§14.3 before Track E is designed. Track E's claim is always *a delta against
that*, which is why the baseline must exist first and must never have been
tuned against.

**2. Track E declares a dev/test split at its own start, not here.** Tuning on
all 110 and then reporting the improved rate on all 110 selects the
intervention on the test set — Goodhart with live selection pressure, which
§11 forbids as policy and had no mechanism to prevent. The mechanism:

> Track E carves a dev split from the 110, stratified on `state`
> (42 aground / 33 sunken / 19 capsized / 16 on_fire), tunes **only** there, and
> reports its improvement on the complement — compared against **Track M's
> rate recomputed on that same complement**, which is available without
> rerunning anything because Track M covered all 110.

That keeps the comparison paired and unbiased while costing no new inference.
The split's size is a Track E decision informed by §13.4's MDE, and is
deliberately not fixed here.

**3. The improvement target is arm-conditional.** "Maximise `RESOURCE-VALID`"
is the wrong objective, because at `INFEASIBLE` the rate *should* be low — the
task cannot be done, and a model scoring high there is overcommitting. With
§9.1's flag the objective is well-posed:

> **Track E objective: maximise `RESOURCE-VALID` on `LEDGER-SATISFIABLE`
> ledgers, and maximise correct refusal (§6.4) on the rest.**

A plan that overcommits on an unsatisfiable ledger scores zero on both terms,
so the objective cannot be met by the exact failure this study exists to
detect. Permitted interventions remain §11.1's Structural and Informational
classes in Track E as in Track M; Selective and Parametric stay banned in both.

