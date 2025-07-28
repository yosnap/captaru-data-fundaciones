import pymongo
from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

def final_clean_text(text):
    if not isinstance(text, str):
        return text
    
    # Fix remaining character issues
    result = text
    result = result.replace('ÁÓ', 'Ó')    # FUNDACIÁÓN -> FUNDACIÓN
    result = result.replace('ÁÑ', 'Ñ')    # ESPAÁÑOLA -> ESPAÑOLA  
    result = result.replace('ÁÍ', 'Í')    # CIRUGÁÍA -> CIRUGÍA
    
    return result

def final_database_clean():
    try:
        client = MongoClient('mongodb://localhost:27017')
        db = client['fundaciones_espana']
        collection = db.fundaciones
        
        print("🔧 Final character cleanup...")
        
        updated = 0
        cursor = collection.find({})
        
        for doc in cursor:
            updates = {}
            
            # Fix nombre
            if doc.get('nombre') and ('ÁÓ' in doc['nombre'] or 'ÁÑ' in doc['nombre'] or 'ÁÍ' in doc['nombre']):
                updates['nombre'] = final_clean_text(doc['nombre'])
                updated += 1
            
            # Fix estado
            if doc.get('estado') and ('ÁÓ' in doc['estado'] or 'ÁÑ' in doc['estado'] or 'ÁÍ' in doc['estado']):
                updates['estado'] = final_clean_text(doc['estado'])
            
            # Fix fines
            if doc.get('fines') and ('ÁÓ' in doc['fines'] or 'ÁÑ' in doc['fines'] or 'ÁÍ' in doc['fines']):
                updates['fines'] = final_clean_text(doc['fines'])
            
            # Fix direcciones
            if doc.get('direccionEstatutaria'):
                addr = doc['direccionEstatutaria']
                addr_updates = {}
                if addr.get('provincia') and ('ÁÓ' in addr['provincia'] or 'ÁÑ' in addr['provincia']):
                    addr_updates['direccionEstatutaria.provincia'] = final_clean_text(addr['provincia'])
                if addr.get('domicilio') and ('ÁÓ' in addr['domicilio'] or 'ÁÑ' in addr['domicilio']):
                    addr_updates['direccionEstatutaria.domicilio'] = final_clean_text(addr['domicilio'])
                updates.update(addr_updates)
            
            # Fix patronos
            if doc.get('patronos'):
                patronos_fixed = False
                for patron in doc['patronos']:
                    if patron.get('nombre') and ('ÁÓ' in patron['nombre'] or 'ÁÑ' in patron['nombre']):
                        patron['nombre'] = final_clean_text(patron['nombre'])
                        patronos_fixed = True
                    if patron.get('cargo') and ('ÁÓ' in patron['cargo'] or 'ÁÑ' in patron['cargo']):
                        patron['cargo'] = final_clean_text(patron['cargo'])
                        patronos_fixed = True
                
                if patronos_fixed:
                    updates['patronos'] = doc['patronos']
            
            # Apply updates
            if updates:
                collection.update_one({'_id': doc['_id']}, {'$set': updates})
            
            if updated % 50 == 0 and updated > 0:
                print(f"✅ Cleaned {updated} documents...")
        
        print(f"🎉 Final cleanup complete! Cleaned {updated} documents")
        
        # Test result
        sample = collection.find_one({'nombre': {'$regex': 'FUNDACI'}})
        print(f"Final sample: {sample['nombre']}")
        
        if sample.get('patronos') and len(sample['patronos']) > 0:
            print(f"Sample patron: {sample['patronos'][0]['nombre']}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    final_database_clean()