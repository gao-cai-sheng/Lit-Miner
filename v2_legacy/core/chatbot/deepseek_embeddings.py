"""
DeepSeek Embeddings Client
Use DeepSeek API for text embeddings instead of local models
"""

import requests
from typing import List
from config import DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL


class DeepSeekEmbeddings:
    """Client for DeepSeek Embeddings API"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or DEEPSEEK_API_KEY
        if not self.api_key:
            raise ValueError("DEEPSEEK_API_KEY not configured")
        
        self.base_url = DEEPSEEK_BASE_URL
        # DeepSeek embeddings endpoint
        self.model = "text-embedding-3"  # DeepSeek's embedding model
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        Embed multiple documents
        
        Args:
            texts: List of text strings to embed
            
        Returns:
            List of embedding vectors
        """
        # DeepSeek API supports batch embedding
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.model,
            "input": texts,
            "encoding_format": "float"
        }
        
        response = requests.post(
            f"{self.base_url}/v1/embeddings",  # Fixed endpoint
            json=data,
            headers=headers,
            timeout=60
        )
        
        response.raise_for_status()
        result = response.json()
        
        # Extract embeddings from response
        embeddings = [item["embedding"] for item in result["data"]]
        return embeddings
    
    def embed_query(self, text: str) -> List[float]:
        """
        Embed a single query
        
        Args:
            text: Query text
            
        Returns:
            Embedding vector
        """
        embeddings = self.embed_documents([text])
        return embeddings[0]


if __name__ == "__main__":
    # Test
    client = DeepSeekEmbeddings()
    
    # Test single query
    query_embedding = client.embed_query("牙周炎的病因是什么？")
    print(f"Query embedding dimension: {len(query_embedding)}")
    
    # Test batch
    docs = ["Periodontitis is caused by bacteria", "治疗方法包括刮治"]
    doc_embeddings = client.embed_documents(docs)
    print(f"Document embeddings: {len(doc_embeddings)} docs, {len(doc_embeddings[0])} dims each")
