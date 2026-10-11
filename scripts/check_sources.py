"""Check every brew/cask name in the library exists (run locally on a machine with brew)."""

import json
import subprocess
import sys

from rigsmith import library  # noqa: F401
from rigsmith.backends import Brew, Cask
from rigsmith.model import ARTIFACTS

formulae = sorted({s.pkg for a in ARTIFACTS.values() for s in a.sources if type(s) is Brew})
casks = sorted({s.pkg for a in ARTIFACTS.values() for s in a.sources if type(s) is Cask})
bad = []
for kind, names in (("--formula", formulae), ("--cask", casks)):
    for name in names:
        r = subprocess.run(["brew", "info", "--json=v2", kind, name], capture_output=True, text=True)
        if r.returncode != 0:
            bad.append(f"{kind[2:]} {name}: not found")
            continue
        data = json.loads(r.stdout)
        item = (data["formulae"] or data["casks"])[0]
        if item.get("deprecated") or item.get("disabled"):
            bad.append(f"{kind[2:]} {name}: deprecated/disabled")
print("\n".join(bad) or f"ok: {len(formulae)} formulae, {len(casks)} casks")
sys.exit(1 if bad else 0)
