import pandas as pd

# Test the encoding fix approach
def test_encoding_fix():
    # Read a sample from the Excel file
    file_path = "/Users/paulo/Documents/Proyectos/Trabajo/Captaru/Datos Subvenciones/BBDD de fundaciones España actualizada 040724.xls"
    df = pd.read_excel(file_path, nrows=10)
    
    print("Original text samples:")
    for i, row in df.iterrows():
        nombre = row.get('Nombre', '')
        print(f"Row {i}: {nombre}")
        if i >= 5:
            break
    
    print("\nTesting encoding fixes:")
    
    # Test different approaches
    test_text = "REAL FUNDACIÃ"N DE TOLEDO"
    print(f"Original: {test_text}")
    
    # Approach 1: Try latin-1 to utf-8
    try:
        fixed1 = test_text.encode('latin-1').decode('utf-8')
        print(f"Method 1 (latin-1->utf-8): {fixed1}")
    except Exception as e:
        print(f"Method 1 failed: {e}")
    
    # Approach 2: Try cp1252 to utf-8
    try:
        fixed2 = test_text.encode('cp1252').decode('utf-8')
        print(f"Method 2 (cp1252->utf-8): {fixed2}")
    except Exception as e:
        print(f"Method 2 failed: {e}")
    
    # Approach 3: Manual replacement
    fixed3 = test_text.replace('Ã"', 'Ó')
    print(f"Method 3 (manual): {fixed3}")

if __name__ == "__main__":
    test_encoding_fix()