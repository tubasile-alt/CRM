"""Contrato estrutural das rotas antes da migração para Blueprints."""

from tests.route_audit import collect_route_inventory, duplicate_route_method_pairs


# Duplicidades preexistentes identificadas na Fase 0. Este baseline não as
# considera corretas: apenas impede que novas duplicidades sejam introduzidas
# antes da etapa específica de consolidação.
KNOWN_DUPLICATE_ROUTE_METHODS = {
    ("/api/patient/<int:patient_id>/surgeries", "GET"): [
        "get_patient_surgeries",
        "patient.get_patient_surgeries",
    ],
    ("/api/patient/<int:patient_id>/surgery", "POST"): [
        "create_patient_surgery",
        "patient.create_patient_surgery",
    ],
}


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
