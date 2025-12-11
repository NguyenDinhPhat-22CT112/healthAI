"""
Database Helpers - Utility functions for food and health data queries
Centralized database access to avoid code duplication across tools
"""
import json
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import or_, text

from app.database.models import Food, MedicalCondition, FoodNutrient, Nutrient, DiseaseRecommendation
from app.database.connection import SessionLocal

try:
    from app.data.disease_nutrition_rules import get_disease_info, get_all_diseases
except ImportError:
    # Fallback if disease_nutrition_rules doesn't exist
    def get_disease_info(disease_name: str) -> Optional[dict]:
        return None
    
    def get_all_diseases() -> List[str]:
        return ["tiểu đường", "béo phì", "huyết áp cao"]


class DatabaseHelpers:
    """Database helper functions for food and health data"""
    
    @staticmethod
    def get_food_nutrition(food_name: str) -> Optional[Dict[str, Any]]:
        """
        Get nutrition information for a specific food item
        
        Args:
            food_name: Name of the food item
            
        Returns:
            Dictionary with nutrition data or None if not found
        """
        db = SessionLocal()
        try:
            # Search for food item (case insensitive, partial match)
            food_item = db.query(Food).filter(
                Food.name.ilike(f"%{food_name}%")
            ).first()
            
            if food_item:
                # Get nutrition data
                nutrition_data = {
                    "name": food_item.name,
                    "category": food_item.category,
                    "calories": float(food_item.calories_per_100g) if food_item.calories_per_100g else 0,
                    "high_glycemic": food_item.high_glycemic,
                    "high_sodium": food_item.high_sodium,
                    "image_url": food_item.image_url
                }
                
                # Get detailed nutrients
                for nutrient_rel in food_item.nutrients:
                    nutrient_name = nutrient_rel.nutrient.name.lower()
                    amount = float(nutrient_rel.amount_per_100g) if nutrient_rel.amount_per_100g else 0
                    
                    if 'protein' in nutrient_name:
                        nutrition_data['protein'] = amount
                    elif 'carb' in nutrient_name or 'carbohydrate' in nutrient_name:
                        nutrition_data['carbs'] = amount
                    elif 'fat' in nutrient_name:
                        nutrition_data['fat'] = amount
                    elif 'fiber' in nutrient_name:
                        nutrition_data['fiber'] = amount
                    elif 'sodium' in nutrient_name:
                        nutrition_data['sodium'] = amount
                
                return nutrition_data
            return None
            
        except Exception as e:
            print(f"Error getting food nutrition: {e}")
            return None
        finally:
            db.close()
    
    @staticmethod
    def get_disease_rules(disease_name: str) -> Optional[Dict[str, Any]]:
        """
        Get dietary rules for a specific disease
        
        Args:
            disease_name: Name of the disease
            
        Returns:
            Dictionary with disease rules or None if not found
        """
        db = SessionLocal()
        try:
            # Normalize disease name
            disease_name = disease_name.strip().lower()
            disease_map = {
                "tiểu đường": "Tiểu đường type 2",
                "đái tháo đường": "Tiểu đường type 2",
                "diabetes": "Tiểu đường type 2",
                "béo phì": "Béo phì",
                "obesity": "Béo phì",
                "huyết áp cao": "Cao huyết áp",
                "tăng huyết áp": "Cao huyết áp",
                "cao huyết áp": "Cao huyết áp",
                "hypertension": "Cao huyết áp",
                "gout": "Gout"
            }
            
            standardized_name = disease_map.get(disease_name, disease_name.title())
            
            # Query database
            medical_condition = db.query(MedicalCondition).filter(
                MedicalCondition.name.ilike(f"%{standardized_name}%")
            ).first()
            
            if medical_condition:
                # Get disease recommendations
                recommendations = db.query(DiseaseRecommendation).filter(
                    DiseaseRecommendation.condition_id == medical_condition.id
                ).all()
                
                nutrient_limits = {}
                for rec in recommendations:
                    nutrient_limits[rec.nutrient.name] = {
                        "min": float(rec.recommended_daily_min) if rec.recommended_daily_min else None,
                        "max": float(rec.recommended_daily_max) if rec.recommended_daily_max else None,
                        "notes": rec.notes
                    }
                
                return {
                    "disease_name": medical_condition.name,
                    "code": medical_condition.code,
                    "description": medical_condition.description,
                    "recommended_diet_type": medical_condition.recommended_diet_type,
                    "warnings": medical_condition.warnings,
                    "recommended_calories_multiplier": float(medical_condition.recommended_calories_multiplier) if medical_condition.recommended_calories_multiplier else 1.0,
                    "nutrient_limits": nutrient_limits,
                    "guidelines": medical_condition.description or medical_condition.warnings
                }
            
            # Fallback to hardcoded rules if not in database
            return DatabaseHelpers._get_fallback_disease_rules(standardized_name)
            
        except Exception as e:
            print(f"Error getting disease rules: {e}")
            return DatabaseHelpers._get_fallback_disease_rules(disease_name)
        finally:
            db.close()
    
    @staticmethod
    def _get_fallback_disease_rules(disease_name: str) -> Optional[Dict[str, Any]]:
        """Fallback disease rules when database is empty"""
        rules = {
            "Tiểu đường": {
                "disease_name": "Tiểu đường",
                "max_daily_calories": 1800,
                "max_daily_carbs": 150.0,
                "foods_to_avoid": ["đường trắng", "bánh ngọt", "nước ngọt", "cơm trắng"],
                "recommended_foods": ["rau xanh", "cá", "trứng", "yến mạch"],
                "guidelines": "Ăn ít đường, nhiều chất xơ. Chia nhỏ bữa ăn."
            },
            "Béo phì": {
                "disease_name": "Béo phì",
                "max_daily_calories": 1500,
                "max_daily_fat": 50.0,
                "foods_to_avoid": ["đồ chiên", "thức ăn nhanh", "nước ngọt"],
                "recommended_foods": ["rau củ", "trái cây ít đường", "ức gà", "cá"],
                "guidelines": "Giảm calo, tăng vận động. Ăn nhiều rau, ít chất béo."
            },
            "Huyết áp cao": {
                "disease_name": "Huyết áp cao",
                "max_daily_sodium": 1500.0,
                "foods_to_avoid": ["muối", "nước mắm", "đồ hộp", "thịt hun khói"],
                "recommended_foods": ["chuối", "rau bina", "cá hồi", "yến mạch"],
                "guidelines": "Hạn chế muối, tăng kali. Ăn nhiều rau quả."
            }
        }
        return rules.get(disease_name)
    
    @staticmethod
    def search_foods_by_category(category: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search foods by category
        
        Args:
            category: Food category
            limit: Maximum number of results
            
        Returns:
            List of food items
        """
        db = SessionLocal()
        try:
            foods = db.query(Food).filter(
                Food.category.ilike(f"%{category}%")
            ).limit(limit).all()
            
            result = []
            for food in foods:
                food_data = {
                    "name": food.name,
                    "category": food.category,
                    "calories": float(food.calories_per_100g) if food.calories_per_100g else 0,
                    "high_glycemic": food.high_glycemic,
                    "high_sodium": food.high_sodium
                }
                
                # Get nutrients
                for nutrient_rel in food.nutrients:
                    nutrient_name = nutrient_rel.nutrient.name.lower()
                    amount = float(nutrient_rel.amount_per_100g) if nutrient_rel.amount_per_100g else 0
                    
                    if 'protein' in nutrient_name:
                        food_data['protein'] = amount
                    elif 'carb' in nutrient_name:
                        food_data['carbs'] = amount
                    elif 'fat' in nutrient_name:
                        food_data['fat'] = amount
                
                result.append(food_data)
            
            return result
            
        except Exception as e:
            print(f"Error searching foods by category: {e}")
            return []
        finally:
            db.close()
    
    @staticmethod
    def get_suitable_foods_for_disease(disease_name: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Get foods suitable for a specific disease
        
        Args:
            disease_name: Name of the disease
            limit: Maximum number of results
            
        Returns:
            List of suitable food items
        """
        db = SessionLocal()
        try:
            disease_name = disease_name.strip().lower()
            
            if "tiểu đường" in disease_name or "diabetes" in disease_name:
                # Low glycemic foods
                foods = db.query(Food).filter(
                    Food.high_glycemic == False
                ).order_by(Food.calories_per_100g.asc()).limit(limit).all()
            elif "huyết áp" in disease_name or "hypertension" in disease_name:
                # Low sodium foods
                foods = db.query(Food).filter(
                    Food.high_sodium == False
                ).order_by(Food.calories_per_100g.asc()).limit(limit).all()
            else:  # Béo phì or others - low calorie foods
                foods = db.query(Food).filter(
                    Food.calories_per_100g < 100
                ).order_by(Food.calories_per_100g.asc()).limit(limit).all()
            
            result = []
            for food in foods:
                food_data = {
                    "name": food.name,
                    "calories": float(food.calories_per_100g) if food.calories_per_100g else 0,
                    "category": food.category or "khác",
                    "protein": 0,
                    "carbs": 0
                }
                
                # Get protein and carbs from nutrients
                for nutrient_rel in food.nutrients:
                    nutrient_name = nutrient_rel.nutrient.name.lower()
                    amount = float(nutrient_rel.amount_per_100g) if nutrient_rel.amount_per_100g else 0
                    
                    if 'protein' in nutrient_name:
                        food_data['protein'] = amount
                    elif 'carb' in nutrient_name:
                        food_data['carbs'] = amount
                
                result.append(food_data)
            
            return result if result else DatabaseHelpers._get_fallback_suitable_foods(disease_name)
            
        except Exception as e:
            print(f"Error getting suitable foods: {e}")
            return DatabaseHelpers._get_fallback_suitable_foods(disease_name)
        finally:
            db.close()
    
    @staticmethod
    def _get_fallback_suitable_foods(disease_name: str) -> List[Dict[str, Any]]:
        """Fallback suitable foods when database is empty"""
        if "tiểu đường" in disease_name.lower():
            return [
                {"name": "Rau xanh", "calories": 25, "protein": 3, "carbs": 5, "category": "rau"},
                {"name": "Cá hồi", "calories": 180, "protein": 25, "carbs": 0, "category": "protein"},
                {"name": "Trứng gà", "calories": 155, "protein": 13, "carbs": 1, "category": "protein"},
                {"name": "Yến mạch", "calories": 68, "protein": 2.5, "carbs": 12, "category": "ngũ cốc"},
                {"name": "Quả bơ", "calories": 160, "protein": 2, "carbs": 9, "category": "trái cây"}
            ]
        elif "béo phì" in disease_name.lower():
            return [
                {"name": "Dưa chuột", "calories": 16, "protein": 0.7, "carbs": 4, "category": "rau"},
                {"name": "Cà chua", "calories": 18, "protein": 0.9, "carbs": 4, "category": "rau"},
                {"name": "Ức gà luộc", "calories": 165, "protein": 31, "carbs": 0, "category": "protein"},
                {"name": "Rau muống", "calories": 19, "protein": 2.6, "carbs": 3, "category": "rau"},
                {"name": "Cá diếc", "calories": 90, "protein": 18, "carbs": 0, "category": "protein"}
            ]
        else:  # Huyết áp cao
            return [
                {"name": "Chuối", "calories": 89, "protein": 1.1, "carbs": 23, "category": "trái cây"},
                {"name": "Rau bina", "calories": 23, "protein": 2.9, "carbs": 4, "category": "rau"},
                {"name": "Yến mạch", "calories": 68, "protein": 2.5, "carbs": 12, "category": "ngũ cốc"},
                {"name": "Cá thu", "calories": 140, "protein": 25, "carbs": 0, "category": "protein"},
                {"name": "Đậu đen", "calories": 132, "protein": 9, "carbs": 23, "category": "đậu"}
            ]
    
    @staticmethod
    def estimate_meal_calories(food_items: List[str], portions: List[float] = None) -> Dict[str, Any]:
        """
        Estimate total calories for a meal
        
        Args:
            food_items: List of food names
            portions: List of portion sizes (default 1.0 for each)
            
        Returns:
            Dictionary with calorie estimation
        """
        if portions is None:
            portions = [1.0] * len(food_items)
        
        total_calories = 0
        total_protein = 0
        total_carbs = 0
        total_fat = 0
        found_items = []
        
        for i, food_name in enumerate(food_items):
            portion = portions[i] if i < len(portions) else 1.0
            nutrition = DatabaseHelpers.get_food_nutrition(food_name)
            
            if nutrition:
                calories = (nutrition.get('calories', 0) or 0) * portion
                protein = (nutrition.get('protein', 0) or 0) * portion
                carbs = (nutrition.get('carbs', 0) or 0) * portion
                fat = (nutrition.get('fat', 0) or 0) * portion
                
                total_calories += calories
                total_protein += protein
                total_carbs += carbs
                total_fat += fat
                
                found_items.append({
                    "name": food_name,
                    "portion": portion,
                    "calories": calories,
                    "protein": protein,
                    "carbs": carbs,
                    "fat": fat
                })
        
        return {
            "total_calories": round(total_calories, 1),
            "total_protein": round(total_protein, 1),
            "total_carbs": round(total_carbs, 1),
            "total_fat": round(total_fat, 1),
            "items": found_items,
            "found_items_count": len(found_items),
            "total_items_count": len(food_items)
        }


# Convenience functions for backward compatibility
def get_food_nutrition(food_name: str) -> Optional[Dict[str, Any]]:
    """Get nutrition info for a food item"""
    return DatabaseHelpers.get_food_nutrition(food_name)


def get_disease_rules(disease_name: str) -> Optional[Dict[str, Any]]:
    """Get dietary rules for a disease"""
    return DatabaseHelpers.get_disease_rules(disease_name)


def get_suitable_foods_for_disease(disease_name: str, limit: int = 5) -> List[Dict[str, Any]]:
    """Get suitable foods for a disease"""
    return DatabaseHelpers.get_suitable_foods_for_disease(disease_name, limit)