"""
Database operations cho training data
Sử dụng MongoDB để lưu interactions và feedback
"""
from pymongo import MongoClient, DESCENDING
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from app.config import settings
from app.models.training import (
    AgentInteraction, 
    UserFeedback, 
    TrainingDataset,
    InteractionType,
    FeedbackType
)
import uuid


class TrainingDatabase:
    """Database handler cho training data"""
    
    def __init__(self):
        self._client = None
        self._db = None
        self._interactions_collection = None
        self._feedback_collection = None
        self._datasets_collection = None
        self._initialized = False
    
    def _ensure_connection(self):
        """Lazy initialization - chỉ kết nối khi cần"""
        if self._initialized:
            return
        
        try:
            self._client = MongoClient(settings.mongo_url, serverSelectionTimeoutMS=5000)
            self._db = self._client[settings.get_mongo_db_name()]
            self._interactions_collection = self._db["agent_interactions"]
            self._feedback_collection = self._db["user_feedback"]
            self._datasets_collection = self._db["training_datasets"]
            
            # Create indexes
            self._create_indexes()
            self._initialized = True
        except Exception as e:
            print(f"Warning: Could not connect to MongoDB for training: {e}")
            print("Training features will be disabled. Please check MongoDB connection.")
    
    @property
    def client(self):
        self._ensure_connection()
        return self._client
    
    @property
    def db(self):
        self._ensure_connection()
        return self._db
    
    @property
    def interactions_collection(self):
        self._ensure_connection()
        return self._interactions_collection
    
    @property
    def feedback_collection(self):
        self._ensure_connection()
        return self._feedback_collection
    
    @property
    def datasets_collection(self):
        self._ensure_connection()
        return self._datasets_collection
    
    def _create_indexes(self):
        """Tạo indexes cho performance"""
        try:
            # Interactions indexes
            self._interactions_collection.create_index("interaction_id", unique=True)
            self._interactions_collection.create_index("user_id")
            self._interactions_collection.create_index("interaction_type")
            self._interactions_collection.create_index("timestamp")
            self._interactions_collection.create_index([("timestamp", DESCENDING)])
            
            # Feedback indexes
            self._feedback_collection.create_index("interaction_id")
            self._feedback_collection.create_index("user_id")
            self._feedback_collection.create_index("feedback_type")
            self._feedback_collection.create_index("rating")
            
            # Datasets indexes
            self._datasets_collection.create_index("dataset_id", unique=True)
        except Exception as e:
            print(f"Warning: Could not create indexes: {e}")
    
    # ==================== INTERACTIONS ====================
    
    def save_interaction(self, interaction: AgentInteraction) -> str:
        """
        Lưu agent interaction vào database
        
        Args:
            interaction: AgentInteraction object
            
        Returns:
            interaction_id
        """
        interaction_dict = interaction.model_dump()
        self.interactions_collection.insert_one(interaction_dict)
        return interaction.interaction_id
    
    def get_interaction(self, interaction_id: str) -> Optional[AgentInteraction]:
        """Lấy interaction theo ID"""
        doc = self.interactions_collection.find_one({"interaction_id": interaction_id})
        if doc:
            doc.pop("_id", None)
            return AgentInteraction(**doc)
        return None
    
    def get_interactions_by_user(
        self, 
        user_id: str, 
        limit: int = 100,
        skip: int = 0
    ) -> List[AgentInteraction]:
        """Lấy interactions của một user"""
        cursor = self.interactions_collection.find(
            {"user_id": user_id}
        ).sort("timestamp", DESCENDING).skip(skip).limit(limit)
        
        interactions = []
        for doc in cursor:
            doc.pop("_id", None)
            interactions.append(AgentInteraction(**doc))
        return interactions
    
    def get_interactions_by_type(
        self,
        interaction_type: InteractionType,
        limit: int = 100,
        skip: int = 0
    ) -> List[AgentInteraction]:
        """Lấy interactions theo loại"""
        cursor = self.interactions_collection.find(
            {"interaction_type": interaction_type}
        ).sort("timestamp", DESCENDING).skip(skip).limit(limit)
        
        interactions = []
        for doc in cursor:
            doc.pop("_id", None)
            interactions.append(AgentInteraction(**doc))
        return interactions
    
    def get_interactions_with_feedback(
        self,
        feedback_type: Optional[FeedbackType] = None,
        min_rating: Optional[int] = None,
        limit: int = 100
    ) -> List[AgentInteraction]:
        """Lấy interactions có feedback (dùng cho training)"""
        query = {"feedback": {"$ne": None}}
        
        if feedback_type:
            query["feedback.feedback_type"] = feedback_type
        
        if min_rating:
            query["feedback.rating"] = {"$gte": min_rating}
        
        cursor = self.interactions_collection.find(query).limit(limit)
        
        interactions = []
        for doc in cursor:
            doc.pop("_id", None)
            interactions.append(AgentInteraction(**doc))
        return interactions
    
    # ==================== FEEDBACK ====================
    
    def save_feedback(self, feedback: UserFeedback) -> str:
        """
        Lưu user feedback và update interaction
        
        Args:
            feedback: UserFeedback object
            
        Returns:
            feedback_id
        """
        # Save feedback
        feedback_dict = feedback.model_dump()
        result = self.feedback_collection.insert_one(feedback_dict)
        
        # Update interaction với feedback
        self.interactions_collection.update_one(
            {"interaction_id": feedback.interaction_id},
            {"$set": {"feedback": feedback_dict}}
        )
        
        return str(result.inserted_id)
    
    def get_feedback_by_interaction(self, interaction_id: str) -> Optional[UserFeedback]:
        """Lấy feedback của một interaction"""
        doc = self.feedback_collection.find_one({"interaction_id": interaction_id})
        if doc:
            doc.pop("_id", None)
            return UserFeedback(**doc)
        return None
    
    def get_feedback_stats(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Lấy thống kê feedback"""
        query = {}
        if start_date or end_date:
            query["timestamp"] = {}
            if start_date:
                query["timestamp"]["$gte"] = start_date
            if end_date:
                query["timestamp"]["$lte"] = end_date
        
        total = self.feedback_collection.count_documents(query)
        
        positive = self.feedback_collection.count_documents({
            **query,
            "feedback_type": FeedbackType.POSITIVE
        })
        
        negative = self.feedback_collection.count_documents({
            **query,
            "feedback_type": FeedbackType.NEGATIVE
        })
        
        neutral = self.feedback_collection.count_documents({
            **query,
            "feedback_type": FeedbackType.NEUTRAL
        })
        
        # Average rating
        pipeline = [
            {"$match": query},
            {"$group": {
                "_id": None,
                "avg_rating": {"$avg": "$rating"}
            }}
        ]
        avg_result = list(self.feedback_collection.aggregate(pipeline))
        avg_rating = avg_result[0]["avg_rating"] if avg_result else 0
        
        return {
            "total_feedback": total,
            "positive": positive,
            "negative": negative,
            "neutral": neutral,
            "average_rating": round(avg_rating, 2),
            "satisfaction_rate": round(positive / total, 2) if total > 0 else 0
        }
    
    # ==================== TRAINING DATASETS ====================
    
    def create_training_dataset(
        self,
        name: str,
        description: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None
    ) -> TrainingDataset:
        """
        Tạo training dataset từ interactions có feedback tốt
        
        Args:
            name: Tên dataset
            description: Mô tả
            filters: Filters để chọn interactions (min_rating, interaction_types, etc.)
            
        Returns:
            TrainingDataset object
        """
        # Build query
        query = {"feedback": {"$ne": None}}
        
        if filters:
            if filters.get("min_rating"):
                query["feedback.rating"] = {"$gte": filters["min_rating"]}
            
            if filters.get("interaction_types"):
                query["interaction_type"] = {"$in": filters["interaction_types"]}
            
            if filters.get("start_date"):
                query.setdefault("timestamp", {})["$gte"] = filters["start_date"]
            
            if filters.get("end_date"):
                query.setdefault("timestamp", {})["$lte"] = filters["end_date"]
        
        # Get interactions
        cursor = self.interactions_collection.find(query)
        interactions = []
        positive_count = 0
        negative_count = 0
        
        for doc in cursor:
            doc.pop("_id", None)
            interaction = AgentInteraction(**doc)
            interactions.append(interaction)
            
            if interaction.feedback:
                if interaction.feedback.feedback_type == FeedbackType.POSITIVE:
                    positive_count += 1
                elif interaction.feedback.feedback_type == FeedbackType.NEGATIVE:
                    negative_count += 1
        
        # Create dataset
        dataset = TrainingDataset(
            dataset_id=f"ds_{uuid.uuid4().hex[:8]}",
            name=name,
            description=description,
            interactions=interactions,
            total_interactions=len(interactions),
            positive_feedback_count=positive_count,
            negative_feedback_count=negative_count
        )
        
        # Save to database
        dataset_dict = dataset.model_dump()
        self.datasets_collection.insert_one(dataset_dict)
        
        return dataset
    
    def get_training_dataset(self, dataset_id: str) -> Optional[TrainingDataset]:
        """Lấy training dataset theo ID"""
        doc = self.datasets_collection.find_one({"dataset_id": dataset_id})
        if doc:
            doc.pop("_id", None)
            return TrainingDataset(**doc)
        return None
    
    def list_training_datasets(self, limit: int = 50) -> List[TrainingDataset]:
        """List tất cả training datasets"""
        cursor = self.datasets_collection.find().sort("created_at", DESCENDING).limit(limit)
        
        datasets = []
        for doc in cursor:
            doc.pop("_id", None)
            datasets.append(TrainingDataset(**doc))
        return datasets
    
    # ==================== ANALYTICS ====================
    
    def get_training_metrics(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Lấy metrics cho training evaluation"""
        query = {}
        if start_date or end_date:
            query["timestamp"] = {}
            if start_date:
                query["timestamp"]["$gte"] = start_date
            if end_date:
                query["timestamp"]["$lte"] = end_date
        
        # Total interactions
        total_interactions = self.interactions_collection.count_documents(query)
        
        # Interactions with feedback
        feedback_query = {**query, "feedback": {"$ne": None}}
        interactions_with_feedback = self.interactions_collection.count_documents(feedback_query)
        
        # Feedback stats
        feedback_stats = self.get_feedback_stats(start_date, end_date)
        
        # Average response time
        pipeline = [
            {"$match": query},
            {"$group": {
                "_id": None,
                "avg_response_time": {"$avg": "$response_time_ms"}
            }}
        ]
        avg_result = list(self.interactions_collection.aggregate(pipeline))
        avg_response_time = avg_result[0]["avg_response_time"] if avg_result else 0
        
        # Accuracy (based on is_correct field)
        correct_query = {**query, "is_correct": True}
        correct_count = self.interactions_collection.count_documents(correct_query)
        accuracy = correct_count / interactions_with_feedback if interactions_with_feedback > 0 else 0
        
        return {
            "total_interactions": total_interactions,
            "interactions_with_feedback": interactions_with_feedback,
            "feedback_coverage": round(interactions_with_feedback / total_interactions, 2) if total_interactions > 0 else 0,
            "accuracy": round(accuracy, 2),
            "avg_response_time_ms": round(avg_response_time, 2),
            **feedback_stats
        }


# Singleton instance
training_db = TrainingDatabase()
