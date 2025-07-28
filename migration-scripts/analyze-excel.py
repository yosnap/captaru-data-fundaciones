import pandas as pd
import json
from datetime import datetime

def analyze_excel_file(file_path):
    """Analyze the Excel file structure and content"""
    try:
        df = pd.read_excel(file_path)
        
        print("=== EXCEL FILE ANALYSIS ===")
        print(f"\nFile: {file_path}")
        print(f"Total rows: {len(df)}")
        print(f"Total columns: {len(df.columns)}")
        
        print("\n=== COLUMNS ===")
        for i, col in enumerate(df.columns):
            non_null = df[col].notna().sum()
            dtype = df[col].dtype
            print(f"{i+1}. {col} - Type: {dtype}, Non-null: {non_null}/{len(df)}")
        
        print("\n=== DATA TYPES ===")
        print(df.dtypes)
        
        print("\n=== SAMPLE DATA (First 5 rows) ===")
        print(df.head())
        
        print("\n=== BASIC STATISTICS ===")
        print(df.describe())
        
        print("\n=== NULL VALUES COUNT ===")
        print(df.isnull().sum())
        
        column_info = {}
        for col in df.columns:
            column_info[col] = {
                'dtype': str(df[col].dtype),
                'non_null_count': int(df[col].notna().sum()),
                'null_count': int(df[col].isna().sum()),
                'unique_values': int(df[col].nunique()),
                'sample_values': df[col].dropna().head(5).tolist() if not df[col].isna().all() else []
            }
        
        with open('migration-scripts/excel_analysis.json', 'w', encoding='utf-8') as f:
            json.dump({
                'file_name': file_path.split('/')[-1],
                'total_rows': len(df),
                'total_columns': len(df.columns),
                'columns': list(df.columns),
                'column_info': column_info,
                'analysis_date': datetime.now().isoformat()
            }, f, ensure_ascii=False, indent=2)
        
        print("\n✅ Analysis complete! Results saved to excel_analysis.json")
        
    except Exception as e:
        print(f"❌ Error analyzing file: {e}")

if __name__ == "__main__":
    file_path = "/Users/paulo/Documents/Proyectos/Trabajo/Captaru/Datos Subvenciones/BBDD de fundaciones España actualizada 040724.xls"
    analyze_excel_file(file_path)