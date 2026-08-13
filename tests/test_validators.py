import pytest
from fastapi import HTTPException

from app.utils.validators import validate_nickname


def test_should_accept_safe_nickname():
    assert validate_nickname("Pikachu") == "Pikachu"
    assert validate_nickname("  Raichu  ") == "Raichu"


def test_should_return_none_for_empty_nickname():
    assert validate_nickname(None) is None
    assert validate_nickname("   ") is None


def test_should_reject_nickname_longer_than_20_chars():
    with pytest.raises(HTTPException) as exc:
        validate_nickname("A" * 21)
    assert exc.value.status_code == 400


def test_should_reject_xss_in_nickname():
    with pytest.raises(HTTPException) as exc:
        validate_nickname("<script>alert(1)</script>")
    assert exc.value.status_code == 400


def test_should_reject_event_handler_in_nickname():
    with pytest.raises(HTTPException) as exc:
        validate_nickname('bad" onerror="alert(1)')
    assert exc.value.status_code == 400
