import pymongo
from pymongo import MongoClient
import os
from dotenv import load_dotenv
import re

load_dotenv()

def fix_encoding_v2(text):
    """Fix encoding issues using comprehensive approach"""
    if not isinstance(text, str):
        return text
    
    # Fix specific Unicode characters we see in the data
    result = text
    
    # Remove problematic Unicode quotation marks
    result = result.replace('"', 'Ó')  # Unicode 8220 -> Ó  
    result = result.replace(''', 'Ñ')  # Unicode 8216 -> Ñ
    result = result.replace('𼀽', 'Í')  # Unicode 61837 -> Í
    
    # Fix standard encoding issues
    result = result.replace('Á', 'Á')  # 193 -> Á (already correct)
    result = result.replace('É', 'É')  # 201 -> É (already correct) 
    
    # Additional common fixes
    result = result.replace('Ã¡', 'á')
    result = result.replace('Ã©', 'é')
    result = result.replace('Ã­', 'í')
    result = result.replace('Ã³', 'ó')
    result = result.replace('Ãº', 'ú')
    result = result.replace('Ã±', 'ñ')
    
    return result.strip() if result else None

def fix_database_encoding_v2():
    """Fix encoding in existing MongoDB data - comprehensive version"""
    try:
        # MongoDB connection
        mongodb_uri = os.getenv('MONGODB_URI', 'mongodb://localhost:27017')
        client = MongoClient(mongodb_uri)
        db_name = os.getenv('MONGODB_DB_NAME', 'fundaciones_espana')
        db = client[db_name]
        collection = db.fundaciones
        
        print("🔧 Starting comprehensive encoding fix...")
        
        # Process all documents
        cursor = collection.find({})
        processed = 0
        fixed = 0
        
        for doc in cursor:
            updates = {}
            
            # Fix nombre
            if doc.get('nombre') and isinstance(doc['nombre'], str):
                original = doc['nombre']
                fixed_nombre = fix_encoding_v2(original)
                if fixed_nombre != original:
                    updates['nombre'] = fixed_nombre
                    fixed += 1
            
            # Fix estado  
            if doc.get('estado') and isinstance(doc['estado'], str):
                original = doc['estado']
                fixed_estado = fix_encoding_v2(original)
                if fixed_estado != original:
                    updates['estado'] = fixed_estado
            
            # Fix fines
            if doc.get('fines') and isinstance(doc['fines'], str):
                original = doc['fines']
                fixed_fines = fix_encoding_v2(original)
                if fixed_fines != original:
                    updates['fines'] = fixed_fines
            
            # Fix direccionEstatutaria
            if doc.get('direccionEstatutaria'):
                addr = doc['direccionEstatutaria']
                if addr.get('provincia') and isinstance(addr['provincia'], str):
                    original = addr['provincia']
                    fixed_prov = fix_encoding_v2(original)
                    if fixed_prov != original:
                        updates['direccionEstatutaria.provincia'] = fixed_prov
                
                if addr.get('domicilio') and isinstance(addr['domicilio'], str):
                    original = addr['domicilio']
                    fixed_dom = fix_encoding_v2(original)
                    if fixed_dom != original:
                        updates['direccionEstatutaria.domicilio'] = fixed_dom
            
            # Fix direccionNotificacion
            if doc.get('direccionNotificacion'):
                addr = doc['direccionNotificacion']
                if addr.get('provincia') and isinstance(addr['provincia'], str):
                    original = addr['provincia']
                    fixed_prov = fix_encoding_v2(original)
                    if fixed_prov != original:
                        updates['direccionNotificacion.provincia'] = fixed_prov
                        
                if addr.get('localidad') and isinstance(addr['localidad'], str):
                    original = addr['localidad']
                    fixed_loc = fix_encoding_v2(original)
                    if fixed_loc != original:
                        updates['direccionNotificacion.localidad'] = fixed_loc
            
            # Fix patronos names
            if doc.get('patronos'):
                patronos_updated = []
                patronos_changed = False
                for patron in doc['patronos']:
                    if patron.get('nombre') and isinstance(patron['nombre'], str):
                        original = patron['nombre']
                        fixed_nombre = fix_encoding_v2(original)
                        if fixed_nombre != original:
                            patron['nombre'] = fixed_nombre
                            patronos_changed = True
                    
                    if patron.get('cargo') and isinstance(patron['cargo'], str):
                        original = patron['cargo']
                        fixed_cargo = fix_encoding_v2(original)
                        if fixed_cargo != original:
                            patron['cargo'] = fixed_cargo
                            patronos_changed = True
                
                if patronos_changed:
                    updates['patronos'] = doc['patronos']
            
            # Fix actividades names
            if doc.get('actividades'):
                actividades_changed = False
                for actividad in doc['actividades']:
                    if actividad.get('nombre') and isinstance(actividad['nombre'], str):
                        original = actividad['nombre']
                        fixed_nombre = fix_encoding_v2(original)
                        if fixed_nombre != original:
                            actividad['nombre'] = fixed_nombre
                            actividades_changed = True
                
                if actividades_changed:
                    updates['actividades'] = doc['actividades']
            
            # Apply updates
            if updates:
                collection.update_one({'_id': doc['_id']}, {'$set': updates})
            
            processed += 1
            if processed % 500 == 0:
                print(f"✅ Processed {processed} documents, fixed {fixed} with encoding issues")
        
        print(f"\n🎉 Comprehensive encoding fix complete!")
        print(f"📊 Total processed: {processed}")
        print(f"🔧 Documents fixed: {fixed}")
        
        # Verify fix
        sample = collection.find_one({'nombre': {'$regex': 'FUNDACI'}})
        if sample:
            print(f"\n📄 Sample after comprehensive fix:")
            print(f"Nombre: {sample['nombre']}")
            print(f"Estado: {sample['estado']}")
            
            if sample.get('patronos') and len(sample['patronos']) > 0:
                print(f"Primer Patrono: {sample['patronos'][0]['nombre']}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    fix_database_encoding_v2()