import pymongo
from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

def normalize_activity_name(name):
    """Normalize activity names by removing periods and standardizing case"""
    if not isinstance(name, str):
        return name
    
    # Remove trailing periods and extra spaces
    normalized = name.strip().rstrip('.')
    
    # Standardize common activities to proper case
    activity_map = {
        'SANIDAD': 'Sanidad',
        'CULTURA': 'Cultura', 
        'EDUCACION': 'Educación',
        'INVESTIGACION': 'Investigación',
        'SERVICIOS SOCIALES': 'Servicios Sociales',
        'DEPORTE': 'Deporte'
    }
    
    # Check if it matches any of our standardized names
    normalized_upper = normalized.upper()
    if normalized_upper in activity_map:
        return activity_map[normalized_upper]
    
    # Otherwise return with proper capitalization
    return normalized.title()

def normalize_database_activities():
    try:
        client = MongoClient('mongodb://localhost:27017')
        db = client['fundaciones_espana']
        collection = db.fundaciones
        
        print("🔧 Normalizing activity names...")
        
        updated = 0
        cursor = collection.find({'actividades': {'$exists': True, '$ne': []}})
        
        for doc in cursor:
            activities_updated = False
            
            for actividad in doc['actividades']:
                if actividad.get('clasificacion1'):
                    original = actividad['clasificacion1']
                    normalized = normalize_activity_name(original)
                    
                    if normalized != original:
                        actividad['clasificacion1'] = normalized
                        activities_updated = True
                        print(f"Normalized: '{original}' -> '{normalized}'")
                
                if actividad.get('nombre'):
                    original = actividad['nombre']
                    # Also normalize the activity name field
                    if original.endswith('.'):
                        actividad['nombre'] = original.rstrip('.')
                        activities_updated = True
            
            if activities_updated:
                collection.update_one(
                    {'_id': doc['_id']}, 
                    {'$set': {'actividades': doc['actividades']}}
                )
                updated += 1
            
            if updated % 100 == 0 and updated > 0:
                print(f"✅ Processed {updated} documents...")
        
        print(f"🎉 Activity normalization complete! Updated {updated} documents")
        
        # Show the normalized activity distribution
        print("\n📊 Normalized activity distribution:")
        stats = collection.aggregate([
            {'$unwind': '$actividades'},
            {'$match': {'actividades.clasificacion1': {'$exists': True, '$ne': None}}},
            {'$group': {'_id': '$actividades.clasificacion1', 'count': {'$sum': 1}}},
            {'$sort': {'count': -1}},
            {'$limit': 10}
        ])
        
        for stat in stats:
            print(f"{stat['_id']}: {stat['count']}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    normalize_database_activities()