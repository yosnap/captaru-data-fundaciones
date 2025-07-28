# 🏛️ Fundaciones Frontend - España

Sistema completo para visualizar y analizar datos de fundaciones españolas con frontend Next.js y base de datos MongoDB.

## 📊 Características

- **Base de datos**: 5,657 fundaciones españolas
- **Frontend moderno**: Next.js 15 + TypeScript + Tailwind CSS
- **Filtros avanzados**: Por provincia, estado, actividad y función con conteos
- **Analíticas**: Gráficos interactivos y estadísticas detalladas
- **Búsqueda**: Por nombre, NIF o fines
- **Responsive**: Diseño adaptativo para móviles y desktop

## 🚀 Funcionalidades

### 📋 Vista Principal
- Listado paginado de fundaciones
- Filtros dinámicos con contadores
- Ordenación por nombre o fecha de constitución
- Badges de estado con colores
- Información de resultados totales

### 📈 Analíticas
- Distribución por estado, provincia y actividad
- Estadísticas de patronos y fundadores
- Tendencias anuales de constitución
- Gráficos interactivos con Recharts

### 🔍 Vista Detallada
- Información completa de cada fundación
- Pestañas para múltiples actividades
- Datos de contacto y ubicación
- Modal con información expandida

## 🛠️ Tecnologías

- **Frontend**: Next.js 15, React, TypeScript
- **Styling**: Tailwind CSS
- **Base de datos**: MongoDB
- **Gráficos**: Recharts
- **Iconos**: Lucide React

## 📁 Estructura del Proyecto

```
fundaciones-frontend/           # Aplicación Next.js
├── src/
│   ├── app/                   # App Router (Next.js 13+)
│   │   ├── page.tsx          # Página principal
│   │   ├── analytics/        # Página de analíticas
│   │   ├── data/            # Vista de datos detallada
│   │   └── api/             # API Routes
│   ├── components/          # Componentes React
│   └── lib/                # Utilidades y configuración
migration-scripts/            # Scripts de migración y limpieza
├── migrate-to-mongodb.py    # Migración inicial desde Excel
├── fix-encoding-*.py       # Corrección de codificación
├── normalize-activities.py  # Normalización de datos
deployment/                  # Archivos de despliegue
├── docker-compose.yml      # Docker Compose
├── Dockerfile             # Imagen Docker
└── restore-database.js    # Restauración de BD
```

## ⚙️ Instalación y Desarrollo

### Prerrequisitos
- Node.js 18+
- MongoDB
- Python 3.8+ (para scripts de migración)

### 🔧 Configuración Local

1. **Clonar repositorio**
```bash
git clone <repo-url>
cd fundaciones-frontend
```

2. **Instalar dependencias**
```bash
npm install
```

3. **Configurar variables de entorno**
```bash
cp .env.example .env.local
# Editar .env.local con tu configuración
```

4. **Configurar base de datos**
```bash
# Opción A: Restaurar desde backup (recomendado)
node restore-database.js

# Opción B: Migrar desde Excel
python migration-scripts/migrate-to-mongodb.py
```

5. **Ejecutar en desarrollo**
```bash
npm run dev
```

## 🌐 Despliegue

### Variables de Entorno
```env
MONGODB_URI=mongodb://localhost:27017/fundaciones_espana
NEXTAUTH_SECRET=your-secret-key
NEXTAUTH_URL=http://localhost:3000
```

### Docker
```bash
docker-compose up -d
```

### Easypanel
Ver `easypanel-setup.md` para instrucciones detalladas.

## 📊 Base de Datos

### Estructura de Datos
- **Colección**: `fundaciones`
- **Documentos**: 5,657 fundaciones
- **Campos principales**:
  - Información básica (nombre, NIF, estado)
  - Dirección estatutaria
  - Fechas de constitución e inscripción
  - Actividades y clasificaciones
  - Patronos, fundadores y directivos
  - Fines de la fundación

### Codificación
- ✅ **UTF-8 corregida**: Caracteres españoles (á, é, í, ó, ú, ñ)
- ✅ **Normalizada**: Actividades duplicadas fusionadas
- ✅ **Limpia**: Sin entidades HTML ni caracteres invisibles

## 🎯 API Endpoints

- `GET /api/fundaciones` - Listado con filtros y paginación
- `POST /api/fundaciones` - Detalles de fundación específica
- `GET /api/fundaciones/filters` - Opciones de filtros con conteos
- `GET /api/fundaciones/stats` - Estadísticas para analíticas

## 📈 Características Técnicas

### Performance
- Paginación eficiente (20 elementos por página)
- Agregaciones MongoDB optimizadas
- Carga incremental de datos
- Responsive design

### UX/UI
- Interfaz intuitiva y moderna
- Filtros con contadores en tiempo real
- Ordenación flexible
- Estados visuales con códigos de color
- Tooltips informativos en gráficos

## 🐛 Solución de Problemas

### Problemas Comunes

**Caracteres mal codificados**
```bash
# Restaurar desde backup limpio
node restore-database.js
```

**MongoDB no conecta**
```bash
# Verificar servicio MongoDB
brew services start mongodb-community
# o
sudo systemctl start mongod
```

**Dependencias faltantes**
```bash
npm install
```

## 🤝 Contribución

1. Fork del proyecto
2. Crear rama feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit cambios (`git commit -am 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crear Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - ver archivo `LICENSE` para detalles.

## 📞 Soporte

Para problemas o preguntas:
- Revisar la documentación en `/docs`
- Crear issue en GitHub
- Consultar `deployment-guide.md` para despliegue

---

**Desarrollado con ❤️ para el análisis de fundaciones españolas**