"""
Food Service - Business logic for food operations
"""
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from typing import List, Dict, Optional
import pandas as pd
from app.config import settings


class FoodService:
    """Service for food-related operations"""
    
    def __init__(self):
        """Initialize database connection"""
        self.engine = create_engine(settings.postgres_url)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
    
    def get_all_foods(self, limit: int = 100, offset: int = 0) -> List[Dict]:
        """Get all foods with pagination"""
        query = text("""
            SELECT 
                food_id,
                name,
                description,
                region,
                category,
                calories,
                protein,
                carbs,
                fat,
                fiber,
                sugar,
                sodium,
                is_vegetarian,
                is_vegan
            FROM foods
            ORDER BY food_id
            LIMIT :limit OFFSET :offset
        """)
        
        result = self.session.execute(query, {"limit": limit, "offset": offset})
        foods = []
        for row in result:
            foods.append({
                'food_id': row[0],
                'name': row[1],
                'description': row[2],
                'region': row[3],
                'category': row[4],
                'calories': float(row[5]) if row[5] else 0,
                'protein': float(row[6]) if row[6] else 0,
                'carbs': float(row[7]) if row[7] else 0,
                'fat': float(row[8]) if row[8] else 0,
                'fiber': float(row[9]) if row[9] else 0,
                'sugar': float(row[10]) if row[10] else 0,
                'sodium': float(row[11]) if row[11] else 0,
                'is_vegetarian': row[12],
                'is_vegan': row[13]
            })
        
        return foods
    
    def get_food_by_id(self, food_id: int) -> Optional[Dict]:
        """Get food by ID"""
        query = text("""
            SELECT 
                f.food_id,
                f.name,
                f.description,
                f.region,
                f.category,
                f.calories,
                f.protein,
                f.carbs,
                f.fat,
                f.fiber,
                f.sugar,
                f.sodium,
                f.cholesterol,
                f.is_vegetarian,
                f.is_vegan,
                f.is_gluten_free,
                f.spicy_level,
                f.preparation_time,
                f.difficulty_level
            FROM foods f
            WHERE f.food_id = :food_id
        """)
        
        result = self.session.execute(query, {"food_id": food_id}).fetchone()
        
        if not result:
            return None
        
        return {
            'food_id': result[0],
            'name': result[1],
            'description': result[2],
            'region': result[3],
            'category': result[4],
            'calories': float(result[5]) if result[5] else 0,
            'protein': float(result[6]) if result[6] else 0,
            'carbs': float(result[7]) if result[7] else 0,
            'fat': float(result[8]) if result[8] else 0,
            'fiber': float(result[9]) if result[9] else 0,
            'sugar': float(result[10]) if result[10] else 0,
            'sodium': float(result[11]) if result[11] else 0,
            'cholesterol': float(result[12]) if result[12] else 0,
            'is_vegetarian': result[13],
            'is_vegan': result[14],
            'is_gluten_free': result[15],
            'spicy_level': result[16],
            'preparation_time': result[17],
            'difficulty_level': result[18]
        }
    
    def search_foods(self, query: str, limit: int = 20) -> List[Dict]:
        """Search foods by name"""
        sql = text("""
            SELECT 
                food_id,
                name,
                description,
                region,
                category,
                calories,
                protein,
                carbs,
                fat
            FROM foods
            WHERE name ILIKE :query OR description ILIKE :query
            ORDER BY name
            LIMIT :limit
        """)
        
        result = self.session.execute(sql, {"query": f"%{query}%", "limit": limit})
        
        foods = []
        for row in result:
            foods.append({
                'food_id': row[0],
                'name': row[1],
                'description': row[2],
                'region': row[3],
                'category': row[4],
                'calories': float(row[5]) if row[5] else 0,
                'protein': float(row[6]) if row[6] else 0,
                'carbs': float(row[7]) if row[7] else 0,
                'fat': float(row[8]) if row[8] else 0
            })
        
        return foods
    
    def get_foods_by_health_condition(self, condition: str) -> List[Dict]:
        """Get recommended foods for health condition"""
        # Get health rules for condition
        rules_query = text("""
            SELECT 
                nutrient_name,
                operator,
                threshold_value,
                recommendation
            FROM health_rules
            WHERE disease_name = :condition AND is_active = true
        """)
        
        rules = self.session.execute(rules_query, {"condition": condition}).fetchall()
        
        if not rules:
            return []
        
        # Build dynamic query based on rules
        conditions = []
        for rule in rules:
            nutrient = rule[0]
            operator = rule[1]
            threshold = rule[2]
            
            if operator == '<':
                conditions.append(f"{nutrient} < {threshold}")
            elif operator == '>':
                conditions.append(f"{nutrient} > {threshold}")
            elif operator == '<=':
                conditions.append(f"{nutrient} <= {threshold}")
            elif operator == '>=':
                conditions.append(f"{nutrient} >= {threshold}")
        
        where_clause = " AND ".join(conditions) if conditions else "1=1"
        
        foods_query = text(f"""
            SELECT 
                food_id,
                name,
                description,
                calories,
                protein,
                carbs,
                fat,
                fiber,
                sugar,
                sodium
            FROM foods
            WHERE {where_clause}
            ORDER BY name
            LIMIT 20
        """)
        
        result = self.session.execute(foods_query)
        
        foods = []
        for row in result:
            foods.append({
                'food_id': row[0],
                'name': row[1],
                'description': row[2],
                'calories': float(row[3]) if row[3] else 0,
                'protein': float(row[4]) if row[4] else 0,
                'carbs': float(row[5]) if row[5] else 0,
                'fat': float(row[6]) if row[6] else 0,
                'fiber': float(row[7]) if row[7] else 0,
                'sugar': float(row[8]) if row[8] else 0,
                'sodium': float(row[9]) if row[9] else 0
            })
        
        return foods
    
    def get_food_ingredients(self, food_id: int) -> List[Dict]:
        """Get ingredients for a food"""
        query = text("""
            SELECT 
                i.ingredient_id,
                i.name,
                i.category,
                fi.quantity,
                fi.unit,
                i.calories_per_100g,
                i.protein_per_100g
            FROM food_ingredients fi
            JOIN ingredients i ON fi.ingredient_id = i.ingredient_id
            WHERE fi.food_id = :food_id
        """)
        
        result = self.session.execute(query, {"food_id": food_id})
        
        ingredients = []
        for row in result:
            ingredients.append({
                'ingredient_id': row[0],
                'name': row[1],
                'category': row[2],
                'quantity': float(row[3]) if row[3] else 0,
                'unit': row[4],
                'calories_per_100g': float(row[5]) if row[5] else 0,
                'protein_per_100g': float(row[6]) if row[6] else 0
            })
        
        return ingredients
    
    def analyze_food_nutrition(self, food_id: int) -> Dict:
        """Analyze food nutrition with detailed breakdown"""
        food = self.get_food_by_id(food_id)
        if not food:
            return {"error": "Food not found"}
        
        ingredients = self.get_food_ingredients(food_id)
        
        # Calculate nutrition score
        score = 0
        if food['protein'] > 20:
            score += 20
        if food['fiber'] > 5:
            score += 20
        if food['sugar'] < 10:
            score += 20
        if food['sodium'] < 500:
            score += 20
        if food['calories'] < 400:
            score += 20
        
        # Health classification
        if food['calories'] < 300 and food['protein'] > 15:
            health_class = 'healthy'
        elif food['protein'] > 25:
            health_class = 'high_protein'
        elif food['carbs'] < 30:
            health_class = 'low_carb'
        elif food['fiber'] > 8:
            health_class = 'high_fiber'
        else:
            health_class = 'balanced'
        
        return {
            'food': food,
            'ingredients': ingredients,
            'nutrition_score': score,
            'health_classification': health_class,
            'macros': {
                'protein': food['protein'],
                'carbs': food['carbs'],
                'fat': food['fat']
            },
            'micronutrients': {
                'fiber': food['fiber'],
                'sugar': food['sugar'],
                'sodium': food['sodium'],
                'cholesterol': food.get('cholesterol', 0)
            }
        }
    
    def close(self):
        """Close database connection"""
        self.session.close()


# Global instance
food_service = FoodService()
