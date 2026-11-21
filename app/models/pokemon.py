from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Optional, List, Dict, Literal
from datetime import datetime

from app.utils.card_presentation import build_card_presentation, build_sprites_dict


class CardPresentation(BaseModel):
    """Stable face payload for Three.js holo cards on /equipo."""

    sprite_url: Optional[str] = None
    artwork_url: Optional[str] = None
    types: List[str] = Field(default_factory=list)
    foil: Literal["standard", "holo", "shiny"] = "holo"


def _attach_presentation_fields(model: BaseModel) -> BaseModel:
    """Shared post-init enrichment for responses that mirror sprite URLs."""
    sprite = getattr(model, "pokemon_sprite", None)
    artwork = getattr(model, "pokemon_artwork", None)
    types = getattr(model, "pokemon_types", None)
    name = getattr(model, "pokemon_name", None)

    if getattr(model, "sprites", None) is None:
        model.sprites = build_sprites_dict(sprite)

    if getattr(model, "card_presentation", None) is None:
        model.card_presentation = CardPresentation(
            **build_card_presentation(
                sprite_url=sprite,
                artwork_url=artwork,
                types=types,
                pokemon_name=name,
            )
        )
    return model


# Modelos para User Pokemon
class UserPokemonCreate(BaseModel):
    pokemon_id: int
    pokemon_name: str
    pokemon_sprite: Optional[str] = None
    pokemon_artwork: Optional[str] = None
    pokemon_types: Optional[List[str]] = None
    selected_ability: Optional[str] = None
    nickname: Optional[str] = None
    level: int = 1
    base_stats: Optional[Dict[str, int]] = None


class UserPokemonResponse(BaseModel):
    id: int
    user_id: int
    pokemon_id: int
    pokemon_name: str
    pokemon_sprite: Optional[str]
    pokemon_artwork: Optional[str] = None
    pokemon_types: Optional[List[str]] = None
    selected_ability: Optional[str]
    nickname: Optional[str]
    level: int
    added_at: datetime

    # Estructura compatible con frontend
    sprites: Optional[Dict[str, str]] = None
    card_presentation: Optional[CardPresentation] = None

    class Config:
        from_attributes = True

    @model_validator(mode="after")
    def enrich_presentation(self):
        return _attach_presentation_fields(self)


# Modelos para Training Sessions
class TrainingSessionCreate(BaseModel):
    pokemon_id: int
    pokemon_name: str
    pokemon_sprite: Optional[str] = None
    pokemon_types: Optional[List[str]] = None
    base_stats: Dict[str, int]
    current_evs: Optional[Dict[str, int]] = None


class TrainingSessionUpdate(BaseModel):
    current_evs: Dict[str, int]
    is_completed: Optional[bool] = False


class TrainingSessionResponse(BaseModel):
    id: int
    user_id: int
    pokemon_id: int
    pokemon_name: str
    pokemon_sprite: Optional[str] = None
    pokemon_artwork: Optional[str] = None
    pokemon_types: Optional[List[str]] = None
    base_stats: Dict[str, int]
    current_evs: Dict[str, int]
    max_evs: Dict[str, int]
    total_ev_points: int
    max_ev_points: int
    remaining_points: int
    is_completed: bool
    created_at: datetime
    updated_at: Optional[datetime]

    # Estructura compatible con frontend
    sprites: Optional[Dict[str, str]] = None
    card_presentation: Optional[CardPresentation] = None

    class Config:
        from_attributes = True

    @model_validator(mode="after")
    def enrich_presentation(self):
        return _attach_presentation_fields(self)


# Modelos para Favorite Pokemon
class FavoritePokemonCreate(BaseModel):
    pokemon_id: int
    pokemon_name: str
    pokemon_sprite: Optional[str] = None
    pokemon_types: Optional[List[str]] = None


class FavoritePokemonResponse(BaseModel):
    id: int
    user_id: int
    pokemon_id: int
    pokemon_name: str
    pokemon_sprite: Optional[str]
    pokemon_types: Optional[List[str]]
    usage_count: int
    last_used: Optional[datetime]
    added_at: datetime

    class Config:
        from_attributes = True


# Modelos para Search History
class SearchHistoryCreate(BaseModel):
    pokemon_id: int
    pokemon_name: str
    pokemon_sprite: Optional[str] = None
    pokemon_types: Optional[List[str]] = None


class SearchHistoryResponse(BaseModel):
    id: int
    user_id: int
    pokemon_id: int
    pokemon_name: str
    pokemon_sprite: Optional[str]
    pokemon_types: Optional[List[str]]
    search_count: int
    last_searched: datetime
    created_at: datetime

    class Config:
        from_attributes = True


class SmartFavoriteResponse(BaseModel):
    pokemon_id: int
    pokemon_name: str
    pokemon_sprite: Optional[str]
    pokemon_types: Optional[List[str]]
    relevance_score: float
    source: str  # "search_history", "global_popular", "team_usage"

    class Config:
        from_attributes = True


class PokemonTeamMemberCreate(BaseModel):
    pokemon_id: int
    pokemon_name: str
    pokemon_sprite: Optional[str] = None
    pokemon_artwork: Optional[str] = None
    pokemon_types: Optional[List[str]] = None
    nickname: Optional[str] = None
    level: int = 50
    selected_ability: Optional[str] = None
    position: int
    move_1: Optional[str] = None
    move_2: Optional[str] = None
    move_3: Optional[str] = None
    move_4: Optional[str] = None
    held_item: Optional[str] = None
    nature: Optional[str] = None
    evs: Optional[Dict[str, int]] = None
    ivs: Optional[Dict[str, int]] = None


class PokemonTeamMemberResponse(BaseModel):
    id: int
    team_id: int
    pokemon_id: int
    pokemon_name: str
    pokemon_sprite: Optional[str]
    pokemon_artwork: Optional[str] = None
    pokemon_types: Optional[List[str]]
    nickname: Optional[str]
    level: int
    selected_ability: Optional[str]
    position: int
    move_1: Optional[str]
    move_2: Optional[str]
    move_3: Optional[str]
    move_4: Optional[str]
    held_item: Optional[str]
    nature: Optional[str]
    evs: Optional[Dict[str, int]]
    ivs: Optional[Dict[str, int]]
    added_at: datetime

    # Estructura compatible con frontend
    sprites: Optional[Dict[str, str]] = None
    card_presentation: Optional[CardPresentation] = None

    class Config:
        from_attributes = True

    @model_validator(mode="after")
    def enrich_presentation(self):
        return _attach_presentation_fields(self)


class PokemonTeamCreate(BaseModel):
    team_name: str
    description: Optional[str] = None
    is_favorite: bool = False
    team_members: List[PokemonTeamMemberCreate]


class PokemonTeamUpdate(BaseModel):
    team_name: Optional[str] = None
    description: Optional[str] = None
    is_favorite: Optional[bool] = None
    team_members: Optional[List[PokemonTeamMemberCreate]] = None


class PokemonTeamResponse(BaseModel):
    id: int
    user_id: int
    team_name: str
    description: Optional[str]
    is_favorite: bool
    team_members: List[PokemonTeamMemberResponse]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


# Modelos para actualización de miembros de equipo
class UpdateNicknameRequest(BaseModel):
    nickname: Optional[str] = Field(None, max_length=20, description="Nickname del Pokémon (máx 20 caracteres)")


class UpdateLevelRequest(BaseModel):
    level: int = Field(..., ge=1, le=100, description="Nivel del Pokémon (1-100)")

    @field_validator("level")
    def validate_level(cls, v):
        if v < 1 or v > 100:
            raise ValueError("El nivel debe estar entre 1 y 100")
        return v


class UpdateMovesRequest(BaseModel):
    move_1: Optional[str] = Field(None, max_length=30, description="Movimiento 1 (máx 30 caracteres)")
    move_2: Optional[str] = Field(None, max_length=30, description="Movimiento 2 (máx 30 caracteres)")
    move_3: Optional[str] = Field(None, max_length=30, description="Movimiento 3 (máx 30 caracteres)")
    move_4: Optional[str] = Field(None, max_length=30, description="Movimiento 4 (máx 30 caracteres)")

    @field_validator("move_1", "move_2", "move_3", "move_4")
    def validate_move_name(cls, v):
        if v is not None and len(v.strip()) > 0:
            # Validar longitud máxima
            if len(v) > 30:
                raise ValueError("El nombre del movimiento no puede exceder 30 caracteres")

            # Permitir letras, números, espacios y caracteres especiales básicos
            import re

            if not re.match(r"^[a-zA-Z0-9\sñÑáéíóúÁÉÍÓÚüÜ\-_'\.!?]+$", v):
                raise ValueError("El movimiento contiene caracteres no permitidos")

        # Convertir cadenas vacías a None
        return v.strip() if v and len(v.strip()) > 0 else None


# Actualización de EVs en equipos guardados (PATCH update-evs)
class UpdateTeamMemberEvs(BaseModel):
    pokemon_id: int = Field(..., gt=0)
    evs: Dict[str, int]

    @field_validator("evs")
    @classmethod
    def validar_evs(cls, evs: Dict[str, int]) -> Dict[str, int]:
        if not evs:
            raise ValueError("Los EVs no pueden estar vacíos")
        for stat, puntos in evs.items():
            if puntos < 0 or puntos > 252:
                raise ValueError(f"EV inválido para {stat}: debe estar entre 0 y 252")
        if sum(evs.values()) > 510:
            raise ValueError("La suma de EVs no puede superar 510")
        return evs


class UpdateTeamEvsRequest(BaseModel):
    updated_members: List[UpdateTeamMemberEvs] = Field(..., min_length=1)
