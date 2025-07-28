import pandas as pd
import pymongo
from pymongo import MongoClient
import json
from datetime import datetime
import os
from dotenv import load_dotenv
import sys
import html

load_dotenv()

def fix_encoding(text):
    """Fix encoding issues in text"""
    if not isinstance(text, str):
        return text
    
    # Common encoding fixes
    fixes = {
        'Ã¡': 'á', 'Ã©': 'é', 'Ã­': 'í', 'Ã³': 'ó', 'Ãº': 'ú',
        'Ã ': 'à', 'Ã¨': 'è', 'Ã¬': 'ì', 'Ã²': 'ò', 'Ã¹': 'ù',
        'Ã¢': 'â', 'Ãª': 'ê', 'Ã®': 'î', 'Ã´': 'ô', 'Ã»': 'û',
        'Ã': 'Á', 'Ã‰': 'É', 'ÃÃ': 'Í', 'Ã"': 'Ó', 'Ãš': 'Ú',
        'Ã€': 'À', 'Ãˆ': 'È', 'ÃŒ': 'Ì', 'Ã™': 'Ù',
        'Ã‚': 'Â', 'ÃŠ': 'Ê', 'ÃŽ': 'Î', 'Ã"': 'Ô', 'Ã›': 'Û',
        'Ã±': 'ñ', 'Ã'': 'Ñ',
        'Ã§': 'ç', 'Ã‡': 'Ç',
        'Ã¼': 'ü', 'Ãœ': 'Ü',
        'Ã¤': 'ä', 'Ã„': 'Ä',
        'Ã¶': 'ö', 'Ã–': 'Ö',
        'Ã"N': 'ÓN', 'Ã³n': 'ón'
    }
    
    result = text
    for wrong, correct in fixes.items():
        result = result.replace(wrong, correct)
    
    return result

def clean_data_for_mongodb(data):
    """Clean data for MongoDB insertion"""
    cleaned = {}
    for key, value in data.items():
        # Clean column names (remove special characters, use nested structure)
        clean_key = key.replace('/', '_').replace('@', '').replace(' ', '_')
        
        # Handle NaN values
        if pd.isna(value):
            value = None
        elif isinstance(value, float) and value.is_integer():
            value = int(value)
        elif isinstance(value, str):
            value = fix_encoding(value)
            
        cleaned[clean_key] = value
    return cleaned

def restructure_foundation_data(row):
    """Restructure flat Excel data into nested MongoDB document"""
    foundation = {
        '_id': int(row['@_idfundacion']),
        'nombre': fix_encoding(row['Nombre']) if pd.notna(row['Nombre']) else None,
        'numRegistro': fix_encoding(row['NumRegistro']) if pd.notna(row['NumRegistro']) else None,
        'fechaConstitucion': row['FechaConstitucion'] if pd.notna(row['FechaConstitucion']) else None,
        'fechaInscripcion': row['FechaInscripcion'] if pd.notna(row['FechaInscripcion']) else None,
        'nif': row['NIFFundacion'] if pd.notna(row['NIFFundacion']) else None,
        'fechaExtincion': row['FechaExtincion'] if pd.notna(row['FechaExtincion']) else None,
        'estado': fix_encoding(row['EstadoFundacion']) if pd.notna(row['EstadoFundacion']) else None,
        'fines': fix_encoding(row['Fines']) if pd.notna(row['Fines']) else None,
        
        # Direcciones
        'direccionEstatutaria': None,
        'direccionNotificacion': None,
        
        # Arrays
        'actividades': [],
        'fundadores': [],
        'patronos': [],
        'directivos': [],
        'organos': []
    }
    
    # Dirección Estatutaria
    if pd.notna(row.get('DireccionEstatutaria/DireccionEstatutaria/Domicilio')):
        foundation['direccionEstatutaria'] = {
            'domicilio': fix_encoding(row.get('DireccionEstatutaria/DireccionEstatutaria/Domicilio')),
            'codigoPostal': int(row.get('DireccionEstatutaria/DireccionEstatutaria/CodigoPostal')) if pd.notna(row.get('DireccionEstatutaria/DireccionEstatutaria/CodigoPostal')) else None,
            'provincia': fix_encoding(row.get('DireccionEstatutaria/DireccionEstatutaria/Provincia')),
            'telefono': str(int(row.get('DireccionEstatutaria/DireccionEstatutaria/Telefono'))) if pd.notna(row.get('DireccionEstatutaria/DireccionEstatutaria/Telefono')) else None,
            'fax': str(int(row.get('DireccionEstatutaria/DireccionEstatutaria/Fax'))) if pd.notna(row.get('DireccionEstatutaria/DireccionEstatutaria/Fax')) else None,
            'email': row.get('DireccionEstatutaria/DireccionEstatutaria/CorreoElectronico'),
            'web': row.get('DireccionEstatutaria/DireccionEstatutaria/Web')
        }
    
    # Dirección Notificación
    if pd.notna(row.get('DireccionNotificacion/DireccionNotificacion/Domicilio')):
        foundation['direccionNotificacion'] = {
            'domicilio': fix_encoding(row.get('DireccionNotificacion/DireccionNotificacion/Domicilio')),
            'localidad': fix_encoding(row.get('DireccionNotificacion/DireccionNotificacion/Localidad')),
            'codigoPostal': int(row.get('DireccionNotificacion/DireccionNotificacion/CodigoPostal')) if pd.notna(row.get('DireccionNotificacion/DireccionNotificacion/CodigoPostal')) else None,
            'provincia': fix_encoding(row.get('DireccionNotificacion/DireccionNotificacion/Provincia'))
        }
    
    # Actividades (check both single and array formats)
    if pd.notna(row.get('Actividades/Actividades/NombreActividad')):
        foundation['actividades'].append({
            'nombre': fix_encoding(row.get('Actividades/Actividades/NombreActividad')),
            'clasificacion1': fix_encoding(row.get('Actividades/Actividades/Clasificacion1')),
            'clasificacion2': fix_encoding(row.get('Actividades/Actividades/Clasificacion2')),
            'clasificacion3': fix_encoding(row.get('Actividades/Actividades/Clasificacion3')),
            'clasificacion4': fix_encoding(row.get('Actividades/Actividades/Clasificacion4')),
            'funcion1': fix_encoding(row.get('Actividades/Actividades/Funcion1')),
            'funcion2': fix_encoding(row.get('Actividades/Actividades/Funcion2'))
        })
    
    # Add array activities (0, 1, 2, 3)
    for i in range(4):
        if pd.notna(row.get(f'Actividades/Actividades/{i}/NombreActividad')):
            foundation['actividades'].append({
                'nombre': fix_encoding(row.get(f'Actividades/Actividades/{i}/NombreActividad')),
                'clasificacion1': fix_encoding(row.get(f'Actividades/Actividades/{i}/Clasificacion1')),
                'clasificacion2': fix_encoding(row.get(f'Actividades/Actividades/{i}/Clasificacion2')),
                'clasificacion3': fix_encoding(row.get(f'Actividades/Actividades/{i}/Clasificacion3')),
                'clasificacion4': fix_encoding(row.get(f'Actividades/Actividades/{i}/Clasificacion4')),
                'funcion1': fix_encoding(row.get(f'Actividades/Actividades/{i}/Funcion1')),
                'funcion2': fix_encoding(row.get(f'Actividades/Actividades/{i}/Funcion2'))
            })
    
    # Fundadores (up to 30)
    for i in range(30):
        if pd.notna(row.get(f'Fundadores/Fundador/{i}/NombreFundador')):
            foundation['fundadores'].append({
                'nombre': fix_encoding(row.get(f'Fundadores/Fundador/{i}/NombreFundador'))
            })
    
    # Patronos (up to 31)
    for i in range(31):
        if pd.notna(row.get(f'Patronos/Patron/{i}/NombrePatron')):
            foundation['patronos'].append({
                'nombre': fix_encoding(row.get(f'Patronos/Patron/{i}/NombrePatron')),
                'cargo': fix_encoding(row.get(f'Patronos/Patron/{i}/CargoPatron'))
            })
    
    # Directivos (up to 12)
    for i in range(12):
        if pd.notna(row.get(f'Directivos/Directivo/{i}/NombreDirectivo')):
            foundation['directivos'].append({
                'nombre': fix_encoding(row.get(f'Directivos/Directivo/{i}/NombreDirectivo')),
                'cargo': fix_encoding(row.get(f'Directivos/Directivo/{i}/CargoDirectivo'))
            })
    
    # Órganos
    if pd.notna(row.get('Organos/Organo/NombreOrgano')):
        foundation['organos'].append({
            'nombre': fix_encoding(row.get('Organos/Organo/NombreOrgano'))
        })
    
    # Add array organs (0, 1, 2)
    for i in range(3):
        if pd.notna(row.get(f'Organos/Organo/{i}/NombreOrgano')):
            foundation['organos'].append({
                'nombre': fix_encoding(row.get(f'Organos/Organo/{i}/NombreOrgano'))
            })
    
    # Add metadata
    foundation['metadata'] = {
        'fechaActualizacion': datetime.now(),
        'fuenteDatos': 'BBDD de fundaciones España actualizada 040724.xls',
        'encodingFixed': True
    }
    
    return foundation

def migrate_excel_to_mongodb():
    """Main migration function"""
    try:
        # MongoDB connection
        mongodb_uri = os.getenv('MONGODB_URI', 'mongodb://localhost:27017')
        client = MongoClient(mongodb_uri)
        db_name = os.getenv('MONGODB_DB_NAME', 'fundaciones_espana')
        db = client[db_name]
        
        # Drop existing collection
        if 'fundaciones' in db.list_collection_names():
            print("⚠️  Dropping existing 'fundaciones' collection...")
            db.fundaciones.drop()
        
        collection = db.fundaciones
        
        # Read Excel file with different encodings
        print("📖 Reading Excel file with encoding fixes...")
        file_path = "/Users/paulo/Documents/Proyectos/Trabajo/Captaru/Datos Subvenciones/BBDD de fundaciones España actualizada 040724.xls"
        
        try:
            # Try reading with different engines and options
            df = pd.read_excel(file_path, engine='xlrd')
        except:
            try:
                df = pd.read_excel(file_path, engine='openpyxl')
            except Exception as e:
                print(f"❌ Error reading Excel file: {e}")
                return
        
        print(f"📊 Found {len(df)} foundations to migrate with encoding fixes")
        
        # Process and insert documents
        documents = []
        errors = []
        
        for index, row in df.iterrows():
            try:
                doc = restructure_foundation_data(row)
                documents.append(doc)
                
                # Insert in batches of 1000
                if len(documents) >= 1000:
                    collection.insert_many(documents)
                    print(f"✅ Inserted {len(documents)} documents with fixed encoding (total: {index + 1}/{len(df)})")
                    documents = []
                    
            except Exception as e:
                errors.append({
                    'index': index,
                    'id': row['@_idfundacion'],
                    'error': str(e)
                })
                print(f"❌ Error processing row {index}: {e}")
        
        # Insert remaining documents
        if documents:
            collection.insert_many(documents)
            print(f"✅ Inserted final {len(documents)} documents with fixed encoding")
        
        # Create indexes
        print("\n🔧 Creating indexes...")
        collection.create_index('nombre')
        collection.create_index('nif')
        collection.create_index('estado')
        collection.create_index('direccionEstatutaria.provincia')
        collection.create_index([('nombre', pymongo.TEXT), ('fines', pymongo.TEXT)])
        
        # Summary
        total_docs = collection.count_documents({})
        print(f"\n✅ Migration complete with encoding fixes!")
        print(f"📊 Total documents in MongoDB: {total_docs}")
        print(f"❌ Errors encountered: {len(errors)}")
        
        if errors:
            with open('migration-scripts/migration_errors_fixed.json', 'w', encoding='utf-8') as f:
                json.dump(errors, f, indent=2, ensure_ascii=False)
            print("⚠️  Error details saved to migration_errors_fixed.json")
        
        # Sample query to verify encoding
        sample = collection.find_one()
        print(f"\n📄 Sample document with fixed encoding:")
        print(f"Nombre: {sample['nombre']}")
        print(f"Estado: {sample['estado']}")
        if sample.get('direccionEstatutaria'):
            print(f"Provincia: {sample['direccionEstatutaria'].get('provincia')}")
        
    except Exception as e:
        print(f"❌ Fatal error during migration: {e}")
        sys.exit(1)

if __name__ == "__main__":
    print("🚀 Starting Excel to MongoDB migration with encoding fixes...")
    migrate_excel_to_mongodb()