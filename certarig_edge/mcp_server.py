from __future__ import annotations

import os
from typing import Any

from .agent import propose_plan_with_openai
from .client import CertaRigClient


def build_server():
    try:
        from mcp.server.fastmcp import FastMCP
    except ImportError as exc:
        raise RuntimeError("install the agent extra with: pip install -e '.[agent]'") from exc

    base_url = os.environ.get("CERTARIG_EDGE_URL", "http://127.0.0.1:8080")
    client = CertaRigClient(base_url)
    server = FastMCP("CertaRig review tools")

    @server.tool()
    def get_rig_snapshot() -> dict[str, Any]:
        """Read the current rig snapshot. This tool cannot change an output."""
        return client.snapshot()

    @server.tool()
    def propose_commissioning_plan(objective: str) -> dict[str, Any]:
        """Propose and validate a reviewable plan. This tool cannot approve or execute it."""
        health = client.health()
        snapshot = client.snapshot()
        proposal = propose_plan_with_openai(
            snapshot=snapshot,
            pressure_abort_bar=float(health.get("pressure_abort_bar", 4.2)),
            objective=objective,
        )
        return client.create_plan(proposal)

    @server.tool()
    def get_run_evidence(run_id: str) -> dict[str, Any]:
        """Read an existing evidence bundle by run identifier."""
        return client.evidence(run_id)

    return server


def main() -> None:
    build_server().run()


if __name__ == "__main__":
    main()
