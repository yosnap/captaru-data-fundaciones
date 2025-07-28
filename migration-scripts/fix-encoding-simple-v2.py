import pymongo
from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

def fix_unicode_chars(text):
    if not isinstance(text, str):
        return text
    
    # Fix the specific problematic characters we identified
    result = text
    result = result.replace(chr(8220), 'Ó')  # Unicode 8220 -> Ó  
    result = result.replace(chr(8216), 'Ñ')  # Unicode 8216 -> Ñ
    result = result.replace(chr(61837), 'Í') # Unicode 61837 -> Í
    
    return result

def fix_database():
    try:
        client = MongoClient('mongodb://localhost:27017')
        db = client['fundaciones_espana']
        collection = db.fundaciones
        
        print("🔧 Fixing Unicode characters...")
        
        updated = 0
        cursor = collection.find({})
        
        for doc in cursor:
            updates = {}
            
            # Fix nombre
            if doc.get('nombre'):
                fixed = fix_unicode_chars(doc['nombre'])
                if fixed != doc['nombre']:
                    updates['nombre'] = fixed
                    updated += 1
            
            # Fix patronos
            if doc.get('patronos'):
                patronos_fixed = False
                for patron in doc['patronos']:
                    if patron.get('nombre'):
                        fixed = fix_unicode_chars(patron['nombre'])
                        if fixed != patron['nombre']:
                            patron['nombre'] = fixed
                            patronos_fixed = True
                
                if patronos_fixed:
                    updates['patronos'] = doc['patronos']
            
            # Apply updates
            if updates:
                collection.update_one({'_id': doc['_id']}, {'$set': updates})
            
            if updated % 100 == 0 and updated > 0:
                print(f"✅ Fixed {updated} documents...")
        
        print(f"🎉 Complete! Fixed {updated} documents")
        
        # Test result
        sample = collection.find_one({'nombre': {'$regex': 'FUNDACI'}})
        print(f"Sample: {sample['nombre']}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    fix_database()