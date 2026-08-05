"""EXP-HEKB007's HEKB MCP Daemon Service: a real, standalone network daemon.

Every prior experiment's MCP interface (`_mcp_reference.MCPReferenceQuery`,
EXP-HEKB002) is explicitly, deliberately in-process -- "implementing the
actual MCP wire/transport format is infrastructure this experiment does not
need" (`docs/RFC_ALIGNMENT.md`). EXP-HEKB007's own specification names a
standalone TCP/Unix Socket daemon and a 100-concurrent-client load test as
an explicit target component, and this workspace's stdlib (`socketserver`,
`threading`, `socket`, `json`) is always available -- unlike a real image
decoder or a real homotopy algorithm, a local TCP daemon is not "an
external repository or unavailable runtime" this experiment must report
BLOCKED on. This module is the missing piece: a real, minimal TCP daemon
wrapping `_mcp_reference.MCPReferenceQuery` unmodified (no new retrieval
algorithm, no change to `_semantic_closure.compute_closure`), so
Test D / tau_mcp_net can be measured over a genuine socket round-trip
instead of an in-process call.

Wire format is deliberately simple, not the full formal MCP JSON-RPC 2.0
envelope: one newline-terminated JSON request object per connection
(`{"concept_id": "..."}`), one newline-terminated JSON response object back
(`_mcp_reference.MCPResponse`, plus an `"error"` field on failure). This is
a real network transport -- real listening socket, real accepted
connections, real bytes over 127.0.0.1 -- not a claim about implementing
the full Model Context Protocol wire specification.
"""

from __future__ import annotations

import dataclasses
import json
import socket
import socketserver
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from typing import Any

from _mcp_reference import MCPReferenceQuery
from hekb.category import KnowledgeCategory

_ENCODING = "utf-8"
_RECV_CHUNK = 4096
_CLIENT_TIMEOUT_S = 5.0


class _Handler(socketserver.StreamRequestHandler):
    def handle(self) -> None:
        server: HEKBMCPDaemon = self.server  # type: ignore[assignment]
        line = self.rfile.readline()
        if not line:
            return
        try:
            request = json.loads(line.decode(_ENCODING))
            concept_id = request["concept_id"]
            response = server.query.query(concept_id)
            payload: dict[str, Any] = {"ok": True, "response": dataclasses.asdict(response)}
        except Exception as exc:
            # crash the daemon or hang the connection; it gets a real error
            # response instead, the network-transport analogue of
            # `_run_pipeline`'s harness-level quarantine elsewhere in this repo.
            payload = {"ok": False, "error": f"{type(exc).__name__}: {exc}"}
        self.wfile.write((json.dumps(payload) + "\n").encode(_ENCODING))


class HEKBMCPDaemon(socketserver.ThreadingTCPServer):
    """A real, standalone TCP daemon over `_mcp_reference.MCPReferenceQuery`.

    `allow_reuse_address` avoids `TIME_WAIT` bind failures across repeated
    experiment runs; binding to port 0 lets the OS pick a free ephemeral
    port, so this daemon claims no fixed port and can run alongside anything
    else already listening on this machine.
    """

    daemon_threads = True
    allow_reuse_address = True
    # A 100-concurrent-client burst arriving on one listening socket needs a
    # real backlog deeper than `socketserver`'s default of 5, or the OS
    # itself queues/delays the excess SYNs -- a real accept-queue effect,
    # not a simulated one, but one this daemon should not be measured
    # against by leaving an under-provisioned default in place.
    request_queue_size = 256

    def __init__(self, query: MCPReferenceQuery) -> None:
        super().__init__(("127.0.0.1", 0), _Handler)
        self.query = query

    @property
    def port(self) -> int:
        return self.server_address[1]


@dataclass(frozen=True, slots=True)
class ClientResult:
    concept_id: str
    ok: bool
    latency_ms: float
    error: str | None


def _send_one(port: int, concept_id: str) -> ClientResult:
    start = time.perf_counter()
    try:
        with socket.create_connection(("127.0.0.1", port), timeout=_CLIENT_TIMEOUT_S) as sock:
            sock.sendall((json.dumps({"concept_id": concept_id}) + "\n").encode(_ENCODING))
            sock.shutdown(socket.SHUT_WR)
            chunks: list[bytes] = []
            while True:
                chunk = sock.recv(_RECV_CHUNK)
                if not chunk:
                    break
                chunks.append(chunk)
                if chunks[-1].endswith(b"\n"):
                    break
            body = b"".join(chunks).decode(_ENCODING)
        elapsed_ms = (time.perf_counter() - start) * 1000.0
        payload = json.loads(body)
        return ClientResult(
            concept_id=concept_id,
            ok=bool(payload.get("ok")),
            latency_ms=elapsed_ms,
            error=payload.get("error"),
        )
    except OSError as exc:
        elapsed_ms = (time.perf_counter() - start) * 1000.0
        return ClientResult(
            concept_id=concept_id,
            ok=False,
            latency_ms=elapsed_ms,
            error=f"{type(exc).__name__}: {exc}",
        )


def run_concurrent_load_test(
    category: KnowledgeCategory,
    relation_kind: dict[str, str],
    object_category: dict[str, str],
    concept_ids: tuple[str, ...],
    *,
    concurrent_clients: int = 100,
) -> dict[str, Any]:
    """Test D: start the real daemon, fire `concurrent_clients` real,
    concurrent TCP client connections at it (round-robin over
    `concept_ids`), and report real measured latency -- no simulated
    timing anywhere in this function."""
    query = MCPReferenceQuery(
        category=category, relation_kind=relation_kind, object_category=object_category
    )
    daemon = HEKBMCPDaemon(query)
    thread = threading.Thread(target=daemon.serve_forever, daemon=True)
    thread.start()
    try:
        targets = [concept_ids[i % len(concept_ids)] for i in range(concurrent_clients)]
        with ThreadPoolExecutor(max_workers=concurrent_clients) as pool:
            results = list(pool.map(lambda cid: _send_one(daemon.port, cid), targets))
    finally:
        daemon.shutdown()
        daemon.server_close()
        thread.join(timeout=_CLIENT_TIMEOUT_S)

    latencies = sorted(r.latency_ms for r in results)
    successes = [r for r in results if r.ok]
    p50 = latencies[len(latencies) // 2] if latencies else None
    p99 = latencies[int(len(latencies) * 0.99)] if latencies else None
    return {
        "port": daemon.port,
        "concurrent_clients": concurrent_clients,
        "requests_sent": len(results),
        "requests_succeeded": len(successes),
        "requests_failed": len(results) - len(successes),
        "failures": [{"concept_id": r.concept_id, "error": r.error} for r in results if not r.ok],
        "latency_p50_ms": p50,
        "latency_p99_ms": p99,
        "latency_max_ms": latencies[-1] if latencies else None,
        "all_succeeded": len(successes) == len(results),
    }


__all__ = [
    "ClientResult",
    "HEKBMCPDaemon",
    "run_concurrent_load_test",
]
