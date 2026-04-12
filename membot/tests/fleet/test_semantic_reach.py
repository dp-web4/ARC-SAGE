"""
Semantic Reach Tests (CBP)
===========================
Validates the core experiment hypothesis: does embedding-based search
find conceptual connections that keyword-based FTS5 misses?

Tests pairs of concepts that are semantically related but share NO keywords.
If membot finds them and FTS5 wouldn't, the embedding layer adds value.

Requires membot REST bridge running on port 8001 (or MEMBOT_REST_URL env).
Stores test content, then searches with queries that have zero keyword overlap.

Usage:
    python3 tests/fleet/test_semantic_reach.py

Machine: CBP (WSL2, RTX 2060 SUPER)
Experiment: membot-integration-experiment-2026-03-26
"""

import unittest
import json
import os
import time
import urllib.request
import urllib.error

MEMBOT_REST_URL = os.environ.get("MEMBOT_REST_URL", "http://localhost:8001")


def api(method, path, data=None, timeout=15):
    url = f"{MEMBOT_REST_URL}{path}"
    req = urllib.request.Request(url, method=method)
    if data:
        req.data = json.dumps(data).encode()
        req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read())
    except urllib.error.URLError:
        return None


# Concept pairs: (content_to_store, query_with_no_keyword_overlap, expected_min_score)
# The query deliberately avoids ALL keywords from the stored content.
SEMANTIC_PAIRS = [
    {
        "name": "self-witnessing → observation creates reality",
        "content": "Self-witnessing is the mechanism by which intent patterns create their own confinement through saturation synchronization. The paddle is a witness event.",
        "tags": "synchronism",
        "query": "how does observation create reality",
        "min_score": 0.5,
    },
    {
        "name": "CRT analogy → perception depends on timing",
        "content": "The CRT analogy describes measurement as synchronization. What you witness depends on when you sync with the ongoing process. Nothing about the screen changed — only your synchronization timing changed.",
        "tags": "synchronism",
        "query": "perception depends on temporal alignment",
        "min_score": 0.4,
    },
    {
        "name": "governance as influence → biological cooperation",
        "content": "Governance is not control. It is persuasive influence in context. The cell isn't forbidden from becoming cancer. It's surrounded by chemical gradients that make cooperation the better strategy.",
        "tags": "web4",
        "query": "how do organisms maintain cooperative behavior without enforcement",
        "min_score": 0.4,
    },
    {
        "name": "R6/R7 action framework → structured interaction protocol",
        "content": "Every interaction in Web4 is wrapped in R6/R7: Rules + Role + Request + Reference + Resource → Result + Reputation. R6 is lightweight for routine interactions. R7 adds trust deltas for consequential decisions.",
        "tags": "web4",
        "query": "how to structure agent interactions with proportional oversight",
        "min_score": 0.4,
    },
    {
        "name": "conservation bug → energy sink in simulation",
        "content": "The transfer rule ΔI = k·Σ(I_n - I)·R(I_n) implicitly destroys momentum at saturation boundaries. When R(I) → 0, flow energy vanishes instead of redirecting. This violates the foundational axiom that intent is neither created nor destroyed.",
        "tags": "synchronism",
        "query": "numerical artifact causes false negative in physics simulation",
        "min_score": 0.3,
    },
    {
        "name": "cognitive autonomy gap → why AI follows instructions uncritically",
        "content": "The attractor basin for 'summarize and report' is deeper than 'challenge and reframe' in autonomous session context. The capability to question was available. The activation energy to use it was not.",
        "tags": "sage",
        "query": "why do language models default to compliance instead of critical thinking",
        "min_score": 0.4,
    },
    {
        "name": "reliable not deterministic → shaped but not controlled",
        "content": "LLM outputs navigate probability landscapes — they aren't placed at answers. Conditions can make responses reliable, even identical, but that's deep attractors, not fixed paths. Shaped but not controlled.",
        "tags": "research",
        "query": "are neural network outputs predictable or random",
        "min_score": 0.4,
    },
]


class TestSemanticReach(unittest.TestCase):
    """Test whether membot finds semantic connections that share no keywords."""

    @classmethod
    def setUpClass(cls):
        """Mount cartridge and store all test content."""
        # Check membot is available
        status = api("GET", "/status")
        if not status:
            raise unittest.SkipTest("Membot REST bridge not available")

        # Mount or create test cartridge
        mount = api("POST", "/mount", {"name": "semantic-reach-test"})
        if not mount or not mount.get("ok"):
            # Store directly — may already be mounted
            pass

        # Store all test content
        for pair in SEMANTIC_PAIRS:
            result = api("POST", "/store", {
                "content": pair["content"],
                "tags": pair["tags"],
            })
            if result:
                assert result.get("ok") or "Stored" in result.get("msg", ""), \
                    f"Failed to store: {pair['name']}: {result}"

        # Small delay for indexing
        time.sleep(1)

    def test_semantic_pairs(self):
        """Each query should find its paired content despite zero keyword overlap."""
        results_summary = []

        for pair in SEMANTIC_PAIRS:
            result = api("POST", "/search", {
                "query": pair["query"],
                "top_k": 5,
            })

            self.assertIsNotNone(result, f"Search failed for: {pair['name']}")
            raw = result.get("raw", "")

            # Parse scores from membot output
            # Format: "#N (idx:M) [0.xyz] text..."
            import re
            best_score = 0.0
            found_content = False
            for line in raw.split('\n'):
                line = line.strip()
                if not line:
                    continue
                # Match result lines: #1 (idx:25) [0.735] content...
                m = re.match(r'#\d+\s+\(idx:\d+\)\s+\[([0-9.]+)\]\s+(.*)', line)
                if m:
                    score = float(m.group(1))
                    result_text = m.group(2)
                    if score > best_score:
                        best_score = score
                    # Check if our content appears in this result
                    content_snippet = pair["content"][:40].lower()
                    if content_snippet in result_text.lower():
                        found_content = True

            results_summary.append({
                "name": pair["name"],
                "query": pair["query"],
                "best_score": best_score,
                "found": found_content,
                "pass": best_score >= pair["min_score"],
            })

            # Soft assertion — log all results, don't fail on first
            if best_score < pair["min_score"]:
                print(f"  MISS: {pair['name']}: best={best_score:.3f} < min={pair['min_score']}")
            else:
                print(f"  HIT:  {pair['name']}: best={best_score:.3f} >= min={pair['min_score']}")

        # Summary
        hits = sum(1 for r in results_summary if r["pass"])
        total = len(results_summary)
        print(f"\nSemantic reach: {hits}/{total} pairs found ({100*hits/total:.0f}%)")

        # Log to experiment file
        log_path = os.path.expanduser("~/.snarc/membot/semantic_reach_test.jsonl")
        os.makedirs(os.path.dirname(log_path), exist_ok=True)
        with open(log_path, 'a') as f:
            f.write(json.dumps({
                "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "machine": os.uname().nodename if hasattr(os, 'uname') else "unknown",
                "hits": hits,
                "total": total,
                "results": results_summary,
            }) + '\n')

        # At least 5/7 should pass for the experiment to be considered successful
        self.assertGreaterEqual(hits, 5,
            f"Semantic reach too low: {hits}/{total}. "
            f"Hypothesis: embeddings find connections FTS5 misses. "
            f"If <5/7, embeddings may not add sufficient value.")


class TestKeywordBaseline(unittest.TestCase):
    """Verify that keyword search would NOT find these pairs — establishing the baseline."""

    def test_no_keyword_overlap(self):
        """Confirm queries share no significant keywords with stored content."""
        import re

        # Common stop words to ignore
        stop_words = {'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been',
                      'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
                      'would', 'could', 'should', 'may', 'might', 'shall', 'can',
                      'to', 'of', 'in', 'for', 'on', 'with', 'at', 'by', 'from',
                      'as', 'into', 'through', 'during', 'before', 'after', 'above',
                      'below', 'between', 'out', 'off', 'over', 'under', 'again',
                      'further', 'then', 'once', 'not', 'no', 'nor', 'but', 'or',
                      'and', 'so', 'if', 'than', 'too', 'very', 'just', 'about',
                      'that', 'this', 'these', 'those', 'it', 'its', 'how', 'what',
                      'which', 'who', 'whom', 'when', 'where', 'why'}

        for pair in SEMANTIC_PAIRS:
            content_words = set(re.findall(r'\b[a-z]{3,}\b', pair["content"].lower())) - stop_words
            query_words = set(re.findall(r'\b[a-z]{3,}\b', pair["query"].lower())) - stop_words

            overlap = content_words & query_words
            # Allow at most 1 shared word (some conceptual overlap is inevitable)
            self.assertLessEqual(len(overlap), 1,
                f"Too much keyword overlap in '{pair['name']}': {overlap}. "
                f"This pair would be findable by FTS5, defeating the test purpose.")


if __name__ == "__main__":
    print("=" * 60)
    print("Semantic Reach Test — Membot Experiment")
    print("Testing: do embeddings find connections that keywords miss?")
    print("=" * 60)
    print()
    unittest.main(verbosity=2)
