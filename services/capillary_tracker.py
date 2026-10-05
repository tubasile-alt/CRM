"""Cliente somente leitura para consultar cirurgias no CapillaryTracker."""

import json
import logging
import os
import re
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from difflib import SequenceMatcher

logger = logging.getLogger(__name__)

TIMEOUT_SECONDS = 12
MAX_RESULTS = 30


class TrackerNotConfigured(RuntimeError):
    """URL/chave do Tracker ausentes ou recusadas pelo Tracker."""


def _config():
    base = (os.environ.get("TRACKER_API_URL") or "").strip().rstrip("/")
    key = (os.environ.get("TRACKER_API_KEY") or "").strip()
    if not base or not key:
        raise TrackerNotConfigured(
            "TRACKER_API_URL / TRACKER_API_KEY não configuradas"
        )

    parsed = urllib.parse.urlparse(base)
    host = parsed.hostname or ""
    local_http = parsed.scheme == "http" and host in ("localhost", "127.0.0.1")
    if parsed.scheme != "https" and not local_http:
        raise TrackerNotConfigured("TRACKER_API_URL deve usar https://")
    if not host or parsed.username or parsed.password:
        raise TrackerNotConfigured("TRACKER_API_URL inválida")

    return base, key


def normalize_name(name):
    """Minúsculas, sem acento, sem pontuação e com espaços colapsados."""
    if not name:
        return ""
    normalized = unicodedata.normalize("NFKD", str(name))
    normalized = "".join(
        char for char in normalized if not unicodedata.combining(char)
    )
    normalized = re.sub(r"[^a-zA-Z0-9\s]", " ", normalized).lower()
    return re.sub(r"\s+", " ", normalized).strip()


def score_names(a_norm, b_norm):
    """Similaridade de 0 a 1 entre nomes já normalizados."""
    if not a_norm or not b_norm:
        return 0.0
    if a_norm == b_norm:
        return 1.0

    tokens_a, tokens_b = set(a_norm.split()), set(b_norm.split())
    jaccard = len(tokens_a & tokens_b) / len(tokens_a | tokens_b)
    sequence = SequenceMatcher(
        None, " ".join(sorted(tokens_a)), " ".join(sorted(tokens_b))
    ).ratio()
    score = max(jaccard, sequence)
    if min(len(tokens_a), len(tokens_b)) >= 2 and (
        tokens_a <= tokens_b or tokens_b <= tokens_a
    ):
        score = max(score, 0.9)
    return round(score, 3)


def _label(score):
    if score >= 1.0:
        return "exato"
    if score >= 0.85:
        return "provavel"
    return "possivel"


def _fetch_candidates(name):
    base, key = _config()
    url = f"{base}/api/integracao/cirurgias?" + urllib.parse.urlencode(
        {"nome": name}
    )
    request = urllib.request.Request(
        url,
        headers={"X-API-Key": key, "Accept": "application/json"},
    )

    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        if exc.code in (401, 503):
            raise TrackerNotConfigured(
                f"Tracker recusou a chave (HTTP {exc.code})"
            ) from exc
        raise

    if not isinstance(payload, dict):
        return []
    matches = payload.get("matches")
    return matches if isinstance(matches, list) else []


def search_by_name(name):
    """Retorna cirurgias do Tracker que correspondem ao nome informado."""
    target = normalize_name(name)
    if not any(len(token) >= 2 for token in target.split()):
        return []

    results = []
    for candidate in _fetch_candidates(name):
        if not isinstance(candidate, dict):
            continue
        score = score_names(target, normalize_name(candidate.get("nome")))
        if score < 0.5:
            continue
        result = dict(candidate)
        result["match_score"] = score
        result["match_label"] = _label(score)
        result.setdefault("necroses", [])
        results.append(result)

    results.sort(
        key=lambda item: (item["match_score"], str(item.get("data") or "")),
        reverse=True,
    )
    return results[:MAX_RESULTS]
