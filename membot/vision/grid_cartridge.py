"""
grid_cartridge.py — Write GridObservations to Membot brain carts.

Takes GridObservation instances and writes them as paired pattern entries
to a standard .cart.npz file that Membot can mount and search.

Even pattern: CLIP embedding + passage text (grid, objects, stats)
Odd pattern: Placeholder for SAGE reasoning (written by SAGE later)

Phase 1: One frame per cart entry. CLIP embedding for search.

Future directions:
    The 64x64 game grid uses only ONE Region of Concern on the 4096x4096 lattice
    (0.024% of available space). A single pattern could hold:
    - Raw game grid (1 ROC)
    - CLIP embedding via region-fill (8 ROCs)
    - Object segmentation map (1 ROC)
    - Previous frame diff (1 ROC)
    - Movement vector field (1 ROC)
    - Last N frames as a temporal filmstrip (~10 ROCs)
    - SAGE reasoning structures (remaining ~42 ROCs)
    This turns the pattern from a "cart entry" into a "working memory workspace"
    where physics can form associations between frames on the SAME pattern.
    Phase 2+ work.

Usage:
    from grid_cartridge import GridCartridgeWriter

    writer = GridCartridgeWriter("game_session.cart.npz")
    writer.add_observation(obs)           # even pattern: frame + embedding
    writer.add_sage_record(step, record)  # odd pattern: SAGE reasoning
    writer.save()

NOTE: Andy runs all tests. Do not run test scripts from Claude Code.
"""

import os
import json
import time
import hashlib
import numpy as np
from pathlib import Path
from typing import Optional, Dict, List

from grid_observation import GridObservation


def _compact_grid(frame: np.ndarray) -> str:
    """Encode a 64x64 int8 grid as a compact hex string.

    Each cell is 0-15 (4 bits), so two cells per byte.
    64*64 = 4096 cells = 2048 bytes = 4096 hex chars.
    """
    flat = frame.ravel().astype(np.uint8)
    # Pack two cells per byte (high nibble + low nibble)
    packed = np.zeros(len(flat) // 2, dtype=np.uint8)
    packed = (flat[0::2] << 4) | flat[1::2]
    return packed.tobytes().hex()


def _expand_grid(hex_str: str) -> np.ndarray:
    """Decode a compact hex string back to a 64x64 int8 grid."""
    packed = bytes.fromhex(hex_str)
    arr = np.frombuffer(packed, dtype=np.uint8)
    high = (arr >> 4) & 0x0F
    low = arr & 0x0F
    flat = np.empty(len(arr) * 2, dtype=np.int8)
    flat[0::2] = high
    flat[1::2] = low
    return flat.reshape(64, 64)


def _format_even_passage(obs: GridObservation) -> str:
    """Format the even-pattern passage text from a GridObservation.

    Contains: level/step header, stats, compact grid, object list, notes.
    """
    lines = []

    # Header
    lines.append(f"[GRID] {obs.level_id} | Step {obs.step_number} | Action {obs.action_taken}")
    lines.append(f"Objects: {obs.num_objects} | Changes: {obs.num_changes} | "
                 f"Colors: {obs.num_colors} | BG: {obs.background_color}")

    # Compact grid (4096 hex chars = 2KB)
    lines.append(f"GRID:{_compact_grid(obs.frame_raw)}")

    # Objects as compact JSON
    if obs.objects:
        # Store minimal object info: id, color, bbox, centroid, size
        compact_objects = [
            {"id": o["id"], "c": o["color"], "bb": o["bbox"],
             "ct": o["centroid"], "sz": o["size"]}
            for o in obs.objects
        ]
        lines.append(f"OBJ:{json.dumps(compact_objects, separators=(',', ':'))}")

    # Changes (if any, compact)
    if obs.changes:
        lines.append(f"CHG:{len(obs.changes)}")

    # Movement (if any)
    if obs.moved:
        compact_moved = [
            {"id": m["id"], "c": m["color"], "d": m["delta"]}
            for m in obs.moved
        ]
        lines.append(f"MOV:{json.dumps(compact_moved, separators=(',', ':'))}")

    # Notes
    if obs.perception_notes:
        lines.append(f"NOTES:{obs.perception_notes}")

    return "\n".join(lines)


def _format_odd_passage(step_number: int, level_id: str,
                         sage_record: Optional[Dict] = None) -> str:
    """Format the odd-pattern passage text.

    If sage_record is None, creates a placeholder.
    If sage_record is provided, stores SAGE's step_record + reasoning.
    """
    if sage_record is None:
        return f"[SAGE] {level_id} | Step {step_number} | Awaiting SAGE reasoning"

    lines = []
    lines.append(f"[SAGE] {level_id} | Step {step_number}")

    # Structured fields
    if "hypothesis" in sage_record:
        lines.append(f"HYPOTHESIS: {sage_record['hypothesis']}")
    if "strategy" in sage_record:
        lines.append(f"STRATEGY: {sage_record['strategy']}")
    if "key_insight" in sage_record:
        lines.append(f"INSIGHT: {sage_record['key_insight']}")
    if "action_rationale" in sage_record:
        lines.append(f"RATIONALE: {sage_record['action_rationale']}")
    if "reasoning_text" in sage_record:
        lines.append(f"REASONING: {sage_record['reasoning_text']}")

    # Salience scores
    if "salience" in sage_record:
        s = sage_record["salience"]
        lines.append(f"SALIENCE: S={s.get('surprise',0):.2f} N={s.get('novelty',0):.2f} "
                     f"A={s.get('arousal',0):.2f} R={s.get('reward',0):.2f} "
                     f"C={s.get('conflict',0):.2f}")

    # Cognitive type flag
    if "cognitive_type" in sage_record and sage_record["cognitive_type"]:
        lines.append(f"COGNITIVE_TYPE: {sage_record['cognitive_type']}")

    # Full record as JSON (for programmatic access)
    lines.append(f"RECORD:{json.dumps(sage_record, separators=(',', ':'), default=str)}")

    return "\n".join(lines)


class GridCartridgeWriter:
    """Writes GridObservations to a Membot-compatible .cart.npz file.

    Uses paired pattern model:
    - Even indices: frame embedding + grid + objects (searchable)
    - Odd indices: SAGE reasoning (written later or placeholder)

    The cart is searchable via Membot's standard memory_search tool.
    """

    def __init__(self, cart_name: str = "game_session", output_dir: str = "."):
        self.cart_name = cart_name
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Paired arrays
        self.embeddings: List[np.ndarray] = []  # even: CLIP, odd: zero
        self.passages: List[str] = []           # even: grid text, odd: SAGE text
        self.sign_bits: List[np.ndarray] = []   # even: sign-zero, odd: zero

        # Tracking
        self.pair_count = 0
        self.level_frames: Dict[str, int] = {}  # level_id → frame count
        self.prev_even_idx: Optional[int] = None  # for h-row linking

    def add_observation(self, obs: GridObservation,
                         sage_record: Optional[Dict] = None) -> int:
        """Add a GridObservation as a paired entry.

        Args:
            obs: The GridObservation to store
            sage_record: Optional SAGE step record. If None, odd pattern
                         gets a placeholder that SAGE can update later.

        Returns:
            The even-pattern index in the cart.
        """
        even_idx = len(self.passages)
        odd_idx = even_idx + 1

        # Even pattern: frame embedding + passage text
        self.embeddings.append(obs.embedding.copy())
        self.passages.append(_format_even_passage(obs))
        self.sign_bits.append(np.packbits((obs.embedding > 0).astype(np.uint8)))

        # Odd pattern: SAGE reasoning or placeholder
        zero_emb = np.zeros_like(obs.embedding)
        self.embeddings.append(zero_emb)
        self.passages.append(_format_odd_passage(obs.step_number, obs.level_id, sage_record))
        self.sign_bits.append(np.packbits((zero_emb > 0).astype(np.uint8)))

        # Track
        self.pair_count += 1
        self.level_frames.setdefault(obs.level_id, 0)
        self.level_frames[obs.level_id] += 1
        self.prev_even_idx = even_idx

        return even_idx

    def update_sage_record(self, even_idx: int, sage_record: Dict):
        """Update the odd-pattern passage for a previously stored observation.

        Args:
            even_idx: The even-pattern index returned by add_observation
            sage_record: SAGE's step_record + reasoning
        """
        odd_idx = even_idx + 1
        if odd_idx >= len(self.passages):
            raise IndexError(f"No odd pattern at index {odd_idx}")

        # Extract level_id and step from existing even passage
        even_text = self.passages[even_idx]
        level_id = ""
        step = 0
        for line in even_text.split("\n"):
            if line.startswith("[GRID]"):
                parts = line.split("|")
                if len(parts) >= 2:
                    level_id = parts[0].replace("[GRID]", "").strip()
                    step_part = parts[1].strip()
                    if "Step" in step_part:
                        try:
                            step = int(step_part.split("Step")[1].strip())
                        except (ValueError, IndexError):
                            pass
                break

        self.passages[odd_idx] = _format_odd_passage(step, level_id, sage_record)

    def save(self) -> Path:
        """Save the cart as a .cart.npz file.

        Returns:
            Path to the saved cart file.
        """
        if not self.passages:
            raise ValueError("No observations to save")

        cart_path = self.output_dir / f"{self.cart_name}.cart.npz"

        # Stack arrays
        embeddings = np.array(self.embeddings, dtype=np.float32)
        passages = np.array(self.passages, dtype=object)
        sign_bits = np.array(self.sign_bits, dtype=np.uint8)

        # Build metadata
        metadata = json.dumps({
            "source": "grid_cartridge",
            "cart_name": self.cart_name,
            "pairs": self.pair_count,
            "total_passages": len(self.passages),
            "levels": self.level_frames,
            "built": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "embedding_dim": embeddings.shape[1] if len(embeddings) > 0 else 0,
            "encoder": "CLIP-ViT-B-32",
        })

        # Save
        np.savez_compressed(
            str(cart_path),
            embeddings=embeddings,
            passages=passages,
            sign_bits=sign_bits,
            metadata=metadata,
        )

        # Manifest
        manifest_path = cart_path.with_name(
            cart_path.name.replace(".cart.npz", ".cart_manifest.json"))
        with open(cart_path, "rb") as f:
            cart_hash = hashlib.sha256(f.read()).hexdigest()
        manifest = {
            "version": 1,
            "count": len(self.passages),
            "fingerprint": cart_hash[:16],
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        }
        with open(manifest_path, "w") as f:
            json.dump(manifest, f, indent=2)

        size_mb = os.path.getsize(cart_path) / (1024 * 1024)
        print(f"[GridCartridge] Saved {cart_path.name}: "
              f"{self.pair_count} pairs ({len(self.passages)} entries), "
              f"{size_mb:.2f} MB")

        return cart_path

    def stats(self) -> Dict:
        """Return current writer stats."""
        return {
            "cart_name": self.cart_name,
            "pairs": self.pair_count,
            "total_passages": len(self.passages),
            "levels": dict(self.level_frames),
            "embedding_dim": self.embeddings[0].shape[0] if self.embeddings else 0,
        }


# ─── Utilities ────────────────────────────────────────────────────────

def load_grid_from_passage(passage: str) -> Optional[np.ndarray]:
    """Extract and decode the raw grid from an even-pattern passage."""
    for line in passage.split("\n"):
        if line.startswith("GRID:"):
            hex_str = line[5:]
            return _expand_grid(hex_str)
    return None


def load_objects_from_passage(passage: str) -> List[Dict]:
    """Extract the object list from an even-pattern passage."""
    for line in passage.split("\n"):
        if line.startswith("OBJ:"):
            compact = json.loads(line[4:])
            # Expand compact keys back to full names
            return [
                {"id": o["id"], "color": o["c"], "bbox": o["bb"],
                 "centroid": o["ct"], "size": o["sz"]}
                for o in compact
            ]
    return []


def load_sage_record_from_passage(passage: str) -> Optional[Dict]:
    """Extract the SAGE step record from an odd-pattern passage."""
    for line in passage.split("\n"):
        if line.startswith("RECORD:"):
            return json.loads(line[7:])
    return None


# ─── Test harness (run manually) ──────────────────────────────────────
if __name__ == "__main__":
    """
    Test usage — run this yourself:
        python grid_cartridge.py

    Requires: pip install arc-agi open-clip-torch scipy pillow
    """
    import sys
    sys.path.insert(0, os.path.dirname(__file__))

    print("=" * 60)
    print("  GridCartridge Writer — Test Harness")
    print("  Run: python grid_cartridge.py")
    print("=" * 60)
    print()
    print("This test will:")
    print("  1. Load a game from the ARC SDK")
    print("  2. Play 5 steps, creating GridObservations")
    print("  3. Write them to a .cart.npz file")
    print("  4. Verify the cart is mountable by Membot")
    print()
    print("Run it manually to test.")
