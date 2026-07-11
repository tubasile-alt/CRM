"""Contrato estrutural das rotas antes da migração para Blueprints."""

import json
import os

from tests.route_audit import collect_route_inventory, duplicate_route_method_pairs


INVENTORY_PATH = os.path.join(
    os.path.dirname(__file__), os.pardir, "route-inventory.json"
)


# As duplicidades conhecidas foram removidas intencionalmente no commit 8fca445.
# Qualquer nova colisão deve falhar até revisão explícita.
KNOWN_DUPLICATE_ROUTE_METHODS = {}


def test_route_inventory_has_unique_endpoint_rules(flask_app):
    inventory = collect_route_inventory(flask_app)

    signatures = [
        (item["path"], tuple(item["methods"]), item["endpoint"])
        for item in inventory
    ]

    assert len(signatures) == len(set(signatures)), (
        "A mesma regra, métodos e endpoint foram registrados mais de uma vez."
    )


def test_duplicate_route_method_baseline(flask_app):
    inventory = collect_route_inventory(flask_app)
    duplicates = duplicate_route_method_pairs(inventory)

    assert duplicates == KNOWN_DUPLICATE_ROUTE_METHODS, (
        "O conjunto de rotas duplicadas mudou. Consolide a implementação ou "
        "atualize este baseline somente após revisão explícita.\n"
        f"Esperado: {KNOWN_DUPLICATE_ROUTE_METHODS}\n"
        f"Encontrado: {duplicates}"
    )


def test_inventory_records_endpoint_and_blueprint(flask_app):
    inventory = collect_route_inventory(flask_app)

    assert inventory, "A aplicação não registrou rotas."
    for item in inventory:
        assert item["path"].startswith("/")
        assert item["methods"]
        assert item["endpoint"]
        if "." in item["endpoint"]:
            assert item["blueprint"] == item["endpoint"].split(".", 1)[0]
        else:
            assert item["blueprint"] is None


def test_no_route_removed_or_methods_changed(flask_app):
    """Nenhuma rota do snapshot pode sumir ou mudar de métodos.

    Rotas novas são permitidas; remoção exige regenerar o snapshot
    conscientemente via scripts/audit_routes.py.
    """
    with open(INVENTORY_PATH, encoding="utf-8") as inventory_file:
        snapshot = json.load(inventory_file)["routes"]

    current = {
        (item["path"], tuple(sorted(item["methods"]))): item["endpoint"]
        for item in collect_route_inventory(flask_app)
    }
    missing = []
    for item in snapshot:
        key = (item["path"], tuple(sorted(item["methods"])))
        if key not in current:
            missing.append(key)

    assert not missing, f"Rotas REMOVIDAS ou com métodos alterados: {missing}"
