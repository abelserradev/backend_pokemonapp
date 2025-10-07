# 🚀 Guía de Despliegue en Railway

## 📋 Requisitos Previos

- Cuenta en [Railway](https://railway.app)
- Cuenta en GitHub (para conectar tu repositorio)
- Base de datos MySQL configurada (Railway proporciona una)

## 🔧 Archivos de Configuración

Railway usa **Docker** para construir y desplegar tu aplicación. Los siguientes archivos ya están configurados:

- **`Dockerfile`** - Define el entorno y comando de inicio
- **`.dockerignore`** - Archivos ignorados durante el build de Docker
- **`railway.json`** - Configuración específica de Railway (usa builder DOCKERFILE)

## 🔧 Variables de Entorno Requeridas

Configura estas variables de entorno en tu proyecto de Railway:

### 1. DATABASE_URL
```
DATABASE_URL=mysql+pymysql://usuario:contraseña@host:puerto/database
```

**Ejemplo con Railway MySQL:**
```
DATABASE_URL=mysql+pymysql://root:contraseña@containers-us-west-XXX.railway.app:XXXX/railway
```

### 2. SECRET_KEY
```
SECRET_KEY=tu_clave_secreta_muy_segura_aqui
```

**Genera una clave segura con:**
```python
import secrets
print(secrets.token_urlsafe(32))
```

### 3. ALLOWED_ORIGINS
```
ALLOWED_ORIGINS=https://tu-frontend.vercel.app,http://localhost:4200
```

**Importante:** Separa múltiples URLs con comas SIN espacios.

---

## 🚂 Pasos para Desplegar

### 1. Prepara tu Repositorio Git

```bash
# Inicializa git si no lo has hecho
git init

# Añade los archivos
git add .

# Commit
git commit -m "Preparado para despliegue en Railway"

# Conecta con tu repositorio remoto (GitHub)
git remote add origin https://github.com/tu-usuario/tu-repo.git
git push -u origin main
```

### 2. Crea un Proyecto en Railway

1. Ve a [railway.app](https://railway.app)
2. Haz clic en "New Project"
3. Selecciona "Deploy from GitHub repo"
4. Autoriza Railway y selecciona tu repositorio
5. Railway detectará automáticamente que es un proyecto Python

### 3. Añade una Base de Datos MySQL

1. En tu proyecto de Railway, haz clic en "+ New"
2. Selecciona "Database" → "MySQL"
3. Railway creará una base de datos MySQL
4. Copia la URL de conexión (Variables → DATABASE_URL)

### 4. Configura las Variables de Entorno

En Railway, ve a tu servicio → **Variables** y añade:

```env
DATABASE_URL=mysql+pymysql://root:xxx@containers-us-west-xxx.railway.app:xxxx/railway
SECRET_KEY=genera_una_clave_segura_aqui
ALLOWED_ORIGINS=https://tu-frontend.vercel.app,http://localhost:4200
```

### 5. Despliega

Railway desplegará automáticamente tu aplicación. Puedes ver los logs en tiempo real.

---

## 🔍 Verificación del Despliegue

### Comprueba el Estado

1. **Health Check:**
   ```
   https://tu-app.up.railway.app/health
   ```
   Debería devolver: `{"status": "healthy"}`

2. **Endpoint Principal:**
   ```
   https://tu-app.up.railway.app/
   ```
   Debería devolver: `{"message": "¡Bienvenido al backend de Pokemon"}`

3. **Documentación API:**
   ```
   https://tu-app.up.railway.app/docs
   ```

### Prueba los Endpoints

```bash
# Test de registro
curl -X POST "https://tu-app.up.railway.app/api/register" \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123"}'

# Test de login
curl -X POST "https://tu-app.up.railway.app/api/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=test@example.com&password=test123"
```

---

## 🔄 Actualizaciones

Railway despliega automáticamente cuando haces push a tu rama principal:

```bash
git add .
git commit -m "Actualización"
git push
```

---

## 📱 Conectar con Frontend (Vercel)

En tu proyecto de Angular, actualiza la URL del API:

**`src/environments/environment.prod.ts`:**
```typescript
export const environment = {
  production: true,
  apiUrl: 'https://tu-app.up.railway.app/api'
};
```

**No olvides añadir la URL de Vercel a ALLOWED_ORIGINS en Railway.**

---

## ⚠️ Solución de Problemas

### Error de Conexión a Base de Datos

1. Verifica que DATABASE_URL esté correctamente configurada
2. Asegúrate de usar el formato: `mysql+pymysql://...`
3. Comprueba que la base de datos MySQL esté activa en Railway

### Error de CORS

1. Verifica que ALLOWED_ORIGINS incluya la URL de tu frontend
2. No uses espacios después de las comas
3. Incluye el protocolo (https://)

### Error 500

1. Revisa los logs en Railway: Settings → Logs
2. Verifica que SECRET_KEY esté configurada
3. Comprueba las migraciones de base de datos

### Puerto Incorrecto

Railway proporciona automáticamente la variable `$PORT`. El Procfile ya la usa correctamente.

---

## 📊 Monitoreo

- **Logs en tiempo real:** Railway Dashboard → Logs
- **Métricas:** Railway Dashboard → Metrics
- **Health Check:** Visita `/health` regularmente

---

## 🔒 Seguridad

✅ **Buenas prácticas implementadas:**
- Variables de entorno para secretos
- CORS configurado
- Autenticación JWT
- Contraseñas hasheadas con bcrypt

⚠️ **Recuerda:**
- Nunca commitear archivos `.env`
- Usar SECRET_KEY única y segura
- Actualizar dependencias regularmente

---

## 📞 Soporte

Si tienes problemas:
1. Revisa los logs en Railway
2. Consulta la [documentación de Railway](https://docs.railway.app)
3. Verifica que todas las variables de entorno estén configuradas

---

## ✨ Comandos Útiles

```bash
# Ver logs en Railway CLI
railway logs

# Conectar a la base de datos
railway connect

# Ejecutar comando en Railway
railway run python manage.py migrate
```

---

**¡Tu backend está listo para producción! 🎉**

