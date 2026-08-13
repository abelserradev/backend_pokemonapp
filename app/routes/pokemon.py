import logging

from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from typing import List
from app.models.pokemon import (
    UserPokemonCreate, UserPokemonResponse,
    TrainingSessionCreate, TrainingSessionUpdate, TrainingSessionResponse,
    FavoritePokemonCreate, FavoritePokemonResponse,
    SearchHistoryCreate, SearchHistoryResponse, SmartFavoriteResponse,
    PokemonTeamCreate, PokemonTeamUpdate, PokemonTeamResponse,
    PokemonTeamMemberResponse, UpdateNicknameRequest, UpdateLevelRequest,
    UpdateMovesRequest, UpdateTeamEvsRequest
)
from app.utils.validators import validate_nickname
from app.models.database import User, UserPokemon, TrainingSession, PokemonTeam, PokemonTeamMember
from app.service.pokemon import (
    add_pokemon_to_team, get_user_team, remove_pokemon_from_team,
    create_training_session, update_training_session, get_user_training_sessions, delete_training_session,
    add_favorite_pokemon, get_user_favorites, increment_pokemon_usage, remove_favorite_pokemon,
    track_pokemon_search, get_user_search_history, get_smart_favorites,
    create_pokemon_team, get_user_teams, get_team_by_id, 
    update_pokemon_team, delete_pokemon_team, toggle_favorite_team,
    load_team_for_training, update_team_evs
)
from app.service.auth import get_current_user
from app.database import get_db
from app.utils.dates import utc_now

logger = logging.getLogger("pokemon-api.pokemon")

MSG_ERROR_INTERNO = "Error interno del servidor"

router = APIRouter()

# ===== UTILIDADES DE LIMPIEZA =====

@router.delete("/team/clear-all")
async def clear_team(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Eliminar todos los Pokémon del equipo actual del usuario.
    
    Útil para limpiar manualmente el equipo y empezar desde cero.
    """
    try:
        deleted_count = db.query(UserPokemon).filter(
            UserPokemon.user_id == current_user.id
        ).delete()
        
        db.commit()
        
        return {
            "message": f"Equipo actual limpiado exitosamente",
            "deleted_count": deleted_count
        }
        
    except Exception:
        db.rollback()
        logger.exception("Error al limpiar el equipo actual")
        raise HTTPException(status_code=500, detail=MSG_ERROR_INTERNO) from None


@router.delete("/training/clear-all")
async def clear_all_training_sessions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Eliminar todas las sesiones de training del usuario.
    
    Útil para limpiar manualmente las sesiones y empezar desde cero.
    """
    try:
        deleted_count = db.query(TrainingSession).filter(
            TrainingSession.user_id == current_user.id
        ).delete()
        
        db.commit()
        
        return {
            "message": f"Sesiones de training limpiadas exitosamente",
            "deleted_count": deleted_count
        }
        
    except Exception:
        db.rollback()
        logger.exception("Error al limpiar sesiones de training")
        raise HTTPException(status_code=500, detail=MSG_ERROR_INTERNO) from None

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
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception:
        logger.exception("Error al agregar pokémon al equipo")
        raise HTTPException(status_code=500, detail=MSG_ERROR_INTERNO) from None

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
    except Exception:
        logger.exception("Error al obtener favoritos inteligentes")
        raise HTTPException(status_code=500, detail=MSG_ERROR_INTERNO) from None

@router.post("/search/track", response_model=SearchHistoryResponse)
async def track_pokemon_search_endpoint(
    search_data: SearchHistoryCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    
    try:
        return track_pokemon_search(current_user.id, search_data, db)
    except Exception:
        logger.exception("Error al registrar búsqueda de pokémon")
        raise HTTPException(status_code=500, detail=MSG_ERROR_INTERNO) from None

@router.get("/search/history", response_model=List[SearchHistoryResponse])
async def get_user_search_history_endpoint(
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    
    try:
        return get_user_search_history(current_user.id, limit, db)
    except Exception:
        logger.exception("Error al obtener historial de búsqueda")
        raise HTTPException(status_code=500, detail=MSG_ERROR_INTERNO) from None



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
    Después de guardar, limpia el equipo actual para permitir crear uno nuevo.
    """
    try:
        # Crear el equipo guardado
        result = create_pokemon_team(current_user.id, team_data, db)
        
        # Limpiar el equipo actual para permitir crear un nuevo equipo
        db.query(UserPokemon).filter(UserPokemon.user_id == current_user.id).delete()
        db.commit()
        
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception:
        db.rollback()
        logger.exception("Error al crear equipo guardado")
        raise HTTPException(status_code=500, detail=MSG_ERROR_INTERNO) from None


@router.get("/teams", response_model=List[PokemonTeamResponse])
async def get_all_teams(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    try:
        return get_user_teams(current_user.id, db)
    except Exception:
        logger.exception("Error al listar equipos guardados")
        raise HTTPException(status_code=500, detail=MSG_ERROR_INTERNO) from None


@router.get("/teams/{team_id}", response_model=PokemonTeamResponse)
async def get_team(
    team_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    try:
        return get_team_by_id(current_user.id, team_id, db)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    except Exception:
        logger.exception("Error al obtener equipo guardado (team_id=%s)", team_id)
        raise HTTPException(status_code=500, detail=MSG_ERROR_INTERNO) from None


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
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception:
        logger.exception("Error al actualizar equipo guardado (team_id=%s)", team_id)
        raise HTTPException(status_code=500, detail=MSG_ERROR_INTERNO) from None


@router.delete("/teams/{team_id}")
async def delete_team(
    team_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    try:
        return delete_pokemon_team(current_user.id, team_id, db)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    except Exception:
        logger.exception("Error al eliminar equipo guardado (team_id=%s)", team_id)
        raise HTTPException(status_code=500, detail=MSG_ERROR_INTERNO) from None


@router.patch("/teams/{team_id}/favorite", response_model=PokemonTeamResponse)
async def toggle_team_favorite(
    team_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    try:
        return toggle_favorite_team(current_user.id, team_id, db)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    except Exception:
        logger.exception("Error al alternar favorito de equipo (team_id=%s)", team_id)
        raise HTTPException(status_code=500, detail=MSG_ERROR_INTERNO) from None


@router.post("/teams/{team_id}/load-for-training")
async def load_team_for_training_endpoint(
    team_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Cargar un equipo guardado para entrenamiento.
    """
    try:
        return load_team_for_training(current_user.id, team_id, db)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    except HTTPException:
        raise
    except Exception:
        db.rollback()
        logger.exception("Error al cargar equipo para entrenamiento (team_id=%s)", team_id)
        raise HTTPException(status_code=500, detail=MSG_ERROR_INTERNO) from None


@router.patch("/teams/{team_id}/update-evs")
async def update_team_evs_endpoint(
    team_id: int,
    request: UpdateTeamEvsRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Actualizar los EVs de un equipo guardado tras una sesión de training.
    """
    try:
        return update_team_evs(current_user.id, team_id, request, db)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    except HTTPException:
        raise
    except Exception:
        db.rollback()
        logger.exception("Error al actualizar EVs del equipo (team_id=%s)", team_id)
        raise HTTPException(status_code=500, detail=MSG_ERROR_INTERNO) from None


@router.patch("/teams/{team_id}/members/{member_id}/nickname", response_model=PokemonTeamMemberResponse)
async def update_team_member_nickname(
    team_id: int,
    member_id: int,
    request: UpdateNicknameRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Actualizar el nickname (mote) de un Pokémon específico en un equipo guardado.
    
    Validaciones:
    - Longitud máxima: 20 caracteres
    - Sin HTML tags (prevención XSS)
    - Sin event handlers (onclick, onerror, etc.)
    - Sin javascript: protocol
    - Solo caracteres alfanuméricos, espacios y símbolos seguros: - _ ' . ! ?
    """
    try:
        # Verificar que el equipo pertenece al usuario
        team = db.query(PokemonTeam).filter(
            PokemonTeam.id == team_id,
            PokemonTeam.user_id == current_user.id
        ).first()
        
        if not team:
            raise HTTPException(
                status_code=404, 
                detail="Equipo no encontrado"
            )
        
        # Buscar el miembro del equipo
        member = db.query(PokemonTeamMember).filter(
            PokemonTeamMember.id == member_id,
            PokemonTeamMember.team_id == team_id
        ).first()
        
        if not member:
            raise HTTPException(
                status_code=404, 
                detail="Miembro del equipo no encontrado"
            )
        
        # Validar y actualizar nickname
        validated_nickname = validate_nickname(request.nickname)
        member.nickname = validated_nickname
        
        # Actualizar timestamp del equipo
        team.updated_at = utc_now()

        db.commit()
        db.refresh(member)

        return member
        
    except HTTPException:
        raise
    except Exception:
        db.rollback()
        logger.exception(
            "Error al actualizar nickname (team_id=%s, member_id=%s)",
            team_id,
            member_id,
        )
        raise HTTPException(status_code=500, detail=MSG_ERROR_INTERNO) from None


@router.patch("/teams/{team_id}/members/{member_id}/level", response_model=PokemonTeamMemberResponse)
async def update_team_member_level(
    team_id: int,
    member_id: int,
    request: UpdateLevelRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Actualizar el nivel de un Pokémon específico en un equipo guardado.
    
    Validaciones:
    - El nivel debe estar entre 1 y 100 (inclusive)
    - Debe ser un número entero
    """
    try:
        # Verificar que el equipo pertenece al usuario
        team = db.query(PokemonTeam).filter(
            PokemonTeam.id == team_id,
            PokemonTeam.user_id == current_user.id
        ).first()
        
        if not team:
            raise HTTPException(
                status_code=404, 
                detail="Equipo no encontrado"
            )
        
        # Buscar el miembro del equipo
        member = db.query(PokemonTeamMember).filter(
            PokemonTeamMember.id == member_id,
            PokemonTeamMember.team_id == team_id
        ).first()
        
        if not member:
            raise HTTPException(
                status_code=404, 
                detail="Miembro del equipo no encontrado"
            )
        
        # Actualizar nivel
        member.level = request.level
        
        # Actualizar timestamp del equipo
        team.updated_at = utc_now()

        db.commit()
        db.refresh(member)

        return member
        
    except HTTPException:
        raise
    except Exception:
        db.rollback()
        logger.exception(
            "Error al actualizar nivel (team_id=%s, member_id=%s)",
            team_id,
            member_id,
        )
        raise HTTPException(status_code=500, detail=MSG_ERROR_INTERNO) from None

@router.patch("/teams/{team_id}/members/{member_id}/moves", response_model=PokemonTeamMemberResponse)
async def update_team_member_moves(
    team_id: int,
    member_id: int,
    request: UpdateMovesRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        # Verificar que el equipo pertenece al usuario
        team = db.query(PokemonTeam).filter(
            PokemonTeam.id == team_id,
            PokemonTeam.user_id == current_user.id
        ).first()
        
        if not team:
            raise HTTPException(
                status_code=404, 
                detail="Equipo no encontrado"
            )
        
        # Buscar el miembro del equipo
        member = db.query(PokemonTeamMember).filter(
            PokemonTeamMember.id == member_id,
            PokemonTeamMember.team_id == team_id
        ).first()
        
        if not member:
            raise HTTPException(
                status_code=404, 
                detail="Miembro del equipo no encontrado"
            )
        
        # Actualizar solo los movimientos que se enviaron en el request
        # Si el campo no se envió (None), no se modifica
        if request.move_1 is not None:
            member.move_1 = request.move_1
        if request.move_2 is not None:
            member.move_2 = request.move_2
        if request.move_3 is not None:
            member.move_3 = request.move_3
        if request.move_4 is not None:
            member.move_4 = request.move_4
        
        # Actualizar timestamp del equipo
        team.updated_at = utc_now()

        db.commit()
        db.refresh(member)

        return member
        
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e
    except Exception:
        db.rollback()
        logger.exception(
            "Error al actualizar movimientos (team_id=%s, member_id=%s)",
            team_id,
            member_id,
        )
        raise HTTPException(status_code=500, detail=MSG_ERROR_INTERNO) from None