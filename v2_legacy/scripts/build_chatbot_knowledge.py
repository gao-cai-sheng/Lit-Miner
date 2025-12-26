"""
Build Knowledge Base for Chatbot
Run this script to process PDFs and create vector database
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.chatbot import KnowledgeBuilder

def main():
    print("=" * 60)
    print("Building Knowledge Base for Chatbot")
    print("=" * 60)
    
    # Initialize builder
    builder = KnowledgeBuilder(
        collection_name="periodontal_core",
        chunk_size=500,
        chunk_overlap=50
    )
    
    # Build from PDF directory
    pdf_dir = "data/pdfs/chatbot_knowledge"
    
    print(f"\nProcessing PDFs from: {pdf_dir}")
    print("This may take a few minutes...\n")
    
    try:
        stats = builder.build_from_directory(pdf_dir)
        
        print("\n" + "=" * 60)
        print("✅ Knowledge Base Built Successfully!")
        print("=" * 60)
        print(f"Total PDFs: {stats['total_pdfs']}")
        print(f"Processed: {stats['processed']}")
        print(f"Failed: {stats['failed']}")
        print(f"Total Chunks: {stats['total_chunks']}")
        
        # Show collection stats
        collection_stats = builder.get_stats()
        print(f"\nCollection: {collection_stats['collection_name']}")
        print(f"Embedding Model: {collection_stats['embedding_model']}")
        
        print("\n✨ You can now use the Chatbot page!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
