import pymongo
from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

def fix_encoding_simple(text):
    """Simple fix for common encoding issues"""
    if not isinstance(text, str):
        return text
    
    # Most common fixes for Spanish text
    replacements = [
        ('Ã±', 'ñ'),
        ('Ã'', 'Ñ'),
        ('Ã³', 'ó'),
        ('Ã¡', 'á'),
        ('Ã©', 'é'),
        ('Ã­', 'í'),
        ('Ãº', 'ú'),
        ('Ã‰', 'É'),
        ('Ã"N', 'ÓN'),
        ('Ã³n', 'ón')
    ]
    
    result = text
    for wrong, correct in replacements:
        result = result.replace(wrong, correct)
    
    return result

def fix_database_encoding():
    """Fix encoding in existing MongoDB data"""
    try:
        # MongoDB connection
        mongodb_uri = os.getenv('MONGODB_URI', 'mongodb://localhost:27017')
        client = MongoClient(mongodb_uri)
        db_name = os.getenv('MONGODB_DB_NAME', 'fundaciones_espana')
        db = client[db_name]
        collection = db.fundaciones
        
        print("🔧 Starting encoding fix for existing data...")
        
        # Get all documents
        total_docs = collection.count_documents({})
        print(f"📊 Processing {total_docs} documents...")
        
        processed = 0
        batch_size = 100
        
        cursor = collection.find({})
        
        for doc in cursor:
            updates = {}
            
            # Fix main fields
            if doc.get('nombre'):
                fixed_nombre = fix_encoding_simple(doc['nombre'])
                if fixed_nombre != doc['nombre']:
                    updates['nombre'] = fixed_nombre
            
            if doc.get('estado'):
                fixed_estado = fix_encoding_simple(doc['estado'])
                if fixed_estado != doc['estado']:
                    updates['estado'] = fixed_estado
            
            if doc.get('fines'):
                fixed_fines = fix_encoding_simple(doc['fines'])
                if fixed_fines != doc['fines']:
                    updates['fines'] = fixed_fines
            
            # Fix address fields
            if doc.get('direccionEstatutaria'):
                addr = doc['direccionEstatutaria']
                addr_updates = {}
                
                if addr.get('provincia'):
                    fixed_prov = fix_encoding_simple(addr['provincia'])
                    if fixed_prov != addr['provincia']:
                        addr_updates['direccionEstatutaria.provincia'] = fixed_prov
                
                if addr.get('domicilio'):
                    fixed_dom = fix_encoding_simple(addr['domicilio'])
                    if fixed_dom != addr['domicilio']:
                        addr_updates['direccionEstatutaria.domicilio'] = fixed_dom
                
                updates.update(addr_updates)
            
            # Fix notification address
            if doc.get('direccionNotificacion'):
                addr = doc['direccionNotificacion']
                addr_updates = {}
                
                if addr.get('provincia'):
                    fixed_prov = fix_encoding_simple(addr['provincia'])
                    if fixed_prov != addr['provincia']:
                        addr_updates['direccionNotificacion.provincia'] = fixed_prov
                
                if addr.get('localidad'):
                    fixed_loc = fix_encoding_simple(addr['localidad'])
                    if fixed_loc != addr['localidad']:
                        addr_updates['direccionNotificacion.localidad'] = fixed_loc
                
                updates.update(addr_updates)
            
            # Apply updates if any
            if updates:
                collection.update_one({'_id': doc['_id']}, {'$set': updates})
            
            processed += 1
            if processed % batch_size == 0:
                print(f"✅ Processed {processed}/{total_docs} documents...")
        
        print(f"\n🎉 Encoding fix complete! Processed {processed} documents")
        
        # Show sample of fixed data
        sample = collection.find_one()
        print(f"\n📄 Sample after encoding fix:")
        print(f"Nombre: {sample['nombre']}")
        print(f"Estado: {sample['estado']}")
        if sample.get('direccionEstatutaria'):
            print(f"Provincia: {sample['direccionEstatutaria'].get('provincia')}")
        
    except Exception as e:
        print(f"❌ Error fixing encoding: {e}")

if __name__ == "__main__":
    fix_database_encoding()