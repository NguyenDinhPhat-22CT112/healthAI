"""
Data Collector - Thu thập training data từ PostgreSQL, MongoDB và Images
"""
import os
import json
from typing import List, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from pymongo import MongoClient

from app.database.connection import get_db_context
from app.database.models import FoodItem, MealAnalysis, RecipeQuery, User, HealthProfile
from app.config import settings


class TrainingDataCollector:
    """Thu thập và chuẩn bị training data"""
    
    def __init__(self):
        # MongoDB connection
        try:
            self.mongo_client = MongoClient(settings.mongo_url, serverSelectionTimeoutMS=5000)
            self.mongo_db = self.mongo_client[settings.get_mongo_db_name()]
            self.mongo_available = True
        except:
            self.mongo_available = False
            print("⚠️  MongoDB not available")
    
    def collect_nutrition_data(self) -> List[Dict[str, Any]]:
        """Thu thập nutrition data từ PostgreSQL"""
        print("\n" + "="*70)
        print("COLLECTING NUTRITION DATA FROM POSTGRESQL")
        print("="*70)
        
        training_examples = []
        
        with get_db_context() as db:
            # Get all food items
            food_items = db.query(FoodItem).all()
            print(f"Found {len(food_items)} food items")
            
            for food in food_items:
                # Example 1: Hỏi về calo
                example1 = {
                    "type": "nutrition_query",
                    "input": {
                        "query": f"{food.name} có bao nhiêu calo?",
                        "food_name": food.name
                    },
                    "output": {
                        "answer": f"{food.name} có {food.calories} calo (trên 100g).\n\n"
                                 f"**Dinh dưỡng:**\n"
                                 f"- Protein: {food.protein}g\n"
                                 f"- Carbs: {food.carbs}g\n"
                                 f"- Fat: {food.fat}g\n"
                                 f"- Chất xơ: {food.fiber}g",
                        "calories": food.calories,
                        "protein": food.protein,
                        "carbs": food.carbs,
                        "fat": food.fat
                    },
                    "metadata": {
                        "source": "postgresql",
                        "food_id": food.id
                    }
                }
                training_examples.append(example1)
                
                # Example 2: Phân tích dinh dưỡng
                example2 = {
                    "type": "nutrition_analysis",
                    "input": {
                        "query": f"Phân tích dinh dưỡng của {food.name}",
                        "food_name": food.name
                    },
                    "output": {
                        "answer": self._generate_nutrition_analysis(food),
                        "nutrition_data": {
                            "calories": food.calories,
                            "protein": food.protein,
                            "carbs": food.carbs,
                            "fat": food.fat,
                            "fiber": food.fiber
                        }
                    },
                    "metadata": {
                        "source": "postgresql",
                        "food_id": food.id
                    }
                }
                training_examples.append(example2)
        
        print(f"✓ Created {len(training_examples)} nutrition examples")
        return training_examples
    
    def collect_meal_analysis_data(self) -> List[Dict[str, Any]]:
        """Thu thập meal analysis data từ PostgreSQL"""
        print("\n" + "="*70)
        print("COLLECTING MEAL ANALYSIS DATA")
        print("="*70)
        
        training_examples = []
        
        with get_db_context() as db:
            # Get meal analyses with user health profiles
            meals = db.query(MealAnalysis).join(User).join(HealthProfile).limit(1000).all()
            print(f"Found {len(meals)} meal analyses")
            
            for meal in meals:
                if not meal.image_path or not os.path.exists(meal.image_path):
                    continue
                
                # Get user's health profile
                health_profile = db.query(HealthProfile).filter(
                    HealthProfile.user_id == meal.user_id
                ).first()
                
                example = {
                    "type": "meal_analysis_with_image",
                    "input": {
                        "image_path": meal.image_path,
                        "query": "Phân tích bữa ăn này",
                        "user_context": {
                            "diseases": health_profile.diseases if health_profile else [],
                            "allergies": health_profile.allergies if health_profile else [],
                            "dietary_restrictions": health_profile.dietary_restrictions if health_profile else []
                        }
                    },
                    "output": {
                        "detected_foods": meal.detected_foods,
                        "nutrition": {
                            "calories": meal.total_calories,
                            "protein": meal.total_protein,
                            "carbs": meal.total_carbs,
                            "fat": meal.total_fat
                        },
                        "health_assessment": meal.health_assessment,
                        "recommendations": meal.recommendations,
                        "warnings": meal.warnings,
                        "suitability_score": meal.suitability_score
                    },
                    "metadata": {
                        "source": "postgresql",
                        "meal_id": meal.id,
                        "has_diseases": len(health_profile.diseases) > 0 if health_profile else False
                    }
                }
                training_examples.append(example)
        
        print(f"✓ Created {len(training_examples)} meal analysis examples")
        return training_examples
    
    def collect_recipe_data(self) -> List[Dict[str, Any]]:
        """Thu thập recipe data từ PostgreSQL"""
        print("\n" + "="*70)
        print("COLLECTING RECIPE DATA")
        print("="*70)
        
        training_examples = []
        
        with get_db_context() as db:
            recipes = db.query(RecipeQuery).join(User).join(HealthProfile).limit(1000).all()
            print(f"Found {len(recipes)} recipe queries")
            
            for recipe in recipes:
                health_profile = db.query(HealthProfile).filter(
                    HealthProfile.user_id == recipe.user_id
                ).first()
                
                example = {
                    "type": "recipe_suggestion",
                    "input": {
                        "query": f"Gợi ý món ăn từ: {', '.join(recipe.ingredients)}",
                        "ingredients": recipe.ingredients,
                        "preferences": recipe.preferences,
                        "user_context": {
                            "diseases": health_profile.diseases if health_profile else [],
                            "dietary_restrictions": health_profile.dietary_restrictions if health_profile else []
                        }
                    },
                    "output": {
                        "recipes": recipe.suggested_recipes,
                        "health_adapted": recipe.health_adapted,
                        "health_notes": recipe.health_notes
                    },
                    "metadata": {
                        "source": "postgresql",
                        "recipe_id": recipe.id
                    }
                }
                training_examples.append(example)
        
        print(f"✓ Created {len(training_examples)} recipe examples")
        return training_examples
    
    def collect_mongodb_interactions(self) -> List[Dict[str, Any]]:
        """Thu thập interaction data từ MongoDB"""
        print("\n" + "="*70)
        print("COLLECTING INTERACTION DATA FROM MONGODB")
        print("="*70)
        
        if not self.mongo_available:
            print("⚠️  MongoDB not available, skipping")
            return []
        
        training_examples = []
        
        try:
            # Get interactions with positive feedback
            interactions = self.mongo_db.agent_interactions.find({
                "feedback.feedback_type": "positive",
                "feedback.rating": {"$gte": 4}
            }).limit(1000)
            
            count = 0
            for interaction in interactions:
                example = {
                    "type": "general_interaction",
                    "input": {
                        "query": interaction.get("user_query"),
                        "user_context": interaction.get("user_context", {})
                    },
                    "output": {
                        "answer": interaction.get("agent_response")
                    },
                    "metadata": {
                        "source": "mongodb",
                        "interaction_id": interaction.get("interaction_id"),
                        "rating": interaction.get("feedback", {}).get("rating")
                    }
                }
                training_examples.append(example)
                count += 1
            
            print(f"✓ Created {count} interaction examples from MongoDB")
            
        except Exception as e:
            print(f"⚠️  Error collecting from MongoDB: {e}")
        
        return training_examples
    
    def collect_all_data(self) -> Dict[str, List[Dict]]:
        """Thu thập tất cả training data"""
        print("\n" + "="*70)
        print("COLLECTING ALL TRAINING DATA")
        print("="*70)
        print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        all_data = {
            "nutrition_data": self.collect_nutrition_data(),
            "meal_analysis_data": self.collect_meal_analysis_data(),
            "recipe_data": self.collect_recipe_data(),
            "mongodb_interactions": self.collect_mongodb_interactions()
        }
        
        total = sum(len(data) for data in all_data.values())
        
        print("\n" + "="*70)
        print("COLLECTION SUMMARY")
        print("="*70)
        print(f"Nutrition examples: {len(all_data['nutrition_data'])}")
        print(f"Meal analysis examples: {len(all_data['meal_analysis_data'])}")
        print(f"Recipe examples: {len(all_data['recipe_data'])}")
        print(f"MongoDB interactions: {len(all_data['mongodb_interactions'])}")
        print(f"Total examples: {total}")
        
        return all_data
    
    def _generate_nutrition_analysis(self, food: FoodItem) -> str:
        """Generate nutrition analysis text"""
        
        analysis = f"Phân tích dinh dưỡng của {food.name}:\n\n"
        analysis += f"**Năng lượng:** {food.calories} calo (trên 100g)\n\n"
        analysis += f"**Thành phần dinh dưỡng:**\n"
        analysis += f"- Protein: {food.protein}g - Xây dựng và sửa chữa cơ bắp\n"
        analysis += f"- Carbs: {food.carbs}g - Nguồn năng lượng chính\n"
        analysis += f"- Fat: {food.fat}g - Năng lượng dự trữ\n"
        analysis += f"- Chất xơ: {food.fiber}g - Hỗ trợ tiêu hóa\n\n"
        
        # Đánh giá
        if food.calories < 100:
            analysis += "**Đánh giá:** Thực phẩm ít calo, phù hợp cho giảm cân."
        elif food.calories < 200:
            analysis += "**Đánh giá:** Thực phẩm calo trung bình, cân bằng dinh dưỡng."
        else:
            analysis += "**Đánh giá:** Thực phẩm giàu năng lượng, phù hợp cho người hoạt động nhiều."
        
        return analysis
    
    def save_collected_data(self, data: Dict[str, List[Dict]], output_dir: str = "training_data"):
        """Lưu collected data"""
        os.makedirs(output_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(output_dir, f"collected_data_{timestamp}.json")
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"\n✓ Data saved to: {filename}")
        return filename
