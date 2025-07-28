# Guía de Despliegue - Fundaciones Frontend

## 📋 Archivos Necesarios para Easypanel

### 1. Base de Datos
**Opción Recomendada: Usar backup completo**
- `database-backup.json` (se genera con el script)
- `restore-database.js` (script de restauración)

### 2. Aplicación Frontend
Carpeta completa: `fundaciones-frontend/`

### 3. Archivos de Configuración
- `.env.example` (plantilla de variables de entorno)
- `deployment-guide.md` (esta guía)

## 🚀 Pasos para Desplegar

### Paso 1: Crear Backup de la Base de Datos
```bash
cd "/Users/paulo/Documents/Proyectos/Trabajo/Captaru/Datos Subvenciones"
node create-database-backup.js
```

### Paso 2: Preparar Archivos para Subir
Comprimir en un ZIP:
- `fundaciones-frontend/` (toda la carpeta)
- `database-backup.json`
- `restore-database.js`
- `.env.example`
- `deployment-guide.md`

### Paso 3: Configurar en Easypanel

#### 3.1. Crear Servicio MongoDB
1. Crear nuevo servicio MongoDB en Easypanel
2. Anotar la URI de conexión

#### 3.2. Crear Aplicación Next.js
1. Crear nueva aplicación Node.js
2. Subir el código del frontend
3. Configurar variables de entorno:

```env
MONGODB_URI=mongodb://[tu-usuario]:[tu-password]@[host]:[puerto]/fundaciones_espana
NEXTAUTH_SECRET=tu-secret-key-random
NEXTAUTH_URL=https://tu-dominio.com
```

#### 3.3. Restaurar Base de Datos
Una vez desplegado, ejecutar en el contenedor:
```bash
node restore-database.js
```

## 🔧 Variables de Entorno Necesarias

```env
# Base de datos
MONGODB_URI=mongodb://localhost:27017/fundaciones_espana

# Next.js (opcional)
NEXTAUTH_SECRET=your-secret-here
NEXTAUTH_URL=http://localhost:3000
```

## 📊 Datos de la Base de Datos

- **Total documentos**: ~5,657 fundaciones
- **Colección**: `fundaciones`
- **Base de datos**: `fundaciones_espana`
- **Codificación**: UTF-8 (caracteres españoles corregidos)
- **Normalización**: Actividades duplicadas fusionadas

## ✅ Verificaciones Post-Despliegue

1. **Frontend**: Verificar que carga la página principal
2. **Base de datos**: Comprobar conexión en `/analytics`
3. **Filtros**: Verificar que los filtros muestran conteos
4. **Búsqueda**: Probar búsqueda por nombre
5. **Detalles**: Verificar que las páginas de detalle funcionan

## 🐛 Solución de Problemas

### Error de Conexión a MongoDB
- Verificar MONGODB_URI en variables de entorno
- Comprobar que MongoDB está ejecutándose
- Verificar permisos de red

### Caracteres Mal Codificados
- Si aparecen caracteres extraños, restaurar de `database-backup.json`
- Verificar que la restauración completó sin errores

### Filtros Vacíos
- Verificar que los datos se importaron correctamente
- Comprobar conteo de documentos en la base de datos

## 📁 Estructura Final en Easypanel

```
/app
├── fundaciones-frontend/     # Aplicación Next.js
├── database-backup.json      # Backup completo de datos
├── restore-database.js       # Script de restauración
└── deployment-guide.md       # Esta guía
```

## 🔄 Comandos de Mantenimiento

### Verificar datos en MongoDB
```javascript
db.fundaciones.countDocuments()
db.fundaciones.findOne()
```

### Re-ejecutar normalización (si es necesario)
```bash
node normalize-activities.js
```