import pymongo
from pymongo import MongoClient
import os
from dotenv import load_dotenv
import re

load_dotenv()

def fix_ordinal_numbers(text):
    """Fix ordinal number encoding issues"""
    if not isinstance(text, str):
        return text
    
    # Fix ordinal number patterns
    result = text
    result = result.replace('1Âº', '1º')
    result = result.replace('2Âº', '2º')
    result = result.replace('3Âº', '3º')
    result = result.replace('4Âº', '4º')
    result = result.replace('5Âº', '5º')
    result = result.replace('6Âº', '6º')
    result = result.replace('7Âº', '7º')
    result = result.replace('8Âº', '8º')
    result = result.replace('9Âº', '9º')
    result = result.replace('0Âº', '0º')
    
    # Fix feminine ordinals
    result = result.replace('1Âª', '1ª')
    result = result.replace('2Âª', '2ª')
    result = result.replace('3Âª', '3ª')
    result = result.replace('4Âª', '4ª')
    result = result.replace('5Âª', '5ª')
    result = result.replace('6Âª', '6ª')
    result = result.replace('7Âª', '7ª')
    result = result.replace('8Âª', '8ª')
    result = result.replace('9Âª', '9ª')
    result = result.replace('0Âª', '0ª')
    
    # Fix standalone ordinal symbols
    result = result.replace('Âº', 'º')
    result = result.replace('Âª', 'ª')
    
    return result.strip()

def fix_database_ordinals():
    try:
        client = MongoClient('mongodb://localhost:27017')
        db = client['fundaciones_espana']
        collection = db.fundaciones
        
        print("🔧 Fixing ordinal number encoding...")
        
        # Find documents with ordinal encoding issues
        cursor = collection.find({
            '$or': [
                {'direccionEstatutaria.domicilio': {'$regex': 'Âº|Âª'}},
                {'direccionNotificacion.domicilio': {'$regex': 'Âº|Âª'}},
                {'nombre': {'$regex': 'Âº|Âª'}},
                {'fines': {'$regex': 'Âº|Âª'}}
            ]
        })
        
        updated = 0
        
        for doc in cursor:
            updates = {}
            
            # Fix nombre
            if doc.get('nombre') and ('Âº' in doc['nombre'] or 'Âª' in doc['nombre']):
                cleaned = fix_ordinal_numbers(doc['nombre'])
                if cleaned != doc['nombre']:
                    updates['nombre'] = cleaned
                    print(f"Fixed nombre: {doc['nombre']} -> {cleaned}")
                    updated += 1
            
            # Fix fines
            if doc.get('fines') and ('Âº' in doc['fines'] or 'Âª' in doc['fines']):
                cleaned = fix_ordinal_numbers(doc['fines'])
                if cleaned != doc['fines']:
                    updates['fines'] = cleaned
            
            # Fix direccionEstatutaria
            if doc.get('direccionEstatutaria'):
                addr = doc['direccionEstatutaria']
                if addr.get('domicilio') and ('Âº' in addr['domicilio'] or 'Âª' in addr['domicilio']):
                    cleaned = fix_ordinal_numbers(addr['domicilio'])
                    if cleaned != addr['domicilio']:
                        updates['direccionEstatutaria.domicilio'] = cleaned
                        print(f"Fixed address: {addr['domicilio']} -> {cleaned}")
                        
                if addr.get('provincia') and ('Âº' in addr['provincia'] or 'Âª' in addr['provincia']):
                    cleaned = fix_ordinal_numbers(addr['provincia'])
                    if cleaned != addr['provincia']:
                        updates['direccionEstatutaria.provincia'] = cleaned
            
            # Fix direccionNotificacion
            if doc.get('direccionNotificacion'):
                addr = doc['direccionNotificacion']
                if addr.get('domicilio') and ('Âº' in addr['domicilio'] or 'Âª' in addr['domicilio']):
                    cleaned = fix_ordinal_numbers(addr['domicilio'])
                    if cleaned != addr['domicilio']:
                        updates['direccionNotificacion.domicilio'] = cleaned
                        print(f"Fixed notification address: {addr['domicilio']} -> {cleaned}")
                        
                if addr.get('localidad') and ('Âº' in addr['localidad'] or 'Âª' in addr['localidad']):
                    cleaned = fix_ordinal_numbers(addr['localidad'])
                    if cleaned != addr['localidad']:
                        updates['direccionNotificacion.localidad'] = cleaned
            
            # Fix patronos
            if doc.get('patronos'):
                patronos_fixed = False
                for patron in doc['patronos']:
                    if patron.get('nombre') and ('Âº' in patron['nombre'] or 'Âª' in patron['nombre']):
                        original = patron['nombre']
                        cleaned = fix_ordinal_numbers(original)
                        if cleaned != original:
                            patron['nombre'] = cleaned
                            patronos_fixed = True
                    
                    if patron.get('cargo') and ('Âº' in patron['cargo'] or 'Âª' in patron['cargo']):
                        original = patron['cargo']
                        cleaned = fix_ordinal_numbers(original)
                        if cleaned != original:
                            patron['cargo'] = cleaned
                            patronos_fixed = True
                
                if patronos_fixed:
                    updates['patronos'] = doc['patronos']
            
            # Apply updates
            if updates:
                collection.update_one({'_id': doc['_id']}, {'$set': updates})
        
        print(f"🎉 Ordinal number fix complete! Fixed {updated} documents")
        
        # Verify no more ordinal issues remain
        remaining = collection.count_documents({
            '$or': [
                {'direccionEstatutaria.domicilio': {'$regex': 'Âº|Âª'}},
                {'direccionNotificacion.domicilio': {'$regex': 'Âº|Âª'}},
                {'nombre': {'$regex': 'Âº|Âª'}},
                {'fines': {'$regex': 'Âº|Âª'}}
            ]
        })
        
        if remaining == 0:
            print("✅ No ordinal encoding issues found in database")
        else:
            print(f"⚠️  {remaining} documents still contain ordinal encoding issues")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    fix_database_ordinals()