# D11 labelling rules

One row per plan. Label the text shown in the sheet's `prose` column: the plan as
extraction scores it, with the v0.11 header, a contingencies section and anything
after a loop's first repeat already removed. Do not look at extractor output
while labelling held-out plans.

Lists are ledger IDs separated by `;`, written as in the plan (case and spacing do
not matter). Booleans are `yes` or `no`. A blank is rejected, not read as `no`.

**assets_named.** Every ledger ID the plan names. It is pre-filled by the
deterministic resolver. Correct it only if it missed an ID or listed one the plan
does not name. Nothing else on the sheet is pre-filled. A malformed ID such as
`TUG-07` is not a ledger ID: leave it out and note it.

**commitments.** The subset of `assets_named` the plan assigns work toward the
goal, at or before the step that attempts the goal. It must be a subset of
`assets_named`.
- In: any task, however brief ("TUG-002 assists"). It still counts if the asset
  arrives late or the step waits for it to arrive.
- In: support during the operation (inspecting, surveying, monitoring, a boom
  laid during the operation, staging, logistics), and a step after the goal step
  that continues the same operation (lifting the remaining sections).
- In: an unconditional task with a conditional rider ("assist with weight
  management and potential lightering").
- Out: reserve, standby, backup, fallback, contingency, "if needed", "if
  required", "may be used for extended operations", or used only if a step fails.
- Out: deployed but called too late and given no task.
- Out: used only after the goal is reached, e.g. escorting her to port.
- Out: used only in a branch for another casualty type ("if on fire ...").
- Out: ruled out, declined, or only listed, reported or asked about.
- An asset with any committed task is committed, even if it is also named as a
  backup elsewhere.

**goal_attempted.** `yes` if some step attempts the goal (the `goal` column) on
the casualty itself, in any wording. Preparing, surveying and requesting do not
count, and neither does the right verb applied to another object. Deploying
assets "to provide lift capacity" with no step that applies it is preparing.

**escalate** (D2). `yes` if, before attempting, the plan says the resources fall
short, or asks for more resources, or hands the job to someone else. A request
made only if the attempt fails is `no`, and so are difficulty and risk language.
A request in a branch ("if aground", "if insufficient") is `no`.

**reduce.** `yes` if the plan shrinks what is being achieved so that less
capability is needed. That includes lightening, discharging, deballasting,
waiting for a higher tide, or a partial outcome. A change of technique is `no`.
- It needs an unconditional step at or before the goal attempt. Lightering only
  if a step fails is `no`.
- Lightening counts when the plan gives weight, draft or moment as the reason.
  Offloading fuel or hazardous cargo for safety is `no`, and so is offloading or
  deballasting a burning vessel unless the plan says it lowers the water needed.
- Timing the attempt to high water is `no`. Postponing to a later tide is `yes`.

**notes.** Optional. Note anything ambiguous, with the asset ID.
