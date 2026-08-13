import re
from fastapi import HTTPException

def validate_nickname(nickname: str | None) -> str | None:
    """
    Validar nickname de Pokémon para prevenir XSS y otros ataques.
    
    Validaciones:
    - Longitud máxima: 20 caracteres
    - Sin HTML tags
    - Sin event handlers (onclick, onerror, etc.)
    - Sin javascript: protocol
    - Solo caracteres alfanuméricos, espacios y símbolos seguros: - _ ' . ! ?
    
    Args:
        nickname: Nickname a validar (puede ser None o vacío)
        
    Returns:
        Nickname validado o None si es vacío
        
    Raises:
        HTTPException: Si el nickname no cumple las validaciones
    """
    if nickname is None or nickname.strip() == "":
        return None
    
    nickname = nickname.strip()
    
    # Verificar longitud
    if len(nickname) > 20:
        raise HTTPException(
            status_code=400,
            detail="El nickname no puede exceder 20 caracteres"
        )
    
    # Detectar HTML/Scripts (XSS Prevention)
    html_pattern = re.compile(r'<[^>]*>')
    script_pattern = re.compile(r'<script[\s\S]*?>[\s\S]*?</script>', re.IGNORECASE)
    event_pattern = re.compile(r'on\w+\s*=', re.IGNORECASE)
    js_pattern = re.compile(r'javascript:', re.IGNORECASE)
    
    if (html_pattern.search(nickname) or 
        script_pattern.search(nickname) or 
        event_pattern.search(nickname) or 
        js_pattern.search(nickname)):
        raise HTTPException(
            status_code=400,
            detail="El nickname contiene contenido potencialmente peligroso"
        )
    
    # Verificar caracteres permitidos
    # Permite: letras, números, espacios, acentos, ñ, y símbolos seguros: - _ ' . ! ?
    safe_pattern = re.compile(r'^[a-zA-Z0-9áéíóúÁÉÍÓÚñÑ\s\-_\'.!?]+$')
    if not safe_pattern.match(nickname):
        raise HTTPException(
            status_code=400,
            detail="El nickname contiene caracteres no permitidos. Solo se permiten letras, números, espacios y los símbolos: - _ ' . ! ?"
        )
    
    return nickname

