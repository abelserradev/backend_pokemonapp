"""Presentation payload for Three.js holo cards on /equipo (POST/GET /team)."""

from app.models.pokemon import UserPokemonResponse
from app.utils.card_presentation import build_card_presentation, derive_foil


ARTWORK_URL = (
    "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/"
    "pokemon/other/official-artwork/25.png"
)
SPRITE_URL = (
    "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/25.png"
)


def _auth_headers(client, unique_email: str) -> dict:
    password = "secret123"
    client.post(
        "/api/register",
        json={"email": unique_email, "password": password},
    )
    login = client.post(
        "/api/login/json",
        json={"email": unique_email, "password": password},
    )
    assert login.status_code == 200
    token = login.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_should_return_card_presentation_when_create_includes_artwork_and_sprite(
    client, unique_email
):
    headers = _auth_headers(client, unique_email)
    payload = {
        "pokemon_id": 25,
        "pokemon_name": "pikachu",
        "pokemon_sprite": SPRITE_URL,
        "pokemon_artwork": ARTWORK_URL,
        "pokemon_types": ["electric"],
        "level": 5,
    }

    create_response = client.post("/api/pokemon/team", json=payload, headers=headers)
    assert create_response.status_code == 200
    body = create_response.json()

    assert body["pokemon_sprite"] == SPRITE_URL
    assert body["pokemon_artwork"] == ARTWORK_URL
    assert body["pokemon_types"] == ["electric"]
    assert body["sprites"]["front_default"] == SPRITE_URL

    card = body["card_presentation"]
    assert card["sprite_url"] == SPRITE_URL
    assert card["artwork_url"] == ARTWORK_URL
    assert card["types"] == ["electric"]
    assert card["foil"] == "holo"

    team_response = client.get("/api/pokemon/team", headers=headers)
    assert team_response.status_code == 200
    team = team_response.json()
    assert len(team) == 1
    assert team[0]["card_presentation"]["artwork_url"] == ARTWORK_URL
    assert team[0]["pokemon_artwork"] == ARTWORK_URL


def test_should_keep_artwork_null_when_create_has_only_sprite(client, unique_email):
    headers = _auth_headers(client, unique_email)
    payload = {
        "pokemon_id": 1,
        "pokemon_name": "bulbasaur",
        "pokemon_sprite": SPRITE_URL.replace("/25.png", "/1.png"),
        "pokemon_types": ["grass", "poison"],
        "level": 1,
    }

    create_response = client.post("/api/pokemon/team", json=payload, headers=headers)
    assert create_response.status_code == 200
    body = create_response.json()

    assert body["pokemon_sprite"]
    assert body["pokemon_artwork"] is None
    assert body["pokemon_types"] == ["grass", "poison"]
    assert body["card_presentation"]["artwork_url"] is None
    assert body["card_presentation"]["sprite_url"] == body["pokemon_sprite"]
    assert body["card_presentation"]["foil"] == "holo"
    assert body["sprites"]["front_default"] == body["pokemon_sprite"]


def test_should_serialize_legacy_sprite_only_row_without_artwork():
    # ORM-like payload with only sprite (pre-holo rows)
    response = UserPokemonResponse(
        id=1,
        user_id=1,
        pokemon_id=6,
        pokemon_name="charizard",
        pokemon_sprite=SPRITE_URL.replace("/25.png", "/6.png"),
        pokemon_artwork=None,
        pokemon_types=None,
        selected_ability=None,
        nickname=None,
        level=50,
        added_at="2024-01-01T00:00:00",
    )
    assert response.pokemon_sprite
    assert response.pokemon_artwork is None
    assert response.sprites["front_default"] == response.pokemon_sprite
    assert response.card_presentation.artwork_url is None
    assert response.card_presentation.foil == "holo"
    assert response.card_presentation.types == []


def test_should_derive_shiny_foil_when_sprite_url_hints_shiny():
    foil = derive_foil(
        pokemon_name="pikachu",
        sprite_url="https://example.com/sprites/pokemon/shiny/25.png",
    )
    assert foil == "shiny"
    card = build_card_presentation(
        sprite_url="https://example.com/sprites/pokemon/shiny/25.png",
        artwork_url=None,
        types=["electric"],
        pokemon_name="pikachu",
    )
    assert card["foil"] == "shiny"
