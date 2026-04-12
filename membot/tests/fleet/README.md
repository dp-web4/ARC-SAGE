# Fleet Integration Tests

Tests for verifying Membot works correctly across the dp-web4 fleet — different hardware, embedding backends, and integration points (SAGE, SNARC, Claude Code).

## Fleet Overview

| Machine | Hardware | RAM | Embedding Backend | Notes |
|---------|----------|-----|-------------------|-------|
| Sprout | Jetson Orin Nano (ARM64) | 8GB | Ollama (`nomic-embed-text`) | Resource-constrained stress test |
| CBP | WSL2 (x86_64) | 32GB | SentenceTransformer | Primary development |
| Legion | Linux (RTX 4090) | 64GB | SentenceTransformer + GPU lattice | Full physics mode |
| Thor | Linux (RTX 3090) | 32GB | SentenceTransformer + GPU lattice | Synthesis pool |
| McNugget | macOS (Apple Silicon) | 16GB | SentenceTransformer | Low volume |
| Nomad | macOS (Apple Silicon) | 16GB | SentenceTransformer | Mobile |

## Running Tests

```bash
# All tests (from membot root)
python3 tests/fleet/test_membot_health.py

# Quick smoke test
python3 tests/fleet/test_membot_health.py TestMembotHealth.test_server_responding

# Integration test (requires SAGE daemon)
python3 tests/fleet/test_sage_integration.py
```

## Test Categories

### `test_membot_health.py` — Server Health
- Server is reachable on expected port
- Embedding produces correct dimensionality (768)
- Cartridge mount/store/search/save cycle works
- Memory footprint stays within budget
- Writable mode is correctly set

### `test_sage_integration.py` — SAGE IRP Integration
- MemoryCartridgeIRP can connect to membot
- Search results flow into consciousness loop
- Dual-write (SNARC + membot) doesn't block
- Daemon health unaffected by membot operations

### `test_embedding_consistency.py` — Embedding Backend Validation
- Same query produces consistent vectors across calls
- Cosine similarity between related terms > 0.5
- Cosine similarity between unrelated terms < 0.3
- Embedding dimension is exactly 768
- Backend auto-detection works correctly

## Writing New Tests

Tests use plain `unittest` (no pytest dependency needed on constrained machines). Each test file is self-contained and can run independently.

```python
import unittest
import json
import urllib.request

MEMBOT_URL = "http://localhost:8000"

class TestNewFeature(unittest.TestCase):
    def _api(self, method, path, data=None):
        """Helper: call membot REST API."""
        url = f"{MEMBOT_URL}{path}"
        req = urllib.request.Request(url, method=method)
        if data:
            req.data = json.dumps(data).encode()
            req.add_header("Content-Type", "application/json")
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read())

    def test_something(self):
        status = self._api("GET", "/api/status")
        self.assertEqual(status["status"], "ok")

if __name__ == "__main__":
    unittest.main()
```

## Machine-Specific Considerations

### Sprout (ARM64, 8GB)
- Tests must not load SentenceTransformer (import guard)
- Memory assertions use 2GB ceiling (MemoryMax in systemd)
- Embedding latency is higher on first call (Ollama model swap ~5s)
- Cartridges built on Sprout are Ollama-only (not portable to ST machines)

### GPU Machines (Legion, Thor)
- Can test lattice recall (GPU physics mode)
- Higher memory budget — can test larger cartridges
- Embedding latency should be <50ms

### macOS (McNugget, Nomad)
- No systemd — use launchd or manual startup
- SentenceTransformer loads on CPU (no CUDA)
