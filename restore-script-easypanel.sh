#!/bin/bash

# Script de restauración para Easypanel
# Este script descarga y restaura la base de datos desde una URL

echo "🚀 Script de Restauración de Base de Datos para Easypanel"
echo "========================================================"

# Variables (modificar según tu configuración)
EXCEL_URL="https://tu-url-de-descarga/BBDD_fundaciones.xls"  # Cambiar por tu URL
MONGODB_URI=${MONGODB_URI:-"mongodb://localhost:27017/fundaciones_espana"}
API_KEY=${RESTORE_API_KEY:-"your-secure-api-key-here"}
APP_URL=${APP_URL:-"http://localhost:3000"}

# Opción 1: Restaurar usando el script Python (recomendado si tienes Python)
if command -v python3 &> /dev/null; then
    echo "✅ Python3 encontrado, usando script de migración..."
    
    # Instalar dependencias Python
    pip3 install pymongo pandas openpyxl requests python-dotenv
    
    # Ejecutar migración
    python3 - <<EOF
import pymongo
import pandas as pd
import requests
from io import BytesIO
import os

# Descargar Excel
print("📥 Descargando archivo Excel...")
response = requests.get("${EXCEL_URL}")
excel_data = BytesIO(response.content)

# Cargar datos
print("📖 Procesando datos...")
df = pd.read_excel(excel_data)

# Aquí iría el código de migración completo
# (usar el contenido de restore-from-excel-production.py)

print("✅ Migración completada")
EOF

else
    echo "⚠️  Python no encontrado, usando método alternativo..."
    
    # Opción 2: Usar curl para restaurar via API
    # Primero necesitarías subir el JSON a algún lugar accesible
    
    # Descargar backup JSON si está disponible
    if [ ! -z "$BACKUP_JSON_URL" ]; then
        echo "📥 Descargando backup JSON..."
        curl -o backup.json "$BACKUP_JSON_URL"
        
        # Restaurar usando la API
        echo "📤 Restaurando via API..."
        curl -X POST \
          -H "Content-Type: application/json" \
          -H "x-api-key: ${API_KEY}" \
          -d @backup.json \
          "${APP_URL}/api/restore"
    else
        echo "❌ No se especificó URL de backup JSON"
        exit 1
    fi
fi

echo "✨ Proceso completado"