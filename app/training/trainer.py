"""
Agent Trainer - Fine-tune agent với OpenAI API
"""
import openai
from openai import OpenAI
import time
from typing import Optional, Dict, Any
from pathlib import Path
from app.config import settings
import json


class AgentTrainer:
    """Train agent using OpenAI Fine-tuning API"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.openai_api_key
        if not self.api_key:
            raise ValueError("OpenAI API key not found. Set OPENAI_API_KEY in .env")
        
        self.client = OpenAI(api_key=self.api_key)
        self.training_file_id = None
        self.fine_tune_job_id = None
    
    def upload_training_file(self, file_path: str) -> str:
        """
        Upload training file to OpenAI
        
        Args:
            file_path: Path to training JSONL file
            
        Returns:
            File ID from OpenAI
        """
        print(f"📤 Uploading training file: {file_path}")
        
        try:
            with open(file_path, 'rb') as f:
                response = self.client.files.create(
                    file=f,
                    purpose='fine-tune'
                )
            
            self.training_file_id = response.id
            print(f"✅ File uploaded successfully!")
            print(f"📁 File ID: {self.training_file_id}")
            return self.training_file_id
            
        except Exception as e:
            print(f"❌ Error uploading file: {e}")
            raise
    
    def start_fine_tuning(
        self, 
        training_file_id: str,
        model: str = "gpt-3.5-turbo",
        suffix: Optional[str] = None,
        n_epochs: int = 3,
        learning_rate_multiplier: Optional[float] = None
    ) -> str:
        """
        Start fine-tuning job
        
        Args:
            training_file_id: ID of uploaded training file
            model: Base model to fine-tune (gpt-3.5-turbo or gpt-4)
            suffix: Custom suffix for fine-tuned model name
            n_epochs: Number of training epochs
            learning_rate_multiplier: Learning rate multiplier
            
        Returns:
            Fine-tune job ID
        """
        print(f"🚀 Starting fine-tuning job...")
        print(f"📊 Base model: {model}")
        print(f"📁 Training file: {training_file_id}")
        print(f"🔄 Epochs: {n_epochs}")
        
        try:
            hyperparameters = {"n_epochs": n_epochs}
            if learning_rate_multiplier:
                hyperparameters["learning_rate_multiplier"] = learning_rate_multiplier
            
            response = self.client.fine_tuning.jobs.create(
                training_file=training_file_id,
                model=model,
                suffix=suffix or "food-advisor",
                hyperparameters=hyperparameters
            )
            
            self.fine_tune_job_id = response.id
            print(f"✅ Fine-tuning job created!")
            print(f"🆔 Job ID: {self.fine_tune_job_id}")
            print(f"📊 Status: {response.status}")
            
            return self.fine_tune_job_id
            
        except Exception as e:
            print(f"❌ Error starting fine-tuning: {e}")
            raise
    
    def check_job_status(self, job_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Check status of fine-tuning job
        
        Args:
            job_id: Job ID to check (uses self.fine_tune_job_id if not provided)
            
        Returns:
            Job status dict
        """
        job_id = job_id or self.fine_tune_job_id
        if not job_id:
            raise ValueError("No job ID provided")
        
        try:
            response = self.client.fine_tuning.jobs.retrieve(job_id)
            
            status_info = {
                "job_id": response.id,
                "status": response.status,
                "model": response.model,
                "fine_tuned_model": response.fine_tuned_model,
                "created_at": response.created_at,
                "finished_at": response.finished_at,
                "trained_tokens": response.trained_tokens,
                "error": response.error if hasattr(response, 'error') else None
            }
            
            return status_info
            
        except Exception as e:
            print(f"❌ Error checking job status: {e}")
            raise
    
    def wait_for_completion(
        self, 
        job_id: Optional[str] = None,
        check_interval: int = 60,
        max_wait_time: int = 7200  # 2 hours
    ) -> Dict[str, Any]:
        """
        Wait for fine-tuning job to complete
        
        Args:
            job_id: Job ID to wait for
            check_interval: Seconds between status checks
            max_wait_time: Maximum time to wait (seconds)
            
        Returns:
            Final job status
        """
        job_id = job_id or self.fine_tune_job_id
        if not job_id:
            raise ValueError("No job ID provided")
        
        print(f"⏳ Waiting for fine-tuning to complete...")
        print(f"🔄 Checking every {check_interval} seconds")
        
        start_time = time.time()
        
        while True:
            elapsed = time.time() - start_time
            
            if elapsed > max_wait_time:
                print(f"⏰ Max wait time ({max_wait_time}s) exceeded")
                break
            
            status_info = self.check_job_status(job_id)
            status = status_info['status']
            
            print(f"📊 Status: {status} (elapsed: {int(elapsed)}s)")
            
            if status == 'succeeded':
                print(f"\n✅ Fine-tuning completed successfully!")
                print(f"🎉 Fine-tuned model: {status_info['fine_tuned_model']}")
                print(f"📊 Trained tokens: {status_info['trained_tokens']}")
                return status_info
            
            elif status == 'failed':
                print(f"\n❌ Fine-tuning failed!")
                print(f"Error: {status_info.get('error', 'Unknown error')}")
                return status_info
            
            elif status == 'cancelled':
                print(f"\n⚠️ Fine-tuning was cancelled")
                return status_info
            
            # Still running
            time.sleep(check_interval)
        
        # Timeout
        return self.check_job_status(job_id)
    
    def list_fine_tuned_models(self) -> list:
        """List all fine-tuned models"""
        try:
            response = self.client.fine_tuning.jobs.list(limit=20)
            
            models = []
            for job in response.data:
                if job.fine_tuned_model:
                    models.append({
                        "job_id": job.id,
                        "model": job.fine_tuned_model,
                        "base_model": job.model,
                        "status": job.status,
                        "created_at": job.created_at,
                        "finished_at": job.finished_at
                    })
            
            return models
            
        except Exception as e:
            print(f"❌ Error listing models: {e}")
            return []
    
    def train_from_file(
        self,
        training_file_path: str,
        model: str = "gpt-3.5-turbo",
        n_epochs: int = 3,
        wait_for_completion: bool = True
    ) -> Dict[str, Any]:
        """
        Complete training workflow: upload file, start training, wait for completion
        
        Args:
            training_file_path: Path to training JSONL file
            model: Base model to fine-tune
            n_epochs: Number of epochs
            wait_for_completion: Whether to wait for job to complete
            
        Returns:
            Training result dict
        """
        print("=" * 60)
        print("🎓 STARTING AGENT TRAINING")
        print("=" * 60)
        
        result = {
            "success": False,
            "file_id": None,
            "job_id": None,
            "status": None,
            "fine_tuned_model": None,
            "error": None
        }
        
        try:
            # Step 1: Upload training file
            print("\n📤 Step 1: Uploading training file...")
            file_id = self.upload_training_file(training_file_path)
            result["file_id"] = file_id
            
            # Step 2: Start fine-tuning
            print("\n🚀 Step 2: Starting fine-tuning job...")
            job_id = self.start_fine_tuning(
                training_file_id=file_id,
                model=model,
                n_epochs=n_epochs
            )
            result["job_id"] = job_id
            
            # Step 3: Wait for completion (optional)
            if wait_for_completion:
                print("\n⏳ Step 3: Waiting for completion...")
                status_info = self.wait_for_completion(job_id)
                result["status"] = status_info["status"]
                result["fine_tuned_model"] = status_info["fine_tuned_model"]
                
                if status_info["status"] == "succeeded":
                    result["success"] = True
                    print("\n" + "=" * 60)
                    print("✅ TRAINING COMPLETED SUCCESSFULLY!")
                    print("=" * 60)
                    print(f"🎉 Fine-tuned model: {result['fine_tuned_model']}")
                    print(f"📊 Job ID: {result['job_id']}")
                    print(f"📁 Training file ID: {result['file_id']}")
                else:
                    print("\n" + "=" * 60)
                    print("❌ TRAINING FAILED OR CANCELLED")
                    print("=" * 60)
                    result["error"] = status_info.get("error")
            else:
                result["status"] = "running"
                print("\n" + "=" * 60)
                print("✅ TRAINING JOB STARTED")
                print("=" * 60)
                print(f"🆔 Job ID: {result['job_id']}")
                print(f"📊 Check status with: trainer.check_job_status('{job_id}')")
            
            return result
            
        except Exception as e:
            result["error"] = str(e)
            print("\n" + "=" * 60)
            print("❌ TRAINING ERROR")
            print("=" * 60)
            print(f"Error: {e}")
            return result


def train_agent_from_dataset(
    data_dir: str = "Data",
    model: str = "gpt-3.5-turbo",
    n_epochs: int = 3,
    wait_for_completion: bool = True
) -> Dict[str, Any]:
    """
    Complete workflow: Load dataset, prepare training data, and train agent
    
    Args:
        data_dir: Directory containing food data
        model: Base model to fine-tune
        n_epochs: Number of training epochs
        wait_for_completion: Wait for training to complete
        
    Returns:
        Training result dict
    """
    from .dataset_loader import DatasetLoader
    
    print("=" * 60)
    print("🍜 FOOD ADVISOR AGENT TRAINING")
    print("=" * 60)
    
    # Step 1: Prepare dataset
    print("\n📊 Step 1: Preparing training dataset...")
    loader = DatasetLoader(data_dir=data_dir)
    training_file = loader.create_training_dataset()
    
    if not training_file:
        return {
            "success": False,
            "error": "Failed to prepare training dataset"
        }
    
    # Step 2: Train agent
    print("\n🎓 Step 2: Training agent...")
    trainer = AgentTrainer()
    result = trainer.train_from_file(
        training_file_path=training_file,
        model=model,
        n_epochs=n_epochs,
        wait_for_completion=wait_for_completion
    )
    
    return result
