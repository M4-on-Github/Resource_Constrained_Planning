"""Register a finished run: checksum it, make it read-only, archive it, index it.

`results/` is gitignored, so a run's outputs live on one disk and nothing in git
says what they were. Freezing a run writes `runs/<name>.json` (tracked): every
file's sha256, size and line count, the jobs that wrote them (from the
`*.env.jsonl` / `env.jsonl` records the stages already write), and the repo
commit at freeze time. The files are then made read-only, so a later stage that
points at them fails instead of overwriting, and copied to a read-only archive on
the /data volume. `verify` rechecks every registered file and its archive copy.

    python3 tools/runs.py freeze v011_full_gen --purpose "..." results/v011/gen_*
    python3 tools/runs.py verify            # every registered run
    python3 tools/runs.py verify v010       # one

Standard library only (runs on the host's python3.6 as well as in a container).
See runs/README.md for the layout and the naming rule.
"""

import argparse
import datetime
import hashlib
import json
import os
import pathlib
import shutil
import stat
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
RUNS = REPO / "runs"
ARCHIVE = pathlib.Path(os.path.expandvars("/data/$USER/rcp_archive"))

#: Fields kept from each environment record; the rest (package lists) stay in the
#: record itself, which is one of the frozen files.
ENV_KEYS = ("run_id", "stage", "host", "gpu", "time_utc", "git_commit", "git_dirty",
            "condition", "arms", "domain_digest", "max_tokens", "dtype", "input",
            "weights_sha256", "container_sha256", "corpus_sha256")


def sha256(path):
    h = hashlib.sha256()
    with open(str(path), "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def rel(path):
    p = pathlib.Path(path).resolve()
    try:
        return str(p.relative_to(REPO))
    except ValueError:
        return str(p)


def expand(paths):
    files = []
    for p in paths:
        p = pathlib.Path(p)
        if p.is_dir():
            files += sorted(x for x in p.rglob("*") if x.is_file())
        elif p.is_file():
            files.append(p)
        else:
            sys.exit("ERROR: no such file or directory: {}".format(p))
    return sorted(set(f.resolve() for f in files))


def head_commit():
    try:
        out = subprocess.check_output(["git", "-C", str(REPO), "rev-parse", "HEAD"])
        dirty = subprocess.check_output(["git", "-C", str(REPO), "status", "--porcelain"])
        return out.decode().strip(), bool(dirty.strip())
    except (OSError, subprocess.CalledProcessError):
        return None, None


def jobs_from(files):
    jobs = []
    for f in files:
        if not (f.name == "env.jsonl" or f.name.endswith(".env.jsonl")):
            continue
        for line in f.read_text(encoding="utf-8").splitlines():
            if line.strip():
                r = json.loads(line)
                jobs.append(dict({k: r[k] for k in ENV_KEYS if k in r}, record=rel(f)))
    return jobs


def readonly(path):
    mode = os.stat(str(path)).st_mode
    os.chmod(str(path), mode & ~(stat.S_IWUSR | stat.S_IWGRP | stat.S_IWOTH))


def registered():
    """path -> run name, over every registered run."""
    owner = {}
    for j in sorted(RUNS.glob("*.json")):
        for f in json.loads(j.read_text(encoding="utf-8"))["files"]:
            owner[f["path"]] = j.stem
    return owner


def freeze(args):
    entry = RUNS / "{}.json".format(args.name)
    if entry.exists():
        sys.exit("ERROR: {} exists; a run is registered once. Pick a new name.".format(rel(entry)))
    files = expand(args.paths)
    owner = registered()
    clash = [rel(f) for f in files if rel(f) in owner]
    if clash:
        sys.exit("ERROR: already registered: {} (run {})".format(clash[0], owner[clash[0]]))
    archive = ARCHIVE / args.name
    if not args.no_archive and archive.exists():
        sys.exit("ERROR: archive {} exists".format(archive))

    commit, dirty = head_commit()
    rows = []
    for f in files:
        data = f.read_bytes()
        rows.append({"path": rel(f), "sha256": sha256(f), "bytes": len(data),
                     "lines": data.count(b"\n")})
    rec = {
        "name": args.name,
        "purpose": args.purpose,
        "frozen_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
        "repo_commit_at_freeze": commit,
        "repo_dirty_at_freeze": dirty,
        "archive": None if args.no_archive else str(archive),
        "jobs": jobs_from(files),
        "files": rows,
    }

    for f in files:
        if not args.no_archive:
            r = rel(f)
            dest = archive / (r if not r.startswith("/") else r.lstrip("/"))
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(str(f), str(dest))
            readonly(dest)
        readonly(f)

    RUNS.mkdir(exist_ok=True)
    entry.write_text(json.dumps(rec, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    index = RUNS / "README.md"
    with index.open("a", encoding="utf-8") as fh:
        fh.write("| `{}` | {} | {} | {} |\n".format(
            args.name, rec["frozen_utc"][:10], len(rows), args.purpose.replace("|", "/")))
    print("froze {} files -> {}{}".format(
        len(rows), rel(entry), "" if args.no_archive else ", archive " + str(archive)))
    print("files are now read-only; commit {} and runs/README.md".format(rel(entry)))
    return 0


def verify(args):
    names = args.names or sorted(j.stem for j in RUNS.glob("*.json"))
    bad = 0
    for name in names:
        rec = json.loads((RUNS / "{}.json".format(name)).read_text(encoding="utf-8"))
        problems = []
        for f in rec["files"]:
            p = pathlib.Path(f["path"])
            p = p if p.is_absolute() else REPO / p
            copies = [("", p)]
            if rec.get("archive"):
                copies.append(("archive ", pathlib.Path(rec["archive"]) / f["path"].lstrip("/")))
            for label, c in copies:
                if not c.exists():
                    problems.append("{}missing: {}".format(label, f["path"]))
                elif sha256(c) != f["sha256"]:
                    problems.append("{}changed: {}".format(label, f["path"]))
                elif os.access(str(c), os.W_OK):
                    problems.append("{}writable: {}".format(label, f["path"]))
        bad += bool(problems)
        print("{:4} {} ({} files)".format("OK" if not problems else "FAIL", name, len(rec["files"])))
        for msg in problems[:20]:
            print("       " + msg)
    return 1 if bad else 0


def main(argv=None):
    ap = argparse.ArgumentParser(description="register and verify finished runs")
    sub = ap.add_subparsers(dest="cmd")
    f = sub.add_parser("freeze", help="checksum, make read-only, archive, index")
    f.add_argument("name")
    f.add_argument("paths", nargs="+")
    f.add_argument("--purpose", required=True)
    f.add_argument("--no-archive", action="store_true")
    v = sub.add_parser("verify", help="recheck checksums of registered runs")
    v.add_argument("names", nargs="*")
    args = ap.parse_args(argv)
    if args.cmd == "freeze":
        return freeze(args)
    if args.cmd == "verify":
        return verify(args)
    ap.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
