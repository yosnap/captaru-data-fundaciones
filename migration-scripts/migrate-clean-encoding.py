import pandas as pd
import pymongo
from pymongo import MongoClient
import json
from datetime import datetime
import os
from dotenv import load_dotenv
import sys
import codecs

load_dotenv()

def clean_text(text):
    """Clean and fix encoding issues in text"""
    if not isinstance(text, str) or pd.isna(text):
        return None
    
    # Try to fix common encoding issues by decoding and re-encoding
    try:
        # First, try to decode as latin-1 and then encode as utf-8
        if 'Ã' in text:
            # This suggests UTF-8 bytes were decoded as latin-1
            fixed = text.encode('latin-1').decode('utf-8')
            return fixed
    except (UnicodeDecodeError, UnicodeEncodeError):
        pass
    
    # If that doesn't work, clean up manually
    text = text.replace('Ã¡', 'á')
    text = text.replace('Ã©', 'é') 
    text = text.replace('Ã­', 'í')
    text = text.replace('Ã³', 'ó')
    text = text.replace('Ãº', 'ú')
    text = text.replace('Ã±', 'ñ')
    text = text.replace('Ã"', 'Ó')
    text = text.replace('Ã‰', 'É')
    text = text.replace('Ã', 'Á')
    
    return text.strip() if text else None

def restructure_foundation_data(row):
    """Restructure flat Excel data into nested MongoDB document with clean encoding"""
    foundation = {
        '_id': int(row['@_idfundacion']),
        'nombre': clean_text(row.get('Nombre')),
        'numRegistro': clean_text(row.get('NumRegistro')),
        'fechaConstitucion': row.get('FechaConstitucion') if pd.notna(row.get('FechaConstitucion')) else None,
        'fechaInscripcion': row.get('FechaInscripcion') if pd.notna(row.get('FechaInscripcion')) else None,
        'nif': row.get('NIFFundacion') if pd.notna(row.get('NIFFundacion')) else None,
        'fechaExtincion': row.get('FechaExtincion') if pd.notna(row.get('FechaExtincion')) else None,
        'estado': clean_text(row.get('EstadoFundacion')),
        'fines': clean_text(row.get('Fines')),
        
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
            'domicilio': clean_text(row.get('DireccionEstatutaria/DireccionEstatutaria/Domicilio')),
            'codigoPostal': int(row.get('DireccionEstatutaria/DireccionEstatutaria/CodigoPostal')) if pd.notna(row.get('DireccionEstatutaria/DireccionEstatutaria/CodigoPostal')) else None,
            'provincia': clean_text(row.get('DireccionEstatutaria/DireccionEstatutaria/Provincia')),
            'telefono': str(int(row.get('DireccionEstatutaria/DireccionEstatutaria/Telefono'))) if pd.notna(row.get('DireccionEstatutaria/DireccionEstatutaria/Telefono')) else None,
            'fax': str(int(row.get('DireccionEstatutaria/DireccionEstatutaria/Fax'))) if pd.notna(row.get('DireccionEstatutaria/DireccionEstatutaria/Fax')) else None,
            'email': row.get('DireccionEstatutaria/DireccionEstatutaria/CorreoElectronico') if pd.notna(row.get('DireccionEstatutaria/DireccionEstatutaria/CorreoElectronico')) else None,
            'web': row.get('DireccionEstatutaria/DireccionEstatutaria/Web') if pd.notna(row.get('DireccionEstatutaria/DireccionEstatutaria/Web')) else None
        }
    
    # Dirección Notificación
    if pd.notna(row.get('DireccionNotificacion/DireccionNotificacion/Domicilio')):
        foundation['direccionNotificacion'] = {
            'domicilio': clean_text(row.get('DireccionNotificacion/DireccionNotificacion/Domicilio')),
            'localidad': clean_text(row.get('DireccionNotificacion/DireccionNotificacion/Localidad')),
            'codigoPostal': int(row.get('DireccionNotificacion/DireccionNotificacion/CodigoPostal')) if pd.notna(row.get('DireccionNotificacion/DireccionNotificacion/CodigoPostal')) else None,
            'provincia': clean_text(row.get('DireccionNotificacion/DireccionNotificacion/Provincia'))
        }
    
    # Actividades (check both single and array formats)
    if pd.notna(row.get('Actividades/Actividades/NombreActividad')):
        foundation['actividades'].append({
            'nombre': clean_text(row.get('Actividades/Actividades/NombreActividad')),
            'clasificacion1': clean_text(row.get('Actividades/Actividades/Clasificacion1')),
            'clasificacion2': clean_text(row.get('Actividades/Actividades/Clasificacion2')),
            'clasificacion3': clean_text(row.get('Actividades/Actividades/Clasificacion3')),
            'clasificacion4': clean_text(row.get('Actividades/Actividades/Clasificacion4')),
            'funcion1': clean_text(row.get('Actividades/Actividades/Funcion1')),
            'funcion2': clean_text(row.get('Actividades/Actividades/Funcion2'))
        })
    
    # Add array activities (0, 1, 2, 3)
    for i in range(4):
        if pd.notna(row.get(f'Actividades/Actividades/{i}/NombreActividad')):
            foundation['actividades'].append({
                'nombre': clean_text(row.get(f'Actividades/Actividades/{i}/NombreActividad')),
                'clasificacion1': clean_text(row.get(f'Actividades/Actividades/{i}/Clasificacion1')),
                'clasificacion2': clean_text(row.get(f'Actividades/Actividades/{i}/Clasificacion2')),
                'clasificacion3': clean_text(row.get(f'Actividades/Actividades/{i}/Clasificacion3')),
                'clasificacion4': clean_text(row.get(f'Actividades/Actividades/{i}/Clasificacion4')),
                'funcion1': clean_text(row.get(f'Actividades/Actividades/{i}/Funcion1')),
                'funcion2': clean_text(row.get(f'Actividades/Actividades/{i}/Funcion2'))
            })
    
    # Fundadores (up to 30)
    for i in range(30):
        if pd.notna(row.get(f'Fundadores/Fundador/{i}/NombreFundador')):
            foundation['fundadores'].append({
                'nombre': clean_text(row.get(f'Fundadores/Fundador/{i}/NombreFundador'))
            })
    
    # Patronos (up to 31)
    for i in range(31):
        if pd.notna(row.get(f'Patronos/Patron/{i}/NombrePatron')):
            foundation['patronos'].append({
                'nombre': clean_text(row.get(f'Patronos/Patron/{i}/NombrePatron')),
                'cargo': clean_text(row.get(f'Patronos/Patron/{i}/CargoPatron'))
            })
    
    # Directivos (up to 12)
    for i in range(12):
        if pd.notna(row.get(f'Directivos/Directivo/{i}/NombreDirectivo')):
            foundation['directivos'].append({
                'nombre': clean_text(row.get(f'Directivos/Directivo/{i}/NombreDirectivo')),
                'cargo': clean_text(row.get(f'Directivos/Directivo/{i}/CargoDirectivo'))
            })
    
    # Órganos
    if pd.notna(row.get('Organos/Organo/NombreOrgano')):
        foundation['organos'].append({
            'nombre': clean_text(row.get('Organos/Organo/NombreOrgano'))
        })
    
    # Add array organs (0, 1, 2)
    for i in range(3):
        if pd.notna(row.get(f'Organos/Organo/{i}/NombreOrgano')):
            foundation['organos'].append({
                'nombre': clean_text(row.get(f'Organos/Organo/{i}/NombreOrgano'))
            })
    
    # Add metadata
    foundation['metadata'] = {
        'fechaActualizacion': datetime.now(),
        'fuenteDatos': 'BBDD de fundaciones España actualizada 040724.xls',
        'encodingFixed': True,
        'cleanImport': True
    }
    
    return foundation

def migrate_excel_to_mongodb_clean():
    """Main migration function with clean encoding"""
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
        
        # Read Excel file
        print("📖 Reading Excel file with proper encoding handling...")
        file_path = "/Users/paulo/Documents/Proyectos/Trabajo/Captaru/Datos Subvenciones/BBDD de fundaciones España actualizada 040724.xls"
        
        # Read Excel file - try different approaches
        try:
            df = pd.read_excel(file_path, engine='xlrd')
            print(f"✅ Successfully read Excel with xlrd engine")
        except Exception as e:
            print(f"❌ Failed with xlrd: {e}")
            try:
                df = pd.read_excel(file_path, engine='openpyxl')
                print(f"✅ Successfully read Excel with openpyxl engine")
            except Exception as e2:
                print(f"❌ Failed with openpyxl: {e2}")
                return
        
        print(f"📊 Found {len(df)} foundations to migrate with clean encoding")
        
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
                    print(f"✅ Inserted {len(documents)} documents with clean encoding (total: {index + 1}/{len(df)})")
                    documents = []
                    
            except Exception as e:
                errors.append({
                    'index': index,
                    'id': row.get('@_idfundacion', 'unknown'),
                    'error': str(e)
                })
                print(f"❌ Error processing row {index}: {e}")
        
        # Insert remaining documents
        if documents:
            collection.insert_many(documents)
            print(f"✅ Inserted final {len(documents)} documents with clean encoding")
        
        # Create indexes
        print("\n🔧 Creating indexes...")
        collection.create_index('nombre')
        collection.create_index('nif')
        collection.create_index('estado')
        collection.create_index('direccionEstatutaria.provincia')
        collection.create_index([('nombre', pymongo.TEXT), ('fines', pymongo.TEXT)])
        
        # Summary
        total_docs = collection.count_documents({})
        print(f"\n✅ Clean migration complete!")
        print(f"📊 Total documents in MongoDB: {total_docs}")
        print(f"❌ Errors encountered: {len(errors)}")
        
        if errors:
            with open('migration-scripts/migration_errors_clean.json', 'w', encoding='utf-8') as f:
                json.dump(errors, f, indent=2, ensure_ascii=False)
            print("⚠️  Error details saved to migration_errors_clean.json")
        
        # Sample query to verify clean encoding
        sample = collection.find_one({'nombre': {'$regex': 'FUNDACI'}})
        if sample:
            print(f"\n📄 Sample document with clean encoding:")
            print(f"ID: {sample['_id']}")
            print(f"Nombre: {sample['nombre']}")
            print(f"Estado: {sample['estado']}")
            if sample.get('direccionEstatutaria'):
                print(f"Provincia: {sample['direccionEstatutaria'].get('provincia')}")
            
            # Test a patron name if available
            if sample.get('patronos') and len(sample['patronos']) > 0:
                print(f"Primer Patrono: {sample['patronos'][0]['nombre']}")
        
    except Exception as e:
        print(f"❌ Fatal error during clean migration: {e}")
        sys.exit(1)

if __name__ == "__main__":
    print("🚀 Starting clean Excel to MongoDB migration...")
    migrate_excel_to_mongodb_clean()