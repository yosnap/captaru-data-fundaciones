import pymongo
from pymongo import MongoClient
import pandas as pd
import json
import os
from datetime import datetime
from dotenv import load_dotenv
import requests
from io import BytesIO

# Load environment variables
load_dotenv()

def download_excel_from_url(url):
    """Download Excel file from URL"""
    print(f"📥 Descargando archivo Excel desde URL...")
    response = requests.get(url)
    if response.status_code == 200:
        return BytesIO(response.content)
    else:
        raise Exception(f"Error al descargar archivo: {response.status_code}")

def load_excel_data(excel_source):
    """Load data from Excel file or URL"""
    print("📖 Leyendo archivo Excel...")
    
    # Si es una URL, descargar primero
    if isinstance(excel_source, str) and excel_source.startswith('http'):
        excel_file = download_excel_from_url(excel_source)
    else:
        excel_file = excel_source
    
    df = pd.read_excel(excel_file, sheet_name=0)
    print(f"✅ Datos cargados: {len(df)} filas, {len(df.columns)} columnas")
    return df

def clean_text(text):
    """Clean text with proper encoding"""
    if pd.isna(text):
        return None
    if not isinstance(text, str):
        return str(text)
    
    # Diccionario de reemplazos de caracteres mal codificados
    replacements = {
        'Ã³': 'ó', 'Ã¡': 'á', 'Ã©': 'é', 'Ã­': 'í', 'Ãº': 'ú', 'Ã±': 'ñ',
        'Ã'': 'Ñ', 'Ã': 'Á', 'Ã‰': 'É', 'Ã': 'Í', 'Ã"': 'Ó', 'Ãš': 'Ú',
        'Â¡': '¡', 'Â¿': '¿', 'Âº': 'º', 'Âª': 'ª',
        'â€œ': '"', 'â€': '"', 'â€™': "'", 'â€"': '–', 'â€"': '—',
        'â‚¬': '€', 'Â°': '°',
        '&#xD;': '\n', '&#xA;': '\n', '&#x20;': ' ',
        '3Âº': '3º', '1Âª': '1ª', '2Âº': '2º', '4Âº': '4º',
        'MEDITERRÃNEO': 'MEDITERRÁNEO',
        'BRITÃNICA': 'BRITÁNICA',
        'InvestigaciÃ³n': 'Investigación',
        'FundaciÃ³n': 'Fundación',
        'EducaciÃ³n': 'Educación',
        'TecnolÃ³gica': 'Tecnológica',
        'ColaboraciÃ³n': 'Colaboración'
    }
    
    # Aplicar reemplazos
    result = text
    for old, new in replacements.items():
        result = result.replace(old, new)
    
    # Limpiar espacios múltiples
    result = ' '.join(result.split())
    
    # Eliminar caracteres invisibles Unicode
    invisible_chars = [8220, 8216, 61837]
    for char_code in invisible_chars:
        result = result.replace(chr(char_code), '')
    
    return result.strip()

def normalize_activity_name(name):
    """Normalize activity names"""
    if not isinstance(name, str):
        return name
    
    # Remove trailing periods and extra spaces
    normalized = name.strip().rstrip('.')
    
    # Standardize common activities
    activity_map = {
        'SANIDAD': 'Sanidad',
        'CULTURA': 'Cultura', 
        'EDUCACION': 'Educación',
        'INVESTIGACION': 'Investigación',
        'SERVICIOS SOCIALES': 'Servicios Sociales',
        'DEPORTE': 'Deporte'
    }
    
    normalized_upper = normalized.upper()
    if normalized_upper in activity_map:
        return activity_map[normalized_upper]
    
    return normalized.title()

def convert_to_mongodb_document(row):
    """Convert DataFrame row to MongoDB document with fixed encoding"""
    doc = {
        '_id': int(row['Nº Hoja Registral']),
        'nombre': clean_text(row['Denominación']),
        'numRegistro': str(row['Número de Registro']),
        'estado': clean_text(row['Estado']),
        'fechaConstitucion': str(row['Fecha de Constitución']) if pd.notna(row['Fecha de Constitución']) else None,
        'fechaInscripcion': str(row['Fecha de Inscripción']) if pd.notna(row['Fecha de Inscripción']) else None,
        'fines': clean_text(row['Fines']),
        'nif': str(row['N.I.F.']) if pd.notna(row['N.I.F.']) else None
    }
    
    # Dirección estatutaria
    doc['direccionEstatutaria'] = {
        'domicilio': clean_text(row['Domicilio']),
        'provincia': clean_text(row['Provincia']),
        'codigoPostal': int(row['Código Postal']) if pd.notna(row['Código Postal']) else None,
        'telefono': str(row['Teléfono']) if pd.notna(row['Teléfono']) else None,
        'email': clean_text(row['E-mail']),
        'web': clean_text(row['Web'])
    }
    
    # Dirección de notificación
    doc['direccionNotificacion'] = {
        'domicilio': clean_text(row['Domicilio (a efectos de notificación)']),
        'provincia': clean_text(row['Provincia (a efectos de notificación)']),
        'localidad': clean_text(row['Localidad (a efectos de notificación)']),
        'codigoPostal': int(row['Código Postal (a efectos de notificación)']) if pd.notna(row['Código Postal (a efectos de notificación)']) else None
    }
    
    # Actividades
    actividades = []
    for i in range(1, 6):
        if pd.notna(row[f'Actividad {i}']):
            actividad = {
                'nombre': clean_text(row[f'Actividad {i}']),
                'clasificacion1': normalize_activity_name(clean_text(row[f'Clasificación {i}.1'])),
                'clasificacion2': clean_text(row[f'Clasificación {i}.2']),
                'funcion1': clean_text(row[f'Función {i}.1'])
            }
            actividades.append(actividad)
    doc['actividades'] = actividades
    
    # Fundadores
    fundadores = []
    for i in range(1, 16):
        if pd.notna(row[f'Fundador {i}']):
            fundadores.append({'nombre': clean_text(row[f'Fundador {i}'])})
    doc['fundadores'] = fundadores
    
    # Patronos
    patronos = []
    for i in range(1, 23):
        if pd.notna(row[f'Patrono {i}']):
            patrono = {'nombre': clean_text(row[f'Patrono {i}'])}
            if pd.notna(row.get(f'Cargo Patrono {i}')):
                patrono['cargo'] = clean_text(row[f'Cargo Patrono {i}'])
            patronos.append(patrono)
    doc['patronos'] = patronos
    
    # Directivos
    directivos = []
    for i in range(1, 6):
        if pd.notna(row[f'Nombre y Apellidos {i}']):
            directivo = {
                'nombre': clean_text(row[f'Nombre y Apellidos {i}']),
                'cargo': clean_text(row[f'Cargo {i}'])
            }
            directivos.append(directivo)
    doc['directivos'] = directivos
    
    # Órganos
    organos = []
    for i in range(1, 6):
        if pd.notna(row[f'Órgano de Representación {i}']):
            organos.append({'nombre': clean_text(row[f'Órgano de Representación {i}'])})
    doc['organos'] = organos
    
    return doc

def migrate_to_mongodb(excel_source, connection_string=None):
    """Main migration function"""
    try:
        # Use provided connection string or default
        mongo_uri = connection_string or os.getenv('MONGODB_URI', 'mongodb://localhost:27017')
        
        # Load data
        df = load_excel_data(excel_source)
        
        # Connect to MongoDB
        print(f"🔌 Conectando a MongoDB...")
        client = MongoClient(mongo_uri)
        db = client['fundaciones_espana']
        collection = db.fundaciones
        
        # Clear existing data
        print("🗑️  Limpiando colección existente...")
        collection.delete_many({})
        
        # Convert and insert documents
        print("💾 Migrando datos...")
        documents = []
        for idx, row in df.iterrows():
            doc = convert_to_mongodb_document(row)
            documents.append(doc)
            
            if len(documents) >= 100:
                collection.insert_many(documents)
                documents = []
                print(f"  Procesados {idx + 1} documentos...")
        
        # Insert remaining documents
        if documents:
            collection.insert_many(documents)
        
        # Create indexes
        print("📇 Creando índices...")
        collection.create_index('nombre')
        collection.create_index('estado')
        collection.create_index('nif')
        collection.create_index('direccionEstatutaria.provincia')
        collection.create_index('actividades.clasificacion1')
        
        # Verify migration
        total_docs = collection.count_documents({})
        print(f"\n✅ Migración completada!")
        print(f"📊 Total de documentos: {total_docs}")
        
        # Show sample stats
        estados = collection.distinct('estado')
        provincias = collection.distinct('direccionEstatutaria.provincia')
        print(f"📈 Estados únicos: {len(estados)}")
        print(f"📍 Provincias únicas: {len(provincias)}")
        
        # Sample document
        sample = collection.find_one()
        print(f"\n📄 Documento de muestra:")
        print(f"  Nombre: {sample['nombre']}")
        print(f"  Estado: {sample['estado']}")
        print(f"  Provincia: {sample.get('direccionEstatutaria', {}).get('provincia', 'N/A')}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error durante la migración: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Script de Migración y Restauración para Producción")
    print("=" * 50)
    
    # Opciones de fuente de datos
    print("\n📥 Opciones de fuente de datos:")
    print("1. Archivo Excel local")
    print("2. URL de descarga (Google Drive, Dropbox, etc.)")
    print("3. Usar archivo por defecto")
    
    choice = input("\nSeleccione opción (1-3): ").strip()
    
    if choice == '1':
        excel_path = input("Ruta del archivo Excel: ").strip()
        excel_source = excel_path
    elif choice == '2':
        excel_url = input("URL del archivo Excel: ").strip()
        excel_source = excel_url
    else:
        # Archivo por defecto
        excel_source = 'BBDD de fundaciones España actualizada 040724.xls'
    
    # Solicitar connection string (opcional)
    print("\n🔌 Configuración de MongoDB:")
    print("Dejar vacío para usar MONGODB_URI del entorno o localhost")
    connection_string = input("Connection string (opcional): ").strip()
    
    if not connection_string:
        connection_string = None
    
    # Ejecutar migración
    print(f"\n🚀 Iniciando migración...")
    success = migrate_to_mongodb(excel_source, connection_string)
    
    if success:
        print("\n✨ ¡Migración completada exitosamente!")
        print("La base de datos está lista para usar con la aplicación.")
    else:
        print("\n❌ La migración falló. Revise los errores arriba.")