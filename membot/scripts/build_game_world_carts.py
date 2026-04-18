#!/usr/bin/env python3
"""
build_game_world_carts.py — Build one brain cart per ARC-AGI-3 game from its mechanics doc.

For each `<game>.md` in knowledge/game-mechanics/, this produces a
`<game>_world_model.cart.npz` in knowledge/game-world-carts/.

Loads the Nomic embedder once, reuses it for all 25 carts.
Entries are raw text (no filename prefix) per Dennis's Q6 answer: free-text
cartridges proved to support correct in-context reasoning on cd82 with gemma3:4b
(A/B test, 2026-04-16). Chunking at 300 words preserves per-section granularity
for semantic retrieval within a game.

Usage (from ARC-SAGE repo root):
    python membot/scripts/build_game_world_carts.py
    python membot/scripts/build_game_world_carts.py --games sk48 cd82 bp35
    python membot/scripts/build_game_world_carts.py --input-dir knowledge/game-mechanics \\
        --output-dir knowledge/game-world-carts --chunk-size 300

Skips games whose target cart already exists unless --force is passed.
"""

from __future__ import annotations

import argparse
import os
import sys
import time
from pathlib import Path

# Import from the vendored cart builder next to this script's membot dir.
SCRIPT_DIR = Path(__file__).resolve().parent
MEMBOT_DIR = SCRIPT_DIR.parent  # ARC-SAGE/membot
sys.path.insert(0, str(MEMBOT_DIR))

from cartridge_builder import (  # noqa: E402
    read_file,
    chunk_text,
    embed_texts,
    build_metadata,
    save_cartridge,
    get_embedder,
)


def build_one(
    md_path: Path,
    output_dir: Path,
    chunk_size: int,
    overlap: int,
    batch_size: int,
    cooldown_every: int,
    cooldown_secs: float,
) -> tuple[str, int, float] | None:
    """Build one cart from one .md file. Returns (cart_name, n_entries, elapsed_s) or None on skip."""
    game_id = md_path.stem  # "sk48" from "sk48.md"
    cart_name = f"{game_id}_world_model"

    text = read_file(str(md_path))
    if not text.strip():
        print(f"  [skip] {md_path.name}: empty or unsupported")
        return None

    # Chunk — no filename prefix per Dennis Q6: free text is what the small model reads
    chunks = chunk_text(text, chunk_size=chunk_size, overlap=overlap)
    entries = [c for c in chunks if c.strip()]
    doc_map = [(md_path.name, i, len(entries)) for i in range(len(entries))]

    if not entries:
        print(f"  [skip] {md_path.name}: no entries after chunking")
        return None

    t0 = time.time()
    embeddings = embed_texts(
        entries,
        batch_size=batch_size,
        cooldown_every=cooldown_every,
        cooldown_secs=cooldown_secs,
    )
    metadata, pattern0 = build_metadata(entries, doc_map, cart_name=cart_name)

    cart_path, size_mb, fingerprint = save_cartridge(
        str(output_dir),
        cart_name,
        embeddings,
        entries,
        metadata=metadata,
        pattern0=pattern0,
    )
    elapsed = time.time() - t0
    print(
        f"  {cart_name:<28} {len(entries):>4} entries  "
        f"{size_mb:>5.2f} MB  {elapsed:>5.1f}s  {fingerprint}"
    )
    return cart_name, len(entries), elapsed


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build one brain cart per game from knowledge/game-mechanics/*.md",
    )
    # Default to knowledge/ paths relative to the ARC-SAGE repo root (parent of membot/).
    default_input = MEMBOT_DIR.parent / "knowledge" / "game-mechanics"
    default_output = MEMBOT_DIR.parent / "knowledge" / "game-world-carts"

    parser.add_argument(
        "--input-dir",
        type=Path,
        default=default_input,
        help=f"Directory containing <game>.md files (default: {default_input})",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=default_output,
        help=f"Where to write the cart files (default: {default_output})",
    )
    parser.add_argument(
        "--games",
        nargs="+",
        help="Only build these games (e.g. --games sk48 cd82). Default: all .md files.",
    )
    parser.add_argument("--chunk-size", type=int, default=300)
    parser.add_argument("--overlap", type=int, default=50)
    parser.add_argument("--batch-size", type=int, default=16)
    parser.add_argument("--cooldown-every", type=int, default=500)
    parser.add_argument("--cooldown-secs", type=float, default=3.0)
    parser.add_argument(
        "--force",
        action="store_true",
        help="Rebuild even if the cart file already exists",
    )
    args = parser.parse_args()

    input_dir = args.input_dir.resolve()
    output_dir = args.output_dir.resolve()

    if not input_dir.is_dir():
        print(f"Error: input dir not found: {input_dir}")
        return 1

    output_dir.mkdir(parents=True, exist_ok=True)

    # Select source files
    if args.games:
        md_files = [input_dir / f"{g}.md" for g in args.games]
        missing = [p for p in md_files if not p.is_file()]
        if missing:
            print(f"Error: missing files: {[str(p) for p in missing]}")
            return 1
    else:
        md_files = sorted(input_dir.glob("*.md"))
        if not md_files:
            print(f"Error: no .md files in {input_dir}")
            return 1

    print(f"\n{'='*72}")
    print("ARC-SAGE Game-World Cart Batch Builder")
    print(f"{'='*72}")
    print(f"Input:  {input_dir}")
    print(f"Output: {output_dir}")
    print(f"Games:  {len(md_files)}")
    print(f"{'='*72}\n")

    # Pre-load embedder so the first cart doesn't pay the 15s model-load cost alone
    print("Loading Nomic embedder (one load for all carts)...")
    t_model = time.time()
    get_embedder()
    print(f"  Embedder ready in {time.time() - t_model:.1f}s\n")

    # Header for the per-cart progress table
    print(f"  {'cart name':<28} {'ents':>4}  {'size':>5}       time  fingerprint")
    print(f"  {'-'*28} {'-'*4}  {'-'*5}       ---- {'-'*16}")

    results = []
    skipped = []
    for md in md_files:
        cart_file = output_dir / f"{md.stem}_world_model.cart.npz"
        if cart_file.exists() and not args.force:
            print(f"  {md.stem + '_world_model':<28}   --    --         --  (exists, skipped)")
            skipped.append(md.stem)
            continue

        try:
            result = build_one(
                md_path=md,
                output_dir=output_dir,
                chunk_size=args.chunk_size,
                overlap=args.overlap,
                batch_size=args.batch_size,
                cooldown_every=args.cooldown_every,
                cooldown_secs=args.cooldown_secs,
            )
            if result:
                results.append(result)
        except Exception as e:  # pragma: no cover — fail loud but keep going
            print(f"  [ERROR] {md.name}: {e}")

    # Summary
    print(f"\n{'='*72}")
    print("BATCH COMPLETE")
    print(f"{'='*72}")
    print(f"  Built:    {len(results)} carts")
    print(f"  Skipped:  {len(skipped)} carts (already existed — use --force to rebuild)")
    if results:
        total_entries = sum(n for _, n, _ in results)
        total_time = sum(t for _, _, t in results)
        print(f"  Entries:  {total_entries} total")
        print(f"  Time:     {total_time:.1f}s total "
              f"({total_time / len(results):.1f}s/cart avg)")
    print(f"  Output:   {output_dir}")
    print(f"{'='*72}\n")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
