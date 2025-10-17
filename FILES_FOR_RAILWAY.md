# 📁 Archivos para Railway

## ✅ Archivos que SÍ se suben a Railway

### **Código de la Aplicación**
- `app/` - Todo el código de la aplicación
- `requirements.txt` - Dependencias de Python
- `Dockerfile` - Configuración del contenedor
- `start.sh` - Script de inicio
- `railway.json` - Configuración de Railway

### **Documentación**
- `README.md` - Documentación principal
- `ENVIRONMENT_SETUP.md` - Configuración de entornos
- `RAILWAY_DEPLOYMENT.md` - Guía de despliegue
- `FILES_FOR_RAILWAY.md` - Este archivo

### **Scripts de Desarrollo**
- `start_local.py` - Para desarrollo local
- `start_production.py` - Para producción local
- `.env.example` - Plantilla de variables

## ❌ Archivos que NO se suben a Railway

### **Configuración Local**
- `.env.local` - Variables de desarrollo local
- `.env.production` - Plantilla de producción
- `pokemon_local.db` - Base de datos local SQLite

### **Archivos del Sistema**
- `__pycache__/` - Caché de Python
- `venv/` - Entorno virtual
- `.git/` - Control de versiones
- `*.log` - Archivos de log

## 🔧 Configuración en Railway

### **Variables de Entorno Requeridas**
```
DATABASE_URL=mysql+pymysql://usuario:password@host:puerto/database
SECRET_KEY=tu-clave-secreta-super-segura
ALLOWED_ORIGINS=https://tu-frontend.vercel.app
```

### **Variables Automáticas de Railway**
```
PORT=8000 (asignado automáticamente)
RAILWAY_ENVIRONMENT=production (automática)
```

## 🚀 Proceso de Despliegue

1. **Commit y Push** del código al repositorio
2. **Railway detecta** los cambios automáticamente
3. **Construye** el contenedor usando `Dockerfile`
4. **Configura** las variables de entorno
5. **Inicia** el servidor usando `start.sh`
6. **Verifica** que la aplicación esté funcionando

## 🔍 Verificación Post-Despliegue

### **Logs Esperados**
```
🚂 Detectado Railway - usando variables de entorno del sistema
🚂 Railway - Starting server on port: 8000
🗄️ Database: mysql+pymysql://...
INFO: Application startup complete.
```

### **Endpoints de Prueba**
- `https://tu-app.railway.app/` - Health check
- `https://tu-app.railway.app/docs` - API documentation
- `https://tu-app.railway.app/api/login/json` - Login endpoint

## 📝 Notas Importantes

1. **Railway detecta automáticamente** el entorno por las variables del sistema
2. **No necesitas** archivos `.env` en Railway
3. **Las variables de entorno** se configuran en el dashboard de Railway
4. **El puerto** se asigna automáticamente
5. **Los logs** se pueden ver en el dashboard de Railway
