"""
Knowledge Builder - Build vector database from PDF documents
"""

import os
import sys
from pathlib import Path
from typing import List, Dict
import chromadb
from chromadb.config import Settings

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.insert(0, project_root)

from streamlit_app.utils.local_pdf_processor import extract_structured_content
from config import VECTOR_DB_DIR, EMBEDDING_MODEL


class KnowledgeBuilder:
    """Build and manage knowledge base from PDF documents"""
    
    def __init__(
        self,
        collection_name: str = "periodontal_core",
        chunk_size: int = 500,
        chunk_overlap: int = 50
    ):
        self.collection_name = collection_name
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
        # Initialize ChromaDB
        self.client = chromadb.PersistentClient(
            path=str(VECTOR_DB_DIR / "chatbot"),
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"description": "Periodontal disease core literature"}
        )
        
    def build_from_directory(self, pdf_dir: str) -> Dict[str, int]:
        """
        Process all PDFs in directory and build knowledge base
        
        Args:
            pdf_dir: Path to directory containing PDF files
            
        Returns:
            Statistics dict with counts
        """
        pdf_path = Path(pdf_dir)
        if not pdf_path.exists():
            raise ValueError(f"Directory not found: {pdf_dir}")
        
        pdf_files = list(pdf_path.glob("*.pdf"))
        print(f"Found {len(pdf_files)} PDF files")
        
        stats = {
            "total_pdfs": len(pdf_files),
            "processed": 0,
            "failed": 0,
            "total_chunks": 0
        }
        
        for pdf_file in pdf_files:
            try:
                print(f"Processing: {pdf_file.name}")
                chunks_added = self._process_pdf(pdf_file)
                stats["processed"] += 1
                stats["total_chunks"] += chunks_added
                print(f"  ✓ Added {chunks_added} chunks")
            except Exception as e:
                print(f"  ✗ Failed: {e}")
                stats["failed"] += 1
        
        print(f"\n=== Build Complete ===")
        print(f"Processed: {stats['processed']}/{stats['total_pdfs']}")
        print(f"Total chunks: {stats['total_chunks']}")
        print(f"Failed: {stats['failed']}")
        
        return stats
    
    def _process_pdf(self, pdf_path: Path) -> int:
        """Process single PDF and add to collection"""
        
        # Extract content using existing processor
        pdf_id = pdf_path.stem
        result = extract_structured_content(str(pdf_path), pdf_id)
        
        # Extract metadata from filename (format: "J Clinic Periodontology - 2020 - Author - Title.pdf")
        filename = pdf_path.stem
        parts = filename.split(" - ")
        
        metadata = {
            "filename": pdf_path.name,
            "pdf_id": pdf_id,
            "journal": parts[0] if len(parts) > 0 else "Unknown",
            "year": parts[1] if len(parts) > 1 else "Unknown",
            "authors": parts[2] if len(parts) > 2 else "Unknown",
            "title": parts[3] if len(parts) > 3 else filename
        }
        
        # Split text into chunks
        chunks = self._create_chunks(result.markdown, metadata)
        
        if not chunks:
            return 0
        
        # Add to ChromaDB
        self.collection.add(
            documents=[c["text"] for c in chunks],
            metadatas=[c["metadata"] for c in chunks],
            ids=[c["id"] for c in chunks]
        )
        
        return len(chunks)
    
    def _create_chunks(self, text: str, base_metadata: Dict) -> List[Dict]:
        """Split text into overlapping chunks"""
        chunks = []
        
        # Simple chunking by character count
        start = 0
        chunk_id = 0
        
        while start < len(text):
            end = start + self.chunk_size
            chunk_text = text[start:end]
            
            # Try to break at sentence boundary
            if end < len(text):
                last_period = chunk_text.rfind('。')
                if last_period == -1:
                    last_period = chunk_text.rfind('.')
                if last_period > self.chunk_size * 0.5:  # At least 50% of chunk
                    end = start + last_period + 1
                    chunk_text = text[start:end]
            
            chunk = {
                "id": f"{base_metadata['pdf_id']}_chunk_{chunk_id}",
                "text": chunk_text.strip(),
                "metadata": {
                    **base_metadata,
                    "chunk_id": chunk_id,
                    "chunk_start": start,
                    "chunk_end": end
                }
            }
            
            chunks.append(chunk)
            chunk_id += 1
            
            # Move start position with overlap
            start = end - self.chunk_overlap
        
        return chunks
    
    def get_stats(self) -> Dict:
        """Get collection statistics"""
        count = self.collection.count()
        return {
            "collection_name": self.collection_name,
            "total_chunks": count,
            "embedding_model": EMBEDDING_MODEL
        }
    
    def clear_collection(self):
        """Clear all data from collection (use with caution!)"""
        self.client.delete_collection(self.collection_name)
        self.collection = self.client.create_collection(
            name=self.collection_name,
            metadata={"description": "Periodontal disease core literature"}
        )
        print(f"Collection '{self.collection_name}' cleared")


if __name__ == "__main__":
    # Test build
    builder = KnowledgeBuilder()
    stats = builder.build_from_directory("data/pdfs/chatbot_knowledge")
    print(f"\nFinal stats: {builder.get_stats()}")
