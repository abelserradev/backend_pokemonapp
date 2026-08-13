from datetime import datetime, timezone


def utc_now() -> datetime:
    """UTC actual como datetime naive.

    datetime.utcnow() está deprecado (3.12+), pero las columnas DateTime de
    SQLAlchemy son naive: usar now(timezone.utc) directo rompe las restas
    contra fechas leídas de MySQL. Se conserva la semántica naive-UTC.

    TODO: migrar columnas a DateTime(timezone=True) y devolver aware datetimes.
    """
    return datetime.now(timezone.utc).replace(tzinfo=None)
