import pandas as pd
import pymongo
from pymongo import MongoClient
import json
from datetime import datetime
import os
from dotenv import load_dotenv
import sys

load_dotenv()

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
            
        cleaned[clean_key] = value
    return cleaned

def restructure_foundation_data(row):
    """Restructure flat Excel data into nested MongoDB document"""
    foundation = {
        '_id': int(row['@_idfundacion']),
        'nombre': row['Nombre'],
        'numRegistro': row['NumRegistro'],
        'fechaConstitucion': row['FechaConstitucion'],
        'fechaInscripcion': row['FechaInscripcion'],
        'nif': row['NIFFundacion'],
        'fechaExtincion': row['FechaExtincion'] if pd.notna(row['FechaExtincion']) else None,
        'estado': row['EstadoFundacion'],
        'fines': row['Fines'] if pd.notna(row['Fines']) else None,
        
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
            'domicilio': row.get('DireccionEstatutaria/DireccionEstatutaria/Domicilio'),
            'codigoPostal': int(row.get('DireccionEstatutaria/DireccionEstatutaria/CodigoPostal')) if pd.notna(row.get('DireccionEstatutaria/DireccionEstatutaria/CodigoPostal')) else None,
            'provincia': row.get('DireccionEstatutaria/DireccionEstatutaria/Provincia'),
            'telefono': str(int(row.get('DireccionEstatutaria/DireccionEstatutaria/Telefono'))) if pd.notna(row.get('DireccionEstatutaria/DireccionEstatutaria/Telefono')) else None,
            'fax': str(int(row.get('DireccionEstatutaria/DireccionEstatutaria/Fax'))) if pd.notna(row.get('DireccionEstatutaria/DireccionEstatutaria/Fax')) else None,
            'email': row.get('DireccionEstatutaria/DireccionEstatutaria/CorreoElectronico'),
            'web': row.get('DireccionEstatutaria/DireccionEstatutaria/Web')
        }
    
    # Dirección Notificación
    if pd.notna(row.get('DireccionNotificacion/DireccionNotificacion/Domicilio')):
        foundation['direccionNotificacion'] = {
            'domicilio': row.get('DireccionNotificacion/DireccionNotificacion/Domicilio'),
            'localidad': row.get('DireccionNotificacion/DireccionNotificacion/Localidad'),
            'codigoPostal': int(row.get('DireccionNotificacion/DireccionNotificacion/CodigoPostal')) if pd.notna(row.get('DireccionNotificacion/DireccionNotificacion/CodigoPostal')) else None,
            'provincia': row.get('DireccionNotificacion/DireccionNotificacion/Provincia')
        }
    
    # Actividades (check both single and array formats)
    if pd.notna(row.get('Actividades/Actividades/NombreActividad')):
        foundation['actividades'].append({
            'nombre': row.get('Actividades/Actividades/NombreActividad'),
            'clasificacion1': row.get('Actividades/Actividades/Clasificacion1'),
            'clasificacion2': row.get('Actividades/Actividades/Clasificacion2'),
            'clasificacion3': row.get('Actividades/Actividades/Clasificacion3'),
            'clasificacion4': row.get('Actividades/Actividades/Clasificacion4'),
            'funcion1': row.get('Actividades/Actividades/Funcion1'),
            'funcion2': row.get('Actividades/Actividades/Funcion2')
        })
    
    # Add array activities (0, 1, 2, 3)
    for i in range(4):
        if pd.notna(row.get(f'Actividades/Actividades/{i}/NombreActividad')):
            foundation['actividades'].append({
                'nombre': row.get(f'Actividades/Actividades/{i}/NombreActividad'),
                'clasificacion1': row.get(f'Actividades/Actividades/{i}/Clasificacion1'),
                'clasificacion2': row.get(f'Actividades/Actividades/{i}/Clasificacion2'),
                'clasificacion3': row.get(f'Actividades/Actividades/{i}/Clasificacion3'),
                'clasificacion4': row.get(f'Actividades/Actividades/{i}/Clasificacion4'),
                'funcion1': row.get(f'Actividades/Actividades/{i}/Funcion1'),
                'funcion2': row.get(f'Actividades/Actividades/{i}/Funcion2')
            })
    
    # Fundadores (up to 30)
    for i in range(30):
        if pd.notna(row.get(f'Fundadores/Fundador/{i}/NombreFundador')):
            foundation['fundadores'].append({
                'nombre': row.get(f'Fundadores/Fundador/{i}/NombreFundador')
            })
    
    # Patronos (up to 31)
    for i in range(31):
        if pd.notna(row.get(f'Patronos/Patron/{i}/NombrePatron')):
            foundation['patronos'].append({
                'nombre': row.get(f'Patronos/Patron/{i}/NombrePatron'),
                'cargo': row.get(f'Patronos/Patron/{i}/CargoPatron')
            })
    
    # Directivos (up to 12)
    for i in range(12):
        if pd.notna(row.get(f'Directivos/Directivo/{i}/NombreDirectivo')):
            foundation['directivos'].append({
                'nombre': row.get(f'Directivos/Directivo/{i}/NombreDirectivo'),
                'cargo': row.get(f'Directivos/Directivo/{i}/CargoDirectivo')
            })
    
    # Órganos
    if pd.notna(row.get('Organos/Organo/NombreOrgano')):
        foundation['organos'].append({
            'nombre': row.get('Organos/Organo/NombreOrgano')
        })
    
    # Add array organs (0, 1, 2)
    for i in range(3):
        if pd.notna(row.get(f'Organos/Organo/{i}/NombreOrgano')):
            foundation['organos'].append({
                'nombre': row.get(f'Organos/Organo/{i}/NombreOrgano')
            })
    
    # Add metadata
    foundation['metadata'] = {
        'fechaActualizacion': datetime.now(),
        'fuenteDatos': 'BBDD de fundaciones España actualizada 040724.xls'
    }
    
    return foundation

def migrate_excel_to_mongodb():
    """Main migration function"""
    try:
        # MongoDB connection
        mongodb_uri = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/fundaciones_espana')
        client = MongoClient(mongodb_uri)
        db_name = os.getenv('MONGODB_DB_NAME', 'fundaciones_espana')
        db = client[db_name]
        
        # Drop existing collection
        if 'fundaciones' in db.list_collection_names():
            print("⚠️  Dropping existing 'fundaciones' collection...")
            db.fundaciones.drop()
        
        collection = db.fundaciones
        
        # Read Excel file
        print("📖 Reading Excel file...")
        file_path = "/Users/paulo/Documents/Proyectos/Trabajo/Captaru/Datos Subvenciones/BBDD de fundaciones España actualizada 040724.xls"
        df = pd.read_excel(file_path)
        
        print(f"📊 Found {len(df)} foundations to migrate")
        
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
                    print(f"✅ Inserted {len(documents)} documents (total: {index + 1}/{len(df)})")
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
            print(f"✅ Inserted final {len(documents)} documents")
        
        # Create indexes
        print("\n🔧 Creating indexes...")
        collection.create_index('nombre')
        collection.create_index('nif')
        collection.create_index('estado')
        collection.create_index('direccionEstatutaria.provincia')
        collection.create_index([('nombre', pymongo.TEXT), ('fines', pymongo.TEXT)])
        
        # Summary
        total_docs = collection.count_documents({})
        print(f"\n✅ Migration complete!")
        print(f"📊 Total documents in MongoDB: {total_docs}")
        print(f"❌ Errors encountered: {len(errors)}")
        
        if errors:
            with open('migration-scripts/migration_errors.json', 'w') as f:
                json.dump(errors, f, indent=2)
            print("⚠️  Error details saved to migration_errors.json")
        
        # Sample query to verify
        sample = collection.find_one()
        print(f"\n📄 Sample document structure:")
        print(json.dumps(sample, default=str, indent=2, ensure_ascii=False)[:500] + "...")
        
    except Exception as e:
        print(f"❌ Fatal error during migration: {e}")
        sys.exit(1)

if __name__ == "__main__":
    print("🚀 Starting Excel to MongoDB migration...")
    migrate_excel_to_mongodb()