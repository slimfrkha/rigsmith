"""Check every brew/cask name and VS Code extension id in the library exists (live APIs; brew only for taps)."""

import json
import subprocess
import sys
import urllib.error
import urllib.request

from rigsmith import library  # noqa: F401
from rigsmith.backends import Brew, Cask, VSCodeExt
from rigsmith.model import ARTIFACTS

formulae = sorted({s.pkg for a in ARTIFACTS.values() for s in a.sources if type(s) is Brew})
casks = sorted({s.pkg for a in ARTIFACTS.values() for s in a.sources if type(s) is Cask})
bad = []


def exists(kind: str, name: str) -> bool:
    """Ask the live formulae.brew.sh API (local brew metadata can be stale). Taps are checked with brew."""
    if "/" in name:
        return subprocess.run(["brew", "info", "--json=v2", f"--{kind}", name], capture_output=True).returncode == 0
    try:
        with urllib.request.urlopen(f"https://formulae.brew.sh/api/{kind}/{name}.json", timeout=30) as resp:
            data = json.load(resp)
    except urllib.error.HTTPError as e:
        if e.code != 404:
            raise
        # aliases (e.g. `python` → python@3.x) aren't API paths: let brew resolve them
        return subprocess.run(["brew", "info", "--json=v2", f"--{kind}", name], capture_output=True).returncode == 0
    if data.get("deprecated") or data.get("disabled"):
        bad.append(f"{kind} {name}: deprecated/disabled")
    return True


for kind, names in (("formula", formulae), ("cask", casks)):
    bad += [f"{kind} {n}: not found" for n in names if not exists(kind, n)]
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
