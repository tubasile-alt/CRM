"""Official Alembic entrypoint for this project.

Use this wrapper for every database migration command. Running ``alembic``
directly from the shell is not supported because the project configuration
and database URL are resolved inside the Flask application context.
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
MIGRATIONS_DIR = PROJECT_ROOT / "migrations"

# The application starts a background scheduler during import unless this is
# set. Migration commands must never start that scheduler.
os.environ["DISABLE_SCHEDULER"] = "1"
sys.path.insert(0, str(PROJECT_ROOT))

from alembic import command
from alembic.config import Config


def _alembic_config() -> Config:
    config = Config(str(MIGRATIONS_DIR / "alembic.ini"))
    config.set_main_option("script_location", str(MIGRATIONS_DIR))
    return config


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run Alembic inside the DermaScribe Flask app context."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    heads = subparsers.add_parser("heads", help="Show migration heads.")
    heads.add_argument("-v", "--verbose", action="store_true")

    history = subparsers.add_parser("history", help="Show migration history.")
    history.add_argument("revision_range", nargs="?")
    history.add_argument("-v", "--verbose", action="store_true")

    current = subparsers.add_parser("current", help="Show the database revision.")
    current.add_argument("-v", "--verbose", action="store_true")
    current.add_argument("--check-heads", action="store_true")

    upgrade = subparsers.add_parser("upgrade", help="Upgrade to a revision.")
    upgrade.add_argument("revision")

    downgrade = subparsers.add_parser("downgrade", help="Downgrade to a revision.")
    downgrade.add_argument("revision")

    stamp = subparsers.add_parser("stamp", help="Stamp the database revision.")
    stamp.add_argument("revision")
    stamp.add_argument("--purge", action="store_true")

    return parser


def main() -> None:
    args = _parser().parse_args()
    config = _alembic_config()

    # Import the Flask app only after DISABLE_SCHEDULER has been set.
    from app import app

    with app.app_context():
        if args.command == "heads":
            command.heads(config, verbose=args.verbose)
        elif args.command == "history":
            command.history(
                config,
                rev_range=args.revision_range,
                verbose=args.verbose,
            )
        elif args.command == "current":
            command.current(
                config,
                check_heads=args.check_heads,
                verbose=args.verbose,
            )
        elif args.command == "upgrade":
            command.upgrade(config, args.revision)
        elif args.command == "downgrade":
            command.downgrade(config, args.revision)
        elif args.command == "stamp":
            command.stamp(config, args.revision, purge=args.purge)
        else:
            raise RuntimeError(f"Comando desconhecido: {args.command}")


if __name__ == "__main__":
    main()