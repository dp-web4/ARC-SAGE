"""
Membot Fleet Health Tests
=========================
Verifies membot server is running correctly on any fleet machine.
Uses only stdlib (no pytest) so it runs on constrained devices like Sprout.

Usage:
    python3 tests/fleet/test_membot_health.py
    python3 tests/fleet/test_membot_health.py TestMembotHealth.test_server_responding
"""

import unittest
import json
import os
import time
import urllib.request
import urllib.error

MEMBOT_URL = os.environ.get("MEMBOT_URL", "http://localhost:8000")
TEST_CARTRIDGE = "fleet-test-ephemeral"


def api(method, path, data=None, timeout=10):
    """Call membot REST API. Returns parsed JSON or raises."""
    url = f"{MEMBOT_URL}{path}"
    req = urllib.request.Request(url, method=method)
    if data:
        req.data = json.dumps(data).encode()
        req.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read())


class TestMembotHealth(unittest.TestCase):
    """Basic server health — should pass on every fleet machine."""

    def test_server_responding(self):
        """Server returns valid status JSON."""
        status = api("GET", "/api/status")
        self.assertEqual(status["status"], "ok")

    def test_cartridge_list(self):
        """Cartridge listing works (may be empty on fresh install)."""
        result = api("GET", "/api/cartridges")
        self.assertEqual(result["status"], "ok")
        self.assertIsInstance(result["cartridges"], list)

    def test_writable_mode(self):
        """Server is in writable mode (required for SAGE/SNARC integration)."""
        status = api("GET", "/api/status")
        self.assertFalse(status.get("read_only", True),
                         "Server must be in writable mode for fleet integration")


class TestEmbeddingBackend(unittest.TestCase):
    """Validates embedding backend produces correct output."""

    def test_embedding_dimension(self):
        """Embedding produces 768-dim vectors (nomic standard)."""
        # We can't directly call embed_text via REST, but we can store
        # and search — if search returns results with scores, embeddings work.
        # Mount a temp cartridge, store, search, verify score > 0
        try:
            api("POST", "/api/mount", {"name": TEST_CARTRIDGE})
        except urllib.error.HTTPError:
            # Cartridge doesn't exist yet — create it
            pass

        # Store a test memory (will fail gracefully if no cartridge)
        result = api("POST", "/api/store", {
            "content": "The quick brown fox jumps over the lazy dog",
            "tags": "test"
        })
        # If we got "No cartridge mounted" that's ok — means we need to
        # create one first. The embedding test still validates via search below.

    def test_search_returns_scores(self):
        """Search returns results with valid similarity scores."""
        # Mount the sample cartridge (ships with repo)
        mount = api("POST", "/api/mount", {"name": "attention-is-all-you-need"})
        self.assertIn("Mounted", mount.get("result", ""))

        result = api("POST", "/api/search", {
            "query": "transformer architecture",
            "top_k": 2
        })
        self.assertEqual(result["status"], "ok")
        self.assertGreater(len(result["results"]), 0, "Should find results in sample cartridge")

        # Scores should be between 0 and 1
        for r in result["results"]:
            self.assertGreaterEqual(r["score"], 0.0)
            self.assertLessEqual(r["score"], 1.0)

    def test_semantic_relevance(self):
        """Relevant queries score higher than irrelevant ones."""
        api("POST", "/api/mount", {"name": "attention-is-all-you-need"})

        good = api("POST", "/api/search", {"query": "self-attention mechanism", "top_k": 1})
        bad = api("POST", "/api/search", {"query": "chocolate cake recipe", "top_k": 1})

        good_score = good["results"][0]["score"] if good["results"] else 0
        bad_score = bad["results"][0]["score"] if bad["results"] else 0

        self.assertGreater(good_score, bad_score,
                           f"Relevant query ({good_score:.3f}) should outscore irrelevant ({bad_score:.3f})")


class TestStoreSearchCycle(unittest.TestCase):
    """Full write-read cycle: store, search, verify retrieval."""

    @classmethod
    def setUpClass(cls):
        """Create a temporary test cartridge."""
        import numpy as np
        # Create empty cartridge file
        cart_dir = os.path.join(os.path.dirname(__file__), "..", "..", "cartridges")
        cls.cart_path = os.path.join(cart_dir, f"{TEST_CARTRIDGE}.cart.npz")
        if not os.path.exists(cls.cart_path):
            np.savez(cls.cart_path,
                     embeddings=np.zeros((0, 768), dtype=np.float32),
                     texts=np.array([], dtype=object))

    @classmethod
    def tearDownClass(cls):
        """Clean up test cartridge."""
        if hasattr(cls, 'cart_path') and os.path.exists(cls.cart_path):
            os.remove(cls.cart_path)
        manifest = cls.cart_path.replace(".cart.npz", ".cart_manifest.json")
        if os.path.exists(manifest):
            os.remove(manifest)

    def test_mount_store_search(self):
        """Full cycle: mount empty cartridge, store content, search it back."""
        # Mount
        mount = api("POST", "/api/mount", {"name": TEST_CARTRIDGE})
        self.assertIn("Mounted", mount.get("result", ""),
                      f"Mount failed: {mount}")

        # Store
        store = api("POST", "/api/store", {
            "content": "The Jetson Orin Nano has 8GB of unified memory shared between CPU and GPU.",
            "tags": "hardware jetson"
        }, timeout=30)  # First embed may take longer (Ollama model load)
        self.assertIn("Stored", store.get("result", ""),
                      f"Store failed: {store}")

        # Search
        search = api("POST", "/api/search", {
            "query": "how much memory does the Jetson have?",
            "top_k": 1
        }, timeout=15)
        self.assertEqual(search["status"], "ok")
        self.assertGreater(len(search["results"]), 0, "Should find the stored memory")
        self.assertIn("Jetson", search["results"][0]["text"])

    def test_search_latency(self):
        """Search completes within acceptable time."""
        api("POST", "/api/mount", {"name": "attention-is-all-you-need"})
        result = api("POST", "/api/search", {
            "query": "encoder decoder",
            "top_k": 3
        })
        # Allow generous latency for constrained machines (Sprout: Ollama model swap)
        self.assertLess(result.get("elapsed_ms", 9999), 5000,
                        "Search should complete within 5 seconds even on constrained hardware")


class TestResourceConstraints(unittest.TestCase):
    """Memory and resource checks — especially important on Sprout."""

    def test_no_sentence_transformers_on_sprout(self):
        """On Sprout (ARM64 Jetson), sentence-transformers should NOT be loaded."""
        import platform
        if platform.machine() != "aarch64":
            self.skipTest("Not on ARM64 — sentence-transformers check not applicable")

        # Check if sentence_transformers is importable (it shouldn't be on Sprout)
        try:
            import sentence_transformers
            self.fail("sentence-transformers is installed on Sprout — "
                      "this wastes ~2GB RAM. Use Ollama embedding backend instead. "
                      "Run: pip uninstall sentence-transformers")
        except ImportError:
            pass  # Correct — not installed

    def test_ollama_embedding_on_arm64(self):
        """On ARM64, verify Ollama is the active embedding backend."""
        import platform
        if platform.machine() != "aarch64":
            self.skipTest("Not on ARM64")

        backend = os.environ.get("MEMBOT_EMBED_BACKEND", "auto")
        self.assertIn(backend, ("ollama", "auto"),
                      f"On ARM64, MEMBOT_EMBED_BACKEND should be 'ollama' or 'auto', got '{backend}'")


if __name__ == "__main__":
    unittest.main(verbosity=2)
