# 🚀 Despliegue en Easypanel - Fundaciones Frontend

## 📦 Archivos Necesarios

He creado todo lo necesario para el despliegue:

### ✅ Archivos Creados:
1. **`database-backup.json`** (20 MB) - Backup completo con 5,657 fundaciones
2. **`restore-database.js`** - Script de restauración  
3. **`deployment-guide.md`** - Guía completa de despliegue
4. **`docker-compose.yml`** - Para despliegue con Docker
5. **`fundaciones-frontend/Dockerfile`** - Imagen Docker del frontend

## 🎯 Opción Recomendada: Backup de Base de Datos

**¿Por qué usar el backup en lugar de migración?**
- ✅ **Codificación garantizada**: Todos los caracteres españoles están corregidos
- ✅ **Datos normalizados**: Actividades duplicadas ya fusionadas  
- ✅ **Probado**: Los 5,657 registros funcionan perfectamente
- ✅ **Rápido**: Solo restaurar, no procesar Excel nuevamente

## 📋 Pasos para Easypanel

### 1. Crear Servicio MongoDB
```yaml
# En Easypanel, crear servicio MongoDB
Name: fundaciones-mongodb
Image: mongo:7.0
Environment:
  MONGO_INITDB_ROOT_USERNAME: admin
  MONGO_INITDB_ROOT_PASSWORD: tu-password-seguro
  MONGO_INITDB_DATABASE: fundaciones_espana
Port: 27017
```

### 2. Subir y Restaurar Datos
1. Subir `database-backup.json` y `restore-database.js` al servidor
2. Ejecutar restauración:
```bash
node restore-database.js
```

### 3. Crear Aplicación Next.js
```yaml
# En Easypanel, crear aplicación Node.js
Name: fundaciones-frontend
Source: GitHub o subir carpeta fundaciones-frontend/
Build Command: npm run build
Start Command: npm start
Port: 3000

Environment Variables:
  MONGODB_URI: mongodb://admin:tu-password@fundaciones-mongodb:27017/fundaciones_espana?authSource=admin
  NEXTAUTH_SECRET: tu-secret-random-key
  NEXTAUTH_URL: https://tu-dominio.easypanel.app
```

## 📁 Archivos para Subir a Easypanel

### Opción A: Subir todo comprimido
```bash
# Crear ZIP con estos archivos:
fundaciones-frontend/          # Carpeta completa del frontend
database-backup.json          # Backup de 20MB con todos los datos
restore-database.js           # Script de restauración
deployment-guide.md           # Guía completa
docker-compose.yml           # Para Docker si lo prefieres
.env.example                 # Variables de entorno
```

### Opción B: Solo frontend + base de datos
```bash
# Mínimo necesario:
fundaciones-frontend/         # La aplicación
database-backup.json         # Los datos corregidos
restore-database.js          # Para restaurar datos
```

## 🔧 Variables de Entorno en Easypanel

```env
# Base de datos (REQUERIDO)
MONGODB_URI=mongodb://admin:password@fundaciones-mongodb:27017/fundaciones_espana?authSource=admin

# Next.js (OPCIONAL)
NEXTAUTH_SECRET=genera-un-secret-random-aqui
NEXTAUTH_URL=https://tu-app.easypanel.app
```

## ✅ Verificación Post-Despliegue

1. **MongoDB**: Verificar conexión y datos
   ```javascript
   db.fundaciones.countDocuments() // Debe devolver 5657
   ```

2. **Frontend**: Comprobar páginas
   - `/` - Página principal con filtros
   - `/analytics` - Gráficos y estadísticas  
   - `/data` - Vista de datos detallada

3. **Funcionalidades**: Probar
   - ✅ Búsqueda por nombre
   - ✅ Filtros con conteos
   - ✅ Ordenación alfabética/fecha
   - ✅ Badges de estado con colores
   - ✅ Paginación con totales
   - ✅ Gráficos en Analytics

## 🆘 Solución de Problemas

### MongoDB no conecta
- Verificar MONGODB_URI en variables de entorno
- Comprobar que el servicio MongoDB está corriendo
- Verificar usuario/password en la URI

### Datos mal codificados  
- Si ves caracteres raros (Ã, Â, etc.), restaurar desde `database-backup.json`
- No usar los archivos de migración originales

### Gráficos vacíos
- Verificar que se restauraron todos los datos
- Comprobar en `/api/fundaciones/stats` que devuelve datos

## 💾 Respaldo de Datos Actual

El archivo `database-backup.json` contiene:
- **5,657 fundaciones** completas
- **Codificación UTF-8** perfecta (caracteres españoles)
- **Actividades normalizadas** (sin duplicados)  
- **Todos los campos** preservados
- **Tamaño**: 20 MB

**✨ Esta es tu mejor opción para desplegar sin problemas de codificación!**