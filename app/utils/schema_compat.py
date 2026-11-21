"""Best-effort ALTER helpers for nullable columns that create_all will not add.

Existing SQLite/MySQL databases keep old schemas until these columns are added
(manually or via this helper in tests). Never run against production from here —
callers decide when it is safe.
"""

from __future__ import annotations

from sqlalchemy import inspect, text
from sqlalchemy.engine import Engine

# Minimal presentation columns for Three.js holo cards on /equipo
_HOLO_COLUMNS = (
    ("user_pokemon", "pokemon_artwork", "VARCHAR(500)"),
    ("user_pokemon", "pokemon_types", "JSON"),
    ("pokemon_team_members", "pokemon_artwork", "VARCHAR(500)"),
)


def ensure_holo_presentation_columns(engine: Engine) -> None:
    """Add missing nullable artwork/types columns without touching existing rows."""
    inspector = inspect(engine)
    table_names = set(inspector.get_table_names())
    with engine.begin() as conn:
        for table, column, col_type in _HOLO_COLUMNS:
            if table not in table_names:
                continue
            existing = {col["name"] for col in inspector.get_columns(table)}
            if column in existing:
                continue
            # Identifier names are fixed constants above — not user input.
            conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {column} {col_type}"))
