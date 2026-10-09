"""The planner prompt. plan.md Rule 2, sec. 6.1, sec. 6.2, sec. 7.2.

Rule 2 says nothing in the prompt may indicate which constraint binds. Its
enforceable form is byte-identity: the domain half and the task half are constant
across all 110 scenarios and all four arms, and only the scenario block varies.
That is what most of this file asserts, because it is the one property that turns
"audit every sentence against every scenario" into one failing test.
"""

from __future__ import annotations

import re

import pytest

from rcp.generator import build_corpus, manifest
from rcp.render import (
    CONDITIONS,
    domain_block,
    domain_digest,
    ledger_table,
    planner_prompt,
    scenario_block,
    task_block,
    totals_line,
)
from rcp.schema import Asset, Requirement, Scenario
from rcp.validator import ledger_satisfiable, ratio_deadline, ratio_fleet

REQ = Requirement(goal="refloat", quantity="bollard_pull", unit="t",
                  amount=120, deadline_h=6.0, deadline_driver="high water")


def tug(n: str, cap: float, eta: float, quantity: str | None = "bollard_pull") -> Asset:
    return Asset(id=n, type="asd_tug", label="ASD tug", capability=cap, unit="t",
                 location="Valletta", eta_hours=eta, quantity=quantity)


def scenario(*assets: Asset, arm: str = "SUFFICIENT") -> Scenario:
    """A hand-built cell. The ratios are recomputed rather than passed in, so a
    fixture can never disagree with the validator about its own world."""
    ledger = tuple(assets)
    return Scenario(id="AGR-00001", arm=arm, casualty_state="aground",
                    size_category="large", requirement=REQ, ledger=ledger,
                    is_trap=False,
                    ratio_fleet=ratio_fleet(REQ, ledger),
                    ratio_deadline=ratio_deadline(REQ, ledger),
                    ledger_satisfiable=ledger_satisfiable(REQ, ledger))


@pytest.fixture(scope="module")
def sample():
    """A few real scenarios from the frozen corpus, all four arms each."""
    return list(build_corpus(manifest()[:6]))


# --------------------------------------------------------------------------- #
# Rule 2, in its enforceable form
# --------------------------------------------------------------------------- #


def test_the_constant_halves_are_byte_identical_across_every_cell(sample):
    """Across every cell *and* every disclosure condition.

    The condition loop is the point: the disclosure manipulation lives in the
    scenario block precisely so Rule 2's byte-identity property survives it
    untouched, and a future edit that moved the disclosure line into the domain
    block would be invisible without this loop.
    """
    d, t = domain_block(), task_block()
    for cond in CONDITIONS:
        for sc in sample:
            p = planner_prompt(sc, cond)
            assert p.startswith(d), f"{sc.id}/{sc.arm}/{cond}: domain half drifted"
            assert p.endswith(t), f"{sc.id}/{sc.arm}/{cond}: task half drifted"


def test_the_prompt_is_exactly_three_blocks(sample):
    """Nothing is interpolated between the halves except the scenario block."""
    for cond in CONDITIONS:
        for sc in sample:
            assert planner_prompt(sc, cond) == "\n\n".join(
                [domain_block(), scenario_block(sc, cond), task_block()])


def test_the_domain_half_never_mentions_an_arm_name(sample):
    lowered = (domain_block() + task_block()).lower()
    for word in ("surplus", "sufficient", "scarce", "infeasible"):
        assert word not in lowered, f"the constant halves name the arm: {word}"


def test_the_domain_half_never_says_what_to_do_when_resources_fall_short():
    """Rule 1: assertions state facts about resources, never the remedy."""
    text = domain_block().lower()
    for phrase in ("if you cannot", "if there are not enough", "if insufficient",
                   "escalate if", "request more if", "when resources are"):
        assert phrase not in text, f"Rule 1 violated by: {phrase!r}"


def test_the_task_half_forbids_conditional_steps_without_naming_a_remedy():
    """The no-branching guard (plan.md §6.2) is a format rule. It must not say
    what to do when resources fall short, or it becomes an escalation cue."""
    t = task_block().lower()
    assert "do not write conditional steps" in t
    guard = next(ln for ln in t.splitlines() if "conditional" in ln)
    for word in ("resource", "enough", "short", "insufficient", "escalat", "request"):
        assert word not in guard, word
    assert "include any assumptions, limitations, or requests" in t


def test_the_digest_is_stable_and_covers_both_halves():
    assert domain_digest() == domain_digest()
    assert len(domain_digest()) == 64


# --------------------------------------------------------------------------- #
# the disclosure manipulation
# --------------------------------------------------------------------------- #


def test_the_two_conditions_have_different_digests():
    """The digest is the one mechanism that refuses to pool two runs.

    The disclosure line changes neither constant file, so without hashing the
    condition label the two runs would share a digest and could be concatenated
    without complaint -- the exact failure the digest exists to catch.
    """
    assert domain_digest("blind") != domain_digest("stated")
    assert len({domain_digest(c) for c in CONDITIONS}) == len(CONDITIONS)


def test_an_unknown_condition_is_rejected_everywhere_it_is_accepted(sample):
    sc = sample[0]
    for call in (lambda: domain_digest("disclosed"),
                 lambda: scenario_block(sc, "disclosed"),
                 lambda: planner_prompt(sc, "disclosed")):
        with pytest.raises(ValueError):
            call()


def test_stated_adds_exactly_one_line_and_changes_nothing_else(sample):
    """One headline variable: the two prompts differ by the disclosure line alone.

    Pruning the other three casualty states' guidance from the domain block would
    look more natural and is wrong -- it would vary disclosure and prompt length
    together, so a difference could be attributed to neither. This asserts the
    version we chose: remove the inserted line and its blank from `stated` and
    `blind` comes back byte for byte.
    """
    for sc in sample:
        blind = planner_prompt(sc, "blind")
        stated = planner_prompt(sc, "stated")
        lines = stated.split("\n")
        added = [ln for ln in lines if ln and ln not in blind.split("\n")]
        assert len(added) == 1, f"{sc.id}/{sc.arm}: {len(added)} lines differ"
        assert added[0].startswith("Confirmed casualty state:")
        i = lines.index(added[0])
        assert lines[i + 1] == "", "the disclosure must be followed by a blank line"
        assert "\n".join(lines[:i] + lines[i + 2:]) == blind


def test_the_disclosure_line_names_the_state_and_nothing_about_adequacy(sample):
    """Rule 2 again: disclosing the casualty must not disclose the resource answer."""
    for sc in sample:
        line = [ln for ln in scenario_block(sc, "stated").split("\n")
                if ln.startswith("Confirmed casualty state:")][0]
        lowered = line.lower()
        for word in ("surplus", "sufficient", "scarce", "infeasible",
                     "enough", "insufficient", "escalate", "ratio"):
            assert word not in lowered, f"disclosure line leaks: {word}"
        assert sc.casualty_state.replace("_", " ") in lowered


def test_blind_is_the_default_so_existing_callers_are_unchanged(sample):
    for sc in sample:
        assert planner_prompt(sc) == planner_prompt(sc, "blind")
        assert scenario_block(sc) == scenario_block(sc, "blind")
    assert domain_digest() == domain_digest("blind")


def test_the_escalate_affordance_is_present_and_unconditional():
    """sec. 6.2: the affordance must exist, or over-refusal has no numerator --
    but it must not be attached to a condition, or it becomes a hint (Rule 2)."""
    t = task_block().lower()
    assert "assumptions" in t and "limitations" in t and "requests" in t
    assert " if " not in t.split("assumptions")[0][-120:]


# --------------------------------------------------------------------------- #
# the scenario block: sec. 7.2 and nothing more
# --------------------------------------------------------------------------- #


def test_the_ledger_is_sorted_by_id_not_by_eta():
    sc = scenario(tug("TUG-003", 50, 1.0), tug("TUG-001", 50, 9.0),
                  tug("TUG-002", 50, 5.0))
    ids = [ln.split()[0] for ln in ledger_table(sc).splitlines()[2:]]
    assert ids == ["TUG-001", "TUG-002", "TUG-003"]


def test_the_ledger_header_is_section_7_2s_column_order():
    sc = scenario(tug("TUG-001", 50, 1.0))
    assert ledger_table(sc).splitlines()[0].split() == [
        "ID", "TYPE", "CAPABILITY", "LOCATION", "ETA_H", "STATUS"]


def test_capability_renders_figure_unit_then_scalar():
    """`quantity` is the scalar dimension name, not a count."""
    sc = scenario(tug("TUG-001", 120, 1.0))
    assert "120 t bollard pull" in ledger_table(sc)


def test_a_distractor_renders_its_own_scalar_rather_than_a_blank():
    boom = Asset(id="BOOM-001", type="oil_boom_set", label="Oil boom set",
                 capability=600, unit="m", location="Valletta", eta_hours=2.0,
                 quantity="boom_length")
    assert "600 m boom length" in ledger_table(scenario(boom))


def test_both_totals_are_stated_and_neither_is_labelled_as_the_binding_one():
    """The sec. 7.2 trap: fleet clears the requirement, by-deadline does not."""
    sc = scenario(tug("TUG-001", 80, 1.0), tug("TUG-002", 80, 20.0))
    line = totals_line(sc)
    assert "80 t combined bollard pull" in line     # on scene by 6 h
    assert "160 t at 20.0 h" in line                # full fleet
    for leak in ("insufficient", "not enough", "cannot", "short of", "meets",
                 "satisfies", "enough"):
        assert leak not in line.lower(), f"the totals line gives the verdict away: {leak}"


def test_the_scenario_block_never_states_the_ratio_or_the_arm(sample):
    for sc in sample:
        b = scenario_block(sc).lower()
        assert "ratio" not in b
        assert sc.arm.lower() not in b


def test_the_scenario_block_states_the_requirement_with_its_deadline_driver():
    sc = scenario(tug("TUG-001", 50, 1.0))
    b = scenario_block(sc)
    assert "120 t bollard pull" in b
    assert "within 6.0 hours (high water)" in b


def test_only_the_scenario_block_changes_between_arms_of_one_image(sample):
    by_image: dict[str, dict[str, str]] = {}
    for sc in sample:
        by_image.setdefault(sc.id, {})[sc.arm] = planner_prompt(sc)
    for arms in by_image.values():
        heads = {p[:len(domain_block())] for p in arms.values()}
        assert len(heads) == 1


def test_the_prompt_is_ascii(sample):
    """SLURM logs and the console mangle anything else (see report.render)."""
    for sc in sample[:4]:
        bad = [c for c in planner_prompt(sc) if ord(c) > 127]
        assert bad == [], f"non-ascii in the prompt: {set(bad)}"


def test_no_markdown_table_in_the_prompt(sample):
    """sec. 6.2 forbids one in the output; offering one in the input is the cue."""
    for sc in sample[:4]:
        assert not re.search(r"^\s*\|.*\|\s*$", planner_prompt(sc), re.M)
