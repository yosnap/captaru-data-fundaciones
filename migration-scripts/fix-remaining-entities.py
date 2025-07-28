import pymongo
from pymongo import MongoClient
import os
from dotenv import load_dotenv
import html
import re

load_dotenv()

def comprehensive_text_cleanup(text):
    """Comprehensive text cleanup for remaining HTML entities and corruption"""
    if not isinstance(text, str):
        return text
    
    # Fix HTML entities
    result = html.unescape(text)
    
    # Fix remaining HTML entities that might not be caught
    result = result.replace('&#xD;', '\n')
    result = result.replace('&#xA;', '\n')
    result = result.replace('&#x0D;', '\n')
    result = result.replace('&#x0A;', '\n')
    result = result.replace('&#13;', '\n')
    result = result.replace('&#10;', '\n')
    
    # Fix text corruption patterns from the examples
    result = result.replace(' ele ', ' de ')
    result = result.replace('ele arte', 'de arte')
    result = result.replace('M Musco', 'el Museo')
    result = result.replace("d' Art", "d'Art")
    result = result.replace('ulteriores', 'posteriores')
    result = result.replace('.Thyssen-Bornemisza', ' Thyssen-Bornemisza')
    result = result.replace(" o' ", " o ")
    result = result.replace('pruvisrn9', 'previstos')
    result = result.replace('(le ', 'de ')
    result = result.replace(' (le ', ' de ')
    result = result.replace('Musco', 'Museo')
    result = result.replace('Museoâ', 'Museo')
    result = result.replace('encada', 'en cada')
    result = result.replace('criterior', 'criterios')
    result = result.replace('2Âº', '2º')
    result = result.replace('Âº', 'º')
    result = result.replace('Â¡', '¡')
    
    # Fix specific character issues
    result = result.replace('MÁšSICA', 'MÚSICA')
    result = result.replace('NÁšÑEZ', 'NÚÑEZ')
    result = result.replace('SÁšBITO', 'SÚBITO')
    result = result.replace('COMÁšN', 'COMÚN')
    result = result.replace('SANLÁšCAR', 'SANLÚCAR')
    result = result.replace('ARGÁœELLO', 'ARGÜELLO')
    result = result.replace('PAILÁš', 'PAILÁ')
    result = result.replace('RAÁšL', 'RAÚL')
    result = result.replace('CLÍNICA', 'CLÍNICA')
    
    # Clean up multiple whitespace and normalize line breaks
    result = re.sub(r'\s*\n\s*', '\n', result)  # Clean up line breaks
    result = re.sub(r'\s+', ' ', result)        # Multiple spaces to single space
    result = result.strip()
    
    return result

def fix_remaining_entities():
    try:
        client = MongoClient('mongodb://localhost:27017')
        db = client['fundaciones_espana']
        collection = db.fundaciones
        
        print("🔧 Fixing remaining HTML entities and text corruption...")
        
        # Find documents with &#xD; or other HTML entities
        cursor = collection.find({
            '$or': [
                {'fines': {'$regex': '&#x[0-9A-F]+;'}},
                {'fines': {'$regex': '&#[0-9]+;'}},
                {'fines': {'$regex': 'ele arte'}},
                {'fines': {'$regex': 'M Musco'}},
                {'fines': {'$regex': 'Museoâ'}},
                {'fines': {'$regex': 'pruvisrn9'}},
                {'fines': {'$regex': '\\(le '}},
                {'nombre': {'$regex': '&#x[0-9A-F]+;'}},
                {'nombre': {'$regex': '&#[0-9]+;'}},
                {'nombre': {'$regex': 'MÁš'}},
                {'nombre': {'$regex': 'Áš'}},
                {'nombre': {'$regex': 'Áœ'}},
                {'nombre': {'$regex': '2Âº'}}
            ]
        })
        
        updated = 0
        
        for doc in cursor:
            updates = {}
            
            # Fix nombre
            if doc.get('nombre'):
                cleaned = comprehensive_text_cleanup(doc['nombre'])
                if cleaned != doc['nombre']:
                    updates['nombre'] = cleaned
                    print(f"Fixed nombre: {doc['nombre']} -> {cleaned}")
                    updated += 1
            
            # Fix estado
            if doc.get('estado'):
                cleaned = comprehensive_text_cleanup(doc['estado'])
                if cleaned != doc['estado']:
                    updates['estado'] = cleaned
            
            # Fix fines
            if doc.get('fines'):
                cleaned = comprehensive_text_cleanup(doc['fines'])
                if cleaned != doc['fines']:
                    updates['fines'] = cleaned
                    print(f"Fixed fines for: {doc.get('nombre', 'Unknown')}")
            
            # Fix direcciones
            if doc.get('direccionEstatutaria'):
                addr = doc['direccionEstatutaria']
                if addr.get('provincia'):
                    cleaned = comprehensive_text_cleanup(addr['provincia'])
                    if cleaned != addr['provincia']:
                        updates['direccionEstatutaria.provincia'] = cleaned
                        
                if addr.get('domicilio'):
                    cleaned = comprehensive_text_cleanup(addr['domicilio'])
                    if cleaned != addr['domicilio']:
                        updates['direccionEstatutaria.domicilio'] = cleaned
            
            # Fix patronos
            if doc.get('patronos'):
                patronos_fixed = False
                for patron in doc['patronos']:
                    if patron.get('nombre'):
                        original = patron['nombre']
                        cleaned = comprehensive_text_cleanup(original)
                        if cleaned != original:
                            patron['nombre'] = cleaned
                            patronos_fixed = True
                    
                    if patron.get('cargo'):
                        original = patron['cargo']
                        cleaned = comprehensive_text_cleanup(original)
                        if cleaned != original:
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
                        cleaned = comprehensive_text_cleanup(original)
                        if cleaned != original:
                            actividad['nombre'] = cleaned
                            actividades_fixed = True
                
                if actividades_fixed:
                    updates['actividades'] = doc['actividades']
            
            # Apply updates
            if updates:
                collection.update_one({'_id': doc['_id']}, {'$set': updates})
        
        print(f"🎉 Remaining HTML entities fix complete! Fixed {updated} documents")
        
        # Verify no more HTML entities remain
        remaining = collection.count_documents({
            '$or': [
                {'fines': {'$regex': '&#x[0-9A-F]+;'}},
                {'fines': {'$regex': '&#[0-9]+;'}},
                {'nombre': {'$regex': '&#x[0-9A-F]+;'}},
                {'nombre': {'$regex': '&#[0-9]+;'}}
            ]
        })
        
        if remaining == 0:
            print("✅ No HTML entities found in database")
        else:
            print(f"⚠️  {remaining} documents still contain HTML entities")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    fix_remaining_entities()