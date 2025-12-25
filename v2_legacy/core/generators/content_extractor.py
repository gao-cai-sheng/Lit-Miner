

import os
import json
from typing import Dict, Optional
import sys

# Add project root to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from config import PROMPTS

try:
    from openai import OpenAI
except ImportError:
    pass

class ContentExtractor:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("DEEPSEEK_API_KEY")
        if not self.api_key:
            raise ValueError("DEEPSEEK_API_KEY not found")
            
        self.client = OpenAI(
            api_key=self.api_key,
            base_url="https://api.deepseek.com"
        )
        
    def extract_from_text(self, text: str) -> Dict[str, str]:
        """
        Extract structured content from paper text for PPT generation
        """
        prompt_template = PROMPTS.get("report_generator", {}).get("extraction", "")
        if not prompt_template:
            # Fallback if config fails
            prompt_template = """
            You are a medical research assistant. Extract key information from the following paper text for a presentation.
            Output MUST be valid JSON with these keys: 
            - title (The official title of the paper)
            - background (Problem statement, hypothesis)
            - methods (Study design, sample size, intervention)
            - results (Key findings, statistics)
            - conclusion (Clinical implications)
            
            Paper Data:
            {text}
            """
            
        prompt = prompt_template.format(text=text[:10000])
        
        try:
            response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that outputs JSON."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.3
            )
            
            content = response.choices[0].message.content
            return json.loads(content)
            
        except Exception as e:
            print(f"Extraction failed: {e}")
            return {
                "background": "Extraction Failed",
                "methods": "N/A",
                "results": "N/A", 
                "conclusion": "N/A"
            }

if __name__ == "__main__":
    # Test
    from dotenv import load_dotenv
    load_dotenv()
    
    extractor = ContentExtractor()
    result = extractor.extract_from_text("This is a study about periodontitis...")
    print(result)
