"""Sincroniza a aba Botox sob demanda.

Uso:
    python scripts/sync_botox_sheet.py
    python scripts/sync_botox_sheet.py --dry-run
"""

import argparse
import os
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

os.environ.setdefault('DISABLE_SCHEDULER', '1')

from app import app  # noqa: E402
from services.botox_sheet_service import (  # noqa: E402
    build_botox_sheet_rows,
    run_botox_sheet_sync,
)


def main():
    parser = argparse.ArgumentParser(description='Sincroniza a aba Botox.')
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Mostra a reconciliação sem escrever na planilha.',
    )
    args = parser.parse_args()

    with app.app_context():
        if args.dry_run:
            matrix = build_botox_sheet_rows()
            print(f'linhas de dados: {len(matrix) - 1}')
            print(f'cabeçalho: {matrix[0]}')
            for row in matrix[1:4]:
                print(f'  {row}')
            if len(matrix) > 4:
                print(f'  ... (+{len(matrix) - 4})')
            print('\nDRY-RUN: nada foi escrito na planilha.')
            return 0

        ok, message = run_botox_sheet_sync()
        print(('✓ ' if ok else '✗ ') + message)
        return 0 if ok else 1


if __name__ == '__main__':
    raise SystemExit(main())