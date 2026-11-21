"""Shared sprite/artwork presentation helpers for holo card responses.

Keeps the fake `sprites` dict and `card_presentation` payload in one place so
UserPokemon / TrainingSession / TeamMember responses stay consistent.
"""

from __future__ import annotations

from typing import Any, Dict, List, Literal, Optional

FoilKind = Literal["standard", "holo", "shiny"]


def build_sprites_dict(sprite_url: Optional[str]) -> Optional[Dict[str, str]]:
    """Legacy frontend shape: same URL mirrored into four sprite slots."""
    if not sprite_url:
        return None
    return {
        "front_default": sprite_url,
        "back_default": sprite_url,
        "front_shiny": sprite_url,
        "back_shiny": sprite_url,
    }


def derive_foil(
    pokemon_name: Optional[str] = None,
    sprite_url: Optional[str] = None,
    artwork_url: Optional[str] = None,
) -> FoilKind:
    # Team cards default to holo; only switch when name/URL clearly hints shiny.
    name = (pokemon_name or "").lower()
    blob = " ".join(part for part in (sprite_url or "", artwork_url or "") if part).lower()
    if "shiny" in name or "shiny" in blob:
        return "shiny"
    return "holo"


def build_card_presentation(
    *,
    sprite_url: Optional[str] = None,
    artwork_url: Optional[str] = None,
    types: Optional[List[str]] = None,
    pokemon_name: Optional[str] = None,
) -> Dict[str, Any]:
    return {
        "sprite_url": sprite_url,
        "artwork_url": artwork_url,
        "types": list(types) if types else [],
        "foil": derive_foil(pokemon_name, sprite_url, artwork_url),
    }
