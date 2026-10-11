"""Check every brew/cask name and VS Code extension id in the library exists (run locally with brew)."""

import json
import subprocess
import sys
import urllib.request

from rigsmith import library  # noqa: F401
from rigsmith.backends import Brew, Cask, VSCodeExt
from rigsmith.model import ARTIFACTS

formulae = sorted({s.pkg for a in ARTIFACTS.values() for s in a.sources if type(s) is Brew})
casks = sorted({s.pkg for a in ARTIFACTS.values() for s in a.sources if type(s) is Cask})
bad = []
for kind, names in (("--formula", formulae), ("--cask", casks)):
    for name in names:
        full = name if "/" in name or kind == "--cask" else f"homebrew/core/{name}"  # ignore local taps
        r = subprocess.run(["brew", "info", "--json=v2", kind, full], capture_output=True, text=True)
        if r.returncode != 0 and full != name:
            r = subprocess.run(["brew", "info", "--json=v2", kind, name], capture_output=True, text=True)
        if r.returncode != 0:
            bad.append(f"{kind[2:]} {name}: not found")
            continue
        data = json.loads(r.stdout)
        item = (data["formulae"] or data["casks"])[0]
        if item.get("deprecated") or item.get("disabled"):
            bad.append(f"{kind[2:]} {name}: deprecated/disabled")
exts = sorted({s.pkg for a in ARTIFACTS.values() for s in a.sources if type(s) is VSCodeExt})
query = {
    "filters": [{"criteria": [{"filterType": 7, "value": e} for e in exts], "pageSize": 1000}],
    "flags": 0,
}
req = urllib.request.Request(
    "https://marketplace.visualstudio.com/_apis/public/gallery/extensionquery",
    data=json.dumps(query).encode(),
    headers={"Content-Type": "application/json", "Accept": "application/json;api-version=3.0-preview.1"},
)
with urllib.request.urlopen(req, timeout=60) as resp:
    found = {
        f"{x['publisher']['publisherName']}.{x['extensionName']}".lower()
        for x in json.load(resp)["results"][0]["extensions"]
    }
bad += [f"vscode {e}: not on the marketplace" for e in exts if e.lower() not in found]
print("\n".join(bad) or f"ok: {len(formulae)} formulae, {len(casks)} casks, {len(exts)} extensions")
sys.exit(1 if bad else 0)
