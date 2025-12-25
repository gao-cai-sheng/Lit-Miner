"""
RAG Engine with Gemini Embeddings
"""

import os
import sys
from typing import List, Dict, Optional
import chromadb
from chromadb.config import Settings

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from config import VECTOR_DB_DIR
from core.chatbot.gemini_embeddings import GeminiEmbeddings


class RAGEngine:
    """Retrieval-Augmented Generation Engine with Gemini Embeddings"""
    
    def __init__(
        self,
        collection_name: str = "periodontal_core",
        top_k: int = 5
    ):
        self.collection_name = collection_name
        self.top_k = top_k
        
        # Initialize Gemini embeddings
        self.embeddings = GeminiEmbeddings()
        
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(
            path=str(VECTOR_DB_DIR / "chatbot"),
            settings=Settings(anonymized_telemetry=False)
        )
        
        try:
            self.collection = self.client.get_collection(name=self.collection_name)
        except Exception:
            raise ValueError(
                f"Collection '{self.collection_name}' not found. "
                "Please run rebuild_with_gemini.py first."
            )
    
    def retrieve(
        self,
        query: str,
        conversation_history: Optional[List[Dict]] = None,
        top_k: Optional[int] = None
    ) -> List[Dict]:
        """
        Retrieve relevant document chunks
        
        Args:
            query: User question
            conversation_history: Recent conversation for context
            top_k: Number of results to return (overrides default)
            
        Returns:
            List of retrieved chunks with metadata
        """
        k = top_k or self.top_k
        
        # Enhance query with conversation context if available
        enhanced_query = self._enhance_query(query, conversation_history)
        
        # Get query embedding from Gemini
        query_embedding = self.embeddings.embed_query(enhanced_query)
        
        # Query ChromaDB
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=k
        )
        
        # Format results
        retrieved = []
        if results and results['documents'] and len(results['documents'][0]) > 0:
            for i in range(len(results['documents'][0])):
                retrieved.append({
                    "content": results['documents'][0][i],
                    "metadata": results['metadatas'][0][i],
                    "distance": results['distances'][0][i] if 'distances' in results else None,
                    "id": results['ids'][0][i]
                })
        
        return retrieved
    
    def _enhance_query(
        self,
        query: str,
        conversation_history: Optional[List[Dict]]
    ) -> str:
        """Enhance query with conversation context"""
        
        if not conversation_history or len(conversation_history) == 0:
            return query
        
        # Get last user message for context
        recent_context = []
        for msg in conversation_history[-3:]:  # Last 3 messages
            if msg['role'] == 'user':
                recent_context.append(msg['content'])
        
        if recent_context:
            # Combine recent questions with current query
            enhanced = " ".join(recent_context) + " " + query
            return enhanced
        
        return query
    
    def get_collection_stats(self) -> Dict:
        """Get statistics about the knowledge base"""
        count = self.collection.count()
        
        # Sample a few documents to show what's in the collection
        sample = self.collection.peek(limit=3)
        
        return {
            "collection_name": self.collection_name,
            "total_chunks": count,
            "embedding_model": "Gemini text-embedding-004",
            "sample_documents": [
                {
                    "title": sample['metadatas'][i].get('title', 'N/A'),
                    "year": sample['metadatas'][i].get('year', 'N/A')
                }
                for i in range(min(3, len(sample['metadatas'])))
            ] if sample and sample['metadatas'] else []
        }


if __name__ == "__main__":
    # Test retrieval
    engine = RAGEngine()
    
    print("Collection stats:", engine.get_collection_stats())
    print("\nTesting retrieval with Gemini embeddings...")
    
    results = engine.retrieve("牙周炎的主要致病菌有哪些？")
    
    print(f"\nRetrieved {len(results)} chunks:")
    for i, r in enumerate(results):
        print(f"\n[{i+1}] {r['metadata'].get('title', 'Unknown')[:60]}...")
        print(f"    Distance: {r.get('distance', 'N/A'):.3f if r.get('distance') else 'N/A'}")
        print(f"    Content: {r['content'][:100]}...")
