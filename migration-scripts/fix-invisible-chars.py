import pymongo
from pymongo import MongoClient
import os
from dotenv import load_dotenv
import re

load_dotenv()

def clean_invisible_chars(text):
    if not isinstance(text, str):
        return text
    
    # Remove invisible and control characters, but keep normal spaces
    # Keep characters that are letters, numbers, spaces, and common punctuation
    cleaned = re.sub(r'[^\w\sÁÉÍÓÚáéíóúÑñ.,;:()\-¿?¡!/@#$%&*+=<>{}[\]\\|"\'`~]', '', text)
    
    # Remove extra spaces
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    
    return cleaned

def fix_invisible_characters():
    try:
        client = MongoClient('mongodb://localhost:27017')
        db = client['fundaciones_espana']
        collection = db.fundaciones
        
        print("🔧 Removing invisible characters...")
        
        updated = 0
        cursor = collection.find({})
        
        for doc in cursor:
            updates = {}
            
            # Fix nombre
            if doc.get('nombre'):
                cleaned = clean_invisible_chars(doc['nombre'])
                if cleaned != doc['nombre'] and len(cleaned) > 0:
                    updates['nombre'] = cleaned
                    updated += 1
                    print(f"Fixed: '{doc['nombre']}' -> '{cleaned}'")
            
            # Fix estado
            if doc.get('estado'):
                cleaned = clean_invisible_chars(doc['estado'])
                if cleaned != doc['estado'] and len(cleaned) > 0:
                    updates['estado'] = cleaned
            
            # Fix fines
            if doc.get('fines'):
                cleaned = clean_invisible_chars(doc['fines'])
                if cleaned != doc['fines'] and len(cleaned) > 0:
                    updates['fines'] = cleaned
            
            # Fix direcciones
            if doc.get('direccionEstatutaria'):
                addr = doc['direccionEstatutaria']
                if addr.get('provincia'):
                    cleaned = clean_invisible_chars(addr['provincia'])
                    if cleaned != addr['provincia'] and len(cleaned) > 0:
                        updates['direccionEstatutaria.provincia'] = cleaned
                        
                if addr.get('domicilio'):
                    cleaned = clean_invisible_chars(addr['domicilio'])
                    if cleaned != addr['domicilio'] and len(cleaned) > 0:
                        updates['direccionEstatutaria.domicilio'] = cleaned
            
            # Fix patronos
            if doc.get('patronos'):
                patronos_fixed = False
                for patron in doc['patronos']:
                    if patron.get('nombre'):
                        original = patron['nombre']
                        cleaned = clean_invisible_chars(original)
                        if cleaned != original and len(cleaned) > 0:
                            patron['nombre'] = cleaned
                            patronos_fixed = True
                    
                    if patron.get('cargo'):
                        original = patron['cargo']
                        cleaned = clean_invisible_chars(original)
                        if cleaned != original and len(cleaned) > 0:
                            patron['cargo'] = cleaned
                            patronos_fixed = True
                
                if patronos_fixed:
                    updates['patronos'] = doc['patronos']
            
            # Fix actividades
            if doc.get('actividades'):
                actividades_fixed = False
                for actividad in doc['actividades']:
                    if actividad.get('nombre'):
                        original = actividad['nombre']
                        cleaned = clean_invisible_chars(original)
                        if cleaned != original and len(cleaned) > 0:
                            actividad['nombre'] = cleaned
                            actividades_fixed = True
                
                if actividades_fixed:
                    updates['actividades'] = doc['actividades']
            
            # Apply updates
            if updates:
                collection.update_one({'_id': doc['_id']}, {'$set': updates})
            
            if updated % 50 == 0 and updated > 0:
                print(f"✅ Cleaned {updated} documents...")
        
        print(f"🎉 Invisible character cleanup complete! Cleaned {updated} documents")
        
        # Test results
        sample = collection.find_one({'nombre': {'$regex': 'MEDITERR'}})
        if sample:
            print(f"Sample MEDITERR: '{sample['nombre']}'")
        
        sample2 = collection.find_one({'nombre': {'$regex': 'BRIT'}})
        if sample2:
            print(f"Sample BRIT: '{sample2['nombre']}'")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    fix_invisible_characters()