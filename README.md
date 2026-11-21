# 🎮 Pokemon Backend API

API REST desarrollada con FastAPI para gestión de Pokémon con autenticación de usuarios.

## 🚀 Tecnologías

- **FastAPI** - Framework web moderno y rápido
- **SQLAlchemy** - ORM para Python
- **MySQL** - Base de datos relacional
- **JWT** - Autenticación con tokens
- **Bcrypt** - Hash de contraseñas
- **Pydantic** - Validación de datos

## 📁 Estructura del Proyecto

```
backend/
├── app/
│   ├── models/          # Modelos de base de datos
│   │   ├── user.py
│   │   ├── pokemon.py
│   │   └── database.py
│   ├── routes/          # Endpoints de la API
│   │   ├── auth.py
│   │   └── pokemon.py
│   ├── service/         # Lógica de negocio
│   │   ├── auth.py
│   │   └── pokemon.py
│   ├── utils/           # Utilidades
│   │   └── security.py
│   ├── database.py      # Configuración de BD
│   └── main.py          # Aplicación principal
├── requirements.txt     # Dependencias
├── Dockerfile          # Configuración Docker para Railway
├── .dockerignore       # Archivos ignorados por Docker
├── railway.json        # Configuración Railway
├── .gitignore          # Archivos ignorados por Git
└── .env                # Variables de entorno (no commiteado)
```

## 🔧 Configuración Local

### 1. Clona el repositorio

```bash
git clone <tu-repositorio>
cd backend
```

### 2. Crea un entorno virtual

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3. Instala las dependencias

```bash
pip install -r requirements.txt
```

### 4. Configura las variables de entorno

Crea un archivo `.env` en la raíz del proyecto:

```env
DATABASE_URL=mysql+pymysql://root:tu_password@localhost:3306/pokemon_backend
SECRET_KEY=tu_clave_secreta_muy_segura
ALLOWED_ORIGINS=http://localhost:4200
```

### 5. Ejecuta la aplicación

```bash
# Desarrollo
uvicorn app.main:app --reload

# O usando Python directamente
python -m app.main
```

La API estará disponible en: `http://localhost:8000`

## 📚 Documentación de la API

Una vez que la aplicación esté corriendo, visita:

- **Swagger UI:** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`

## 🔐 Endpoints Principales

### Autenticación

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/api/register` | Registrar nuevo usuario |
| POST | `/api/login` | Login de usuario |
| POST | `/api/token` | Obtener token de acceso |
| GET | `/api/me` | Obtener usuario actual |

### Pokémon

| Método | Endpoint | Descripción | Auth |
|--------|----------|-------------|------|
| GET | `/api/pokemon` | Listar todos los Pokémon | ❌ |
| GET | `/api/pokemon/{id}` | Obtener Pokémon por ID | ❌ |
| POST | `/api/pokemon` | Crear nuevo Pokémon | ✅ |
| PUT | `/api/pokemon/{id}` | Actualizar Pokémon | ✅ |
| DELETE | `/api/pokemon/{id}` | Eliminar Pokémon | ✅ |
| GET | `/api/pokemon/user/me` | Pokémon del usuario | ✅ |

## 🧪 Ejemplos de Uso

### Registro de Usuario

```bash
curl -X POST "http://localhost:8000/api/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "usuario@example.com",
    "password": "password123"
  }'
```

### Login

```bash
curl -X POST "http://localhost:8000/api/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=usuario@example.com&password=password123"
```

### Crear Pokémon (requiere autenticación)

```bash
curl -X POST "http://localhost:8000/api/pokemon" \
  -H "Authorization: Bearer TU_TOKEN_AQUI" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Pikachu",
    "type": "Electric",
    "level": 25
  }'
```

## 🌐 Despliegue en Railway

Consulta [RAILWAY_DEPLOY.md](./RAILWAY_DEPLOY.md) para instrucciones detalladas de despliegue.

### Resumen rápido:

1. Conecta tu repositorio de GitHub con Railway
2. Añade una base de datos MySQL en Railway
3. Configura las variables de entorno:
   - `DATABASE_URL`
   - `SECRET_KEY`
   - `ALLOWED_ORIGINS`
4. Railway desplegará automáticamente

## 🔒 Seguridad

- ✅ Autenticación JWT
- ✅ Contraseñas hasheadas con bcrypt
- ✅ CORS configurado
- ✅ Validación de datos con Pydantic
- ✅ Variables de entorno para secretos

## 🧰 Scripts Disponibles

```bash
# Ejecutar en desarrollo
uvicorn app.main:app --reload

# Ejecutar en producción (Railway usa esto)
uvicorn app.main:app --host 0.0.0.0 --port $PORT

# Instalar dependencias
pip install -r requirements.txt

# Actualizar dependencias
pip freeze > requirements.txt
```

## 📝 Variables de Entorno

| Variable | Descripción | Ejemplo |
|----------|-------------|---------|
| `DATABASE_URL` | URL de conexión a MySQL | `mysql+pymysql://user:pass@host:port/db` |
| `SECRET_KEY` | Clave para JWT | `tu_clave_secreta_muy_larga` |
| `ALLOWED_ORIGINS` | URLs permitidas para CORS | `https://app.vercel.app,http://localhost:4200` |
| `PORT` | Puerto de la aplicación | `8000` (Railway lo proporciona automáticamente) |

## 🐛 Troubleshooting

### Error de conexión a la base de datos

- Verifica que MySQL esté corriendo
- Comprueba las credenciales en `.env`
- Asegúrate de que la base de datos existe

### Error de CORS

- Añade la URL de tu frontend a `ALLOWED_ORIGINS`
- Verifica que no haya espacios en la variable

### Error 401 Unauthorized

- Verifica que el token JWT sea válido
- Comprueba que `SECRET_KEY` sea la misma en todos los entornos

## 📄 Licencia

Este proyecto es de código abierto.

## 👨‍💻 Autor

Desarrollado con ❤️ para la gestión de Pokémon

---

**¿Necesitas ayuda?** Abre un issue en el repositorio.
