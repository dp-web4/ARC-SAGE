"""
test_grid_cartridge.py — End-to-end test: SDK → observe → write cart → verify

Run manually:
    cd membot/vision
    python test_grid_cartridge.py
    python test_grid_cartridge.py --no-clip     # skip CLIP, faster
    python test_grid_cartridge.py --game vc33-9851e02b
"""

import sys
import os
import time
import json
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from grid_observation import GridObservationProducer
from grid_cartridge import (
    GridCartridgeWriter, load_grid_from_passage,
    load_objects_from_passage, load_sage_record_from_passage
)


def main():
    use_clip = "--no-clip" not in sys.argv
    game_id = "g50t-5849a774"
    for i, arg in enumerate(sys.argv):
        if arg == "--game" and i + 1 < len(sys.argv):
            game_id = sys.argv[i + 1]

    print("=" * 60)
    print("  GridCartridge End-to-End Test")
    print(f"  Game: {game_id}")
    print(f"  CLIP: {'yes' if use_clip else 'no (handcrafted)'}")
    print("=" * 60)

    # 1. Init SDK
    print("\n[1/6] Loading game from SDK...")
    import arc_agi
    arcade = arc_agi.Arcade()
    env = arcade.make(game_id)
    state = env.reset()
    print(f"  Game loaded. Actions: {state.available_actions}, Levels: {state.win_levels}")

    # 2. Init producer
    print("\n[2/6] Initializing GridObservationProducer...")
    producer = GridObservationProducer(use_clip=use_clip)

    # 3. Init writer
    print("\n[3/6] Initializing GridCartridgeWriter...")
    out_dir = os.path.join(os.path.dirname(__file__), "test_carts")
    os.makedirs(out_dir, exist_ok=True)
    writer = GridCartridgeWriter(cart_name=f"test_{game_id.split('-')[0]}", output_dir=out_dir)

    # 4. Play 5 steps, observe, write
    print("\n[4/6] Playing 5 steps...")
    level_id = f"{game_id}-L1"

    # Initial frame
    obs = producer.observe(state.frame[0], step_number=0, action_taken=0, level_id=level_id)
    idx = writer.add_observation(obs)
    print(f"  Step 0: {obs.num_objects} objects, {obs.num_changes} changes → even_idx={idx}")

    for step in range(1, 6):
        actions = state.available_actions
        if not actions:
            break
        action = actions[step % len(actions)]
        state = env.step(action)

        obs = producer.observe(state.frame[0], step_number=step, action_taken=action, level_id=level_id)
        idx = writer.add_observation(obs, sage_record={
            "step": step,
            "action_taken": action,
            "hypothesis": f"Testing action {action} at step {step}",
            "salience": {"surprise": 0.5, "novelty": 0.3, "arousal": 0.4, "reward": 0.1, "conflict": 0.0},
            "cognitive_type": "reflection" if step == 3 else None,
        })
        print(f"  Step {step}: action={action}, {obs.num_objects} objects, "
              f"{obs.num_changes} changes, {len(obs.moved)} moved → even_idx={idx}")

    print(f"\n  Writer stats: {writer.stats()}")

    # 5. Save cart
    print("\n[5/6] Saving cart...")
    cart_path = writer.save()

    # 6. Verify
    print("\n[6/6] Verifying cart...")
    errors = 0

    # Load and check
    cart = np.load(str(cart_path), allow_pickle=True)
    passages = list(cart["passages"])
    embeddings = cart["embeddings"]
    sign_bits = cart["sign_bits"]
    metadata = json.loads(str(cart["metadata"]))

    print(f"  Passages: {len(passages)}")
    print(f"  Embeddings: {embeddings.shape}")
    print(f"  Sign bits: {sign_bits.shape}")
    print(f"  Metadata: {json.dumps(metadata, indent=2)}")

    # Check paired structure
    if len(passages) % 2 != 0:
        print(f"  ERROR: Odd number of passages ({len(passages)}), expected even (paired)")
        errors += 1
    else:
        print(f"  OK: {len(passages)//2} pairs")

    # Check even patterns have grid data
    even_with_grid = 0
    for i in range(0, len(passages), 2):
        grid = load_grid_from_passage(str(passages[i]))
        if grid is not None:
            even_with_grid += 1
            if grid.shape != (64, 64):
                print(f"  ERROR: Grid at index {i} has shape {grid.shape}, expected (64,64)")
                errors += 1
    print(f"  Grids decoded: {even_with_grid}/{len(passages)//2}")

    # Check even patterns have objects
    even_with_objects = 0
    for i in range(0, len(passages), 2):
        objects = load_objects_from_passage(str(passages[i]))
        if objects:
            even_with_objects += 1
    print(f"  Passages with objects: {even_with_objects}/{len(passages)//2}")

    # Check odd patterns
    odd_with_sage = 0
    for i in range(1, len(passages), 2):
        record = load_sage_record_from_passage(str(passages[i]))
        if record is not None:
            odd_with_sage += 1
    print(f"  SAGE records: {odd_with_sage}/{len(passages)//2} (step 0 has placeholder)")

    # Check embeddings are non-zero for even, zero for odd
    even_nonzero = 0
    odd_zero = 0
    for i in range(0, len(embeddings), 2):
        if np.any(embeddings[i] != 0):
            even_nonzero += 1
    for i in range(1, len(embeddings), 2):
        if np.all(embeddings[i] == 0):
            odd_zero += 1
    print(f"  Even embeddings non-zero: {even_nonzero}/{len(passages)//2}")
    print(f"  Odd embeddings zero: {odd_zero}/{len(passages)//2}")

    # Check sign bits shape
    expected_sign_bits = embeddings.shape[1] // 8  # 512 dims → 64 bytes
    if sign_bits.shape[1] == expected_sign_bits:
        print(f"  Sign bits: OK ({sign_bits.shape[1]} bytes per entry)")
    else:
        print(f"  WARNING: Sign bits shape {sign_bits.shape[1]}, expected {expected_sign_bits}")

    # Check a grid roundtrip
    original_grid = producer.prev_frame  # last frame we observed
    decoded_grid = load_grid_from_passage(str(passages[-2]))  # last even passage
    if decoded_grid is not None and original_grid is not None:
        match = np.array_equal(original_grid, decoded_grid)
        print(f"  Grid roundtrip (last frame): {'OK — perfect match' if match else 'MISMATCH'}")
        if not match:
            errors += 1
    else:
        print(f"  Grid roundtrip: skipped (no data)")

    # Summary
    print(f"\n{'='*60}")
    if errors == 0:
        print(f"  ALL CHECKS PASSED")
        print(f"  Cart: {cart_path}")
        print(f"  Ready to mount on Membot and search.")
    else:
        print(f"  {errors} ERROR(S) FOUND")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
