"""Configuração compartilhada dos testes.

O app inicia um APScheduler durante o import. Até que o bootstrap seja separado
em uma factory, os testes neutralizam somente o método ``start`` antes de
importar o módulo, evitando threads e acesso periódico ao banco durante pytest.
"""

import os

import pytest


os.environ.setdefault("DISABLE_SCHEDULER", "1")


@pytest.fixture(scope="session")
def flask_app():
    """Importa a aplicação sem iniciar o scheduler em segundo plano."""
    from apscheduler.schedulers.background import BackgroundScheduler

    original_start = BackgroundScheduler.start
    BackgroundScheduler.start = lambda self, *args, **kwargs: None
    try:
        from app import app

        app.config.update(TESTING=True)
        yield app
    finally:
        BackgroundScheduler.start = original_start
