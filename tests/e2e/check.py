"""E2E assertions against the real machine.

check.py installed   [-c CFG] [-p PROFILE] [-s SECTION]...   everything in scope is installed
check.py uninstalled [-c CFG] [-p PROFILE] [-s SECTION]...   no receipts left, pre-existing packages kept
"""

import argparse
import json
import sys
from pathlib import Path

from rigsmith import config, library  # noqa: F401
from rigsmith.effects import shell_d
from rigsmith.model import Platform, ensure_path
from rigsmith.plan import build
from rigsmith.runner import status
from rigsmith.state import NOOP, State

ap = argparse.ArgumentParser()
ap.add_argument("mode", choices=["installed", "uninstalled"])
ap.add_argument("ids", nargs="*")
ap.add_argument("-c")
ap.add_argument("-p")
ap.add_argument("-s", action="append", default=[])
args = ap.parse_args()

ensure_path()
cfg, p, state = config.load(args.c), Platform.detect(), State()
plan = build(cfg, p, ids=args.ids, profile=args.p, sections=args.s)
PRE = Path("/tmp/rigsmith-preexisting.json")
bad = []

if args.mode == "installed":
    for i in plan.order:
        if (st := status(cfg.library[i], p)) != "installed":
            bad.append(f"{i}: {st}")
    pre = [r.artifact for r in state.receipts.values() if r.key.startswith("pkg:") and r.op == NOOP]
    PRE.write_text(json.dumps(pre))
    print(f"installed: {len(plan.order)} artifacts, {len(pre)} pre-existing: {', '.join(pre)}")
else:
    scope = {e.id for e in config.load(args.c).entries} & set(plan.order)
    bad += [f"receipt left: {r.key}" for r in state.receipts.values() if r.artifact in scope and r.op != NOOP]
    bad += [f"snippet left: {f.name}" for f in shell_d().glob("*")] if shell_d().exists() else []
    for i in json.loads(PRE.read_text()):
        if not cfg.library[i].present(p):
            bad.append(f"pre-existing {i} was removed")

print("\n".join(bad) or f"{args.mode}: ok")
sys.exit(1 if bad else 0)
