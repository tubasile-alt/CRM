"""Utilitários para inventariar e comparar rotas Flask."""

from __future__ import annotations

from collections import defaultdict
from typing import Any

IGNORED_METHODS = {"HEAD", "OPTIONS"}


def collect_route_inventory(app: Any) -> list[dict[str, Any]]:
    """Retorna uma lista estável com uma entrada por regra registrada."""
    inventory: list[dict[str, Any]] = []

    for rule in app.url_map.iter_rules():
        methods = sorted(set(rule.methods or ()) - IGNORED_METHODS)
        endpoint = str(rule.endpoint)
        blueprint = endpoint.split(".", 1)[0] if "." in endpoint else None
        inventory.append(
            {
                "path": str(rule.rule),
                "methods": methods,
                "endpoint": endpoint,
                "blueprint": blueprint,
            }
        )

    return sorted(
        inventory,
        key=lambda item: (
            item["path"],
            ",".join(item["methods"]),
            item["endpoint"],
        ),
    )


def duplicate_route_method_pairs(
    inventory: list[dict[str, Any]],
) -> dict[tuple[str, str], list[str]]:
    """Agrupa pares caminho+método atendidos por mais de um endpoint."""
    grouped: dict[tuple[str, str], list[str]] = defaultdict(list)

    for item in inventory:
        for method in item["methods"]:
            grouped[(item["path"], method)].append(item["endpoint"])

    return {
        key: sorted(endpoints)
        for key, endpoints in grouped.items()
        if len(endpoints) > 1
    }
