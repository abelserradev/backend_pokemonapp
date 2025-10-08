from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, JSON, Float
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    
    # Relaciones
    pokemon_team = relationship("UserPokemon", back_populates="user", cascade="all, delete-orphan")
    training_sessions = relationship("TrainingSession", back_populates="user", cascade="all, delete-orphan")
    favorite_pokemon = relationship("FavoritePokemon", back_populates="user", cascade="all, delete-orphan")

class UserPokemon(Base):
    __tablename__ = "user_pokemon"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    pokemon_id = Column(Integer, nullable=False)  # ID del pokémon de la API
    pokemon_name = Column(String(100), nullable=False)
    pokemon_sprite = Column(String(500))
    selected_ability = Column(String(100))
    nickname = Column(String(100))
    level = Column(Integer, default=1)
    added_at = Column(DateTime, server_default=func.now())
    
    # Relación con usuario
    user = relationship("User", back_populates="pokemon_team")

class TrainingSession(Base):
    __tablename__ = "training_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    pokemon_id = Column(Integer, nullable=False)
    pokemon_name = Column(String(100), nullable=False)
    pokemon_sprite = Column(String(500))
    pokemon_types = Column(JSON)
    
    # Estadísticas base
    base_stats = Column(JSON)  # {"hp": 45, "attack": 49, ...}
    
    # EVs (Effort Values)
    current_evs = Column(JSON)  # {"hp": 0, "attack": 0, ...}
    max_evs = Column(JSON)  # {"hp": 252, "attack": 252, ...}
    total_ev_points = Column(Integer, default=0)
    max_ev_points = Column(Integer, default=510)
    remaining_points = Column(Integer, default=510)
    
    # Estado
    is_completed = Column(Boolean, default=False)
    completed_at = Column(DateTime)
    
    # Fechas
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    
    # Relación con usuario
    user = relationship("User", back_populates="training_sessions")

class FavoritePokemon(Base):
    __tablename__ = "favorite_pokemon"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    pokemon_id = Column(Integer, nullable=False, unique=True)
    pokemon_name = Column(String(100), nullable=False)
    pokemon_sprite = Column(String(500))
    pokemon_types = Column(JSON)  # ["grass", "poison"]
    
    # Estadísticas de uso
    usage_count = Column(Integer, default=0)
    last_used = Column(DateTime)
    
    # Fechas
    added_at = Column(DateTime, server_default=func.now())
    
    # Relación con usuario
    user = relationship("User", back_populates="favorite_pokemon")

class UserToken(Base):
    __tablename__ = "user_tokens"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    token = Column(String(500), nullable=False)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, server_default=func.now())