import os
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def templates_auto_reload(replit_deployment):
    """Lê Config.TEMPLATES_AUTO_RELOAD num processo novo (IS_PRODUCTION é lido no import)."""
    env = {**os.environ, 'REPLIT_DEPLOYMENT': replit_deployment}
    result = subprocess.run(
        [sys.executable, '-c', 'import config; print("RESULT", config.Config.TEMPLATES_AUTO_RELOAD)'],
        cwd=ROOT,
        env=env,
        check=True,
        capture_output=True,
        text=True,
    )
    line = next(l for l in result.stdout.splitlines() if l.startswith('RESULT '))
    return line.split(' ', 1)[1] == 'True'


class TemplateAutoReloadTest(unittest.TestCase):
    def test_preview_reloads_changed_templates(self):
        self.assertTrue(templates_auto_reload('0'))

    def test_production_keeps_templates_cached(self):
        self.assertFalse(templates_auto_reload('1'))


if __name__ == '__main__':
    unittest.main()
