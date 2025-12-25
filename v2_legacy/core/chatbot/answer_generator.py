"""
Answer Generator - Generate responses with source citations
"""

import os
import sys
from typing import List, Dict
import requests

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from config import DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL, PROMPTS


class AnswerGenerator:
    """Generate answers with source citations using DeepSeek"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or DEEPSEEK_API_KEY
        if not self.api_key:
            raise ValueError("DEEPSEEK_API_KEY not configured")
        
        self.base_url = DEEPSEEK_BASE_URL
        self.model = "deepseek-chat"
    
    def generate(
        self,
        question: str,
        retrieved_docs: List[Dict],
        conversation_history: List[Dict] = None
    ) -> Dict[str, any]:
        """
        Generate answer with citations
        
        Args:
            question: User's question
            retrieved_docs: Retrieved document chunks from RAG
            conversation_history: Recent conversation messages
            
        Returns:
            Dict with 'answer' and 'sources'
        """
        
        # Build prompt
        prompt = self._build_prompt(question, retrieved_docs, conversation_history)
        
        # Call DeepSeek API
        try:
            response = self._call_api(prompt)
            
            # Extract sources from retrieved docs
            sources = self._extract_sources(retrieved_docs)
            
            return {
                "answer": response,
                "sources": sources
            }
            
        except Exception as e:
            return {
                "answer": f"抱歉，生成回答时出错：{str(e)}",
                "sources": []
            }
    
    def _build_prompt(
        self,
        question: str,
        retrieved_docs: List[Dict],
        conversation_history: List[Dict] = None
    ) -> str:
        """Build prompt for DeepSeek"""
        
        # Get prompt template from config
        template = PROMPTS.get("chatbot", {}).get("answer_template", "")
        
        if not template:
            # Fallback template
            template = """【检索到的相关文献】：
{retrieved_docs}

【对话历史】：
{conversation_history}

【用户问题】：
{user_question}

请基于以上文献回答问题，并使用 [1][2] 格式标注引用来源。"""
        
        # Format retrieved docs
        docs_text = ""
        for i, doc in enumerate(retrieved_docs, 1):
            meta = doc['metadata']
            title = meta.get('title', 'Unknown')
            year = meta.get('year', 'N/A')
            content = doc['content'][:1500]  # Increased from 300 to 1500 for better context
            
            docs_text += f"[{i}] {title} ({year})\n{content}...\n\n"
        
        # Format conversation history
        history_text = ""
        if conversation_history:
            for msg in conversation_history[-3:]:  # Last 3 turns
                role = "用户" if msg['role'] == 'user' else "助手"
                history_text += f"{role}: {msg['content']}\n"
        else:
            history_text = "（无历史对话）"
        
        # Fill template
        prompt = template.format(
            retrieved_docs=docs_text,
            conversation_history=history_text,
            user_question=question
        )
        
        return prompt
    
    def _call_api(self, prompt: str) -> str:
        """Call DeepSeek API"""
        
        # Get system prompt
        system_prompt = PROMPTS.get("chatbot", {}).get("system_prompt", "")
        if not system_prompt:
            system_prompt = "你是一位专业的牙周病学专家助手。"
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 2000
        }
        
        response = requests.post(
            f"{self.base_url}/chat/completions",
            json=data,
            headers=headers,
            timeout=60
        )
        
        response.raise_for_status()
        result = response.json()
        
        return result["choices"][0]["message"]["content"]
    
    def _extract_sources(self, retrieved_docs: List[Dict]) -> List[Dict]:
        """Extract source information from retrieved docs"""
        sources = []
        
        for i, doc in enumerate(retrieved_docs, 1):
            meta = doc['metadata']
            sources.append({
                "index": i,
                "title": meta.get('title', 'Unknown'),
                "authors": meta.get('authors', 'Unknown'),
                "year": meta.get('year', 'N/A'),
                "journal": meta.get('journal', 'Unknown'),
                "chunk_id": meta.get('chunk_id', 0)
            })
        
        return sources


if __name__ == "__main__":
    # Test answer generation
    generator = AnswerGenerator()
    
    # Mock retrieved docs
    mock_docs = [
        {
            "content": "Periodontitis is caused by bacterial infection...",
            "metadata": {
                "title": "Periodontal Disease Review",
                "authors": "Smith et al.",
                "year": "2020",
                "journal": "J Clin Periodontol",
                "chunk_id": 0
            }
        }
    ]
    
    result = generator.generate(
        question="What causes periodontitis?",
        retrieved_docs=mock_docs
    )
    
    print("Answer:", result["answer"])
    print("\nSources:", result["sources"])
