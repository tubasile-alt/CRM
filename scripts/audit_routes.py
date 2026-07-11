"""Exporta o inventário de rotas Flask e destaca colisões.

Uso:
    python scripts/audit_routes.py
    python scripts/audit_routes.py --output route-inventory.json
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path


os.environ.setdefault("DISABLE_SCHEDULER", "1")


def load_app_without_scheduler():
    from apscheduler.schedulers.background import BackgroundScheduler

    original_start = BackgroundScheduler.start
    BackgroundScheduler.start = lambda self, *args, **kwargs: None
    try:
        from app import app

        return app
    finally:
        BackgroundScheduler.start = original_start


def main() -> int:
    parser = argparse.ArgumentParser(description="Audita as rotas registradas no CRM.")
    parser.add_argument(
        "--output",
        type=Path,
        help="Arquivo JSON de saída. Sem esta opção, imprime no terminal.",
    )
    args = parser.parse_args()

    from tests.route_audit import (
        collect_route_inventory,
        duplicate_route_method_pairs,
    )

    app = load_app_without_scheduler()
    inventory = collect_route_inventory(app)
    duplicates = duplicate_route_method_pairs(inventory)

    payload = {
        "route_count": len(inventory),
        "routes": inventory,
        "duplicate_route_method_pairs": [
            {
                "path": path,
                "method": method,
                "endpoints": endpoints,
            }
            for (path, method), endpoints in sorted(duplicates.items())
        ],
    }

    rendered = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered, encoding="utf-8")
        print(f"Inventário gravado em {args.output}")
    else:
        print(rendered, end="")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
