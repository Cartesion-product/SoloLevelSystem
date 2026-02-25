"""Database initialization and migration management script.

Usage:
    python scripts/db_manage.py init        # Create database + run all migrations
    python scripts/db_manage.py migrate     # Run pending migrations (upgrade head)
    python scripts/db_manage.py rollback    # Rollback one migration version
    python scripts/db_manage.py rollback 2  # Rollback N migration versions
    python scripts/db_manage.py status      # Show current migration status
    python scripts/db_manage.py reset       # Drop all tables + re-run migrations (DANGEROUS)
    python scripts/db_manage.py create <message>  # Auto-generate a new migration file
"""

import argparse
import asyncio
import sys
from pathlib import Path

# Ensure project root is on sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from alembic import command
from alembic.config import Config
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from app.config import get_settings


def get_alembic_config() -> Config:
    """Build Alembic config programmatically, using app settings for the DB URL."""
    alembic_ini = PROJECT_ROOT / "alembic.ini"
    cfg = Config(str(alembic_ini))
    cfg.set_main_option("script_location", str(PROJECT_ROOT / "alembic"))
    cfg.set_main_option("sqlalchemy.url", get_settings().DATABASE_URL)
    return cfg


async def check_db_connection() -> bool:
    """Verify that the database is reachable."""
    settings = get_settings()
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return True
    except Exception as e:
        print(f"[ERROR] Cannot connect to database: {e}")
        print(f"        DATABASE_URL = {settings.DATABASE_URL}")
        return False
    finally:
        await engine.dispose()


async def ensure_database_exists():
    """Create the target database if it does not exist.

    Connects to the default 'postgres' database to issue CREATE DATABASE.
    """
    settings = get_settings()
    # Parse the target DB name from the URL
    # e.g. postgresql+asyncpg://user:pass@host:port/solo_leveling
    db_name = settings.DATABASE_URL.rsplit("/", 1)[-1]
    base_url = settings.DATABASE_URL.rsplit("/", 1)[0] + "/postgres"

    engine = create_async_engine(base_url, isolation_level="AUTOCOMMIT")
    try:
        async with engine.connect() as conn:
            result = await conn.execute(
                text("SELECT 1 FROM pg_database WHERE datname = :db"),
                {"db": db_name},
            )
            if result.scalar() is None:
                await conn.execute(text(f'CREATE DATABASE "{db_name}"'))
                print(f"[OK] Database '{db_name}' created.")
            else:
                print(f"[OK] Database '{db_name}' already exists.")
    except Exception as e:
        print(f"[ERROR] Failed to ensure database exists: {e}")
        sys.exit(1)
    finally:
        await engine.dispose()


def cmd_init(_args):
    """Create database (if needed) and run all migrations."""
    print("=== Database Init ===")
    asyncio.run(ensure_database_exists())

    if not asyncio.run(check_db_connection()):
        sys.exit(1)

    print("Running migrations to head...")
    cfg = get_alembic_config()
    command.upgrade(cfg, "head")
    print("[OK] All migrations applied.")


def cmd_migrate(_args):
    """Run pending migrations (upgrade to head)."""
    print("=== Database Migrate ===")
    if not asyncio.run(check_db_connection()):
        sys.exit(1)

    cfg = get_alembic_config()
    command.upgrade(cfg, "head")
    print("[OK] Migrations applied.")


def cmd_rollback(args):
    """Rollback N migration versions (default 1)."""
    steps = args.steps
    print(f"=== Database Rollback ({steps} step(s)) ===")
    if not asyncio.run(check_db_connection()):
        sys.exit(1)

    cfg = get_alembic_config()
    command.downgrade(cfg, f"-{steps}")
    print(f"[OK] Rolled back {steps} migration(s).")


def cmd_status(_args):
    """Show current migration status."""
    print("=== Database Migration Status ===")
    if not asyncio.run(check_db_connection()):
        sys.exit(1)

    cfg = get_alembic_config()
    command.current(cfg, verbose=True)
    print()
    command.history(cfg, verbose=False)


def cmd_reset(args):
    """Drop all tables and re-run all migrations. DANGEROUS."""
    if not args.yes:
        confirm = input("WARNING: This will DROP ALL TABLES. Type 'yes' to confirm: ")
        if confirm.strip().lower() != "yes":
            print("Aborted.")
            return

    print("=== Database Reset ===")
    if not asyncio.run(check_db_connection()):
        sys.exit(1)

    cfg = get_alembic_config()
    # Stamp to base (reset version tracking without running downgrade SQL,
    # which would fail if tables were already dropped externally)
    print("Stamping alembic version to base...")
    command.stamp(cfg, "base")
    # Drop any remaining tables via SQLAlchemy metadata
    from app.infrastructure.database import Base

    async def _drop_all():
        engine = create_async_engine(get_settings().DATABASE_URL)
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        await engine.dispose()

    asyncio.run(_drop_all())
    print("All tables dropped.")
    # Re-apply all migrations
    print("Re-applying all migrations...")
    command.upgrade(cfg, "head")
    print("[OK] Database reset complete.")


def cmd_create(args):
    """Auto-generate a new migration file from model changes."""
    message = args.message
    if not message:
        print("[ERROR] Please provide a migration message: python scripts/db_manage.py create 'add xxx table'")
        sys.exit(1)

    print(f"=== Create Migration: {message} ===")
    if not asyncio.run(check_db_connection()):
        sys.exit(1)

    cfg = get_alembic_config()
    command.revision(cfg, message=message, autogenerate=True)
    print("[OK] Migration file created. Check alembic/versions/")


def main():
    parser = argparse.ArgumentParser(
        description="Solo Leveling System - Database Management",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # init
    subparsers.add_parser("init", help="Create database and run all migrations")

    # migrate
    subparsers.add_parser("migrate", help="Run pending migrations")

    # rollback
    p_rollback = subparsers.add_parser("rollback", help="Rollback migration(s)")
    p_rollback.add_argument("steps", nargs="?", type=int, default=1, help="Number of versions to rollback (default: 1)")

    # status
    subparsers.add_parser("status", help="Show migration status")

    # reset
    p_reset = subparsers.add_parser("reset", help="Drop all tables and re-migrate (DANGEROUS)")
    p_reset.add_argument("-y", "--yes", action="store_true", help="Skip confirmation prompt")

    # create
    p_create = subparsers.add_parser("create", help="Auto-generate a new migration file")
    p_create.add_argument("message", nargs="?", help="Migration description")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    handlers = {
        "init": cmd_init,
        "migrate": cmd_migrate,
        "rollback": cmd_rollback,
        "status": cmd_status,
        "reset": cmd_reset,
        "create": cmd_create,
    }
    handlers[args.command](args)


if __name__ == "__main__":
    main()
