import pytest
from pydantic import ValidationError

from app.models.pokemon import UpdateTeamEvsRequest


def test_should_reject_empty_updated_members_list():
    with pytest.raises(ValidationError):
        UpdateTeamEvsRequest(updated_members=[])


def test_should_reject_evs_above_252():
    with pytest.raises(ValidationError):
        UpdateTeamEvsRequest(
            updated_members=[
                {
                    "pokemon_id": 6,
                    "evs": {"hp": 300, "attack": 0},
                }
            ]
        )


def test_should_reject_total_evs_above_510():
    with pytest.raises(ValidationError):
        UpdateTeamEvsRequest(
            updated_members=[
                {
                    "pokemon_id": 6,
                    "evs": {"hp": 252, "attack": 252, "defense": 10},
                }
            ]
        )


def test_should_accept_valid_evs_payload():
    request = UpdateTeamEvsRequest(
        updated_members=[
            {
                "pokemon_id": 6,
                "evs": {"hp": 252, "attack": 252, "defense": 0},
            }
        ]
    )
    assert request.updated_members[0].pokemon_id == 6
