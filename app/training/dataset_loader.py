"""
Load training data từ Excel dataset
"""
import pandas as pd
from typing import List, Dict, Any, Optional
from pathlib import Path
import json


class DatasetLoader:
    """Load và prepare training data từ Excel files"""
    
    def __init__(self, data_dir: str = "Data"):
        self.data_dir = Path(data_dir)
        self.food_data_path = self.data_dir / "foodData.xlsx"
    
    def load_food_data(self) -> pd.DataFrame:
        """Load food data từ Excel"""
        try:
            df = pd.read_excel(self.food_data_path)
            print(f"✅ Loaded {len(df)} food items from {self.food_data_path}")
            return df
        except Exception as e:
            print(f"❌ Error loading food data: {e}")
            return pd.DataFrame()
    
    def prepare_training_examples(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Chuẩn bị training examples từ food data
        
        Format cho OpenAI fine-tuning:
        {
            "messages": [
                {"role": "system", "content": "System prompt"},
                {"role": "user", "content": "User query"},
                {"role": "assistant", "content": "Assistant response"}
            ]
        }
        """
        training_examples = []
        
        system_prompt = """Bạn là chuyên gia AI về dinh dưỡng và ẩm thực Việt Nam. 
Bạn am hiểu các món ăn truyền thống và hiện đại Việt Nam, dinh dưỡng phù hợp với khẩu phần người Việt, 
và rules dinh dưỡng cho bệnh lý phổ biến tại Việt Nam.
Luôn trả lời bằng tiếng Việt, chuyên nghiệp, và chính xác."""
        
        for idx, row in df.iterrows():
            # Tạo nhiều loại queries khác nhau cho mỗi món ăn
            food_name = row.get('name', row.get('food_name', f'Món ăn {idx}'))
            
            # Query 1: Hỏi về calo
            if 'calories' in row or 'calo' in row:
                calories = row.get('calories', row.get('calo', 0))
                training_examples.append({
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": f"Món {food_name} có bao nhiêu calo?"},
                        {"role": "assistant", "content": f"Món {food_name} có khoảng {calories} calo."}
                    ]
                })
            
            # Query 2: Hỏi về dinh dưỡng tổng quát
            if all(k in row for k in ['protein', 'fat', 'carbs']):
                protein = row.get('protein', 0)
                fat = row.get('fat', 0)
                carbs = row.get('carbs', 0)
                calories = row.get('calories', row.get('calo', 0))
                
                nutrition_info = f"""Món {food_name} có thành phần dinh dưỡng như sau:
- Calo: {calories} kcal
- Protein: {protein}g
- Chất béo: {fat}g
- Carbohydrate: {carbs}g

Đây là một món ăn Việt Nam truyền thống với giá trị dinh dưỡng cân đối."""
                
                training_examples.append({
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": f"Phân tích dinh dưỡng của món {food_name}"},
                        {"role": "assistant", "content": nutrition_info}
                    ]
                })
            
            # Query 3: Hỏi về thành phần
            if 'ingredients' in row or 'thanh_phan' in row:
                ingredients = row.get('ingredients', row.get('thanh_phan', ''))
                if ingredients:
                    training_examples.append({
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": f"Món {food_name} có những thành phần gì?"},
                            {"role": "assistant", "content": f"Món {food_name} bao gồm các thành phần chính: {ingredients}"}
                        ]
                    })
            
            # Query 4: Hỏi về vùng miền
            if 'region' in row or 'vung_mien' in row:
                region = row.get('region', row.get('vung_mien', ''))
                if region:
                    training_examples.append({
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": f"Món {food_name} thuộc vùng miền nào?"},
                            {"role": "assistant", "content": f"Món {food_name} là món ăn đặc trưng của vùng {region}."}
                        ]
                    })
        
        print(f"✅ Prepared {len(training_examples)} training examples")
        return training_examples
    
    def save_training_file(self, examples: List[Dict[str, Any]], output_path: str = "training_data.jsonl"):
        """
        Save training examples to JSONL format (OpenAI fine-tuning format)
        """
        output_file = Path(output_path)
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                for example in examples:
                    f.write(json.dumps(example, ensure_ascii=False) + '\n')
            
            print(f"✅ Saved {len(examples)} examples to {output_file}")
            return str(output_file)
        except Exception as e:
            print(f"❌ Error saving training file: {e}")
            return None
    
    def create_training_dataset(self) -> Optional[str]:
        """
        Main method: Load data, prepare examples, và save training file
        
        Returns:
            Path to training file
        """
        print("🚀 Starting dataset preparation...")
        
        # Load food data
        df = self.load_food_data()
        if df.empty:
            print("❌ No data loaded. Aborting.")
            return None
        
        # Prepare training examples
        examples = self.prepare_training_examples(df)
        if not examples:
            print("❌ No training examples created. Aborting.")
            return None
        
        # Save to file
        training_file = self.save_training_file(examples)
        
        if training_file:
            print(f"\n✅ Training dataset ready!")
            print(f"📁 File: {training_file}")
            print(f"📊 Total examples: {len(examples)}")
            print(f"\nNext steps:")
            print(f"1. Review the training file")
            print(f"2. Upload to OpenAI for fine-tuning")
            print(f"3. Start fine-tuning job")
        
        return training_file


def load_and_prepare_dataset():
    """Helper function để load và prepare dataset"""
    loader = DatasetLoader()
    return loader.create_training_dataset()


if __name__ == "__main__":
    # Test loading
    load_and_prepare_dataset()
