from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from typing import List
from app.models.pokemon import (
    UserPokemonCreate, UserPokemonResponse,
    TrainingSessionCreate, TrainingSessionUpdate, TrainingSessionResponse,
    FavoritePokemonCreate, FavoritePokemonResponse,
    SearchHistoryCreate, SearchHistoryResponse, SmartFavoriteResponse,
    PokemonTeamCreate, PokemonTeamUpdate, PokemonTeamResponse,
    PokemonTeamMemberResponse, UpdateNicknameRequest, UpdateLevelRequest
)
from app.utils.validators import validate_nickname
from app.models.database import User, UserPokemon, TrainingSession, PokemonTeam, PokemonTeamMember
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
from app.utils.validators import validate_nickname

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
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error al limpiar el equipo: {str(e)}"
        )


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
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error al limpiar sesiones de training: {str(e)}"
        )

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
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        db.rollback()
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


@router.post("/teams/{team_id}/load-for-training")
async def load_team_for_training(
    team_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Cargar un equipo guardado para entrenamiento.
    
    Proceso:
    1. Obtener el equipo guardado y validar que pertenece al usuario
    2. Limpiar equipo actual (user_pokemon) y sesiones de training existentes
    3. Copiar Pokémon del equipo guardado al equipo actual (user_pokemon)
    4. Crear sesiones de training con los EVs existentes (obtiene base_stats de PokeAPI)
    5. Hacer commit y verificar que todo se cargó correctamente
    
    IMPORTANTE: Los Pokémon se agregan a user_pokemon para que el componente
    training pueda consultarlos y mostrarlos correctamente.
    """
    import requests
    
    try:
        # 1. Obtener el equipo guardado
        team = db.query(PokemonTeam).filter(
            PokemonTeam.id == team_id,
            PokemonTeam.user_id == current_user.id
        ).first()
        
        if not team:
            raise HTTPException(status_code=404, detail="Equipo no encontrado")
        
        # 2. Limpiar equipo actual y sesiones de training existentes
        db.query(UserPokemon).filter(UserPokemon.user_id == current_user.id).delete()
        db.query(TrainingSession).filter(TrainingSession.user_id == current_user.id).delete()
        db.commit()
        
        # 3. Cargar Pokémon del equipo guardado al equipo actual (user_pokemon)
        team_loaded = []
        for member in team.team_members:
            team_pokemon = UserPokemon(
                user_id=current_user.id,
                pokemon_id=member.pokemon_id,
                pokemon_name=member.pokemon_name,
                pokemon_sprite=member.pokemon_sprite,
                selected_ability=member.selected_ability or '',
                level=member.level
            )
            db.add(team_pokemon)
            db.flush()
            team_loaded.append(team_pokemon)
        
        db.commit()
        
        # 4. Crear sesiones de training para cada Pokémon
        sessions_created = []
        
        for member in team.team_members:
            # Obtener estadísticas base de PokeAPI
            try:
                response = requests.get(
                    f"https://pokeapi.co/api/v2/pokemon/{member.pokemon_id}", 
                    timeout=5
                )
                pokemon_data = response.json()
                base_stats = {
                    'hp': pokemon_data['stats'][0]['base_stat'],
                    'attack': pokemon_data['stats'][1]['base_stat'],
                    'defense': pokemon_data['stats'][2]['base_stat'],
                    'special-attack': pokemon_data['stats'][3]['base_stat'],
                    'special-defense': pokemon_data['stats'][4]['base_stat'],
                    'speed': pokemon_data['stats'][5]['base_stat']
                }
            except Exception:
                # Valores por defecto si falla la API
                base_stats = {
                    'hp': 50,
                    'attack': 50,
                    'defense': 50,
                    'special-attack': 50,
                    'special-defense': 50,
                    'speed': 50
                }
            
            # EVs actuales del equipo guardado
            current_evs = member.evs or {
                'hp': 0,
                'attack': 0,
                'defense': 0,
                'special-attack': 0,
                'special-defense': 0,
                'speed': 0
            }
            
            total_evs = sum(current_evs.values())
            remaining_points = 510 - total_evs
            
            # Calcular max_evs (estadísticas con EVs aplicados)
            max_evs = {
                'hp': base_stats['hp'] + int(current_evs.get('hp', 0) / 4),
                'attack': base_stats['attack'] + int(current_evs.get('attack', 0) / 4),
                'defense': base_stats['defense'] + int(current_evs.get('defense', 0) / 4),
                'special-attack': base_stats['special-attack'] + int(current_evs.get('special-attack', 0) / 4),
                'special-defense': base_stats['special-defense'] + int(current_evs.get('special-defense', 0) / 4),
                'speed': base_stats['speed'] + int(current_evs.get('speed', 0) / 4)
            }
            
            training_session = TrainingSession(
                user_id=current_user.id,
                pokemon_id=member.pokemon_id,
                pokemon_name=member.pokemon_name,
                pokemon_sprite=member.pokemon_sprite,
                pokemon_types=member.pokemon_types,
                base_stats=base_stats,
                current_evs=current_evs,
                max_evs=max_evs,
                total_ev_points=total_evs,
                max_ev_points=510,
                remaining_points=remaining_points,
                is_completed=remaining_points <= 0
            )
            db.add(training_session)
            db.flush()
            sessions_created.append(training_session)
        
        db.commit()
        
        # Verificación final
        loaded_team = db.query(UserPokemon).filter(UserPokemon.user_id == current_user.id).all()
        
        return {
            "message": f"Equipo '{team.team_name}' cargado exitosamente para entrenamiento",
            "team_loaded": {
                "id": team.id,
                "name": team.team_name,
                "pokemon_count": len(loaded_team)
            },
            "sessions_created": [
                {
                    "id": session.id,
                    "pokemon_name": session.pokemon_name,
                    "current_evs": session.current_evs,
                    "training_points": session.remaining_points
                }
                for session in sessions_created
            ]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500, 
            detail=f"Error al cargar equipo para entrenamiento: {str(e)}"
        )


@router.patch("/teams/{team_id}/update-evs")
async def update_team_evs(
    team_id: int,
    request: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Actualizar los EVs de un equipo guardado.
    
    Se llama automáticamente desde el frontend después de aplicar training
    para guardar los nuevos EVs en el equipo guardado.
    
    Request body:
    {
        "updated_members": [
            {
                "pokemon_id": 6,
                "evs": {"hp": 252, "attack": 252, ...}
            }
        ]
    }
    """
    from datetime import datetime
    
    try:
        # 1. Obtener el equipo guardado
        team = db.query(PokemonTeam).filter(
            PokemonTeam.id == team_id,
            PokemonTeam.user_id == current_user.id
        ).first()
        
        if not team:
            raise HTTPException(status_code=404, detail="Equipo no encontrado")
        
        # 2. Obtener datos actualizados del request
        updated_members = request.get('updated_members', [])
        
        if not updated_members:
            raise HTTPException(
                status_code=400, 
                detail="No se proporcionaron datos para actualizar"
            )
        
        # 3. Actualizar EVs de cada Pokémon
        updated_count = 0
        for update_data in updated_members:
            pokemon_id = update_data.get('pokemon_id')
            new_evs = update_data.get('evs')
            
            if not pokemon_id or not new_evs:
                continue
            
            # Buscar el miembro del equipo
            member = db.query(PokemonTeamMember).filter(
                PokemonTeamMember.team_id == team_id,
                PokemonTeamMember.pokemon_id == pokemon_id
            ).first()
            
            if member:
                member.evs = new_evs
                updated_count += 1
        
        # 4. Actualizar timestamp del equipo
        team.updated_at = datetime.utcnow()
        
        db.commit()
        
        return {
            "message": f"EVs actualizados en {updated_count} Pokémon",
            "team_id": team_id,
            "team_name": team.team_name,
            "updated_count": updated_count
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500, 
            detail=f"Error al actualizar EVs: {str(e)}"
        )


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
        from datetime import datetime
        team.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(member)
        
        return member
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error al actualizar nickname: {str(e)}"
        )


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
        from datetime import datetime
        team.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(member)
        
        return member
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error al actualizar nivel: {str(e)}"
        )

