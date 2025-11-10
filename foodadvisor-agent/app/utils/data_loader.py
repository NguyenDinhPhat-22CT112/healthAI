"""
Load Excel vào PostgreSQL - Dataset món ăn Việt Nam
"""
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from typing import Optional, List
from app.config import settings
from app.database.postgres import SessionLocal
from app.database.models import Food, Recipe, DiseaseRule, Base
import json


def load_excel_to_postgres(
    excel_path: str,
    table_name: str = "foods",
    sheet_name: Optional[str] = None
):
    """
    Load dữ liệu từ file Excel vào PostgreSQL
    
    Args:
        excel_path: Đường dẫn đến file Excel (foodData.xlsx)
        table_name: Tên bảng cần load (food_items, recipes, disease_rules)
        sheet_name: Tên sheet trong Excel (nếu có nhiều sheet)
    
    Excel format mong đợi cho food_items:
    - name_vn: Tên món ăn tiếng Việt
    - name_en: Tên tiếng Anh (optional)
    - category: Nhóm món (phở, bún, cơm, etc.)
    - region: Vùng miền (Bắc, Trung, Nam)
    - meal_type: Loại bữa (sáng, trưa, tối)
    - calories: Calo per 100g
    - protein, fat, carbs, fiber: Dinh dưỡng per 100g
    - main_ingredients: Thành phần chính (JSON string hoặc comma-separated)
    - typical_serving_g: Khẩu phần điển hình (gram)
    """
    try:
        # Đọc Excel
        if sheet_name:
            df = pd.read_excel(excel_path, sheet_name=sheet_name)
        else:
            df = pd.read_excel(excel_path)
        
        db: Session = SessionLocal()
        
        try:
            if table_name == "foods":
                _load_food_items(df, db, skip_existing=True)
            elif table_name == "recipes":
                _load_recipes(df, db)
            elif table_name == "disease_rules":
                _load_disease_rules(df, db)
            else:
                raise ValueError(f"Table name không hợp lệ: {table_name}")
            
            db.commit()
            print(f"✅ Đã load {len(df)} records vào {table_name}")
            return True
        except Exception as e:
            db.rollback()
            print(f"❌ Lỗi khi load: {str(e)}")
            return False
        finally:
            db.close()
        
    except Exception as e:
        print(f"Lỗi khi load Excel: {str(e)}")
        return False


def _load_food_items(df: pd.DataFrame, db: Session, skip_existing: bool = True):
    """Load foods vào database từ Excel (format mới với vitamins)"""
    # Map columns từ Vietnamese sang English nếu cần
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
    
    # Rename columns nếu có Vietnamese names
    if 'Tên thực phẩm' in df.columns:
        df = df.rename(columns=column_mapping)
    
    # Skip row đầu tiên nếu có NaN
    if pd.isna(df.iloc[0].get('name', '')):
        df = df.iloc[1:].reset_index(drop=True)
    
    vitamin_cols = ['vitA', 'vitB1', 'vitB2', 'vitB3', 'vitB6', 'vitB9', 'vitB12', 
                   'vitC', 'vitD', 'vitE', 'vitK', 'vitH']
    
    for _, row in df.iterrows():
        # Skip nếu không có name
        name = str(row.get("name", "")).strip()
        if pd.isna(row.get("name")) or not name or name == 'nan':
            continue
        
        # Parse vitamins thành JSONB
        vitamins = {}
        for vit_col in vitamin_cols:
            if vit_col in df.columns and pd.notna(row.get(vit_col)):
                try:
                    vitamins[vit_col] = float(row[vit_col])
                except:
                    vitamins[vit_col] = 0.0
            else:
                vitamins[vit_col] = 0.0
        
        # Parse tags (nếu có)
        tags = {}
        if pd.notna(row.get("tags")):
            tags_str = str(row["tags"])
            # Parse tags từ string hoặc dict
            try:
                tags = json.loads(tags_str) if tags_str.startswith("{") else {}
            except:
                tags = {}
        
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
        
        # Kiểm tra nếu food đã tồn tại
        existing = db.query(Food).filter(Food.name == name).first()
        if existing:
            if skip_existing:
                print(f"⚠️  Skip (đã tồn tại): {name}")
                continue
            else:
                # Update existing
                existing.glucid = safe_float(row.get("glucid"))
                existing.fiber = safe_float(row.get("fiber"))
                existing.lipid = safe_float(row.get("lipid"))
                existing.protid = safe_float(row.get("protid"))
                existing.calo = safe_float(row.get("calo"))
                existing.vitamins = vitamins if vitamins else None
                existing.tags = tags if tags else {}
                print(f"🔄 Updated: {name}")
                continue
        
        food = Food(
            name=name,
            glucid=safe_float(row.get("glucid")),
            fiber=safe_float(row.get("fiber")),
            lipid=safe_float(row.get("lipid")),
            protid=safe_float(row.get("protid")),
            calo=safe_float(row.get("calo")),
            vitamins=vitamins if vitamins else None,
            tags=tags if tags else {}
        )
        
        db.add(food)


def _load_recipes(df: pd.DataFrame, db: Session):
    """Load recipes vào database"""
    for _, row in df.iterrows():
        # Parse ingredients và steps từ JSON
        ingredients_json = json.dumps(row.get("ingredients", [])) if pd.notna(row.get("ingredients")) else None
        steps_json = json.dumps(row.get("steps", [])) if pd.notna(row.get("steps")) else None
        
        # Parse tags
        tags = []
        if pd.notna(row.get("tags")):
            tags_str = str(row["tags"])
            if "," in tags_str:
                tags = [t.strip() for t in tags_str.split(",")]
            else:
                tags = [tags_str.strip()]
        
        recipe = Recipe(
            name=row.get("name", row.get("name_vn", "")),
            name_vn=row.get("name_vn", row.get("name", "")),
            name_en=row.get("name_en"),
            category=row.get("category", ""),
            region=row.get("region"),
            difficulty=row.get("difficulty"),
            cooking_time_minutes=int(row.get("cooking_time_minutes")) if pd.notna(row.get("cooking_time_minutes")) else None,
            servings=int(row.get("servings")) if pd.notna(row.get("servings")) else None,
            calories_per_serving=float(row.get("calories_per_serving")) if pd.notna(row.get("calories_per_serving")) else None,
            protein_per_serving=float(row.get("protein_per_serving")) if pd.notna(row.get("protein_per_serving")) else None,
            fat_per_serving=float(row.get("fat_per_serving")) if pd.notna(row.get("fat_per_serving")) else None,
            carbs_per_serving=float(row.get("carbs_per_serving")) if pd.notna(row.get("carbs_per_serving")) else None,
            ingredients_json=ingredients_json,
            steps_json=steps_json,
            tags=tags,
            description=row.get("description"),
            image_url=row.get("image_url")
        )
        
        db.add(recipe)


def _load_disease_rules(df: pd.DataFrame, db: Session):
    """Load disease rules vào database (format mới với JSONB constraints)"""
    for _, row in df.iterrows():
        # Parse constraints thành JSONB
        constraints = {}
        if pd.notna(row.get("constraints")):
            constraints_str = str(row["constraints"])
            try:
                constraints = json.loads(constraints_str) if constraints_str.startswith("{") else {}
            except:
                # Parse từ các columns riêng lẻ
                if pd.notna(row.get("max_lipid")):
                    constraints["max_lipid"] = float(row["max_lipid"])
                if pd.notna(row.get("min_fiber")):
                    constraints["min_fiber"] = float(row["min_fiber"])
                if pd.notna(row.get("max_calo")):
                    constraints["max_calo"] = float(row["max_calo"])
                if pd.notna(row.get("max_sodium")):
                    constraints["max_sodium"] = float(row["max_sodium"])
        
        avoid_foods = _parse_array(row.get("avoid_foods"))
        recommend_foods = _parse_array(row.get("recommend_foods"))
        
        disease_rule = DiseaseRule(
            disease=row.get("disease", row.get("disease_name", "")),
            constraints=constraints if constraints else {},
            avoid_foods=avoid_foods if avoid_foods else [],
            recommend_foods=recommend_foods if recommend_foods else [],
            priority_level=row.get("priority_level", "medium"),
            notes=row.get("notes"),
            is_custom=bool(row.get("is_custom", False)),
            user_id=None  # System rules không có user_id
        )
        
        db.add(disease_rule)


def _parse_array(value) -> Optional[List[str]]:
    """Parse array từ Excel cell"""
    if pd.isna(value):
        return None
    
    value_str = str(value)
    if "," in value_str:
        return [item.strip() for item in value_str.split(",")]
    else:
        return [value_str.strip()]


def init_sample_data():
    """
    Khởi tạo dữ liệu mẫu cho món ăn Việt Nam phổ biến
    """
    db: Session = SessionLocal()
    
    # Sample foods (format mới với vitamins JSONB)
    sample_foods = [
        {
            "name": "Phở bò",
            "glucid": 20.0,
            "fiber": 1.0,
            "lipid": 3.0,
            "protid": 12.0,
            "calo": 150.0,
            "vitamins": {
                "vitA": 0, "vitB1": 0.1, "vitB2": 0.05, "vitB3": 2.0,
                "vitB6": 0.1, "vitB9": 10, "vitB12": 0.5, "vitC": 0,
                "vitD": 0, "vitE": 0.1, "vitK": 0.2, "vitH": 0.3
            },
            "tags": {"vietnamese": True, "breakfast": True, "region": "Bắc"}
        },
        {
            "name": "Cơm tấm sườn nướng",
            "glucid": 18.0,
            "fiber": 0.5,
            "lipid": 8.0,
            "protid": 15.0,
            "calo": 186.0,
            "vitamins": {
                "vitA": 0, "vitB1": 0.2, "vitB2": 0.1, "vitB3": 3.0,
                "vitB6": 0.2, "vitB9": 15, "vitB12": 1.0, "vitC": 0,
                "vitD": 0, "vitE": 0.2, "vitK": 0.1, "vitH": 0.5
            },
            "tags": {"vietnamese": True, "lunch": True, "region": "Nam"}
        },
        {
            "name": "Gỏi cuốn",
            "glucid": 6.0,
            "fiber": 1.0,
            "lipid": 0.5,
            "protid": 3.0,
            "calo": 40.0,
            "vitamins": {
                "vitA": 100, "vitB1": 0.05, "vitB2": 0.05, "vitB3": 0.5,
                "vitB6": 0.05, "vitB9": 10, "vitB12": 0.2, "vitC": 15.0,
                "vitD": 0, "vitE": 0.1, "vitK": 5.0, "vitH": 0.2
            },
            "tags": {"vietnamese": True, "healthy": True, "low_calorie": True}
        }
    ]
    
    for food_data in sample_foods:
        food = Food(**food_data)
        db.add(food)
    
    # Sample disease rules (format mới với JSONB constraints)
    sample_rules = [
        {
            "disease": "Mỡ trong máu",
            "constraints": {"max_lipid": 15, "min_omega3": 0.5, "min_fiber": 8, "max_glucid": 40},
            "avoid_foods": ["mỡ bò", "ba chỉ lợn", "dừa cùi"],
            "recommend_foods": ["cá basa", "bí đỏ", "hạt chia", "yến mạch"],
            "priority_level": "high",
            "notes": "Ưu tiên omega-3 từ cá sông, chất xơ từ rau củ địa phương."
        },
        {
            "disease": "Béo phì",
            "constraints": {"max_calo": 450, "max_glucid": 40, "min_protid": 20, "min_fiber": 7},
            "avoid_foods": ["gạo trắng", "bánh mì kẹp", "thức ăn nhanh"],
            "recommend_foods": ["rau muống", "ức gà", "khoai lang", "rau bina"],
            "priority_level": "high",
            "notes": "Giảm tinh bột tinh chế, tăng rau quả; khẩu phần nhỏ cho người Việt."
        },
        {
            "disease": "Tăng huyết áp",
            "constraints": {"max_sodium": 400, "min_kali": 1000, "min_fiber": 7, "lipid_max": 10},
            "avoid_foods": ["nước mắm mặn", "thịt hun khói", "mì gói"],
            "recommend_foods": ["cải thìa", "cam", "cà chua", "khoai lang"],
            "priority_level": "high",
            "notes": "DASH-style: Ít muối, giàu kali từ trái cây múi; tránh gia vị mặn phổ biến."
        }
    ]
    
    for rule_data in sample_rules:
        rule = DiseaseRule(**rule_data)
        db.add(rule)
    
    db.commit()
    db.close()
    
    print("Đã khởi tạo dữ liệu mẫu")

