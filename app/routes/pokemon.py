from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from typing import List
from app.models.pokemon import (
    UserPokemonCreate, UserPokemonResponse,
    TrainingSessionCreate, TrainingSessionUpdate, TrainingSessionResponse,
    FavoritePokemonCreate, FavoritePokemonResponse,
    SearchHistoryCreate, SearchHistoryResponse, SmartFavoriteResponse,
    PokemonTeamCreate, PokemonTeamUpdate, PokemonTeamResponse
)
from app.models.database import User
from app.service.pokemon import (
    add_pokemon_to_team, get_user_team, remove_pokemon_from_team,
    create_training_session, update_training_session, get_user_training_sessions, delete_training_session,
    add_favorite_pokemon, get_user_favorites, increment_pokemon_usage, remove_favorite_pokemon,
    track_pokemon_search, get_user_search_history, get_smart_favorites,
    create_pokemon_team, get_user_teams, get_team_by_id, 
    update_pokemon_team, delete_pokemon_team, toggle_favorite_team
)
from app.service.auth import get_current_user
from app.database import get_db

router = APIRouter()


@router.post("/team", response_model=UserPokemonResponse)
async def add_to_team(
    pokemon_data: UserPokemonCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    try:
        return add_pokemon_to_team(current_user.id, pokemon_data, db)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/team", response_model=List[UserPokemonResponse])
async def get_team(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return get_user_team(current_user.id, db)

@router.delete("/team/{team_pokemon_id}")
async def remove_from_team(
    team_pokemon_id: int,  # Este es el ID de la base de datos
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        return remove_pokemon_from_team(current_user.id, team_pokemon_id, db)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/training", response_model=TrainingSessionResponse)
async def create_session(
    session_data: TrainingSessionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return create_training_session(current_user.id, session_data, db)

@router.get("/training", response_model=List[TrainingSessionResponse])
async def get_sessions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return get_user_training_sessions(current_user.id, db)

@router.put("/training/{session_id}", response_model=TrainingSessionResponse)
async def update_session(
    session_id: int,
    update_data: TrainingSessionUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        return update_training_session(current_user.id, session_id, update_data, db)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/training/{session_id}")
async def delete_session(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        return delete_training_session(current_user.id, session_id, db)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

# ===== POKÉMON FAVORITOS =====
@router.post("/favorites", response_model=FavoritePokemonResponse)
async def add_to_favorites(
    pokemon_data: FavoritePokemonCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        return add_favorite_pokemon(current_user.id, pokemon_data, db)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/favorites", response_model=List[FavoritePokemonResponse])
async def get_favorites(
    limit: int = 5,  # AGREGAR PARÁMETRO LIMIT
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return get_user_favorites(current_user.id, limit, db)  # PASAR LIMIT

@router.post("/favorites/{pokemon_id}/use")
async def use_pokemon(
    pokemon_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    result = increment_pokemon_usage(current_user.id, pokemon_id, db)
    if not result:
        raise HTTPException(status_code=404, detail="Pokémon favorito no encontrado")
    return result

@router.delete("/favorites/{pokemon_id}")
async def remove_from_favorites(
    pokemon_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        return remove_favorite_pokemon(current_user.id, pokemon_id, db)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/favorites/smart", response_model=List[SmartFavoriteResponse])
async def get_smart_favorites_endpoint(
    limit: int = 5,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        return get_smart_favorites(current_user.id, limit, db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener favoritos inteligentes: {str(e)}")

@router.post("/search/track", response_model=SearchHistoryResponse)
async def track_pokemon_search_endpoint(
    search_data: SearchHistoryCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    try:
        return track_pokemon_search(current_user.id, search_data, db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al registrar búsqueda: {str(e)}")

@router.get("/search/history", response_model=List[SearchHistoryResponse])
async def get_user_search_history_endpoint(
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    try:
        return get_user_search_history(current_user.id, limit, db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener historial: {str(e)}")



@router.get("/favorites/legacy", response_model=List[FavoritePokemonResponse])
async def get_favorites_legacy(
    limit: int = 5,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    return get_user_favorites(current_user.id, limit, db)

@router.post("/teams", response_model=PokemonTeamResponse, status_code=status.HTTP_201_CREATED)
async def create_team(
    team_data: PokemonTeamCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Crear un nuevo equipo de Pokémon (1-6 miembros).
    """
    try:
        return create_pokemon_team(current_user.id, team_data, db)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al crear equipo: {str(e)}")


@router.get("/teams", response_model=List[PokemonTeamResponse])
async def get_all_teams(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    try:
        return get_user_teams(current_user.id, db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener equipos: {str(e)}")


@router.get("/teams/{team_id}", response_model=PokemonTeamResponse)
async def get_team(
    team_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    try:
        return get_team_by_id(current_user.id, team_id, db)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener equipo: {str(e)}")


@router.put("/teams/{team_id}", response_model=PokemonTeamResponse)
async def update_team(
    team_id: int,
    update_data: PokemonTeamUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    try:
        return update_pokemon_team(current_user.id, team_id, update_data, db)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al actualizar equipo: {str(e)}")


@router.delete("/teams/{team_id}")
async def delete_team(
    team_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    try:
        return delete_pokemon_team(current_user.id, team_id, db)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al eliminar equipo: {str(e)}")


@router.patch("/teams/{team_id}/favorite", response_model=PokemonTeamResponse)
async def toggle_team_favorite(
    team_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    try:
        return toggle_favorite_team(current_user.id, team_id, db)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al actualizar favorito: {str(e)}")
