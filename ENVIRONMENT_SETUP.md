# 🔧 Configuración de Entornos

Este proyecto maneja diferentes entornos de manera segura para evitar conflictos entre desarrollo local y producción.

## 📁 Archivos de Configuración

### `.env.local` (Desarrollo Local)
- **Propósito**: Configuración para desarrollo local
- **Base de datos**: SQLite local (`pokemon_local.db`)
- **Seguridad**: Claves de desarrollo (no sensibles)
- **CORS**: `http://localhost:4200`

### `.env.production` (Producción)
- **Propósito**: Plantilla para configuración de producción
- **Base de datos**: MySQL (Railway)
- **Seguridad**: Claves de producción (sensibles)
- **CORS**: Dominio de producción

### `.env.example` (Plantilla)
- **Propósito**: Plantilla para nuevos desarrolladores
- **Contenido**: Variables necesarias con ejemplos
- **Uso**: Copiar como `.env.local` para desarrollo

## 🚀 Cómo Usar

### Desarrollo Local
```bash
# Opción 1: Script automático
python start_local.py

# Opción 2: Manual
export ENVIRONMENT=development
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Producción
```bash
# Opción 1: Script automático
python start_production.py

# Opción 2: Manual
export ENVIRONMENT=production
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## 🔒 Seguridad

### ✅ Archivos Protegidos (NO se suben al repositorio)
- `.env.local`
- `.env.production`
- `*.db` (bases de datos)
- `*.sqlite`

### ✅ Archivos Públicos (SÍ se suben al repositorio)
- `.env.example` (plantilla)
- `start_local.py`
- `start_production.py`
- `ENVIRONMENT_SETUP.md`

## 🗄️ Bases de Datos

### Desarrollo Local
- **Tipo**: SQLite
- **Archivo**: `pokemon_local.db`
- **Ventajas**: No requiere instalación, datos locales
- **Desventajas**: No compatible con MySQL

### Producción
- **Tipo**: MySQL
- **Host**: Railway
- **Ventajas**: Escalable, compatible con MySQL
- **Desventajas**: Requiere conexión a internet

## 🔄 Migración de Datos

### De Local a Producción
1. Exportar datos de SQLite local
2. Importar a MySQL de producción
3. Verificar integridad de datos

### De Producción a Local
1. Exportar datos de MySQL
2. Convertir a formato SQLite
3. Importar a base local

## 🚨 Troubleshooting

### Error: "Can't connect to MySQL"
- **Causa**: Intentando conectar a MySQL en desarrollo
- **Solución**: Usar `python start_local.py`

### Error: "Database locked"
- **Causa**: Múltiples procesos accediendo a SQLite
- **Solución**: Cerrar otros procesos, reiniciar servidor

### Error: "Environment variable not set"
- **Causa**: Variables de entorno faltantes
- **Solución**: Verificar `.env.local` o variables de Railway

## 📝 Notas Importantes

1. **NUNCA** subas archivos `.env*` al repositorio
2. **SIEMPRE** usa `ENVIRONMENT=development` para desarrollo local
3. **VERIFICA** que las variables de Railway estén configuradas en producción
4. **BACKUP** regular de datos importantes antes de cambios
