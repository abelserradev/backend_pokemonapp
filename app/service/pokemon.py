from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from app.models.database import UserPokemon, TrainingSession, FavoritePokemon, SearchHistory
from app.models.pokemon import (
    UserPokemonCreate, TrainingSessionCreate, TrainingSessionUpdate, 
    FavoritePokemonCreate, SearchHistoryCreate, SmartFavoriteResponse
)
from datetime import datetime, timedelta
from fastapi import HTTPException
from typing import List, Dict, Any

# ===== USER POKEMON =====
def add_pokemon_to_team(user_id: int, pokemon_data: UserPokemonCreate, db: Session):
    # Verificar si el equipo ya tiene 6 pokémon
    team_count = db.query(UserPokemon).filter(UserPokemon.user_id == user_id).count()
    if team_count >= 6:
        raise ValueError("El equipo ya tiene 6 pokémon")
    
    # NUEVO: Verificar si ya existe el mismo pokémon en el equipo
    existing_pokemon = db.query(UserPokemon).filter(
        UserPokemon.user_id == user_id,
        UserPokemon.pokemon_id == pokemon_data.pokemon_id
    ).first()
    
    if existing_pokemon:
        raise ValueError(f"{pokemon_data.pokemon_name} ya está en tu equipo")
    
    db_pokemon = UserPokemon(
        user_id=user_id,
        pokemon_id=pokemon_data.pokemon_id,
        pokemon_name=pokemon_data.pokemon_name,
        pokemon_sprite=pokemon_data.pokemon_sprite,
        selected_ability=pokemon_data.selected_ability,
        nickname=pokemon_data.nickname,
        level=pokemon_data.level
    )
    db.add(db_pokemon)
    db.commit()
    db.refresh(db_pokemon)
    
    # IMPORTANTE: Crear sesión CON todos los datos
    if pokemon_data.base_stats:
        print(f"DEBUG - Creando sesión con sprite: {pokemon_data.pokemon_sprite}")
        create_training_session_for_pokemon_with_details(
            user_id=user_id,
            pokemon_id=pokemon_data.pokemon_id,
            pokemon_name=pokemon_data.pokemon_name,
            pokemon_sprite=pokemon_data.pokemon_sprite,  # PASAR EL SPRITE
            pokemon_types=getattr(pokemon_data, 'pokemon_types', None),  # PASAR LOS TYPES
            base_stats=pokemon_data.base_stats,
            db=db
        )
    
    # DESPUÉS de agregar al equipo, registrar como búsqueda para favoritos inteligentes
    try:
        # Registrar la interacción con el Pokémon como búsqueda
        search_data = SearchHistoryCreate(
            pokemon_id=pokemon_data.pokemon_id,
            pokemon_name=pokemon_data.pokemon_name,
            pokemon_sprite=pokemon_data.pokemon_sprite,
            pokemon_types=pokemon_data.pokemon_types
        )
        track_pokemon_search(user_id, search_data, db)
    except Exception as e:
        print(f"DEBUG - Error al registrar búsqueda: {e}")
    
    return db_pokemon

def get_user_team(user_id: int, db: Session):
    return db.query(UserPokemon).filter(UserPokemon.user_id == user_id).all()

def remove_pokemon_from_team(user_id: int, pokemon_id: int, db: Session):
    print(f"DEBUG - Intentando eliminar: user_id={user_id}, pokemon_id={pokemon_id}")
    
    pokemon = db.query(UserPokemon).filter(
        UserPokemon.id == pokemon_id,
        UserPokemon.user_id == user_id
    ).first()
    
    print(f"DEBUG - Pokémon encontrado: {pokemon}")
    
    if not pokemon:
        # Ver qué pokémon tiene el usuario
        all_pokemon = db.query(UserPokemon).filter(UserPokemon.user_id == user_id).all()
        print(f"DEBUG - Pokémon del usuario: {[(p.id, p.pokemon_name) for p in all_pokemon]}")
        raise ValueError("Pokémon no encontrado")
    
    db.delete(pokemon)
    db.commit()
    return {"message": "Pokémon eliminado del equipo"}

# ===== TRAINING SESSIONS =====
def create_training_session(user_id: int, session_data: TrainingSessionCreate, db: Session):
    # Inicializar EVs en 0 si no se proporcionan
    current_evs = session_data.current_evs or {
        "hp": 0, "attack": 0, "defense": 0,
        "special-attack": 0, "special-defense": 0, "speed": 0
    }
    
    max_evs = {"hp": 252, "attack": 252, "defense": 252,
               "special-attack": 252, "special-defense": 252, "speed": 252}
    
    db_session = TrainingSession(
        user_id=user_id,
        pokemon_id=session_data.pokemon_id,
        pokemon_name=session_data.pokemon_name,
        base_stats=session_data.base_stats,
        current_evs=current_evs,
        max_evs=max_evs,
        total_ev_points=0,
        max_ev_points=510,
        remaining_points=510
    )
    
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return db_session

def update_training_session(user_id: int, session_id: int, update_data: TrainingSessionUpdate, db: Session):
    session = db.query(TrainingSession).filter(
        TrainingSession.id == session_id,
        TrainingSession.user_id == user_id
    ).first()
    
    if not session:
        raise ValueError("Sesión de entrenamiento no encontrada")
    
    # Calcular total de EVs
    total_evs = sum(update_data.current_evs.values())
    
    if total_evs > 510:
        raise ValueError("El total de EVs no puede exceder 510")
    
    session.current_evs = update_data.current_evs
    session.total_ev_points = total_evs
    session.remaining_points = 510 - total_evs
    session.is_completed = update_data.is_completed
    
    if update_data.is_completed:
        session.completed_at = datetime.utcnow()
    
    db.commit()
    db.refresh(session)
    return session

def get_user_training_sessions(user_id: int, db: Session):
    return db.query(TrainingSession).filter(TrainingSession.user_id == user_id).all()

def delete_training_session(user_id: int, session_id: int, db: Session):
    session = db.query(TrainingSession).filter(
        TrainingSession.id == session_id,
        TrainingSession.user_id == user_id
    ).first()
    
    if not session:
        raise ValueError("Sesión de entrenamiento no encontrada")
    
    db.delete(session)
    db.commit()
    return {"message": "Sesión de entrenamiento eliminada"}

# ===== FAVORITE POKEMON =====
def add_favorite_pokemon(user_id: int, pokemon_data: FavoritePokemonCreate, db: Session):
    # Verificar si ya existe
    existing = db.query(FavoritePokemon).filter(
        FavoritePokemon.user_id == user_id,
        FavoritePokemon.pokemon_id == pokemon_data.pokemon_id
    ).first()
    
    if existing:
        raise ValueError("Este pokémon ya está en favoritos")
    
    db_favorite = FavoritePokemon(
        user_id=user_id,
        pokemon_id=pokemon_data.pokemon_id,
        pokemon_name=pokemon_data.pokemon_name,
        pokemon_sprite=pokemon_data.pokemon_sprite,
        pokemon_types=pokemon_data.pokemon_types,
        usage_count=0
    )
    
    db.add(db_favorite)
    db.commit()
    db.refresh(db_favorite)
    return db_favorite

def get_user_favorites(user_id: int, limit: int = 5, db: Session = None):
    if db is None:
        from app.database import get_db
        db = next(get_db())
    
    favorites = db.query(FavoritePokemon).filter(
        FavoritePokemon.user_id == user_id
    ).order_by(
        FavoritePokemon.usage_count.desc(),  # Ordenar por más usados
        FavoritePokemon.last_used.desc()     # Luego por más recientes
    ).limit(limit).all()
    
    print(f"DEBUG - Favoritos encontrados para user {user_id}: {len(favorites)}")
    return favorites

def increment_pokemon_usage(user_id: int, pokemon_id: int, db: Session):
    favorite = db.query(FavoritePokemon).filter(
        FavoritePokemon.user_id == user_id,
        FavoritePokemon.pokemon_id == pokemon_id
    ).first()
    
    if favorite:
        favorite.usage_count += 1
        favorite.last_used = datetime.utcnow()
        db.commit()
        db.refresh(favorite)
        return favorite
    return None

def remove_favorite_pokemon(user_id: int, pokemon_id: int, db: Session):
    favorite = db.query(FavoritePokemon).filter(
        FavoritePokemon.user_id == user_id,
        FavoritePokemon.pokemon_id == pokemon_id
    ).first()
    
    if not favorite:
        raise ValueError("Pokémon favorito no encontrado")
    
    db.delete(favorite)
    db.commit()
    return {"message": "Pokémon eliminado de favoritos"}

# NUEVA FUNCIÓN: Crear sesión de entrenamiento para un pokémon
def create_training_session_for_pokemon_with_details(
    user_id: int, 
    pokemon_id: int, 
    pokemon_name: str,
    pokemon_sprite: str = None,
    pokemon_types: list = None,
    base_stats: dict = None,
    db: Session = None
):
    print(f"DEBUG - Creando sesión de entrenamiento:")
    print(f"  - pokemon_sprite: {pokemon_sprite}")
    print(f"  - pokemon_types: {pokemon_types}")
    print(f"  - base_stats: {base_stats}")
    
    # Verificar si ya existe
    existing = db.query(TrainingSession).filter(
        TrainingSession.user_id == user_id,
        TrainingSession.pokemon_id == pokemon_id
    ).first()
    
    if existing:
        print(f"DEBUG - Ya existe sesión para pokemon_id={pokemon_id}")
        return existing
    
    # VALIDAR que base_stats no esté vacío
    if not base_stats or len(base_stats) == 0:
        print("WARNING - base_stats está vacío, usando valores por defecto")
        base_stats = {
            "hp": 45,
            "attack": 49,
            "defense": 49,
            "special-attack": 65,
            "special-defense": 65,
            "speed": 45
        }
    
    current_evs = {
        "hp": 0,
        "attack": 0,
        "defense": 0,
        "special-attack": 0,
        "special-defense": 0,
        "speed": 0
    }
    
    max_evs = {
        "hp": 252,
        "attack": 252,
        "defense": 252,
        "special-attack": 252,
        "special-defense": 252,
        "speed": 252
    }
    
    db_session = TrainingSession(
        user_id=user_id,
        pokemon_id=pokemon_id,
        pokemon_name=pokemon_name,
        pokemon_sprite=pokemon_sprite,  # DEBE TENER VALOR
        pokemon_types=pokemon_types,    # DEBE TENER VALOR
        base_stats=base_stats,           # DEBE TENER VALOR
        current_evs=current_evs,
        max_evs=max_evs,
        total_ev_points=0,
        max_ev_points=510,
        remaining_points=510
    )
    
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    
    print(f"DEBUG - Sesión creada exitosamente con ID: {db_session.id}")
    return db_session

# ===== SEARCH HISTORY & SMART FAVORITES =====

def track_pokemon_search(user_id: int, search_data: SearchHistoryCreate, db: Session) -> SearchHistory:
    """
    Registra o actualiza una búsqueda de Pokémon por un usuario.
    
    Args:
        user_id: ID del usuario
        search_data: Datos del Pokémon buscado
        db: Sesión de base de datos
        
    Returns:
        SearchHistory: Registro de búsqueda actualizado
    """
    # Buscar si ya existe una búsqueda previa de este Pokémon por este usuario
    existing_search = db.query(SearchHistory).filter(
        SearchHistory.user_id == user_id,
        SearchHistory.pokemon_id == search_data.pokemon_id
    ).first()
    
    if existing_search:
        # Actualizar contador y timestamp
        existing_search.search_count += 1
        existing_search.last_searched = datetime.utcnow()
        # Actualizar datos del Pokémon por si han cambiado
        existing_search.pokemon_sprite = search_data.pokemon_sprite
        existing_search.pokemon_types = search_data.pokemon_types
        db.commit()
        db.refresh(existing_search)
        return existing_search
    else:
        # Crear nuevo registro de búsqueda
        new_search = SearchHistory(
            user_id=user_id,
            pokemon_id=search_data.pokemon_id,
            pokemon_name=search_data.pokemon_name,
            pokemon_sprite=search_data.pokemon_sprite,
            pokemon_types=search_data.pokemon_types,
            search_count=1,
            last_searched=datetime.utcnow()
        )
        db.add(new_search)
        db.commit()
        db.refresh(new_search)
        return new_search

def get_user_search_history(user_id: int, limit: int = 10, db: Session = None) -> List[SearchHistory]:
    """
    Obtiene el historial de búsquedas de un usuario.
    
    Args:
        user_id: ID del usuario
        limit: Número máximo de resultados
        db: Sesión de base de datos
        
    Returns:
        List[SearchHistory]: Lista de búsquedas ordenadas por relevancia
    """
    if db is None:
        from app.database import get_db
        db = next(get_db())
    
    return db.query(SearchHistory).filter(
        SearchHistory.user_id == user_id
    ).order_by(
        desc(SearchHistory.search_count),
        desc(SearchHistory.last_searched)
    ).limit(limit).all()

def get_global_popular_pokemon(limit: int = 5, db: Session = None) -> List[SmartFavoriteResponse]:
    """
    Obtiene los Pokémon más populares globalmente basándose en búsquedas.
    
    Args:
        limit: Número máximo de resultados
        db: Sesión de base de datos
        
    Returns:
        List[SmartFavoriteResponse]: Lista de Pokémon populares con scores
    """
    if db is None:
        from app.database import get_db
        db = next(get_db())
    
    # Consulta para obtener Pokémon más buscados globalmente
    popular_pokemon = db.query(
        SearchHistory.pokemon_id,
        SearchHistory.pokemon_name,
        SearchHistory.pokemon_sprite,
        SearchHistory.pokemon_types,
        func.sum(SearchHistory.search_count).label('total_searches'),
        func.count(SearchHistory.user_id).label('unique_users')
    ).group_by(
        SearchHistory.pokemon_id,
        SearchHistory.pokemon_name,
        SearchHistory.pokemon_sprite,
        SearchHistory.pokemon_types
    ).order_by(
        desc('total_searches'),
        desc('unique_users')
    ).limit(limit).all()
    
    # Convertir a SmartFavoriteResponse con scoring
    results = []
    for pokemon in popular_pokemon:
        # Calcular score de relevancia (búsquedas totales * usuarios únicos)
        relevance_score = float(pokemon.total_searches * pokemon.unique_users)
        
        results.append(SmartFavoriteResponse(
            pokemon_id=pokemon.pokemon_id,
            pokemon_name=pokemon.pokemon_name,
            pokemon_sprite=pokemon.pokemon_sprite,
            pokemon_types=pokemon.pokemon_types,
            relevance_score=relevance_score,
            source="global_popular"
        ))
    
    return results

def get_user_based_favorites(user_id: int, limit: int = 5, db: Session = None) -> List[SmartFavoriteResponse]:
    """
    Obtiene favoritos basados en el comportamiento del usuario.
    
    Args:
        user_id: ID del usuario
        limit: Número máximo de resultados
        db: Sesión de base de datos
        
    Returns:
        List[SmartFavoriteResponse]: Lista de favoritos personalizados
    """
    if db is None:
        from app.database import get_db
        db = next(get_db())
    
    results = []
    
    # 1. Pokémon más buscados por el usuario (peso alto)
    user_searches = db.query(SearchHistory).filter(
        SearchHistory.user_id == user_id
    ).order_by(
        desc(SearchHistory.search_count),
        desc(SearchHistory.last_searched)
    ).limit(limit * 2).all()  # Obtener más para filtrar después
    
    for search in user_searches:
        # Score basado en frecuencia de búsqueda y recencia
        days_since_last_search = (datetime.utcnow() - search.last_searched).days
        recency_factor = max(0.1, 1.0 - (days_since_last_search / 30))  # Decae en 30 días
        relevance_score = float(search.search_count * recency_factor * 10)  # Factor 10 para búsquedas
        
        results.append(SmartFavoriteResponse(
            pokemon_id=search.pokemon_id,
            pokemon_name=search.pokemon_name,
            pokemon_sprite=search.pokemon_sprite,
            pokemon_types=search.pokemon_types,
            relevance_score=relevance_score,
            source="search_history"
        ))
    
    # 2. Pokémon más usados en el equipo del usuario (peso medio)
    team_pokemon = db.query(UserPokemon).filter(
        UserPokemon.user_id == user_id
    ).all()
    
    for pokemon in team_pokemon:
        # Verificar si ya está en los resultados de búsqueda
        if not any(r.pokemon_id == pokemon.pokemon_id for r in results):
            relevance_score = 5.0  # Score base para Pokémon del equipo
            
            results.append(SmartFavoriteResponse(
                pokemon_id=pokemon.pokemon_id,
                pokemon_name=pokemon.pokemon_name,
                pokemon_sprite=pokemon.pokemon_sprite,
                pokemon_types=None,  # No tenemos tipos en UserPokemon
                relevance_score=relevance_score,
                source="team_usage"
            ))
    
    # 3. Si no hay suficientes resultados, completar con Pokémon populares globalmente
    if len(results) < limit:
        global_popular = get_global_popular_pokemon(limit - len(results), db)
        for pokemon in global_popular:
            # Reducir score de Pokémon globales para que no dominen
            pokemon.relevance_score *= 0.5
            results.append(pokemon)
    
    # Ordenar por score de relevancia y devolver los mejores
    results.sort(key=lambda x: x.relevance_score, reverse=True)
    return results[:limit]

def get_smart_favorites(user_id: int, limit: int = 5, db: Session = None) -> List[SmartFavoriteResponse]:
    """
    Obtiene favoritos inteligentes basándose en el comportamiento del usuario.
    
    Para usuarios nuevos: devuelve Pokémon populares globalmente.
    Para usuarios existentes: devuelve favoritos personalizados.
    
    Args:
        user_id: ID del usuario
        limit: Número máximo de resultados
        db: Sesión de base de datos
        
    Returns:
        List[SmartFavoriteResponse]: Lista de favoritos inteligentes
    """
    if db is None:
        from app.database import get_db
        db = next(get_db())
    
    # Verificar si el usuario tiene historial de búsquedas
    search_count = db.query(SearchHistory).filter(
        SearchHistory.user_id == user_id
    ).count()
    
    if search_count == 0:
        # Usuario nuevo: devolver Pokémon más populares globalmente
        return get_global_popular_pokemon(limit, db)
    else:
        # Usuario existente: devolver favoritos basados en su comportamiento
        return get_user_based_favorites(user_id, limit, db)
