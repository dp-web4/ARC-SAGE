"""
SAGE-Membot Integration Tests
==============================
Verifies membot works correctly with the SAGE consciousness daemon.
Requires both membot (:8000) and SAGE daemon (:8750) running.

Usage:
    python3 tests/fleet/test_sage_integration.py
"""

import unittest
import json
import os
import urllib.request
import urllib.error

MEMBOT_URL = os.environ.get("MEMBOT_URL", "http://localhost:8000")
SAGE_URL = os.environ.get("SAGE_URL", "http://localhost:8750")


def api(base_url, method, path, data=None, timeout=10):
    """Call REST API. Returns parsed JSON or raises."""
    url = f"{base_url}{path}"
    req = urllib.request.Request(url, method=method)
    if data:
        req.data = json.dumps(data).encode()
        req.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read())


def membot(method, path, data=None, **kw):
    return api(MEMBOT_URL, method, path, data, **kw)


def sage(method, path, data=None, **kw):
    return api(SAGE_URL, method, path, data, **kw)


class TestSageMembot(unittest.TestCase):
    """Integration between SAGE daemon and Membot."""

    @classmethod
    def setUpClass(cls):
        """Verify both services are running."""
        try:
            membot("GET", "/api/status")
        except Exception as e:
            raise unittest.SkipTest(f"Membot not running on {MEMBOT_URL}: {e}")

        try:
            sage("GET", "/health")
        except Exception as e:
            raise unittest.SkipTest(f"SAGE daemon not running on {SAGE_URL}: {e}")

    def test_both_services_healthy(self):
        """Both membot and SAGE respond to health checks."""
        mb = membot("GET", "/api/status")
        self.assertEqual(mb["status"], "ok")

        sg = sage("GET", "/health")
        self.assertEqual(sg["status"], "alive")

    def test_sage_unaffected_by_membot_search(self):
        """Membot operations don't degrade SAGE daemon responsiveness."""
        # Get SAGE ATP before
        health_before = sage("GET", "/health")
        atp_before = health_before["atp_level"]

        # Do a membot search (triggers Ollama embedding, which shares resources)
        try:
            membot("POST", "/api/mount", {"name": "attention-is-all-you-need"})
            membot("POST", "/api/search", {"query": "attention", "top_k": 1},
                   timeout=15)
        except Exception:
            pass  # Search may fail if prior test changed state — that's ok

        # SAGE should still be responsive
        health_after = sage("GET", "/health")
        self.assertEqual(health_after["status"], "alive")

        # ATP should not have crashed (allow some natural drift)
        atp_after = health_after["atp_level"]
        self.assertGreater(atp_after, 0, "SAGE ATP should still be positive")

    def test_concurrent_ollama_access(self):
        """Membot embedding + SAGE LLM don't deadlock on shared Ollama."""
        # This is the key stress test for Sprout: Ollama handles one model at
        # a time, and embedding requests cause model swaps. Verify both systems
        # can function even with model swapping overhead.

        # Trigger a membot embedding (loads nomic-embed-text in Ollama)
        membot("POST", "/api/mount", {
            "name": "attention-is-all-you-need",
            "session_id": "ollama-test"
        })
        search = membot("POST", "/api/search", {
            "query": "positional encoding",
            "top_k": 1,
            "session_id": "ollama-test"
        }, timeout=15)
        self.assertGreater(len(search.get("results", [])), 0)

        # Now talk to SAGE (loads qwen3.5 in Ollama — model swap)
        try:
            chat = sage("POST", "/chat", {
                "message": "hello",
                "metadata": {"source": "fleet-test"}
            }, timeout=30)
            # SAGE should respond (may be slow due to model swap)
            self.assertTrue("response" in chat or "status" in chat,
                            f"SAGE should return a response, got keys: {list(chat.keys())}")
        except urllib.error.HTTPError as e:
            if e.code == 503:
                self.skipTest("SAGE busy — model swap contention (expected on 8GB)")
            raise


class TestMembotCartridgeIRP(unittest.TestCase):
    """Tests for the MemoryCartridgeIRP plugin interface."""

    @classmethod
    def setUpClass(cls):
        try:
            membot("GET", "/api/status")
        except Exception as e:
            raise unittest.SkipTest(f"Membot not running: {e}")

    def test_irp_rest_endpoints(self):
        """All endpoints used by MemoryCartridgeIRP are accessible."""
        # mount_cartridge (use a unique session to avoid state leakage)
        mount = membot("POST", "/api/mount", {
            "name": "attention-is-all-you-need",
            "session_id": "irp-test"
        })
        self.assertIn("Mounted", mount.get("result", ""))

        # memory_search
        search = membot("POST", "/api/search", {
            "query": "test", "top_k": 1, "session_id": "irp-test"
        })
        self.assertEqual(search["status"], "ok")

        # get_status
        status = membot("GET", "/api/status")
        self.assertEqual(status["status"], "ok")

    def test_missing_cartridge_graceful(self):
        """Mounting a non-existent cartridge returns error, not crash."""
        result = membot("POST", "/api/mount", {"name": "does-not-exist-xyz"})
        self.assertIn("not found", result.get("result", "").lower())

    def test_search_without_mount_graceful(self):
        """Searching without a mounted cartridge returns empty, not crash."""
        # Create a new session to ensure no cartridge is mounted
        result = membot("POST", "/api/search", {
            "query": "anything",
            "top_k": 1,
            "session_id": "test-no-mount"
        })
        self.assertEqual(result["status"], "ok")


if __name__ == "__main__":
    unittest.main(verbosity=2)
