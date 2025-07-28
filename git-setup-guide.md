# 📚 Guía de Configuración Git - Fundaciones Frontend

## ✅ Archivos QUE SÍ Incluir en Git

### 📂 Código Fuente (ESENCIAL)
```
fundaciones-frontend/
├── src/                     # Código fuente completo
├── public/                  # Assets públicos
├── package.json            # Dependencias
├── package-lock.json       # Lock de dependencias
├── tsconfig.json           # Configuración TypeScript
├── next.config.ts          # Configuración Next.js
├── tailwind.config.ts      # Configuración Tailwind
├── postcss.config.mjs      # Configuración PostCSS
├── Dockerfile              # Imagen Docker
└── README.md               # Documentación del frontend
```

### 📋 Scripts y Configuración
```
migration-scripts/          # Scripts de migración (SIN datos)
├── migrate-to-mongodb.py   # Script de migración base
├── fix-encoding-*.py       # Scripts de corrección
├── normalize-activities.py # Normalización de datos
└── requirements.txt        # Dependencias Python
```

### 🚀 Despliegue y Documentación
```
README.md                   # Documentación principal
.env.example               # Plantilla de variables
.gitignore                 # Este archivo
docker-compose.yml         # Configuración Docker
deployment-guide.md        # Guía de despliegue
easypanel-setup.md        # Guía específica Easypanel
git-setup-guide.md        # Esta guía
restore-database.js       # Script de restauración (SIN datos)
```

## ❌ Archivos QUE NO Incluir en Git

### 🔒 Secretos y Configuración Local
```
.env                       # Variables de entorno REALES
.env.local                # Configuración local
.env.production           # Configuración de producción
```

### 💾 Datos y Backups (MUY IMPORTANTE)
```
database-backup.json      # 20MB - Backup completo BD
*.xls, *.xlsx             # Archivos Excel originales
excel_analysis.json       # Análisis de Excel
*.dump, *.sql             # Otros backups de BD
```

### 🗂️ Archivos Generados y Temporales
```
fundaciones-frontend/
├── node_modules/         # Dependencias (se instalan con npm)
├── .next/               # Build de Next.js
├── out/                 # Export estático
├── build/               # Build de producción
├── coverage/            # Reportes de testing
└── .vercel              # Configuración Vercel

# Python
venv/                    # Entorno virtual Python
__pycache__/            # Cache de Python
*.pyc                   # Bytecode Python

# Sistema
.DS_Store               # macOS
Thumbs.db              # Windows
*.log                  # Logs
*.tmp, *.temp          # Archivos temporales
```

## 🛠️ Comandos para Inicializar Git

### 1. Inicializar Repositorio
```bash
cd "/Users/paulo/Documents/Proyectos/Trabajo/Captaru/Datos Subvenciones"
git init
```

### 2. Configurar Usuario (si es necesario)
```bash
git config user.name "Tu Nombre"
git config user.email "tu@email.com"
```

### 3. Agregar Archivos
```bash
# Agregar archivos importantes
git add README.md
git add .gitignore
git add .env.example
git add docker-compose.yml
git add *-guide.md
git add restore-database.js
git add fundaciones-frontend/
git add migration-scripts/

# Verificar qué se va a commitear
git status
```

### 4. Primer Commit
```bash
git commit -m "Initial commit: Fundaciones Frontend

- Next.js 15 frontend with MongoDB integration
- Complete CRUD operations for Spanish foundations
- Analytics with interactive charts
- Advanced filtering and search
- Responsive design with Tailwind CSS
- Docker support for deployment
- Migration scripts for data processing
- Deployment guides for Easypanel"
```

### 5. Conectar con Repositorio Remoto
```bash
# Agregar repositorio remoto
git remote add origin https://github.com/tu-usuario/fundaciones-frontend.git

# Subir código
git branch -M main
git push -u origin main
```

## ⚠️ IMPORTANTE: Datos Sensibles

### 🚫 NUNCA Subir a Git:
- `database-backup.json` (20MB con datos reales)
- Archivos `.env` con credenciales
- Archivos Excel originales
- Cualquier backup de base de datos

### ✅ Alternativas para Datos:
1. **Para desarrollo**: Usar `restore-database.js` con backup local
2. **Para producción**: Restaurar desde backup en servidor
3. **Para colaboradores**: Compartir `database-backup.json` por separado (Dropbox, Drive, etc.)

## 📋 Checklist Pre-Commit

- [ ] ✅ `.gitignore` configurado correctamente
- [ ] ✅ `.env` no incluido en commit
- [ ] ✅ `database-backup.json` no incluido
- [ ] ✅ `node_modules/` excluido
- [ ] ✅ Archivos Excel excluidos  
- [ ] ✅ Solo código fuente y configuración incluidos
- [ ] ✅ README.md actualizado
- [ ] ✅ Variables sensibles en `.env.example` como placeholders

## 🔄 Workflow Recomendado

### Para nuevas características:
```bash
git checkout -b feature/nueva-funcionalidad
# Hacer cambios
git add .
git commit -m "Add: nueva funcionalidad"
git push origin feature/nueva-funcionalidad
# Crear Pull Request
```

### Para fixes:
```bash
git checkout -b fix/nombre-del-bug
# Hacer cambios
git add .
git commit -m "Fix: descripción del fix"
git push origin fix/nombre-del-bug
```

### Para releases:
```bash
git checkout main
git tag -a v1.0.0 -m "Release v1.0.0: Initial production release"
git push origin v1.0.0
```

## 💡 Consejos

1. **Commits frecuentes**: Hacer commits pequeños y descriptivos
2. **Branches**: Usar branches para cada feature/fix
3. **Mensajes claros**: Escribir mensajes de commit descriptivos
4. **Revisar cambios**: Usar `git diff` antes de commit
5. **Mantener .gitignore**: Actualizar según necesidades

---

**Con esta configuración tu repositorio será limpio, seguro y fácil de desplegar! 🚀**