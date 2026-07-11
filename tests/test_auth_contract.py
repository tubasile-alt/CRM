"""Toda rota não-pública deve exigir login.

Protege a migração contra perda de @login_required durante o copiar-colar.
"""

from werkzeug.routing import IntegerConverter


PUBLIC_PATHS = {
    "/",
    "/login",
    "/health",
    "/manifest.json",
    "/service-worker.js",
    "/apple-touch-icon.png",
    "/apple-touch-icon-precomposed.png",
    "/icon-192.png",
    "/icon-512.png",
    "/icon-1024.png",
    "/api/push/vapid-public-key",
}

# 400 aceito só para métodos com corpo: CSRFProtect pode rejeitar antes
# do login_required. GET sem login jamais pode retornar 2xx/5xx.
ALLOWED_GET = {301, 302, 401, 403}
ALLOWED_WRITE = {301, 302, 400, 401, 403}


def _concrete_path(rule):
    if not rule.arguments:
        return str(rule.rule)
    values = {}
    for name, conv in rule._converters.items():
        values[name] = 999999 if isinstance(conv, IntegerConverter) else "x"
    return rule.build(values, append_unknown=False)[1]


def test_every_route_requires_auth(flask_app):
    client = flask_app.test_client()
    failures = []
    for rule in flask_app.url_map.iter_rules():
        if rule.endpoint == "static" or str(rule.rule) in PUBLIC_PATHS:
            continue
        for method in sorted(rule.methods - {"HEAD", "OPTIONS"}):
            resp = client.open(_concrete_path(rule), method=method)
            allowed = ALLOWED_GET if method == "GET" else ALLOWED_WRITE
            if resp.status_code not in allowed:
                failures.append((method, str(rule.rule), resp.status_code))
    assert not failures, (
        f"Rotas acessíveis SEM LOGIN (regressão de @login_required?): {failures}"
    )
