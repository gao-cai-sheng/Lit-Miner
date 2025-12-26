"""
DeepSeek Writer - AI-powered Literature Review Generator
Uses DeepSeek API to generate comprehensive reviews from RAG-retrieved papers
"""

import requests
from typing import Dict, Any, Optional

from config import DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL, GEMINI_API_KEY, PROMPTS
from core.llm.llm_client import LLMClient



class DeepSeekWriter:
    """
    AI-powered literature review writer using DeepSeek Chat API
    """
    
    
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None, gemini_key: Optional[str] = None):
        """
        Args:
            api_key: DeepSeek API key (uses config if not provided)
            base_url: API base URL (uses config if not provided)
            gemini_key: Gemini API Key (uses config if not provided)
        """
        self.api_key = api_key or DEEPSEEK_API_KEY
        self.gemini_key = gemini_key or GEMINI_API_KEY
        self.base_url = base_url or DEEPSEEK_BASE_URL
        
        self.client = LLMClient(gemini_key=self.gemini_key, deepseek_key=self.api_key)

    
    def generate_review(
        self,
        topic: str,
        evidence: Dict[str, Any],
        raw_query: str = "",
        search_term: str = ""
    ) -> str:
        """
        Generate literature review from RAG evidence.
        
        Args:
            topic: Review topic/title
            evidence: RAG query results with ids, metadatas, documents
            raw_query: Original user query (for context)
            search_term: Expanded search term used
            
        Returns:
            Generated review in Markdown format
        """
        # Build context from evidence
        context = self._build_context(evidence)
        if not context:
            return "❌ No papers found for review generation"
        
        # Build prompt
        prompt = self._build_prompt(topic, context, raw_query, search_term, evidence)
        
        # Call API
        try:
            return self.client.chat_completion(
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7
            )
            
        except Exception as e:
            return f"❌ Review generation failed: {e}"

            
        except Exception as e:
            return f"❌ Review generation failed: {e}"
    
    def _build_context(self, evidence: Dict[str, Any]) -> str:
        """Build context string from evidence"""
        context = ""
        
        if not evidence or not evidence.get("ids") or len(evidence["ids"][0]) == 0:
            return context
        
        for i in range(len(evidence["ids"][0])):
            meta = evidence["metadatas"][0][i]
            context += f"【文献{i + 1}】(PMID:{evidence['ids'][0][i]})\n"
            context += f"标题: {meta.get('title', '')}\n"
            context += f"来源: {meta.get('journal', '')} ({meta.get('year', '')})\n"
            context += f"摘要: {evidence['documents'][0][i][:800]}\n\n"
        
        return context
    
    def _build_prompt(
        self,
        topic: str,
        context: str,
        raw_query: str,
        search_term: str,
        evidence: Dict[str, Any]
    ) -> str:
        """Build prompt for DeepSeek"""
        num_docs = len(evidence["ids"][0])
        display_topic = topic or raw_query or "牙周/口腔医学相关主题"
        
        template = PROMPTS.get("review_writer", {}).get("full_review", "")
        # Fallback omitted as configuration is reliable
        
        prompt = template.format(
            raw_query=raw_query if raw_query else "（未提供）",
            search_term=search_term if search_term else "（未记录）",
            topic=display_topic,
            num_docs=num_docs,
            context=context
        )
        return prompt


def generate_topic_from_evidence(
    evidence: Dict[str, Any],
    api_key: str,
    base_url: str,
    gemini_key: Optional[str] = None
) -> str:

    """
    Auto-generate review topic from evidence.
    
    Args:
        evidence: RAG query results
        api_key: DeepSeek API key
        base_url: API base URL
        
    Returns:
        Generated topic string
    """
    if not evidence or not evidence.get("metadatas"):
        return "Literature Review"
    
    # Extract titles from top papers
    titles = [m.get('title', '') for m in evidence['metadatas'][0][:5]]
    
    template = PROMPTS.get("review_writer", {}).get("topic_summary", "")
    summary_prompt = template.format(titles="\n".join(titles))
    
    
    try:
        client = LLMClient(gemini_key=gemini_key, deepseek_key=api_key)
        return client.chat_completion(
            messages=[{"role": "user", "content": summary_prompt}],
            temperature=0.7,
            max_tokens=100
        ).strip('"\'')
            
    except Exception:
        return "Literature Review"

            
    except Exception:
        return "Literature Review"
