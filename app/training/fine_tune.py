"""
Fine-tuning pipeline cho Food Advisor Agent
"""
import json
import os
from typing import List, Dict, Any, Optional
from datetime import datetime

from app.config import settings
from app.models.training import TrainingDataset, FineTuneConfig
from app.database.training_db import training_db


class FineTuningPipeline:
    """Pipeline để fine-tune agent"""
    
    def __init__(self):
        self.training_data_dir = "training_data"
        os.makedirs(self.training_data_dir, exist_ok=True)
    
    def prepare_training_data(self, dataset: TrainingDataset, output_file: Optional[str] = None) -> str:
        """Chuẩn bị training data theo format OpenAI JSONL"""
        if not output_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = os.path.join(
                self.training_data_dir, 
                f"training_data_{dataset.dataset_id}_{timestamp}.jsonl"
            )
        
        system_prompt = """Bạn là chuyên gia AI về dinh dưỡng và ẩm thực Việt Nam."""
        
        training_examples = []
        for interaction in dataset.interactions:
            if not interaction.feedback or interaction.feedback.feedback_type != "positive":
                continue
            
            user_message = interaction.user_query
            if interaction.user_context:
                context_parts = []
                if interaction.user_context.get("diseases"):
                    context_parts.append(f"Bệnh lý: {', '.join(interaction.user_context['diseases'])}")
                if context_parts:
                    user_message += f"\n\nContext: {'; '.join(context_parts)}"
            
            example = {
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message},
                    {"role": "assistant", "content": interaction.agent_response}
                ]
            }
            training_examples.append(example)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            for example in training_examples:
                f.write(json.dumps(example, ensure_ascii=False) + '\n')
        
        print(f"✓ Prepared {len(training_examples)} training examples")
        print(f"✓ Saved to: {output_file}")
        
        return output_file
    
    def validate_training_data(self, file_path: str) -> Dict[str, Any]:
        """Validate training data format"""
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        total_examples = len(lines)
        valid_examples = 0
        errors = []
        
        for i, line in enumerate(lines):
            try:
                example = json.loads(line)
                if "messages" in example and len(example["messages"]) >= 2:
                    valid_examples += 1
                else:
                    errors.append(f"Line {i+1}: Invalid structure")
            except json.JSONDecodeError:
                errors.append(f"Line {i+1}: Invalid JSON")
        
        return {
            "total_examples": total_examples,
            "valid_examples": valid_examples,
            "invalid_examples": total_examples - valid_examples,
            "errors": errors[:10],
            "is_valid": valid_examples == total_examples
        }
    
    def run_full_pipeline(self, dataset_id: str, config: FineTuneConfig) -> Dict[str, Any]:
        """Run complete fine-tuning pipeline"""
        results = {
            "dataset_id": dataset_id,
            "started_at": datetime.now().isoformat(),
            "steps": []
        }
        
        try:
            # Step 1: Load dataset
            print("\n=== Step 1: Loading dataset ===")
            dataset = training_db.get_training_dataset(dataset_id)
            if not dataset:
                raise ValueError(f"Dataset not found: {dataset_id}")
            
            results["steps"].append({
                "step": "load_dataset",
                "status": "success",
                "total_interactions": dataset.total_interactions
            })
            
            # Step 2: Prepare training data
            print("\n=== Step 2: Preparing training data ===")
            training_file = self.prepare_training_data(dataset)
            
            results["steps"].append({
                "step": "prepare_data",
                "status": "success",
                "file_path": training_file
            })
            
            # Step 3: Validate data
            print("\n=== Step 3: Validating data ===")
            validation = self.validate_training_data(training_file)
            
            if not validation["is_valid"]:
                raise ValueError(f"Invalid training data: {validation['errors']}")
            
            results["steps"].append({
                "step": "validate_data",
                "status": "success",
                "validation": validation
            })
            
            results["status"] = "success"
            results["training_file"] = training_file
            results["completed_at"] = datetime.now().isoformat()
            
            print("\n=== Pipeline completed successfully ===")
            print(f"Training file: {training_file}")
            
        except Exception as e:
            results["status"] = "failed"
            results["error"] = str(e)
            results["completed_at"] = datetime.now().isoformat()
            print(f"\n=== Pipeline failed: {e} ===")
        
        return results


# Singleton instance
fine_tuning_pipeline = FineTuningPipeline()
