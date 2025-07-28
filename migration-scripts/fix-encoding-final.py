import pymongo
from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

def fix_encoding_final(text):
    """Fix encoding issues using direct replacement"""
    if not isinstance(text, str):
        return text
    
    # Complete fixes for Spanish encoding issues
    result = text
    result = result.replace('Ã±', 'ñ')
    result = result.replace('Ã³', 'ó')
    result = result.replace('Ã¡', 'á')
    result = result.replace('Ã©', 'é')
    result = result.replace('Ã­', 'í')
    result = result.replace('Ãº', 'ú')
    result = result.replace('Ã"', 'Ó')
    result = result.replace('Ã‰', 'É')
    result = result.replace('Ã', 'Á')
    result = result.replace('Ã ', 'à')
    result = result.replace('Ã¨', 'è')
    result = result.replace('Ã¬', 'ì')
    result = result.replace('Ã²', 'ò')
    result = result.replace('Ã¹', 'ù')
    
    # Special cases
    result = result.replace('Ã"N', 'ÓN')
    result = result.replace('Ã³n', 'ón')
    
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
        
        # Process all documents
        cursor = collection.find({})
        processed = 0
        fixed = 0
        
        for doc in cursor:
            updates = {}
            
            # Fix nombre
            if doc.get('nombre') and isinstance(doc['nombre'], str) and 'Ã' in doc['nombre']:
                updates['nombre'] = fix_encoding_final(doc['nombre'])
                fixed += 1
            
            # Fix estado  
            if doc.get('estado') and isinstance(doc['estado'], str) and 'Ã' in doc['estado']:
                updates['estado'] = fix_encoding_final(doc['estado'])
            
            # Fix fines
            if doc.get('fines') and isinstance(doc['fines'], str) and 'Ã' in doc['fines']:
                updates['fines'] = fix_encoding_final(doc['fines'])
            
            # Fix direccionEstatutaria
            if doc.get('direccionEstatutaria'):
                addr = doc['direccionEstatutaria']
                if addr.get('provincia') and isinstance(addr['provincia'], str) and 'Ã' in addr['provincia']:
                    updates['direccionEstatutaria.provincia'] = fix_encoding_final(addr['provincia'])
                if addr.get('domicilio') and isinstance(addr['domicilio'], str) and 'Ã' in addr['domicilio']:
                    updates['direccionEstatutaria.domicilio'] = fix_encoding_final(addr['domicilio'])
            
            # Apply updates
            if updates:
                collection.update_one({'_id': doc['_id']}, {'$set': updates})
            
            processed += 1
            if processed % 500 == 0:
                print(f"✅ Processed {processed} documents, fixed {fixed} with encoding issues")
        
        print(f"\n🎉 Encoding fix complete!")
        print(f"📊 Total processed: {processed}")
        print(f"🔧 Documents fixed: {fixed}")
        
        # Verify fix
        sample = collection.find_one({'nombre': {'$regex': 'FUNDACI'}})
        if sample:
            print(f"\n📄 Sample after fix:")
            print(f"Nombre: {sample['nombre']}")
            print(f"Estado: {sample['estado']}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    fix_database_encoding()