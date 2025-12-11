"""
Generate SQL INSERTs từ Excel file foodData.xlsx
Tạo file inserts_foods.sql với format PostgreSQL
"""
import pandas as pd
import json
import sys
from pathlib import Path

def generate_inserts_from_excel(excel_path: str = "data/foodData.xlsx", output_path: str = "inserts_foods.sql"):
    """
    Generate SQL INSERTs từ Excel file
    
    Args:
        excel_path: Đường dẫn đến file Excel
        output_path: Đường dẫn file SQL output
    """
    try:
        # Đọc Excel với header đúng
        print(f"📖 Đang đọc file Excel: {excel_path}")
        df = pd.read_excel(excel_path, sheet_name=0)
        
        # Skip row đầu tiên nếu có NaN hoặc header phụ
        if pd.isna(df.iloc[0]['Tên thực phẩm']):
            df = df.iloc[1:].reset_index(drop=True)
        
        # Map columns từ Vietnamese sang English
        column_mapping = {
            'Tên thực phẩm': 'name',
            'Glucid': 'glucid',
            'Chất Xơ': 'fiber',
            'Lipid (Béo)': 'lipid',
            'Protid (Đạm)': 'protid',
            'Calo': 'calo',
            'Vitamin A': 'vitA',
            'Vitamin B1': 'vitB1',
            'Vitamin B2': 'vitB2',
            'Vitamin B3': 'vitB3',
            'Vitamin B6': 'vitB6',
            'Vitamin B9': 'vitB9',
            'Vitamin B12': 'vitB12',
            'Vitamin C': 'vitC',
            'Vitamin D': 'vitD',
            'Vitamin E': 'vitE',
            'Vitamin K': 'vitK',
            'Vitamin H (B7)': 'vitH'
        }
        
        # Rename columns
        df = df.rename(columns=column_mapping)
        
        # Kiểm tra columns
        print(f"📊 Số dòng: {len(df)}")
        print(f"📋 Columns: {list(df.columns)[:10]}...")
        
        # Vitamin columns
        vitamin_cols = ['vitA', 'vitB1', 'vitB2', 'vitB3', 'vitB6', 'vitB9', 'vitB12', 
                       'vitC', 'vitD', 'vitE', 'vitK', 'vitH']
        
        # Generate SQL INSERTs
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('-- Full INSERTs for foods table\n')
            f.write(f'-- Generated from {excel_path}\n')
            f.write(f'-- Total rows: {len(df)}\n\n')
            
            count = 0
            for i in range(len(df)):
                row = df.iloc[i]
                
                # Get name
                name = str(row.get('name', '')).strip()
                if pd.isna(row.get('name')) or not name or name == 'nan' or name == '':
                    continue
                
                # Escape single quotes
                name = name.replace("'", "''")
                
                # Helper function để convert string/range thành float
                def safe_float(value, default=None):
                    if pd.isna(value):
                        return default
                    try:
                        val_str = str(value).strip()
                        # Xử lý range format "125/171" - lấy giá trị đầu tiên
                        if '/' in val_str:
                            val_str = val_str.split('/')[0].strip()
                        return float(val_str)
                    except (ValueError, TypeError):
                        return default
                
                # Get nutrition values
                glucid = safe_float(row.get('glucid'))
                fiber = safe_float(row.get('fiber'))
                lipid = safe_float(row.get('lipid'))
                protid = safe_float(row.get('protid'))
                calo = safe_float(row.get('calo'))
                
                # Generate vitamins JSON
                vitamins = {}
                for vit_col in vitamin_cols:
                    if vit_col in df.columns and pd.notna(row.get(vit_col)):
                        try:
                            vitamins[vit_col] = float(row[vit_col])
                        except:
                            vitamins[vit_col] = 0.0
                    else:
                        vitamins[vit_col] = 0.0
                
                vitamins_json = json.dumps(vitamins, ensure_ascii=False)
                
                # Generate SQL
                sql = f"INSERT INTO foods (name, glucid, fiber, lipid, protid, calo, vitamins) VALUES "
                sql += f"('{name}', "
                sql += f"{glucid if glucid is not None else 'NULL'}, "
                sql += f"{fiber if fiber is not None else 'NULL'}, "
                sql += f"{lipid if lipid is not None else 'NULL'}, "
                sql += f"{protid if protid is not None else 'NULL'}, "
                sql += f"{calo if calo is not None else 'NULL'}, "
                sql += f"'{vitamins_json.replace(chr(39), chr(39)+chr(39))}'::JSONB);\n"
                
                f.write(sql)
                count += 1
            
            print(f"✅ Đã generate {count} INSERT statements")
            print(f"📄 File output: {output_path}")
            print(f"\n💡 Chạy SQL file:")
            print(f"   psql -d foodadvisor -f {output_path}")
            print(f"   hoặc import vào PostgreSQL client")
            
            return True
            
    except FileNotFoundError:
        print(f"❌ Không tìm thấy file: {excel_path}")
        print(f"💡 Đảm bảo file Excel có trong thư mục data/")
        return False
    except Exception as e:
        print(f"❌ Lỗi khi generate: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    excel_path = sys.argv[1] if len(sys.argv) > 1 else "data/foodData.xlsx"
    output_path = sys.argv[2] if len(sys.argv) > 2 else "inserts_foods.sql"
    
    print("\n" + "🚀"*25)
    print("Generate SQL INSERTs từ Excel")
    print("🚀"*25)
    
    success = generate_inserts_from_excel(excel_path, output_path)
    
    if success:
        print("\n✅ Hoàn tất!")
    else:
        print("\n❌ Có lỗi xảy ra")
        sys.exit(1)

