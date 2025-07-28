# 🚀 Guía Final de Despliegue en Easypanel (Sin Subir Archivos Grandes)

## 🎯 Estrategias para Restaurar Datos sin Subir 20MB

### Opción 1: Migración Directa desde Excel (RECOMENDADA)
**Ventaja**: No necesitas subir el backup JSON de 20MB

1. **Subir el Excel original a Google Drive/Dropbox**
   - Archivo: `BBDD de fundaciones España actualizada 040724.xls` (15MB)
   - Obtener link de descarga directa

2. **En Easypanel, ejecutar**:
```bash
# Instalar Python y dependencias
apt-get update && apt-get install -y python3 python3-pip
pip3 install pymongo pandas openpyxl requests python-dotenv

# Ejecutar script de migración
python3 migration-scripts/restore-from-excel-production.py
```

3. **Cuando pregunte, seleccionar**:
   - Opción 2: URL de descarga
   - Pegar el link de Google Drive/Dropbox

### Opción 2: API de Restauración por Lotes
**Ventaja**: Puedes enviar datos en pequeños chunks

1. **Agregar variable de entorno en Easypanel**:
```env
RESTORE_API_KEY=tu-clave-secreta-segura
```

2. **Dividir el backup en partes más pequeñas** (en tu local):
```javascript
// split-backup.js
const fs = require('fs');
const backup = JSON.parse(fs.readFileSync('database-backup.json'));
const BATCH_SIZE = 500; // 500 documentos por lote

for (let i = 0; i < backup.data.length; i += BATCH_SIZE) {
  const batch = backup.data.slice(i, i + BATCH_SIZE);
  const batchNumber = Math.floor(i / BATCH_SIZE) + 1;
  
  fs.writeFileSync(
    `batch-${batchNumber}.json`,
    JSON.stringify({
      batch,
      batchNumber,
      totalBatches: Math.ceil(backup.data.length / BATCH_SIZE),
      clearFirst: batchNumber === 1
    })
  );
}
```

3. **Enviar cada lote via curl**:
```bash
# Para cada archivo batch-X.json
curl -X PUT \
  -H "Content-Type: application/json" \
  -H "x-api-key: tu-clave-secreta" \
  -d @batch-1.json \
  https://tu-app.easypanel.app/api/restore
```

### Opción 3: Usar MongoDB Atlas (Gratis hasta 512MB)
**Ventaja**: Puedes importar datos localmente y conectar desde Easypanel

1. **Crear cuenta gratuita en MongoDB Atlas**
   - https://www.mongodb.com/cloud/atlas

2. **Importar datos localmente**:
```bash
# En tu máquina local
mongoimport --uri "mongodb+srv://usuario:password@cluster.mongodb.net/fundaciones_espana" \
  --collection fundaciones \
  --file database-backup.json \
  --jsonArray
```

3. **En Easypanel, usar la URI de Atlas**:
```env
MONGODB_URI=mongodb+srv://usuario:password@cluster.mongodb.net/fundaciones_espana
```

### Opción 4: Script de Inicialización en Docker
**Ventaja**: Se ejecuta automáticamente al crear el contenedor

1. **Modificar Dockerfile**:
```dockerfile
FROM node:18-alpine

WORKDIR /app

# Instalar Python para migración inicial
RUN apk add --no-cache python3 py3-pip
RUN pip3 install pymongo pandas openpyxl requests

# Copy package files
COPY package*.json ./
RUN npm ci --only=production

# Copy app source
COPY . .

# Copy migration scripts
COPY migration-scripts /migration-scripts

# Build the application
RUN npm run build

# Script de inicio que verifica/restaura DB
COPY docker-entrypoint.sh /
RUN chmod +x /docker-entrypoint.sh

EXPOSE 3000

ENTRYPOINT ["/docker-entrypoint.sh"]
CMD ["npm", "start"]
```

2. **Crear docker-entrypoint.sh**:
```bash
#!/bin/sh

# Verificar si la BD está vacía
DOCS_COUNT=$(node -e "
const { MongoClient } = require('mongodb');
(async () => {
  const client = new MongoClient(process.env.MONGODB_URI);
  await client.connect();
  const count = await client.db('fundaciones_espana').collection('fundaciones').countDocuments();
  console.log(count);
  await client.close();
})();
")

if [ "$DOCS_COUNT" -eq "0" ]; then
  echo "Base de datos vacía, ejecutando migración..."
  python3 /migration-scripts/restore-from-excel-production.py
fi

# Iniciar aplicación
exec "$@"
```

## 📋 Pasos Simplificados para Easypanel

### 1. Preparar el Código
```bash
# En tu repositorio Git, incluir:
fundaciones-frontend/          # App completa
migration-scripts/            # Scripts de migración
├── restore-from-excel-production.py  # Script principal
docker-compose.yml
Dockerfile
.env.example
```

### 2. Variables de Entorno en Easypanel
```env
# MongoDB (local o Atlas)
MONGODB_URI=mongodb://usuario:password@mongodb:27017/fundaciones_espana

# Restauración
RESTORE_API_KEY=clave-secreta-segura
EXCEL_URL=https://link-a-tu-excel.com/archivo.xls

# Next.js
NEXTAUTH_SECRET=tu-secret-key
NEXTAUTH_URL=https://tu-app.easypanel.app
```

### 3. Comandos Post-Deploy en Easypanel
En la sección "Run Command" después del deploy:
```bash
# Opción A: Si tienes el Excel en una URL
python3 migration-scripts/restore-from-excel-production.py

# Opción B: Si usas MongoDB Atlas (ya con datos)
# No necesitas hacer nada

# Opción C: Si dividiste en lotes
# Ejecutar los curls desde tu máquina local
```

## ✅ Verificación

1. **Comprobar datos**:
```bash
# En el contenedor de Easypanel
node -e "
const { MongoClient } = require('mongodb');
(async () => {
  const client = new MongoClient(process.env.MONGODB_URI);
  await client.connect();
  const db = client.db('fundaciones_espana');
  const count = await db.collection('fundaciones').countDocuments();
  console.log('Total documentos:', count);
  const sample = await db.collection('fundaciones').findOne();
  console.log('Muestra:', sample.nombre);
  await client.close();
})();
"
```

2. **Verificar en el frontend**:
- Visitar `/analytics` - debe mostrar estadísticas
- Probar filtros - deben mostrar conteos
- Buscar "MEDITERRÁNEO" - debe aparecer correctamente

## 🎯 Recomendación Final

**Para Easypanel, la mejor opción es**:
1. Subir el Excel original a Google Drive (15MB es más manejable)
2. Usar el script `restore-from-excel-production.py`
3. Este script:
   - Descarga el Excel
   - Aplica todas las correcciones de encoding
   - Normaliza las actividades
   - Crea los índices

**Ventajas**:
- ✅ No necesitas subir 20MB a Easypanel
- ✅ Proceso automatizado completo
- ✅ Garantiza encoding correcto
- ✅ Un solo comando para restaurar todo

¡Con esto puedes desplegar sin problemas de tamaño de archivos! 🚀