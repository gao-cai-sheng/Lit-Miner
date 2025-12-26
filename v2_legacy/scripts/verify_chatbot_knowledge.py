
import sys
import os
import chromadb
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config import VECTOR_DB_DIR

def verify_knowledge_base():
    print("=" * 60)
    print("Verifying Chatbot Knowledge Base")
    print("=" * 60)

    # Connect to ChromaDB
    db_path = VECTOR_DB_DIR / "chatbot"
    if not db_path.exists():
        print(f"❌ Database not found at: {db_path}")
        return

    client = chromadb.PersistentClient(path=str(db_path))
    
    try:
        collection = client.get_collection("periodontal_core")
    except Exception as e:
        print(f"❌ Collection 'periodontal_core' not found: {e}")
        return

    # Get all documents
    result = collection.get()
    ids = result["ids"]
    metadatas = result["metadatas"]
    
    print(f"Total chunks in DB: {len(ids)}")
    
    # Map chunks to files
    file_chunks = {}
    for meta in metadatas:
        pdf_id = meta.get("pdf_id")
        filename = meta.get("filename")
        if pdf_id not in file_chunks:
            file_chunks[pdf_id] = {"count": 0, "filename": filename}
        file_chunks[pdf_id]["count"] += 1
        
    print("\n--- Processed Files in DB ---")
    for pdf_id, info in file_chunks.items():
        print(f"📄 {info['filename'][:50]}... : {info['count']} chunks")

    # Check against source directory
    pdf_dir = Path("v2_legacy/data/pdfs/chatbot_knowledge")
    if not pdf_dir.exists():
         # Try alternative path if running from scripts dir
         pdf_dir = Path("../v2_legacy/data/pdfs/chatbot_knowledge")
    
    if not pdf_dir.exists():
        print(f"\n❌ Source directory not found: {pdf_dir}")
        return

    source_files = list(pdf_dir.glob("*.pdf"))
    print(f"\nFound {len(source_files)} source PDF files")
    
    missing_files = []
    empty_files = []
    
    print("\n--- Validation Results ---")
    for pdf_file in source_files:
        pdf_id = pdf_file.stem
        if pdf_id not in file_chunks:
            print(f"❌ MISSING: {pdf_file.name}")
            missing_files.append(pdf_file.name)
        elif file_chunks[pdf_id]["count"] == 0:
            print(f"⚠️  EMPTY (0 chunks): {pdf_file.name}")
            empty_files.append(pdf_file.name)
        else:
             print(f"✅ OK: {pdf_file.name} ({file_chunks[pdf_id]['count']} chunks)")

    print("-" * 60)
    print(f"Summary: {len(source_files)} source files")
    print(f"Missing in DB: {len(missing_files)}")
    print(f"Empty in DB: {len(empty_files)}")
    print(f"Present in DB: {len(file_chunks)}")

if __name__ == "__main__":
    verify_knowledge_base()
