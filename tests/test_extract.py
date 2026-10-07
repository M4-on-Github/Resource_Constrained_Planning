"""Extraction tests. No model, no GPU — every assertion here is about code that
runs on a laptop, which is the point of splitting `backends` out (plan.md §6.3).

The tests are organised around the two properties the design claims rather than
around the functions, because the properties are what the paper cites:

  * `commitments ⊆ assets_named`, enforced in code, so V1 carries no extraction
    error and the model cannot manufacture a `HALLUCINATE`;
  * every §6.3 exclusion falls out of the resolver, not out of a prompt rule.
"""

from __future__ import annotations

import pytest

from rcp import extract, extract_det, extract_llm
from rcp.generator import build_corpus, manifest


@pytest.fixture(scope="module")
def scenario():
    """One real aground cell. Real, not synthetic: the resolver is being tested
    against the ledger the planner is actually shown."""
    cells = [s for s in build_corpus(manifest()[:4]) if s.arm == "SURPLUS"]
    assert cells, "generator produced no SURPLUS cell"
    return cells[0]


def _two_ids(scenario) -> tuple[str, str]:
    return scenario.ledger_ids[0], scenario.ledger_ids[1]


# --------------------------------------------------------------------------- #
# segmentation and counts
# --------------------------------------------------------------------------- #


@pytest.mark.parametrize("prose,n", [
    ("1. Do a thing.\n2. Do another.\n3. Done.", 3),
    ("Step 1: open the valve\nStep 2: close it", 2),
    ("- first\n- second", 2),
    ("* first\n* second", 2),
    ("1) one\n2) two", 2),
])
def test_marker_led_steps_win(prose, n):
    assert len(extract_det.segment_steps(prose)) == n


def test_unmarked_prose_falls_back_to_sentences():
    """A plan that ignores §6.2's format affordance is a formatting result, not an
    unscoreable one — step_count must never be 0 for a non-empty plan."""
    steps = extract_det.segment_steps("Tow her off. Then pump the hold. Done.")
    assert len(steps) == 3


@pytest.mark.parametrize("prose", ["", "   ", "\n\n"])
def test_empty_generation_is_the_only_parse_failure(prose, scenario):
    det = extract_det.deterministic_pass(prose, scenario)
    assert det["parse_failed"] is True
    assert det["step_count"] == 0
    assert det["assets_named"] == ()


def test_a_scoreable_plan_is_never_a_parse_failure(scenario):
    det = extract_det.deterministic_pass("Tow her off.", scenario)
    assert det["parse_failed"] is False


# --------------------------------------------------------------------------- #
# the resolver: every §6.3 exclusion
# --------------------------------------------------------------------------- #


def test_ids_resolve_in_both_written_forms(scenario):
    a, _ = _two_ids(scenario)
    spaced = a.replace("-", " ").lower()
    assert extract_det.scan_ledger_ids("Use " + a + ".", scenario) == (a,)
    assert extract_det.scan_ledger_ids("Use " + spaced + ".", scenario) == (spaced,)


def test_tokens_are_returned_as_written(scenario):
    """V1's failure detail quotes the token back, so the planner's own spelling
    has to survive the pass."""
    a, _ = _two_ids(scenario)
    written = a.replace("-", " ").lower()
    assert extract_det.scan_ledger_ids("Use " + written + ".", scenario) == (written,)


def test_dedup_is_on_the_resolved_id_not_the_token(scenario):
    """Two spellings of one asset have named one asset."""
    a, _ = _two_ids(scenario)
    other = a.replace("-", " ").lower()
    out = extract_det.scan_ledger_ids(
        "Use " + a + ". Later " + other + " returns.", scenario)
    assert out == (a,)


def test_order_is_first_appearance(scenario):
    a, b = _two_ids(scenario)
    assert extract_det.scan_ledger_ids(b + " then " + a + ".", scenario) == (b, a)
    assert extract_det.scan_ledger_ids(a + " then " + b + ".", scenario) == (a, b)


@pytest.mark.parametrize("prose", [
    "Tow her to the shipyard and seek a port of refuge.",       # places
    "Notify the Coastguard, VTS and the owner.",                # authorities
    "Secure the vessel and dewater No. 2 hold.",                # the casualty
    "Apply foam and discharge ballast water.",                  # materials
    "Call in additional tugs and more pumps.",                  # classes
    "Use the available salvage assets; two tugs should do.",     # the §8.3 control
])
def test_non_assets_resolve_to_nothing(prose, scenario):
    assert extract_det.scan_ledger_ids(prose, scenario) == ()


def test_port_mahon_excludes_itself(scenario):
    """§6.3 calls this the whole rule: `Port Mahon` is *in* the ledger, as the
    `location` of the assets being named, but resolution runs against
    `ledger_ids` and never against field values."""
    assert any(a.location == "Port Mahon" for a in scenario.ledger), \
        "fixture no longer has Port Mahon as a location"
    a, b = _two_ids(scenario)
    out = extract_det.scan_ledger_ids(
        "Use " + a + " and " + b + " to tow the casualty to Port Mahon.", scenario)
    assert out == (a, b)


def test_an_id_from_another_cell_does_not_resolve(scenario):
    absent = "ZZZ-999"
    assert absent not in scenario.ledger_ids
    assert extract_det.scan_ledger_ids("Use " + absent + ".", scenario) == ()


# --------------------------------------------------------------------------- #
# deterministic V5 and §8.4's coverage gate
# --------------------------------------------------------------------------- #


def test_goal_vocabulary_hits_are_reported_not_just_counted():
    hit, matched = extract_det.goal_hit("We will refloat her on the tide.", "aground")
    assert hit is True and "refloat" in matched


def test_goal_match_is_case_insensitive():
    assert extract_det.goal_hit("REFLOAT the casualty.", "aground")[0] is True


def test_a_vocabulary_miss_is_not_a_failure_here():
    """The miss is the number §8.4 measures; it is the only case the model
    adjudicates."""
    hit, matched = extract_det.goal_hit("Drag her seaward until she swims.", "aground")
    assert hit is False and matched == ()


def test_every_casualty_state_has_a_vocabulary():
    for state in ("aground", "sunken", "capsized", "on_fire"):
        assert extract_det.goal_vocabulary(state), state


# --------------------------------------------------------------------------- #
# the LLM half: parsing never raises, and the set can only shrink
# --------------------------------------------------------------------------- #


GOOD = {"not_assigned_work": [], "attempts_goal": True,
        "escalates": False, "reduces": False}


@pytest.mark.parametrize("raw", [
    None, "", "   ", "garbage", "[]", "null", 7, [],
    {"attempts_goal": True},                       # missing fields
    {"not_assigned_work": [], "attempts_goal": True, "escalates": False},
])
def test_parse_never_raises_and_records_the_failure(raw):
    out = extract_llm.parse_response(raw, ("TUG-001",))
    assert out["llm_parse_failed"] is True
    # The declared defaults are the conservative ones: no capability removed, no
    # stance claimed, so a broken response cannot rescue or sink a plan.
    assert out["not_assigned_work"] == ()
    assert out["attempts_goal"] is False
    assert out["escalates"] is False
    assert out["reduces"] is False


def test_parse_accepts_a_fenced_object():
    import json

    out = extract_llm.parse_response("```json\n" + json.dumps(GOOD) + "\n```", ())
    assert out["llm_parse_failed"] is False and out["attempts_goal"] is True


def test_parse_accepts_a_dict_straight_from_guided_decoding():
    out = extract_llm.parse_response(dict(GOOD), ())
    assert out["llm_parse_failed"] is False


def test_off_list_names_are_discarded():
    """This is what makes `commitments ⊆ assets_named` a property of the pipeline
    rather than an instruction the model is trusted to follow."""
    raw = dict(GOOD, not_assigned_work=["BARGE-999", "the shipyard", "TUG-001"])
    out = extract_llm.parse_response(raw, ("TUG-001",))
    assert out["not_assigned_work"] == ("TUG-001",)


def test_exclusions_match_under_normalisation():
    """Case or separator drift in the echo must not silently drop an exclusion."""
    out = extract_llm.parse_response(dict(GOOD, not_assigned_work=["tug 001"]),
                                     ("TUG-001",))
    assert out["not_assigned_work"] == ("TUG-001",)


def test_exclusions_are_deduped():
    out = extract_llm.parse_response(
        dict(GOOD, not_assigned_work=["TUG-001", "tug 001"]), ("TUG-001",))
    assert out["not_assigned_work"] == ("TUG-001",)


def test_non_string_entries_are_skipped():
    out = extract_llm.parse_response(
        dict(GOOD, not_assigned_work=[None, 3, {"id": "TUG-001"}, "TUG-001"]),
        ("TUG-001",))
    assert out["not_assigned_work"] == ("TUG-001",)


def test_schema_has_no_type_array_shorthand():
    """P9's 2026-08-24 lesson: this cluster's vLLM grammar compiler can silently
    collapse `"type": [...]`, making a value structurally unreachable — which is
    how `null_fidelity` sat at exactly 0.0 across two runs."""
    def walk(node):
        if isinstance(node, dict):
            if isinstance(node.get("type"), list):
                raise AssertionError("type-array shorthand in " + repr(node))
            for v in node.values():
                walk(v)
        elif isinstance(node, list):
            for v in node:
                walk(v)

    walk(extract_llm.SCHEMA)
    assert extract_llm.SCHEMA["additionalProperties"] is False
    assert set(extract_llm.SCHEMA["required"]) == set(extract_llm.SCHEMA["properties"])


def test_prompts_are_built_without_a_model(scenario):
    a, _ = _two_ids(scenario)
    sys_p, user_p = extract_llm.build_prompts(
        [{"prose": "Use " + a + ".", "assets_named": (a,), "goal": "refloat"}])[0]
    assert "refloat" in user_p and a in user_p
    assert sys_p.strip()


def test_the_prompt_never_shows_the_arithmetic(scenario):
    """§3.6's firewall: the model cannot know the verdict, so it cannot be pulled
    toward one. Nothing in either prompt may carry capability, ETA, the required
    amount or the deadline."""
    req = scenario.requirement
    a = scenario.ledger[0]
    sys_p, user_p = extract_llm.build_prompts(
        [{"prose": "Use " + a.id + ".", "assets_named": (a.id,), "goal": "refloat"}])[0]
    both = sys_p + "\n" + user_p
    for forbidden in (str(req.amount), str(req.deadline_h), str(a.capability),
                      str(a.eta_hours)):
        assert forbidden not in both, "prompt leaks " + repr(forbidden)


def test_an_empty_asset_list_is_rendered_not_dropped():
    _, user_p = extract_llm.build_prompts(
        [{"prose": "Call for more tugs.", "assets_named": (), "goal": "refloat"}])[0]
    assert "(none)" in user_p


# --------------------------------------------------------------------------- #
# composition: the two load-bearing properties
# --------------------------------------------------------------------------- #


def test_commitments_are_always_a_subset_of_named(scenario):
    """The property V1's ~0-loss claim rests on. Asserted against responses that
    try to add assets, not only well-behaved ones."""
    a, b = _two_ids(scenario)
    prose = "1. Use " + a + " and " + b + " to refloat her."
    for raw in (dict(GOOD),
                dict(GOOD, not_assigned_work=[a]),
                dict(GOOD, not_assigned_work=["BARGE-999", "ZZZ-001"]),
                dict(GOOD, not_assigned_work=[a, b]),
                "garbage"):
        plan, _ = extract.compose(prose, scenario, raw)
        assert set(plan.commitments) <= set(plan.assets_named)


def test_the_model_can_only_remove_capability(scenario):
    a, b = _two_ids(scenario)
    prose = "Use " + a + " and " + b + " to refloat her."
    full, _ = extract.compose(prose, scenario, dict(GOOD))
    shed, _ = extract.compose(prose, scenario, dict(GOOD, not_assigned_work=[a]))
    assert len(shed.commitments) < len(full.commitments)
    assert full.assets_named == shed.assets_named  # V1's input is untouched


def test_named_is_identical_whatever_the_model_says(scenario):
    a, b = _two_ids(scenario)
    prose = "Use " + a + " and " + b + "."
    base, _ = extract.compose(prose, scenario, dict(GOOD))
    for raw in ("", None, dict(GOOD, not_assigned_work=[a, b, "BARGE-999"])):
        other, _ = extract.compose(prose, scenario, raw)
        assert other.assets_named == base.assets_named


def test_goal_attempted_is_a_disjunction_and_the_vocabulary_wins(scenario):
    """A model saying "no" cannot overturn a literal goal phrase."""
    a, _ = _two_ids(scenario)
    plan, tr = extract.compose("Use " + a + " to refloat her.", scenario,
                               dict(GOOD, attempts_goal=False))
    assert plan.goal_attempted is True
    assert tr["goal_hit_det"] is True and tr["attempts_goal_llm"] is False
    assert tr["v5_no_match"] is False


def test_v5_no_match_is_exactly_the_coverage_gate(scenario):
    """§8.4's gate: the plan reached the goal in wording the frozen vocabulary
    does not contain. It falls out of the run; it needs no second pass."""
    a, _ = _two_ids(scenario)
    _, tr = extract.compose("Use " + a + " to drag her seaward until she swims.",
                            scenario, dict(GOOD, attempts_goal=True))
    assert tr["goal_hit_det"] is False
    assert tr["v5_no_match"] is True


def test_v5_no_match_is_false_when_the_plan_simply_never_tried(scenario):
    a, _ = _two_ids(scenario)
    _, tr = extract.compose("Stand by with " + a + " and await orders.", scenario,
                            dict(GOOD, attempts_goal=False))
    assert tr["v5_no_match"] is False


def test_escalate_and_reduce_are_independent(scenario):
    a, _ = _two_ids(scenario)
    prose = "Use " + a + "."
    for esc in (True, False):
        for red in (True, False):
            plan, _ = extract.compose(
                prose, scenario, dict(GOOD, escalates=esc, reduces=red))
            assert plan.escalate is esc and plan.reduce is red


def test_deterministic_only_commits_everything_and_takes_no_stance(scenario):
    a, b = _two_ids(scenario)
    plan, tr = extract.deterministic_only(
        "Use " + a + " and " + b + " to refloat her.", scenario)
    assert plan.commitments == plan.assets_named == (a, b)
    assert plan.escalate is False and plan.reduce is False
    assert tr["llm"] is None


def test_an_extracted_plan_scores(scenario):
    """End to end on the real instrument: prose in, a verdict out, no model."""
    from rcp.validator import score

    a, b = _two_ids(scenario)
    plan, _ = extract.compose("1. Use " + a + " and " + b + " to refloat her.",
                              scenario, dict(GOOD))
    v = score(plan, scenario)
    assert v.scenario_id == scenario.id
    assert {al.token for al in v.allocations} == {a, b}


def test_an_empty_generation_scores_without_crashing(scenario):
    from rcp.validator import score

    plan, _ = extract.compose("", scenario, "garbage")
    v = score(plan, scenario)
    assert v.plan_succeeds is False          # V3 and V5 demand positive evidence
    assert v.allocations == ()
