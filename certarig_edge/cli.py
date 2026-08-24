from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from .app import CertaRigApplication, make_server
from .client import CertaRigClient
from .config import load_config
from .evidence import EvidenceStore
from .hardware.mock import MockHardware


def _build_hardware(config):
    if config.hardware.mode == "mock":
        return MockHardware(config)
    if config.hardware.mode == "raspberry_pi":
        from .hardware.raspberry_pi import RaspberryPiHardware

        return RaspberryPiHardware(config)
    raise ValueError(f"unsupported hardware mode: {config.hardware.mode}")


def serve(args: argparse.Namespace) -> None:
    operator_key = os.environ.get("CERTARIG_OPERATOR_KEY", "")
    if len(operator_key) < 12:
        raise SystemExit("CERTARIG_OPERATOR_KEY must be set to at least 12 characters")
    config = load_config(args.config)
    hardware = _build_hardware(config)
    store = EvidenceStore(args.database)
    app = CertaRigApplication(
        config=config,
        hardware=hardware,
        store=store,
        operator_key=operator_key,
        actuation_enabled=os.environ.get("CERTARIG_ENABLE_ACTUATION") == "1",
    )
    server = make_server(app, args.bind, args.port)
    print(
        json.dumps(
            {
                "event": "certarig_edge_started",
                "bind": args.bind,
                "port": server.server_port,
                "rig_id": config.rig_id,
                "hardware_mode": config.hardware.mode,
                "actuation_enabled": app.executor.actuation_enabled,
                "config_hash": config.config_hash,
            },
            indent=2,
        )
    )
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
        app.close()


def demo(args: argparse.Namespace) -> None:
    operator_key = os.environ.get("CERTARIG_OPERATOR_KEY")
    client = CertaRigClient(args.url, operator_key)
    health = client.health()
    snapshot = client.snapshot()
    plan = client.create_plan(
        {
            "rig_id": snapshot["rig_id"],
            "config_hash": snapshot["config_hash"],
            "purpose": "Supervised low energy valve response check",
            "pressure_limit_bar": 4.2,
            "steps": [
                {"action": "sample", "duration_ms": 200},
                {"action": "set_valve", "duration_ms": 700, "valve_open": True},
                {"action": "hold", "duration_ms": 500},
                {"action": "set_valve", "duration_ms": 200, "valve_open": False},
            ],
        }
    )
    output: dict[str, object] = {"health": health, "plan": plan}
    if args.execute:
        if not operator_key:
            raise SystemExit("CERTARIG_OPERATOR_KEY is required for approval and execution")
        approved = client.approve_plan(plan["plan_id"], args.operator)
        result = client.execute_plan(plan["plan_id"])
        output["approved_plan"] = approved
        output["result"] = result
        output["evidence"] = client.evidence(result["run_id"])
    print(json.dumps(output, indent=2, sort_keys=True))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="CertaRig deterministic edge service")
    subparsers = parser.add_subparsers(dest="command", required=True)
    serve_parser = subparsers.add_parser("serve", help="run the Raspberry Pi or mock edge API")
    serve_parser.add_argument("--config", default="config/rig.example.json")
    serve_parser.add_argument("--database", default="certarig-evidence.sqlite3")
    serve_parser.add_argument("--bind", default="127.0.0.1")
    serve_parser.add_argument("--port", type=int, default=8080)
    serve_parser.set_defaults(handler=serve)

    demo_parser = subparsers.add_parser("demo", help="run the computer side API workflow")
    demo_parser.add_argument("--url", default="http://127.0.0.1:8080")
    demo_parser.add_argument("--operator", default="Chintan Dedhia")
    demo_parser.add_argument("--execute", action="store_true")
    demo_parser.set_defaults(handler=demo)
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.handler(args)


if __name__ == "__main__":
    main()
