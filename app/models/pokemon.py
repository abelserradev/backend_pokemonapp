from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime

# Modelos para User Pokemon
class UserPokemonCreate(BaseModel):
    pokemon_id: int
    pokemon_name: str
    pokemon_sprite: Optional[str] = None
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
    selected_ability: Optional[str]
    nickname: Optional[str]
    level: int
    added_at: datetime

    class Config:
        from_attributes = True

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

    class Config:
        from_attributes = True

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

    class Config:
        from_attributes = True

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