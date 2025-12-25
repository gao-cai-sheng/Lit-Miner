"""
Build Knowledge Base for Chatbot (Gemini Embeddings Version)
Run this script to process PDFs and create vector database using Gemini API
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.chatbot.gemini_embeddings import GeminiEmbeddings
import chromadb
from chromadb.config import Settings
from pathlib import Path
from streamlit_app.utils.local_pdf_processor import extract_text_to_markdown
from config import VECTOR_DB_DIR, PDF_DIR

def build_knowledge_base():
    print("=" * 60)
    print("Building Knowledge Base with Gemini Embeddings")
    print("=" * 60)
    
    # Initialize Gemini embeddings
    print("\n[1/4] Initializing Gemini Embeddings...")
    embeddings = GeminiEmbeddings()
    print("✅ Gemini API connected")
    
    # Initialize ChromaDB with custom embedding function
    print("\n[2/4] Setting up ChromaDB...")
    client = chromadb.PersistentClient(
        path=str(VECTOR_DB_DIR / "chatbot"),
        settings=Settings(anonymized_telemetry=False)
    )
    
    # Create or get collection
    collection = client.get_or_create_collection(
        name="periodontal_core",
        metadata={"description": "Periodontal disease core literature (Gemini embeddings)"}
    )
    
    # Process PDFs
    print("\n[3/4] Processing PDFs...")
    pdf_dir = PDF_DIR / "chatbot_knowledge"
    pdf_files = list(pdf_dir.glob("*.pdf"))
    print(f"Found {len(pdf_files)} PDF files")
    
    total_chunks = 0
    
    for i, pdf_file in enumerate(pdf_files, 1):
        print(f"\n[{i}/{len(pdf_files)}] Processing: {pdf_file.name[:50]}...")
        
        try:
            # Check if already exists
            pdf_id = pdf_file.stem
            existing = collection.get(where={"pdf_id": pdf_id})
            if existing and existing['ids']:
                print(f"  ⏭️  Skipping (already exists)")
                continue

            # Extract text
            markdown = extract_text_to_markdown(str(pdf_file))
            
            # Extract metadata from filename
            filename = pdf_file.stem
            parts = filename.split(" - ")
            metadata = {
                "filename": pdf_file.name,
                "pdf_id": pdf_id,
                "journal": parts[0] if len(parts) > 0 else "Unknown",
                "year": parts[1] if len(parts) > 1 else "Unknown",
                "authors": parts[2] if len(parts) > 2 else "Unknown",
                "title": parts[3] if len(parts) > 3 else filename
            }
            
            # Create chunks
            chunks = create_chunks(markdown, metadata)
            
            if not chunks:
                print(f"  ⚠️  No chunks created")
                continue
            
            # Get embeddings from Gemini
            print(f"  Getting embeddings for {len(chunks)} chunks...")
            texts = [c["text"] for c in chunks]
            chunk_embeddings = embeddings.embed_documents(texts)
            
            # Add to ChromaDB
            collection.add(
                documents=texts,
                embeddings=chunk_embeddings,
                metadatas=[c["metadata"] for c in chunks],
                ids=[c["id"] for c in chunks]
            )
            
            total_chunks += len(chunks)
            print(f"  ✓ Added {len(chunks)} chunks")
            
        except Exception as e:
            print(f"  ✗ Failed: {e}")
    
    print("\n" + "=" * 60)
    print("✅ Knowledge Base Built Successfully!")
    print("=" * 60)
    print(f"Total chunks: {total_chunks}")
    print(f"Embedding model: Gemini text-embedding-004")
    print("\n✨ You can now use the Chatbot page!")

def create_chunks(text: str, base_metadata: dict, chunk_size: int = 500, overlap: int = 50):
    """Split text into overlapping chunks"""
    chunks = []
    start = 0
    chunk_id = 0
    
    while start < len(text):
        end = start + chunk_size
        chunk_text = text[start:end]
        
        # Try to break at sentence boundary
        if end < len(text):
            last_period = chunk_text.rfind('。')
            if last_period == -1:
                last_period = chunk_text.rfind('.')
            if last_period > chunk_size * 0.5:
                end = start + last_period + 1
                chunk_text = text[start:end]
        
        chunk = {
            "id": f"{base_metadata['pdf_id']}_chunk_{chunk_id}",
            "text": chunk_text.strip(),
            "metadata": {
                **base_metadata,
                "chunk_id": chunk_id
            }
        }
        
        chunks.append(chunk)
        chunk_id += 1
        start = end - overlap
    
    return chunks

if __name__ == "__main__":
    build_knowledge_base()
