"""
Simple Database Query Tool
"""
from langchain.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Optional
import json


class DBQueryInput(BaseModel):
    """Input for database query tool"""
    query_type: str = Field(description="Type of query: nutrition_estimate, food_search")
    food_name: Optional[str] = Field(default=None, description="Name of food to search")


class DBQueryTool(BaseTool):
    """
    Simple database query tool for food information
    """
    
    name: str = "db_query"
    description: str = "Query database for food nutrition information"
    args_schema: type = DBQueryInput

    def _run(self, query_type: str, food_name: Optional[str] = None) -> str:
        """Execute database query"""
        try:
            if query_type == "nutrition_estimate" and food_name:
                return self._get_nutrition_estimate(food_name)
            elif query_type == "food_search" and food_name:
                return self._search_food(food_name)
            else:
                return json.dumps({"error": "Invalid query parameters"})
        except Exception as e:
            return json.dumps({"error": str(e)})

    def _get_nutrition_estimate(self, food_name: str) -> str:
        """Get nutrition estimate for a food"""
        # Simple nutrition database
        nutrition_db = {
            "phở bò": {
                "nutrition_per_serving": {
                    "calories": 450,
                    "protein": 30,
                    "carbs": 45,
                    "fat": 15,
                    "fiber": 3,
                    "sodium": 1200
                }
            },
            "cơm trắng": {
                "nutrition_per_serving": {
                    "calories": 130,
                    "protein": 2.7,
                    "carbs": 28,
                    "fat": 0.3,
                    "fiber": 0.4,
                    "sodium": 1
                }
            },
            "bánh mì": {
                "nutrition_per_serving": {
                    "calories": 250,
                    "protein": 8,
                    "carbs": 40,
                    "fat": 8,
                    "fiber": 2,
                    "sodium": 400
                }
            }
        }
        
        # Fuzzy search
        food_lower = food_name.lower()
        for key, data in nutrition_db.items():
            if food_lower in key or key in food_lower:
                return json.dumps(data, ensure_ascii=False)
        
        # Default estimate
        return json.dumps({
            "nutrition_per_serving": {
                "calories": 300,
                "protein": 15,
                "carbs": 35,
                "fat": 10,
                "fiber": 2,
                "sodium": 500
            },
            "note": "Estimated values"
        }, ensure_ascii=False)

    def _search_food(self, food_name: str) -> str:
        """Search for food in database"""
        # Simple food search
        foods = [
            "Phở bò", "Cơm trắng", "Bánh mì", "Gỏi cuốn", 
            "Bún bò Huế", "Cơm tấm", "Chả cá", "Nem nướng"
        ]
        
        food_lower = food_name.lower()
        matches = [food for food in foods if food_lower in food.lower() or food.lower() in food_lower]
        
        return json.dumps({
            "query": food_name,
            "matches": matches[:5],
            "total": len(matches)
        }, ensure_ascii=False)