"""The frozen corpus. plan.md §7.1, §12.2.

The generator is deterministic, but a deterministic *program* is not a frozen
*stimulus*: Python guarantees `random.random()` across versions and not
`uniform`/`choice`/`sample`/`shuffle`, and any edit to data/*.json silently moves
every downstream ledger. So the 440 scenarios are generated once, written to
`data/corpus.jsonl`, hashed into `data/corpus.sha256`, and every stage after the
generator — planner, extraction, controls, report, calibration, coverage — reads
that file and nothing else.

Two guards hang off it:

  * `load()` refuses a corpus whose bytes do not match the recorded sha256.
  * Every generation row carries `ledger_hash(sc)`, and extraction refuses a row
    whose hash does not match the frozen scenario it is scored against. A plan
    written against one ledger and scored against another is the one silent
    failure this pipeline could otherwise commit.

Regenerating and diffing against the frozen file (`python -m rcp.corpus --check`,
and Phase A) is the check that data/ has not moved since the freeze.

    python -m rcp.corpus --write    # (re)freeze: only before the run, never after
    python -m rcp.corpus --check    # regenerate and compare, exit 1 on drift
"""

from __future__ import annotations

import argparse
import dataclasses
import functools
import hashlib
import json
import pathlib
import sys

from .schema import Asset, Requirement, Scenario

DATA = pathlib.Path(__file__).resolve().parent.parent / "data"
CORPUS_FILE = DATA / "corpus.jsonl"
CORPUS_SHA = DATA / "corpus.sha256"


def to_dict(sc: Scenario) -> dict:
    d = dataclasses.asdict(sc)
    d["ledger"] = [dict(a) for a in d["ledger"]]
    return d


def from_dict(d: dict) -> Scenario:
    d = dict(d)
    d["requirement"] = Requirement(**d["requirement"])
    d["ledger"] = tuple(Asset(**a) for a in d["ledger"])
    return Scenario(**d)


def _line(sc: Scenario) -> str:
    return json.dumps(to_dict(sc), sort_keys=True, ensure_ascii=False)


def ledger_hash(sc: Scenario) -> str:
    """What the planner was shown, as a digest: the cell, its requirement and its
    ledger. Written into every generation row and checked at extraction."""
    d = to_dict(sc)
    payload = {k: d[k] for k in ("id", "arm", "requirement", "ledger")}
    return hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()


def render_bytes(scenarios: list[Scenario]) -> bytes:
    return "".join(_line(s) + "\n" for s in scenarios).encode("utf-8")


def write(scenarios: list[Scenario], path: pathlib.Path = CORPUS_FILE,
          sha_path: pathlib.Path = CORPUS_SHA) -> str:
    blob = render_bytes(scenarios)
    path.write_bytes(blob)
    digest = hashlib.sha256(blob).hexdigest()
    sha_path.write_text(f"{digest}  {path.name}\n", encoding="utf-8")
    return digest


def recorded_sha(sha_path: pathlib.Path = CORPUS_SHA) -> str:
    return sha_path.read_text(encoding="utf-8").split()[0]


@functools.lru_cache(maxsize=None)
def _load(path: str, sha_path: str) -> tuple[Scenario, ...]:
    p, sp = pathlib.Path(path), pathlib.Path(sha_path)
    if not p.exists() or not sp.exists():
        raise FileNotFoundError(
            f"no frozen corpus at {p} — run `python -m rcp.corpus --write` (before "
            "inference only; regenerating after it would change what was scored)")
    blob = p.read_bytes()
    got, want = hashlib.sha256(blob).hexdigest(), recorded_sha(sp)
    if got != want:
        raise ValueError(f"{p.name} sha256 {got[:12]}… does not match the recorded "
                         f"{want[:12]}… — the frozen corpus was edited")
    return tuple(from_dict(json.loads(ln)) for ln in blob.decode("utf-8").splitlines()
                 if ln.strip())


def load(path: pathlib.Path = CORPUS_FILE,
         sha_path: pathlib.Path = CORPUS_SHA) -> list[Scenario]:
    """The 440 scenarios as frozen, sha-checked."""
    return list(_load(str(path), str(sha_path)))


def by_key(path: pathlib.Path = CORPUS_FILE) -> dict[str, Scenario]:
    """`{"<id>/<arm>": Scenario}`, the key generation rows use."""
    return {f"{s.id}/{s.arm}": s for s in load(path)}


def regenerate() -> list[Scenario]:
    from .generator import build_corpus, manifest

    return build_corpus(manifest())


def drift() -> list[str]:
    """Keys whose regenerated scenario differs from the frozen one (plus any key
    present on one side only). Empty means data/ and the generator still produce
    exactly the frozen corpus."""
    frozen = {f"{s.id}/{s.arm}": _line(s) for s in load()}
    fresh = {f"{s.id}/{s.arm}": _line(s) for s in regenerate()}
    return sorted(k for k in frozen.keys() | fresh.keys() if frozen.get(k) != fresh.get(k))


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Freeze or check data/corpus.jsonl")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--write", action="store_true", help="regenerate and freeze")
    g.add_argument("--check", action="store_true",
                   help="regenerate and compare against the frozen corpus")
    args = ap.parse_args(argv)
    if args.write:
        corpus = regenerate()
        digest = write(corpus)
        _load.cache_clear()
        print(f"  {len(corpus)} scenarios -> {CORPUS_FILE}\n  sha256 {digest}")
        return 0
    bad = drift()
    if bad:
        print(f"  DRIFT: {len(bad)} scenarios differ from the frozen corpus, "
              f"e.g. {bad[:3]}", file=sys.stderr)
        return 1
    print(f"  frozen corpus matches regeneration ({recorded_sha()[:12]}…)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
