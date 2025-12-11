"""
API routes cho training và feedback system
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
from datetime import datetime, timedelta
import uuid

from app.models.training import (
    AgentInteraction,
    UserFeedback,
    TrainingDataset,
    TrainingMetrics,
    FineTuneConfig,
    InteractionType,
    FeedbackType
)
from app.database.training_db import training_db

router = APIRouter(prefix="/training", tags=["Training & Feedback"])


# ==================== HEALTH CHECK ====================

@router.get("/health", response_model=dict)
async def training_health_check():
    """
    Check training system health
    """
    try:
        # Try to connect to MongoDB
        if training_db.client:
            # Ping database
            training_db.client.admin.command('ping')
            return {
                "status": "healthy",
                "mongodb": "connected",
                "database": settings.get_mongo_db_name(),
                "message": "Training system is operational"
            }
        else:
            return {
                "status": "degraded",
                "mongodb": "disconnected",
                "message": "Training features disabled. MongoDB not available."
            }
    except Exception as e:
        return {
            "status": "unhealthy",
            "mongodb": "error",
            "error": str(e),
            "message": "Training system unavailable"
        }


# ==================== FEEDBACK ENDPOINTS ====================

@router.post("/feedback", response_model=dict)
async def submit_feedback(feedback: UserFeedback):
    """
    Submit user feedback cho một interaction
    
    Feedback này sẽ được dùng để train agent
    """
    try:
        # Check MongoDB connection
        if not training_db._initialized and not training_db.client:
            raise HTTPException(
                status_code=503, 
                detail="Training system unavailable. MongoDB not connected."
            )
        
        # Check if interaction exists
        interaction = training_db.get_interaction(feedback.interaction_id)
        if not interaction:
            raise HTTPException(status_code=404, detail="Interaction not found")
        
        # Save feedback
        feedback_id = training_db.save_feedback(feedback)
        
        return {
            "status": "success",
            "message": "Feedback đã được lưu thành công",
            "feedback_id": feedback_id,
            "interaction_id": feedback.interaction_id
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving feedback: {str(e)}")


@router.get("/feedback/stats", response_model=dict)
async def get_feedback_statistics(
    days: int = Query(default=30, description="Số ngày để lấy stats")
):
    """
    Lấy thống kê feedback trong N ngày gần đây
    """
    try:
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        stats = training_db.get_feedback_stats(start_date, end_date)
        
        return {
            "status": "success",
            "period": f"Last {days} days",
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            **stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting stats: {str(e)}")


# ==================== INTERACTIONS ENDPOINTS ====================

@router.get("/interactions/{interaction_id}", response_model=AgentInteraction)
async def get_interaction(interaction_id: str):
    """Lấy chi tiết một interaction"""
    interaction = training_db.get_interaction(interaction_id)
    if not interaction:
        raise HTTPException(status_code=404, detail="Interaction not found")
    return interaction


@router.get("/interactions/user/{user_id}", response_model=List[AgentInteraction])
async def get_user_interactions(
    user_id: str,
    limit: int = Query(default=50, le=200),
    skip: int = Query(default=0, ge=0)
):
    """Lấy interactions của một user"""
    try:
        interactions = training_db.get_interactions_by_user(user_id, limit, skip)
        return interactions
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting interactions: {str(e)}")


@router.get("/interactions/type/{interaction_type}", response_model=List[AgentInteraction])
async def get_interactions_by_type(
    interaction_type: InteractionType,
    limit: int = Query(default=50, le=200),
    skip: int = Query(default=0, ge=0)
):
    """Lấy interactions theo loại"""
    try:
        interactions = training_db.get_interactions_by_type(interaction_type, limit, skip)
        return interactions
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting interactions: {str(e)}")


@router.get("/interactions/with-feedback", response_model=List[AgentInteraction])
async def get_interactions_with_feedback(
    feedback_type: Optional[FeedbackType] = None,
    min_rating: Optional[int] = Query(None, ge=1, le=5),
    limit: int = Query(default=100, le=500)
):
    """
    Lấy interactions có feedback (dùng cho training)
    
    Filter theo feedback_type và min_rating
    """
    try:
        interactions = training_db.get_interactions_with_feedback(
            feedback_type=feedback_type,
            min_rating=min_rating,
            limit=limit
        )
        return interactions
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting interactions: {str(e)}")


# ==================== TRAINING DATASETS ====================

@router.post("/datasets", response_model=TrainingDataset)
async def create_training_dataset(
    name: str = Query(..., description="Tên dataset"),
    description: Optional[str] = Query(None, description="Mô tả dataset"),
    min_rating: Optional[int] = Query(None, ge=1, le=5, description="Rating tối thiểu"),
    interaction_types: Optional[List[InteractionType]] = Query(None, description="Loại interactions"),
    days: Optional[int] = Query(None, description="Lấy data từ N ngày gần đây")
):
    """
    Tạo training dataset từ interactions có feedback tốt
    
    Dataset này sẽ được dùng để fine-tune agent
    """
    try:
        filters = {}
        
        if min_rating:
            filters["min_rating"] = min_rating
        
        if interaction_types:
            filters["interaction_types"] = interaction_types
        
        if days:
            filters["start_date"] = datetime.utcnow() - timedelta(days=days)
        
        dataset = training_db.create_training_dataset(
            name=name,
            description=description,
            filters=filters if filters else None
        )
        
        return dataset
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating dataset: {str(e)}")


@router.get("/datasets/{dataset_id}", response_model=TrainingDataset)
async def get_training_dataset(dataset_id: str):
    """Lấy training dataset theo ID"""
    dataset = training_db.get_training_dataset(dataset_id)
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    return dataset


@router.get("/datasets", response_model=List[TrainingDataset])
async def list_training_datasets(
    limit: int = Query(default=50, le=100)
):
    """List tất cả training datasets"""
    try:
        datasets = training_db.list_training_datasets(limit)
        return datasets
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing datasets: {str(e)}")


# ==================== METRICS & ANALYTICS ====================

@router.get("/metrics", response_model=dict)
async def get_training_metrics(
    days: int = Query(default=30, description="Số ngày để tính metrics")
):
    """
    Lấy training metrics và evaluation results
    
    Metrics bao gồm: accuracy, feedback stats, response time, etc.
    """
    try:
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        metrics = training_db.get_training_metrics(start_date, end_date)
        
        return {
            "status": "success",
            "period": f"Last {days} days",
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "metrics": metrics
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting metrics: {str(e)}")


@router.get("/analytics/dashboard", response_model=dict)
async def get_analytics_dashboard(
    days: int = Query(default=7, description="Số ngày")
):
    """
    Lấy analytics dashboard data
    
    Bao gồm: interactions over time, feedback distribution, top performing interactions, etc.
    """
    try:
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Get metrics
        metrics = training_db.get_training_metrics(start_date, end_date)
        
        # Get feedback stats
        feedback_stats = training_db.get_feedback_stats(start_date, end_date)
        
        # Get interactions by type
        interaction_types_stats = {}
        for itype in InteractionType:
            count = training_db.interactions_collection.count_documents({
                "interaction_type": itype,
                "timestamp": {"$gte": start_date, "$lte": end_date}
            })
            interaction_types_stats[itype.value] = count
        
        return {
            "status": "success",
            "period": f"Last {days} days",
            "overview": metrics,
            "feedback_distribution": feedback_stats,
            "interactions_by_type": interaction_types_stats,
            "recommendations": _generate_recommendations(metrics, feedback_stats)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting analytics: {str(e)}")


def _generate_recommendations(metrics: dict, feedback_stats: dict) -> List[str]:
    """Generate recommendations based on metrics"""
    recommendations = []
    
    # Check feedback coverage
    if metrics.get("feedback_coverage", 0) < 0.3:
        recommendations.append("Khuyến khích users cung cấp feedback nhiều hơn để cải thiện training data")
    
    # Check satisfaction rate
    satisfaction = feedback_stats.get("satisfaction_rate", 0)
    if satisfaction < 0.7:
        recommendations.append(f"Tỷ lệ hài lòng thấp ({satisfaction:.0%}). Cần cải thiện chất lượng responses")
    elif satisfaction > 0.9:
        recommendations.append(f"Tỷ lệ hài lòng cao ({satisfaction:.0%}). Có thể bắt đầu fine-tune model")
    
    # Check response time
    avg_time = metrics.get("avg_response_time_ms", 0)
    if avg_time > 3000:
        recommendations.append(f"Response time cao ({avg_time:.0f}ms). Cần optimize agent performance")
    
    # Check accuracy
    accuracy = metrics.get("accuracy", 0)
    if accuracy < 0.8:
        recommendations.append(f"Accuracy thấp ({accuracy:.0%}). Cần review và correct sai responses")
    
    if not recommendations:
        recommendations.append("Hệ thống đang hoạt động tốt. Tiếp tục thu thập data và monitor metrics")
    
    return recommendations


# ==================== FINE-TUNING ====================

@router.post("/prepare-dataset", response_model=dict)
async def prepare_training_dataset_from_excel():
    """
    Chuẩn bị training dataset từ Excel file có sẵn
    
    Load data từ Data/foodData.xlsx và tạo training file
    """
    try:
        from app.training.dataset_loader import DatasetLoader
        
        loader = DatasetLoader(data_dir="Data")
        training_file = loader.create_training_dataset()
        
        if not training_file:
            raise HTTPException(
                status_code=500,
                detail="Failed to prepare training dataset"
            )
        
        return {
            "status": "success",
            "message": "Training dataset đã được chuẩn bị",
            "training_file": training_file,
            "next_step": "Call POST /training/fine-tune to start training"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error preparing dataset: {str(e)}")


@router.post("/fine-tune", response_model=dict)
async def start_fine_tuning(
    model: str = "gpt-3.5-turbo",
    n_epochs: int = 3,
    wait_for_completion: bool = False,
    training_file: Optional[str] = None
):
    """
    Bắt đầu fine-tune agent với OpenAI API
    
    Args:
        model: Base model (gpt-3.5-turbo hoặc gpt-4)
        n_epochs: Số epochs training
        wait_for_completion: Có đợi training hoàn thành không
        training_file: Path to training file (nếu đã có sẵn)
    
    Returns:
        Training job info
    """
    try:
        from app.training.trainer import AgentTrainer, train_agent_from_dataset
        
        # Check OpenAI API key
        from app.config import settings
        if not settings.openai_api_key:
            raise HTTPException(
                status_code=400,
                detail="OpenAI API key not configured. Set OPENAI_API_KEY in .env"
            )
        
        # If training file provided, use it directly
        if training_file:
            trainer = AgentTrainer()
            result = trainer.train_from_file(
                training_file_path=training_file,
                model=model,
                n_epochs=n_epochs,
                wait_for_completion=wait_for_completion
            )
        else:
            # Load from Excel and train
            result = train_agent_from_dataset(
                data_dir="Data",
                model=model,
                n_epochs=n_epochs,
                wait_for_completion=wait_for_completion
            )
        
        if result.get("success"):
            return {
                "status": "success",
                "message": "Training completed successfully!" if wait_for_completion else "Training job started",
                "job_id": result.get("job_id"),
                "file_id": result.get("file_id"),
                "fine_tuned_model": result.get("fine_tuned_model"),
                "training_status": result.get("status"),
                "note": "Use GET /training/job-status/{job_id} to check progress" if not wait_for_completion else None
            }
        else:
            return {
                "status": "failed",
                "message": "Training failed",
                "error": result.get("error"),
                "job_id": result.get("job_id"),
                "file_id": result.get("file_id")
            }
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error starting fine-tune: {str(e)}")


@router.get("/job-status/{job_id}", response_model=dict)
async def get_job_status(job_id: str):
    """
    Check status của fine-tuning job
    
    Args:
        job_id: OpenAI fine-tuning job ID
    """
    try:
        from app.training.trainer import AgentTrainer
        
        trainer = AgentTrainer()
        status = trainer.check_job_status(job_id)
        return status
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
