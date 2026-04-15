#!/usr/bin/env python3
"""Check for server-side game version drift.

Compares game_coordination.json IDs against current server metadata.
Flags any drift. Run before --compete to avoid surprises.

Exits 0 if no drift, 1 if drift detected (so it can gate CI / submit).
"""

import json
import os
import sys
import requests

try:
    from dotenv import load_dotenv
    load_dotenv('/mnt/c/exe/projects/ai-agents/.env')
except ImportError:
    pass


def main():
    # Locate coord.json — prefer ARC-SAGE mirror, fall back to shared-context
    candidates = [
        '/mnt/c/exe/projects/ai-agents/ARC-SAGE/knowledge/game_coordination.json',
        '/mnt/c/exe/projects/ai-agents/shared-context/arc-agi-3/game_coordination.json',
    ]
    coord_path = next((p for p in candidates if os.path.exists(p)), None)
    if not coord_path:
        print("No game_coordination.json found — can't check drift")
        return 2

    coord = json.load(open(coord_path))

    key = os.getenv('ARC_API_KEY', '')
    headers = {'Accept': 'application/json'}
    if key:
        headers['X-API-Key'] = key
    try:
        r = requests.get('https://three.arcprize.org/api/games',
                          headers=headers, timeout=20)
        r.raise_for_status()
    except Exception as e:
        print(f"API fetch failed: {e}")
        return 2

    server_games = {g['game_id'].split('-')[0]: g['game_id']
                    for g in r.json() if g.get('game_id')}

    drifts = []
    for g in coord.get('games', []):
        fam = g.get('family', g['id'].split('-')[0])
        server_id = server_games.get(fam)
        if server_id and g['id'] != server_id:
            drifts.append((fam, g['id'], server_id))

    if not drifts:
        print(f"No drift. {len(coord.get('games', []))} games all match server.")
        return 0

    print(f"⚠ {len(drifts)} drifted game(s):")
    for fam, old, new in drifts:
        print(f"  {fam}: {old} → {new}")
    print()
    print("To update coord.json and flag trace status, run:")
    print("  python3 check_version_drift.py --update")
    return 1


if __name__ == '__main__':
    if '--update' in sys.argv:
        # Update flow — regenerate coord.json with current versions
        # (separate code path so the default run is read-only safe)
        print("Update flow not implemented here — see git log for the one-shot update done 2026-04-15.")
        sys.exit(2)
    sys.exit(main())
