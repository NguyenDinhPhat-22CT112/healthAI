"""
Merge rules cho bệnh lý phổ biến tại Việt Nam
Khi người dùng có nhiều bệnh lý, cần merge các rules lại
"""
from typing import List, Optional
from app.models.disease import DiseaseRule
from app.database.postgres import SessionLocal
from app.database.models import DiseaseRule as DiseaseRuleModel


def merge_disease_rules(disease_names: List[str]) -> dict:
    """
    Merge nhiều rules bệnh lý thành một rule tổng hợp
    
    Args:
        disease_names: Danh sách tên bệnh lý (VD: ["Tiểu đường", "Huyết áp cao"])
    
    Returns:
        Dict chứa rule tổng hợp
    """
    db = SessionLocal()
    
    try:
        # Lấy tất cả rules
        rules = []
        for disease_name in disease_names:
            rule = db.query(DiseaseRuleModel).filter(
                DiseaseRuleModel.disease_name.ilike(f"%{disease_name}%")
            ).first()
            if rule:
                rules.append(rule)
        
        if not rules:
            return {
                "merged_rule": None,
                "message": "Không tìm thấy rules cho các bệnh lý này"
            }
        
        # Merge rules
        merged_restricted_foods = set()
        merged_restricted_categories = set()
        merged_allowed_foods = set()
        merged_allowed_categories = set()
        merged_recommendations = []
        
        min_max_calories_per_meal = None
        min_max_carbs_per_meal = None
        min_max_fat_per_meal = None
        min_max_sodium_per_day = None
        min_min_protein_per_meal = None
        
        for rule in rules:
            # Merge restricted foods
            if rule.restricted_foods:
                merged_restricted_foods.update(rule.restricted_foods)
            if rule.restricted_categories:
                merged_restricted_categories.update(rule.restricted_categories)
            
            # Merge allowed foods (chỉ giữ lại nếu có trong tất cả rules)
            if rule.allowed_foods:
                if not merged_allowed_foods:
                    merged_allowed_foods.update(rule.allowed_foods)
                else:
                    merged_allowed_foods = merged_allowed_foods.intersection(set(rule.allowed_foods))
            
            # Merge recommendations
            if rule.recommendations:
                merged_recommendations.extend(rule.recommendations)
            
            # Merge giới hạn dinh dưỡng (lấy giá trị chặt chẽ nhất)
            if rule.max_calories_per_meal:
                if min_max_calories_per_meal is None or rule.max_calories_per_meal < min_max_calories_per_meal:
                    min_max_calories_per_meal = rule.max_calories_per_meal
            
            if rule.max_carbs_per_meal:
                if min_max_carbs_per_meal is None or rule.max_carbs_per_meal < min_max_carbs_per_meal:
                    min_max_carbs_per_meal = rule.max_carbs_per_meal
            
            if rule.max_fat_per_meal:
                if min_max_fat_per_meal is None or rule.max_fat_per_meal < min_max_fat_per_meal:
                    min_max_fat_per_meal = rule.max_fat_per_meal
            
            if rule.max_sodium_per_day:
                if min_max_sodium_per_day is None or rule.max_sodium_per_day < min_max_sodium_per_day:
                    min_max_sodium_per_day = rule.max_sodium_per_day
            
            if rule.min_protein_per_meal:
                if min_min_protein_per_meal is None or rule.min_protein_per_meal > min_min_protein_per_meal:
                    min_min_protein_per_meal = rule.min_protein_per_meal
        
        # Tạo merged rule
        merged_rule = {
            "diseases": disease_names,
            "restricted_foods": list(merged_restricted_foods),
            "restricted_categories": list(merged_restricted_categories),
            "allowed_foods": list(merged_allowed_foods) if merged_allowed_foods else None,
            "allowed_categories": list(merged_allowed_categories) if merged_allowed_categories else None,
            "max_calories_per_meal": min_max_calories_per_meal,
            "max_carbs_per_meal": min_max_carbs_per_meal,
            "max_fat_per_meal": min_max_fat_per_meal,
            "max_sodium_per_day": min_max_sodium_per_day,
            "min_protein_per_meal": min_min_protein_per_meal,
            "recommendations": list(set(merged_recommendations)),  # Remove duplicates
            "vietnamese_specific_advice": _generate_merged_advice(rules, disease_names)
        }
        
        return {
            "merged_rule": merged_rule,
            "source_rules": [rule.disease_name for rule in rules]
        }
        
    finally:
        db.close()


def _generate_merged_advice(rules: List[DiseaseRuleModel], disease_names: List[str]) -> str:
    """Tạo lời khuyên tổng hợp cho nhiều bệnh lý"""
    advice_parts = []
    
    for rule in rules:
        if rule.vietnamese_specific_advice:
            advice_parts.append(f"- {rule.disease_name}: {rule.vietnamese_specific_advice}")
    
    if not advice_parts:
        return f"Khi có nhiều bệnh lý ({', '.join(disease_names)}), cần tuân thủ chặt chẽ hơn các quy tắc dinh dưỡng."
    
    return "\n".join(advice_parts)


def get_suitable_foods_for_diseases(disease_names: List[str]) -> dict:
    """
    Lấy danh sách món ăn phù hợp cho nhiều bệnh lý
    
    Args:
        disease_names: Danh sách bệnh lý
    
    Returns:
        Dict chứa danh sách món ăn phù hợp và cần tránh
    """
    merged = merge_disease_rules(disease_names)
    
    if not merged.get("merged_rule"):
        return {
            "suitable_foods": [],
            "avoid_foods": [],
            "warning": "Không tìm thấy rules"
        }
    
    rule = merged["merged_rule"]
    
    # Lấy món ăn từ database phù hợp với rules
    db = SessionLocal()
    
    try:
        from app.database.models import FoodItem
        from sqlalchemy import or_, and_, not_
        
        # Tìm món ăn không nằm trong restricted
        query = db.query(FoodItem)
        
        # Filter theo allowed categories nếu có
        if rule.get("allowed_categories"):
            query = query.filter(FoodItem.category.in_(rule["allowed_categories"]))
        
        # Loại bỏ restricted categories
        if rule.get("restricted_categories"):
            query = query.filter(~FoodItem.category.in_(rule["restricted_categories"]))
        
        suitable_foods = query.limit(20).all()
        
        suitable_list = [
            {
                "name": food.name_vn,
                "category": food.category,
                "calories_per_100g": food.calories,
                "region": food.region
            }
            for food in suitable_foods
        ]
        
        return {
            "suitable_foods": suitable_list,
            "avoid_foods": rule.get("restricted_foods", []),
            "restrictions": {
                "max_calories_per_meal": rule.get("max_calories_per_meal"),
                "max_carbs_per_meal": rule.get("max_carbs_per_meal"),
                "max_sodium_per_day": rule.get("max_sodium_per_day")
            },
            "recommendations": rule.get("recommendations", [])
        }
    finally:
        db.close()

