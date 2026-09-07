"""Read-only overlap report for the artist-owned evidence skills and remote commits."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
BASELINE = ROOT / "production/art_pipeline/upstream_baseline.json"


def git(*args):
    return subprocess.check_output(["git", "-c", "core.quotepath=false", *args], cwd=ROOT,
                                   encoding="utf-8", errors="strict").strip()


def snapshot():
    config = json.loads((ROOT / "production/art_pipeline/paths.json").read_text(encoding="utf-8"))
    hashes = {}
    for directory in config["protected_skill_directories"]:
        for name in git("ls-files", "--", directory).splitlines():
            path = ROOT / name
            if path.is_file():
                hashes[name] = hashlib.sha256(path.read_bytes()).hexdigest()
    return {"schema": "ndc-art-upstream-baseline/v1", "commit": git("rev-parse", "HEAD"),
            "protectedDirectories": config["protected_skill_directories"], "protectedHashes": hashes}


def report(fetch=False):
    if fetch:
        subprocess.run(["git", "fetch", "origin"], cwd=ROOT, check=True)
    base = json.loads(BASELINE.read_text(encoding="utf-8"))
    upstream = git("rev-parse", "--abbrev-ref", "@{upstream}")
    remote = set(filter(None, git("diff", "--name-only", base["commit"], upstream).splitlines()))
    # Include staged, unstaged and untracked work; names are NUL-separated for non-ASCII paths.
    raw = subprocess.check_output(["git", "status", "--porcelain=v1", "-z", "--untracked-files=all"], cwd=ROOT)
    records = raw.decode("utf-8").split("\0")
    local = set()
    index = 0
    while index < len(records):
        entry = records[index]
        if entry:
            local.add(entry[3:])
            if "R" in entry[:2] or "C" in entry[:2]:
                index += 1
                if index < len(records):
                    local.add(records[index])
        index += 1
    changed_hashes = []
    for name, digest in base["protectedHashes"].items():
        path = ROOT / name
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != digest:
            changed_hashes.append(name)
    protected_remote = [n for n in sorted(remote) if any(
        n.startswith(d + "/") for d in base["protectedDirectories"])]
    local_protected = [n for n in sorted(local) if any(
        n.startswith(d + "/") for d in base["protectedDirectories"])]
    overlap = sorted(local & remote)
    return {"baselineCommit": base["commit"], "head": git("rev-parse", "HEAD"),
            "upstream": upstream, "upstreamCommit": git("rev-parse", upstream),
            "remoteChangedFiles": sorted(remote), "remoteEvidenceChanges": protected_remote,
            "localRemoteOverlap": overlap, "localProtectedChanges": local_protected,
            "protectedChangedSinceBaseline": sorted(set(changed_hashes) | set(local_protected)),
            "textOverlapDetected": bool(overlap),
            "semanticReviewRequired": bool(protected_remote or local_protected),
            "note": "No text overlap does not prove semantic compatibility. Never rewrites the artist-owned files."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fetch", action="store_true")
    parser.add_argument("--capture-baseline", action="store_true", help="Explicitly create initial baseline; never overwrites")
    args = parser.parse_args()
    try:
        if args.capture_baseline:
            data = snapshot()
            with BASELINE.open("x", encoding="utf-8") as file:
                json.dump(data, file, ensure_ascii=False, indent=2)
                file.write("\n")
            print(json.dumps({"captured": str(BASELINE), "files": len(data["protectedHashes"])}))
            return 0
        data = report(args.fetch)
        print(json.dumps(data, ensure_ascii=False, indent=2))
        return 2 if data["textOverlapDetected"] else 0
    except (OSError, ValueError, subprocess.CalledProcessError) as exc:
        print(json.dumps({"status": "ERROR", "reason": str(exc)}, ensure_ascii=False))
        return 2


if __name__ == "__main__":
    sys.exit(main())
