# 🚂 Guía de Despliegue en Railway

## 📋 Variables de Entorno Requeridas en Railway

Configura estas variables en el dashboard de Railway:

### **Base de Datos**
```
DATABASE_URL=mysql+pymysql://usuario:password@host:puerto/database
```

### **Seguridad**
```
SECRET_KEY=tu-clave-secreta-super-segura-para-produccion
```

### **CORS**
```
ALLOWED_ORIGINS=https://tu-frontend.vercel.app
```

### **Entorno**
```
ENVIRONMENT=production
```

## 🔧 Configuración Automática

El sistema detecta automáticamente Railway por:
- Variable `RAILWAY_ENVIRONMENT` (automática de Railway)
- Variable `PORT` (automática de Railway)

## 🚀 Proceso de Despliegue

1. **Subir código al repositorio**
2. **Conectar Railway al repositorio**
3. **Configurar variables de entorno en Railway**
4. **Railway construye y despliega automáticamente**

## 🔍 Verificación Post-Despliegue

### **Logs de Railway**
```bash
# Verificar que se detecte Railway
🚂 Detectado Railway - usando variables de entorno del sistema

# Verificar conexión a base de datos
🗄️ Database: mysql+pymysql://...

# Verificar que el servidor inicie
🚂 Railway - Starting server on port: 8000
```

### **Endpoints de Prueba**
- **Health Check**: `https://tu-app.railway.app/`
- **API Docs**: `https://tu-app.railway.app/docs`
- **Login**: `https://tu-app.railway.app/api/login/json`

## 🚨 Troubleshooting

### **Error: "Can't connect to MySQL"**
- Verificar que `DATABASE_URL` esté configurada en Railway
- Verificar que la base de datos MySQL esté activa

### **Error: "CORS policy"**
- Verificar que `ALLOWED_ORIGINS` incluya tu frontend
- Verificar que el frontend use HTTPS en producción

### **Error: "401 Unauthorized"**
- Verificar que `SECRET_KEY` esté configurada
- Verificar que el usuario exista en la base de datos de producción

## 📝 Notas Importantes

1. **Railway detecta automáticamente** el entorno por las variables del sistema
2. **No necesitas** configurar `ENVIRONMENT=production` manualmente
3. **Las variables de entorno** se configuran en el dashboard de Railway
4. **El puerto** se asigna automáticamente por Railway
5. **Los logs** se pueden ver en el dashboard de Railway
