import pymongo
from pymongo import MongoClient
import os
from dotenv import load_dotenv
import html
import re

load_dotenv()

def fix_html_entities_and_corruption(text):
    """Fix HTML entities and text corruption"""
    if not isinstance(text, str):
        return text
    
    # Fix HTML entities
    result = html.unescape(text)
    
    # Fix specific text corruption patterns
    result = result.replace('&#xD;', '\n')
    result = result.replace('&#xA;', '\n')
    result = result.replace('&amp;', '&')
    result = result.replace('&lt;', '<')
    result = result.replace('&gt;', '>')
    result = result.replace('&quot;', '"')
    result = result.replace('&apos;', "'")
    
    # Fix specific OCR/encoding errors
    result = result.replace(' ele ', ' de ')
    result = result.replace('M Musco', 'el Museo')
    result = result.replace("d' Art", "d'Art")
    result = result.replace('ulteriores', 'posteriores')
    result = result.replace('.Thyssen-Bornemisza', ' Thyssen-Bornemisza')
    result = result.replace(" o' ", " o ")
    result = result.replace('pruvisrn9', 'previstos')
    result = result.replace('(le ', 'de ')
    result = result.replace(' M ', ' el ')
    
    # Clean up extra whitespace
    result = re.sub(r'\s+', ' ', result)
    result = result.strip()
    
    return result

def fix_database_html_entities():
    try:
        client = MongoClient('mongodb://localhost:27017')
        db = client['fundaciones_espana']
        collection = db.fundaciones
        
        print("🔧 Fixing HTML entities and text corruption...")
        
        updated = 0
        cursor = collection.find({})
        
        for doc in cursor:
            updates = {}
            
            # Fix nombre
            if doc.get('nombre'):
                cleaned = fix_html_entities_and_corruption(doc['nombre'])
                if cleaned != doc['nombre']:
                    updates['nombre'] = cleaned
                    updated += 1
                    print(f"Fixed nombre: {doc['nombre'][:50]}... -> {cleaned[:50]}...")
            
            # Fix estado
            if doc.get('estado'):
                cleaned = fix_html_entities_and_corruption(doc['estado'])
                if cleaned != doc['estado']:
                    updates['estado'] = cleaned
            
            # Fix fines
            if doc.get('fines'):
                cleaned = fix_html_entities_and_corruption(doc['fines'])
                if cleaned != doc['fines']:
                    updates['fines'] = cleaned
                    print(f"Fixed fines for: {doc.get('nombre', 'Unknown')}")
            
            # Fix direcciones
            if doc.get('direccionEstatutaria'):
                addr = doc['direccionEstatutaria']
                if addr.get('provincia'):
                    cleaned = fix_html_entities_and_corruption(addr['provincia'])
                    if cleaned != addr['provincia']:
                        updates['direccionEstatutaria.provincia'] = cleaned
                        
                if addr.get('domicilio'):
                    cleaned = fix_html_entities_and_corruption(addr['domicilio'])
                    if cleaned != addr['domicilio']:
                        updates['direccionEstatutaria.domicilio'] = cleaned
            
            # Fix patronos
            if doc.get('patronos'):
                patronos_fixed = False
                for patron in doc['patronos']:
                    if patron.get('nombre'):
                        original = patron['nombre']
                        cleaned = fix_html_entities_and_corruption(original)
                        if cleaned != original:
                            patron['nombre'] = cleaned
                            patronos_fixed = True
                    
                    if patron.get('cargo'):
                        original = patron['cargo']
                        cleaned = fix_html_entities_and_corruption(original)
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
                        cleaned = fix_html_entities_and_corruption(original)
                        if cleaned != original:
                            actividad['nombre'] = cleaned
                            actividades_fixed = True
                
                if actividades_fixed:
                    updates['actividades'] = doc['actividades']
            
            # Apply updates
            if updates:
                collection.update_one({'_id': doc['_id']}, {'$set': updates})
            
            if updated % 25 == 0 and updated > 0:
                print(f"✅ Fixed {updated} documents...")
        
        print(f"🎉 HTML entities fix complete! Fixed {updated} documents")
        
        # Test results
        sample = collection.find_one({'fines': {'$regex': '&#xD;'}})
        if sample:
            print(f"Sample with HTML entities still found: {sample['nombre']}")
        else:
            print("✅ No more HTML entities found")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    fix_database_html_entities()