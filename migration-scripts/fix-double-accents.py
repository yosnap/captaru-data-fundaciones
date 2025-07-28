import pymongo
from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

def fix_double_accents(text):
    if not isinstance(text, str):
        return text
    
    # Fix double accent issues
    result = text
    result = result.replace('ÁÁ', 'Á')  # Double Á -> single Á
    result = result.replace('ÉÉ', 'É')  # Double É -> single É
    result = result.replace('ÍÍ', 'Í')  # Double Í -> single Í
    result = result.replace('ÓÓ', 'Ó')  # Double Ó -> single Ó
    result = result.replace('ÚÚ', 'Ú')  # Double Ú -> single Ú
    result = result.replace('ÑÑ', 'Ñ')  # Double Ñ -> single Ñ
    
    # Fix specific cases we can see
    result = result.replace('MEDITERRÁÁ', 'MEDITERRÁ')
    result = result.replace('BRITÁNÁ', 'BRITÁ')
    
    return result

def fix_database_double_accents():
    try:
        client = MongoClient('mongodb://localhost:27017')
        db = client['fundaciones_espana']
        collection = db.fundaciones
        
        print("🔧 Fixing double accent characters...")
        
        updated = 0
        cursor = collection.find({})
        
        for doc in cursor:
            updates = {}
            
            # Fix nombre
            if doc.get('nombre') and ('ÁÁ' in doc['nombre'] or 'ÉÉ' in doc['nombre'] or 'ÍÍ' in doc['nombre'] or 'ÓÓ' in doc['nombre'] or 'ÚÚ' in doc['nombre'] or 'ÑÑ' in doc['nombre']):
                fixed = fix_double_accents(doc['nombre'])
                if fixed != doc['nombre']:
                    updates['nombre'] = fixed
                    updated += 1
                    print(f"Fixed: {doc['nombre']} -> {fixed}")
            
            # Fix estado
            if doc.get('estado') and ('ÁÁ' in doc['estado'] or 'ÉÉ' in doc['estado'] or 'ÍÍ' in doc['estado'] or 'ÓÓ' in doc['estado'] or 'ÚÚ' in doc['estado'] or 'ÑÑ' in doc['estado']):
                fixed = fix_double_accents(doc['estado'])
                if fixed != doc['estado']:
                    updates['estado'] = fixed
            
            # Fix fines
            if doc.get('fines') and ('ÁÁ' in doc['fines'] or 'ÉÉ' in doc['fines'] or 'ÍÍ' in doc['fines'] or 'ÓÓ' in doc['fines'] or 'ÚÚ' in doc['fines'] or 'ÑÑ' in doc['fines']):
                fixed = fix_double_accents(doc['fines'])
                if fixed != doc['fines']:
                    updates['fines'] = fixed
            
            # Fix direcciones
            if doc.get('direccionEstatutaria'):
                addr = doc['direccionEstatutaria']
                if addr.get('provincia') and ('ÁÁ' in addr['provincia'] or 'ÉÉ' in addr['provincia']):
                    fixed = fix_double_accents(addr['provincia'])
                    if fixed != addr['provincia']:
                        updates['direccionEstatutaria.provincia'] = fixed
                        
                if addr.get('domicilio') and ('ÁÁ' in addr['domicilio'] or 'ÉÉ' in addr['domicilio']):
                    fixed = fix_double_accents(addr['domicilio'])
                    if fixed != addr['domicilio']:
                        updates['direccionEstatutaria.domicilio'] = fixed
            
            # Fix patronos
            if doc.get('patronos'):
                patronos_fixed = False
                for patron in doc['patronos']:
                    if patron.get('nombre') and ('ÁÁ' in patron['nombre'] or 'ÉÉ' in patron['nombre']):
                        original = patron['nombre']
                        patron['nombre'] = fix_double_accents(original)
                        if patron['nombre'] != original:
                            patronos_fixed = True
                            print(f"Fixed patron: {original} -> {patron['nombre']}")
                    
                    if patron.get('cargo') and ('ÁÁ' in patron['cargo'] or 'ÉÉ' in patron['cargo']):
                        original = patron['cargo']
                        patron['cargo'] = fix_double_accents(original)
                        if patron['cargo'] != original:
                            patronos_fixed = True
                
                if patronos_fixed:
                    updates['patronos'] = doc['patronos']
            
            # Apply updates
            if updates:
                collection.update_one({'_id': doc['_id']}, {'$set': updates})
        
        print(f"🎉 Double accent fix complete! Fixed {updated} documents")
        
        # Test result
        sample = collection.find_one({'nombre': {'$regex': 'MEDITERR'}})
        if sample:
            print(f"Sample result: {sample['nombre']}")
        
        sample2 = collection.find_one({'nombre': {'$regex': 'BRIT'}})
        if sample2:
            print(f"Sample result 2: {sample2['nombre']}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    fix_database_double_accents()