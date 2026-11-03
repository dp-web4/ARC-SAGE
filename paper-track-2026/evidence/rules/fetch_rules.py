"""thor-claude 2026-11-03: archive the ARC Prize 2026 Paper Track competition pages (rules, evaluation, overview) verbatim,
read-only, via the Kaggle API (codex LICENSE_AUDIT.md asked for the exact rule text). Writes <page>.md + pages.json here."""
import json
import os
import sys

from kaggle.api.kaggle_api_extended import KaggleApi

OUT = os.path.dirname(os.path.abspath(__file__))
api = KaggleApi()
api.authenticate()
pages = api.competition_list_pages("arc-prize-2026-paper-track")
index = []
for p in pages:
    d = p if isinstance(p, dict) else {k: getattr(p, k, None) for k in ("name", "content", "post_id", "id")}
    name = d.get("name") or str(d.get("id"))
    body = d.get("content") or ""
    safe = "".join(c if c.isalnum() or c in "-_" else "_" for c in name)[:60]
    open(os.path.join(OUT, safe + ".md"), "w").write(body)
    index.append({"name": name, "file": safe + ".md", "chars": len(body)})
json.dump(index, open(os.path.join(OUT, "pages.json"), "w"), indent=1)
print(json.dumps(index, indent=1))
sys.exit(0 if index else 1)
