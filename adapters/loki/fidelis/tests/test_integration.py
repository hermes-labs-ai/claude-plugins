"""Exercise Loki's real provider discovery against a local Fidelis wire stub."""

from __future__ import annotations

import json
import os
import shutil
import tempfile
import threading
import unittest
from contextlib import redirect_stdout
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from io import StringIO
from pathlib import Path
from unittest.mock import patch

from agent.memory_manager import MemoryManager
from loki_cli.config import load_config
from loki_cli.memory_setup import cmd_setup_provider
from plugins.memory import load_memory_provider


PLUGIN_ROOT = Path(__file__).resolve().parents[1]


class _FidelisStub(BaseHTTPRequestHandler):
    calls: list[tuple[str, dict]] = []
    write_status = "stored"
    superseded = False
    old_api = False

    def do_POST(self):
        body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        self.calls.append((self.path, body))
        if self.path in ("/query", "/recall_hybrid"):
            result = {
                "memories": [
                    {
                        "id": "current-1",
                        "text": "The project uses local memory.",
                        "temporal": {"status": "current"},
                    },
                    {
                        "id": "old-1",
                        "text": "The project used cloud memory.",
                        "temporal": {"status": "superseded"},
                    },
                ]
            }
        elif self.path == "/get":
            if self.old_api:
                encoded = b'{"error":"not found"}'
                self.send_response(404)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(encoded)))
                self.end_headers()
                self.wfile.write(encoded)
                return
            result = {
                "id": body["id"],
                "temporal": {"status": "superseded" if self.superseded else "current"},
            }
        elif self.path == "/store":
            result = {"status": self.write_status, "id": "new-1"}
        else:
            self.send_error(404)
            return
        encoded = json.dumps(result).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def log_message(self, *args):
        pass


class FidelisIntegrationTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        home = Path(self.tmp.name)
        target = home / "plugins" / "fidelis"
        target.mkdir(parents=True)
        for name in ("__init__.py", "plugin.yaml"):
            shutil.copyfile(PLUGIN_ROOT / name, target / name)
        self.env = patch.dict(
            os.environ, {"LOKI_HOME": str(home), "FIDELIS_PORT": "19420"}
        )
        self.env.start()
        self.addCleanup(self.env.stop)
        _FidelisStub.calls = []
        _FidelisStub.write_status = "stored"
        _FidelisStub.superseded = False
        _FidelisStub.old_api = False
        self.server = ThreadingHTTPServer(("127.0.0.1", 0), _FidelisStub)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.addCleanup(self.server.server_close)
        self.addCleanup(self.server.shutdown)
        os.environ["FIDELIS_PORT"] = str(self.server.server_port)

    def test_native_discovery_and_prompt_recall(self):
        provider = load_memory_provider("fidelis")
        self.assertIsNotNone(provider)
        self.assertTrue(provider.is_available())
        with redirect_stdout(StringIO()):
            cmd_setup_provider("fidelis")
        self.assertEqual("fidelis", load_config()["memory"]["provider"])
        manager = MemoryManager()
        manager.add_provider(provider)
        manager.initialize_all(
            session_id="session-1", loki_home=os.environ["LOKI_HOME"]
        )
        self.assertIn(
            "fidelis_store", {tool["name"] for tool in manager.get_all_tool_schemas()}
        )
        result = manager.prefetch_all(
            "What memory does this project use?", session_id="session-1"
        )
        self.assertIn("The project uses local memory.", result)
        self.assertNotIn("The project used cloud memory.", result)
        self.assertIn(
            ("/query", {"text": "What memory does this project use?", "limit": 5}),
            _FidelisStub.calls,
        )
        self.assertEqual("", manager.prefetch_all("thanks", session_id="session-1"))
        manager.shutdown_all()

    def test_explicit_tools_preserve_write_outcome_and_corrections(self):
        provider = load_memory_provider("fidelis")
        manager = MemoryManager()
        manager.add_provider(provider)
        schemas = {item["name"] for item in provider.get_tool_schemas()}
        self.assertEqual(
            {"fidelis_recall", "fidelis_store", "fidelis_correct"}, schemas
        )
        recall = json.loads(
            provider.handle_tool_call(
                "fidelis_recall", {"query": "project memory", "mode": "thorough"}
            )
        )
        self.assertEqual("thorough", recall["mode"])
        self.assertEqual("zero_llm", _FidelisStub.calls[-1][1]["tier"])

        stored = json.loads(
            manager.handle_tool_call(
                "fidelis_store", {"text": "A lasting project fact."}
            )
        )
        self.assertEqual("stored", stored["status"])
        self.assertEqual({"text": "A lasting project fact."}, _FidelisStub.calls[-1][1])

        _FidelisStub.write_status = "queued"
        queued = json.loads(
            provider.handle_tool_call(
                "fidelis_store", {"text": "Another lasting fact."}
            )
        )
        self.assertEqual("queued", queued["status"])
        self.assertIn("Not yet recallable", queued["message"])

        _FidelisStub.write_status = "stored"
        corrected = json.loads(
            provider.handle_tool_call(
                "fidelis_correct",
                {"id": "old-1", "text": "The project uses local memory."},
            )
        )
        self.assertEqual("stored", corrected["status"])
        self.assertEqual(["old-1"], _FidelisStub.calls[-1][1]["supersedes"])

        _FidelisStub.superseded = True
        before = len(_FidelisStub.calls)
        refused = json.loads(
            provider.handle_tool_call(
                "fidelis_correct", {"id": "old-1", "text": "Another correction."}
            )
        )
        self.assertIn("already superseded", refused["error"])
        self.assertEqual(before + 1, len(_FidelisStub.calls))

        _FidelisStub.old_api = True
        obsolete_service = json.loads(
            provider.handle_tool_call(
                "fidelis_correct", {"id": "old-1", "text": "Another correction."}
            )
        )
        self.assertIn("0.3.0rc1", obsolete_service["error"])


if __name__ == "__main__":
    unittest.main()
