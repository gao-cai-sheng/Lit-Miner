"""
Rebuild Knowledge Base with Gemini Embeddings (Fast Version)
Reuses existing text chunks, only regenerates embeddings
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.chatbot.gemini_embeddings import GeminiEmbeddings
import chromadb
from chromadb.config import Settings
from config import VECTOR_DB_DIR

def rebuild_with_gemini():
    print("=" * 60)
    print("Rebuilding with Gemini Embeddings (Fast)")
    print("=" * 60)
    
    # Step 1: Load existing collection
    print("\n[1/4] Loading existing documents...")
    old_client = chromadb.PersistentClient(
        path=str(VECTOR_DB_DIR / "chatbot"),
        settings=Settings(anonymized_telemetry=False)
    )
    
    try:
        old_collection = old_client.get_collection("periodontal_core")
        all_data = old_collection.get(include=["documents", "metadatas"])
        
        documents = all_data['documents']
        metadatas = all_data['metadatas']
        ids = all_data['ids']
        
        print(f"✅ Loaded {len(documents)} existing chunks")
        
    except Exception as e:
        print(f"❌ Failed to load existing collection: {e}")
        print("Please run the full build script first.")
        return
    
    # Step 2: Initialize Gemini
    print("\n[2/4] Initializing Gemini Embeddings...")
    embeddings_client = GeminiEmbeddings()
    print("✅ Gemini API connected")
    
    # Step 3: Delete old collection and create new one
    print("\n[3/4] Creating new collection...")
    old_client.delete_collection("periodontal_core")
    
    new_collection = old_client.create_collection(
        name="periodontal_core",
        metadata={"description": "Periodontal core literature (Gemini embeddings)"}
    )
    print("✅ New collection created")
    
    # Step 4: Generate embeddings and add to new collection
    print(f"\n[4/4] Generating Gemini embeddings for {len(documents)} chunks...")
    print("This will take a few minutes...")
    
    batch_size = 100
    total_batches = (len(documents) + batch_size - 1) // batch_size
    
    for i in range(0, len(documents), batch_size):
        batch_docs = documents[i:i+batch_size]
        batch_metas = metadatas[i:i+batch_size]
        batch_ids = ids[i:i+batch_size]
        
        batch_num = i // batch_size + 1
        print(f"  Batch {batch_num}/{total_batches}: Processing {len(batch_docs)} chunks...")
        
        # Get embeddings from Gemini
        batch_embeddings = embeddings_client.embed_documents(batch_docs)
        
        # Add to collection
        new_collection.add(
            documents=batch_docs,
            embeddings=batch_embeddings,
            metadatas=batch_metas,
            ids=batch_ids
        )
        
        print(f"    ✓ Added {len(batch_docs)} chunks")
    
    print("\n" + "=" * 60)
    print("✅ Knowledge Base Rebuilt Successfully!")
    print("=" * 60)
    print(f"Total chunks: {len(documents)}")
    print(f"Embedding model: Gemini text-embedding-004 (768-dim)")
    print("\n✨ Ready to test retrieval quality!")

if __name__ == "__main__":
    rebuild_with_gemini()
