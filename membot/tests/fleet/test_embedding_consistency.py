"""
Embedding Consistency Tests
============================
Validates that the active embedding backend produces correct, consistent vectors.
Backend-agnostic — works with both Ollama and SentenceTransformer.

Usage:
    python3 tests/fleet/test_embedding_consistency.py
"""

import unittest
import json
import os
import urllib.request
import numpy as np

MEMBOT_URL = os.environ.get("MEMBOT_URL", "http://localhost:8000")
TEST_CARTRIDGE = "embed-consistency-test"


def api(method, path, data=None, timeout=15):
    url = f"{MEMBOT_URL}{path}"
    req = urllib.request.Request(url, method=method)
    if data:
        req.data = json.dumps(data).encode()
        req.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read())


class TestEmbeddingConsistency(unittest.TestCase):
    """Verify embedding backend produces correct, stable vectors."""

    @classmethod
    def setUpClass(cls):
        """Create test cartridge and seed with known content."""
        try:
            api("GET", "/api/status")
        except Exception as e:
            raise unittest.SkipTest(f"Membot not running: {e}")

        # Create cartridge
        cart_dir = os.path.join(os.path.dirname(__file__), "..", "..", "cartridges")
        cls.cart_path = os.path.join(cart_dir, f"{TEST_CARTRIDGE}.cart.npz")
        np.savez(cls.cart_path,
                 embeddings=np.zeros((0, 768), dtype=np.float32),
                 texts=np.array([], dtype=object))

        api("POST", "/api/mount", {"name": TEST_CARTRIDGE})

        # Seed with diverse content
        cls.test_docs = [
            ("Python is a programming language used for web development and data science.", "tech"),
            ("The Eiffel Tower is a wrought-iron lattice tower in Paris, France.", "geography"),
            ("Photosynthesis converts sunlight into chemical energy in plant cells.", "biology"),
            ("Jazz originated in the African-American communities of New Orleans.", "music"),
            ("Neural networks use layers of interconnected nodes to process information.", "tech"),
        ]
        for text, tag in cls.test_docs:
            api("POST", "/api/store", {"content": text, "tags": tag}, timeout=30)

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, 'cart_path') and os.path.exists(cls.cart_path):
            os.remove(cls.cart_path)
        manifest = cls.cart_path.replace(".cart.npz", ".cart_manifest.json")
        if os.path.exists(manifest):
            os.remove(manifest)

    def test_same_query_same_ranking(self):
        """Running the same query twice produces identical rankings."""
        query = "machine learning and artificial intelligence"
        r1 = api("POST", "/api/search", {"query": query, "top_k": 3})
        r2 = api("POST", "/api/search", {"query": query, "top_k": 3})

        texts1 = [r["text"] for r in r1["results"]]
        texts2 = [r["text"] for r in r2["results"]]
        self.assertEqual(texts1, texts2, "Same query should produce same ranking")

        scores1 = [r["score"] for r in r1["results"]]
        scores2 = [r["score"] for r in r2["results"]]
        for s1, s2 in zip(scores1, scores2):
            self.assertAlmostEqual(s1, s2, places=3,
                                   msg="Same query should produce same scores")

    def test_relevant_outscores_irrelevant(self):
        """Semantically relevant queries score higher than irrelevant ones."""
        # Tech query should rank tech docs higher
        tech = api("POST", "/api/search", {"query": "programming and software", "top_k": 5})
        bio = api("POST", "/api/search", {"query": "plant biology and cells", "top_k": 5})

        # Top result for tech query should contain tech content
        tech_top = tech["results"][0]["text"] if tech["results"] else ""
        self.assertTrue(
            any(word in tech_top.lower() for word in ["python", "neural", "programming"]),
            f"Tech query top result should be tech-related, got: {tech_top[:80]}"
        )

        # Top result for bio query should contain bio content
        bio_top = bio["results"][0]["text"] if bio["results"] else ""
        self.assertTrue(
            any(word in bio_top.lower() for word in ["photosynthesis", "plant", "cell"]),
            f"Bio query top result should be bio-related, got: {bio_top[:80]}"
        )

    def test_cross_domain_discrimination(self):
        """Queries in one domain don't falsely match another domain."""
        music = api("POST", "/api/search", {"query": "jazz and blues music history", "top_k": 1})
        geo = api("POST", "/api/search", {"query": "famous landmarks in Europe", "top_k": 1})

        # Each should find its domain, not the other
        if music["results"]:
            self.assertIn("jazz", music["results"][0]["text"].lower(),
                          "Music query should find music content")
        if geo["results"]:
            self.assertIn("eiffel", geo["results"][0]["text"].lower(),
                          "Geography query should find geography content")

    def test_scores_in_valid_range(self):
        """All search scores are between 0.0 and 1.0."""
        result = api("POST", "/api/search", {"query": "test query", "top_k": 5})
        for r in result.get("results", []):
            self.assertGreaterEqual(r["score"], 0.0, f"Score below 0: {r['score']}")
            self.assertLessEqual(r["score"], 1.0, f"Score above 1: {r['score']}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
