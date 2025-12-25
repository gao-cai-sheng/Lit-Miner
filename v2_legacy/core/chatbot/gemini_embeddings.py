"""
Gemini Embeddings Client
Use Google Gemini API for text embeddings
"""

import os
from typing import List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

try:
    import google.generativeai as genai
except ImportError:
    print("Please install: pip install google-generativeai")
    raise
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def retry_with_backoff(retries=3, backoff_in_seconds=1):
    def decorator(func):
        def wrapper(*args, **kwargs):
            x = 0
            while True:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if x == retries:
                        logger.error(f"Failed after {retries} retries: {e}")
                        raise
                    sleep = (backoff_in_seconds * 2 ** x + 
                             float(time.time() % 1))  # Add jitter
                    logger.warning(f"Error: {e}. Retrying in {sleep:.2f}s...")
                    time.sleep(sleep)
                    x += 1
        return wrapper
    return decorator



class GeminiEmbeddings:
    """Client for Google Gemini Embeddings API"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not configured in .env file")
        
        # Configure Gemini
        genai.configure(api_key=self.api_key)
        self.model = "models/text-embedding-004"
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        Embed multiple documents
        
        Args:
            texts: List of text strings to embed
            
        Returns:
            List of embedding vectors
        """
        embeddings = []
        
        # Process one by one (Gemini doesn't support batch in old API)
        for text in texts:
            self._embed_single_with_retry(text, embeddings)
        
        return embeddings
    
    @retry_with_backoff(retries=5, backoff_in_seconds=2)
    def _embed_single_with_retry(self, text, embeddings_list):
        result = genai.embed_content(
            model=self.model,
            content=text,
            task_type="retrieval_document"
        )
        embeddings_list.append(result['embedding'])

    @retry_with_backoff(retries=5, backoff_in_seconds=2)
    def embed_query(self, text: str) -> List[float]:
        """
        Embed a single query
        
        Args:
            text: Query text
            
        Returns:
            Embedding vector
        """
        result = genai.embed_content(
            model=self.model,
            content=text,
            task_type="retrieval_query"
        )
        return result['embedding']



if __name__ == "__main__":
    # Test
    print("Testing Gemini Embeddings API...")
    
    try:
        client = GeminiEmbeddings()
        
        # Test single query
        query_embedding = client.embed_query("牙周炎的病因是什么？")
        print(f"✅ Gemini API 可用！")
        print(f"Query embedding dimension: {len(query_embedding)}")
        
        # Test batch
        docs = ["Periodontitis is caused by bacteria", "治疗方法包括刮治"]
        doc_embeddings = client.embed_documents(docs)
        print(f"Document embeddings: {len(doc_embeddings)} docs, {len(doc_embeddings[0])} dims each")
        
        print("\n✨ 测试成功！可以开始构建知识库了。")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
