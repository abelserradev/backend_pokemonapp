from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from typing import List
from app.models.pokemon import (
    UserPokemonCreate, UserPokemonResponse,
    TrainingSessionCreate, TrainingSessionUpdate, TrainingSessionResponse,
    FavoritePokemonCreate, FavoritePokemonResponse
)
from app.models.database import User
from app.service.pokemon import (
    add_pokemon_to_team, get_user_team, remove_pokemon_from_team,
    create_training_session, update_training_session, get_user_training_sessions, delete_training_session,
    add_favorite_pokemon, get_user_favorites, increment_pokemon_usage, remove_favorite_pokemon
)
from app.service.auth import get_current_user
from app.database import get_db

router = APIRouter()

# ===== EQUIPO POKÉMON =====
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

# ===== SESIONES DE ENTRENAMIENTO =====
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
