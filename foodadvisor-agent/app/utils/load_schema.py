"""
Script load schema SQL vào PostgreSQL
"""
import sys
from sqlalchemy import text
from app.database.postgres import engine, SessionLocal
from pathlib import Path

def load_schema_from_file(schema_file: str = "app/database/schema.sql"):
    """
    Load schema SQL từ file vào PostgreSQL
    
    Args:
        schema_file: Đường dẫn đến file schema.sql
    """
    try:
        schema_path = Path(schema_file)
        if not schema_path.exists():
            print(f"❌ Không tìm thấy file: {schema_file}")
            return False
        
        print(f"📖 Đang đọc schema từ: {schema_file}")
        with open(schema_path, 'r', encoding='utf-8') as f:
            schema_sql = f.read()
        
        # Split by semicolons (basic approach)
        statements = [s.strip() for s in schema_sql.split(';') if s.strip()]
        
        print(f"📝 Số statements: {len(statements)}")
        
        with engine.connect() as conn:
            # Execute each statement
            for i, statement in enumerate(statements, 1):
                if statement.strip():
                    try:
                        conn.execute(text(statement))
                        conn.commit()
                        print(f"✅ [{i}/{len(statements)}] Executed")
                    except Exception as e:
                        # Skip if already exists
                        if "already exists" in str(e).lower() or "duplicate" in str(e).lower():
                            print(f"⚠️  [{i}/{len(statements)}] Already exists (skipped)")
                        else:
                            print(f"❌ [{i}/{len(statements)}] Error: {str(e)}")
                            # Continue with next statement
        
        print("\n✅ Schema đã được load!")
        return True
        
    except Exception as e:
        print(f"❌ Lỗi khi load schema: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    schema_file = sys.argv[1] if len(sys.argv) > 1 else "app/database/schema.sql"
    
    print("\n" + "🚀"*25)
    print("Load PostgreSQL Schema")
    print("🚀"*25)
    
    success = load_schema_from_file(schema_file)
    
    if success:
        print("\n✅ Hoàn tất!")
    else:
        print("\n❌ Có lỗi xảy ra")
        sys.exit(1)

