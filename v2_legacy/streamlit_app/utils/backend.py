"""
Backend Integration Helpers
Wrapper functions for backend components (SmartMiner, DeepSeekWriter, etc.)
"""

import os
import sys
import hashlib
from typing import List, Dict, Callable, Optional
from datetime import datetime

# Get project root directory (parent of streamlit_app)
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from core.miners.smart_miner import SmartMiner, PersistentMemory
from core.miners.query_expansion import expand_query
from core.writers import DeepSeekWriter, generate_topic_from_evidence
from config import PUBMED_EMAIL

# Placeholder for future modules (PDF/figures processing)
PisminFetcher = None
convert_pdf_to_markdown = None
FigureProcessor = None


def run_smart_mining(query: str, limit: int, email: str, gemini_key: Optional[str] = None, log_callback: Optional[Callable] = None) -> List[Dict]:

    """
    Run smart mining with progress logging.
    
    Args:
        query: Search query (raw, will be expanded)
        limit: Maximum number of papers
        email: Email for PubMed
        log_callback: Optional callback for logging (called with message string)
        
    Returns:
        List of paper dictionaries
    """
    # Expand query
    expanded_query = expand_query(query, gemini_key=gemini_key)

    if log_callback:
        log_callback(f"🔍 Expanded query: {expanded_query[:150]}...")
    
    miner = SmartMiner(email=email, log_callback=log_callback)
    papers = miner.mine(expanded_query, limit)
    
    # Store to ChromaDB
    import re
    import json
    slug = re.sub(r"[^a-zA-Z0-9]+", "_", query).strip("_")
    
    # Fix: ChromaDB requires names >= 3 chars, matching [a-zA-Z0-9._-]
    # For Chinese queries, slug might be empty or "db" (too short)
    if not slug or len(slug) < 3:
        # Use MD5 hash of query as fallback
        slug = hashlib.md5(query.encode('utf-8')).hexdigest()[:12]
        if log_callback:
            log_callback(f"ℹ️ Using hash-based collection name: {slug}")
    
    db_path = os.path.join(PROJECT_ROOT, "data/vector_dbs", slug)
    
    # Save original query to metadata file
    os.makedirs(db_path, exist_ok=True)
    metadata_file = os.path.join(db_path, "query_metadata.json")
    metadata = {
        "original_query": query,
        "slug": slug,
        "timestamp": datetime.now().isoformat()
    }
    with open(metadata_file, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)
    
    if log_callback:
        log_callback(f"💾 Storing {len(papers)} papers to ChromaDB...")
    
    mem = PersistentMemory(db_name=f"db_{slug}", data_dir=db_path)
    mem.add_papers(papers)
    
    if log_callback:
        log_callback(f"✅ Storage complete!")
    
    return papers


def generate_ai_review(
    query: str,
    topic: str = "",
    n_results: int = 20,
    gemini_key: Optional[str] = None,
    log_callback: Optional[Callable] = None
) -> Dict:
    """
    Generate AI review from existing vector database.
    
    Args:
        query: Original query name to find the database
        topic: Optional custom topic (auto-generated if empty)
        n_results: Number of papers to retrieve
        log_callback: Optional callback for logging
        
    Returns:
        Dictionary with review text and metadata
    """
    import json
    
    if log_callback:
        log_callback(f"🔍 Looking for database: {query}")
    
    # Find database folder by original query
    db_dir = os.path.join(PROJECT_ROOT, "data/vector_dbs")
    target_folder = None
    
    for folder in os.listdir(db_dir):
        folder_path = os.path.join(db_dir, folder)
        if not os.path.isdir(folder_path):
            continue
            
        # Check metadata file
        metadata_file = os.path.join(folder_path, "query_metadata.json")
        if os.path.exists(metadata_file):
            try:
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                    if metadata.get("original_query") == query:
                        target_folder = folder
                        break
            except Exception:
                pass
        # Legacy: check if slug matches
        elif folder.replace("_", " ") == query or folder == query:
            target_folder = folder
            break
    
    if not target_folder:
        error_msg = f"❌ Database not found for query: {query}"
        if log_callback:
            log_callback(error_msg)
        return {"error": error_msg}
    
    slug = target_folder
    db_path = os.path.join(db_dir, slug)
    
    if log_callback:
        log_callback(f"📚 Loading vector DB from: {db_path}")
    
    # Load vector DB and retrieve papers
    mem = PersistentMemory(db_name=f"db_{slug}", data_dir=db_path)
    search_query = topic or query
    evidence = mem.query(search_query, n=n_results)
    
    if not evidence or not evidence.get("ids") or len(evidence["ids"][0]) == 0:
        raise ValueError("No papers found in vector database")
    
    if log_callback:
        log_callback(f"📖 Retrieved {len(evidence['ids'][0])} papers from vector DB")
    
    # Generate or use provided topic
    final_topic = topic
    if not final_topic:
        if log_callback:
            log_callback("🧠 Auto-generating topic from papers...")
        try:
            writer_temp = DeepSeekWriter(gemini_key=gemini_key)
            final_topic = generate_topic_from_evidence(
                evidence,
                writer_temp.api_key,
                writer_temp.base_url,
                gemini_key=gemini_key
            )


            if log_callback:
                log_callback(f"✅ Generated topic: {final_topic}")
        except Exception as e:
            if log_callback:
                log_callback(f"⚠️ Topic generation failed: {e}, using query as topic")
            final_topic = query
    
    # Generate review
    if log_callback:
        log_callback("✍️ Generating review with DeepSeek...")
    
    writer = DeepSeekWriter(gemini_key=gemini_key)


    markdown = writer.generate_review(
        topic=final_topic,
        evidence=evidence,
        raw_query=query,
        search_term=query
    )
    
    # Append references section
    if evidence and evidence.get("ids") and len(evidence["ids"][0]) > 0:
        references = "\n\n## 参考文献\n\n"
        ids = evidence["ids"][0]
        metas = evidence.get("metadatas", [[]])[0]
        
        for idx, pmid in enumerate(ids, start=1):
            meta = metas[idx - 1] if idx - 1 < len(metas) else {}
            title = meta.get("title", "No Title")
            journal = meta.get("journal", "")
            year = meta.get("year", "")
            citations = meta.get("citations", None)
            
            ref_line = f"{idx}. {title}"
            if journal or year:
                ref_line += f". {journal} {year}."
            ref_line += f" (PMID:{pmid}"
            if citations is not None:
                ref_line += f", 被引:{citations}"
            ref_line += ")\n"
            
            references += ref_line
        
        markdown += references
    
    # Save to file with topic as filename
    import re
    safe_filename = re.sub(r'[^\w\s-]', '', final_topic).strip()
    safe_filename = re.sub(r'[-\s]+', '_', safe_filename)
    if len(safe_filename) > 100:
        safe_filename = safe_filename[:100]
    
    output_path = os.path.join(PROJECT_ROOT, f"{safe_filename}.md")
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(markdown)
        if log_callback:
            log_callback(f"💾 Saved to: {output_path}")
    except Exception as e:
        if log_callback:
            log_callback(f"⚠️ Failed to save file: {e}")
    
    if log_callback:
        log_callback("✅ Review generation complete!")
    
    return {
        "markdown": markdown,
        "topic": final_topic,
        "output_path": output_path
    }


def fetch_fulltext(
    pmid: str,
    doi: str = "",
    title: str = "",
    log_callback: Optional[Callable] = None
) -> Dict:
    """
    Fetch full-text PDF, convert to markdown, and extract figures.
    
    Args:
        pmid: PubMed ID
        doi: DOI (optional, will try to repair if missing)
        title: Paper title (for DOI repair)
        log_callback: Optional callback for logging
        
    Returns:
        Dict with 'markdown', 'figures', 'pdf_path' keys
    """
    import asyncio
    
    target_doi = doi
    
    # Smart DOI repair if missing
    if not target_doi and title:
        if log_callback:
            log_callback("⚠️ Missing DOI. Attempting Smart Repair via CrossRef...")
        
        from app.api.server import fetch_doi_from_crossref
        target_doi = fetch_doi_from_crossref(title)
        
        if target_doi:
            if log_callback:
                log_callback(f"✅ Smart Repair Success! New DOI: {target_doi}")
        else:
            if log_callback:
                log_callback("❌ Smart Repair Failed. Cannot fetch PDF.")
            raise ValueError("DOI missing and could not be found via Smart Repair.")
    
    if not target_doi:
        raise ValueError("No DOI provided and Smart Repair failed.")
    
    # Fetch PDF
    if log_callback:
        log_callback(f"📄 Fetching PDF for DOI: {target_doi}...")
    
    fetcher = PisminFetcher(download_dir=os.path.join(PROJECT_ROOT, "data/raw_pdfs"))
    
    # Run async fetch in event loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    pdf_path = loop.run_until_complete(fetcher.fetch_pdf(target_doi))
    loop.close()
    
    if not pdf_path:
        raise ValueError("Could not fetch PDF from Pismin/SciHub.")
    
    if log_callback:
        log_callback(f"✅ PDF downloaded: {pdf_path}")
    
    # Convert to Markdown
    if log_callback:
        log_callback("📝 Converting PDF to Markdown...")
    
    md_content = convert_pdf_to_markdown(pdf_path)
    if not md_content:
        raise ValueError("Failed to convert PDF to Markdown.")
    
    # Extract Figures
    if log_callback:
        log_callback("🖼️ Extracting figures...")
    
    fig_dir = os.path.join(PROJECT_ROOT, "data/processed_figures", pmid)
    fig_processor = FigureProcessor()
    figures = fig_processor.process_pdf(pdf_path, fig_dir)
    
    if log_callback:
        log_callback(f"✅ Extracted {len(figures)} figures")
    
    return {
        "markdown": md_content,
        "figures": figures,
        "pdf_path": pdf_path
    }


def get_available_queries() -> List[str]:
    """
    Get list of available queries from vector_dbs directory.
    
    Returns:
        List of original query names (not slugs)
    """
    import json
    
    db_dir = os.path.join(PROJECT_ROOT, "data/vector_dbs")
    if not os.path.exists(db_dir):
        return []
    
    queries = []
    for folder in os.listdir(db_dir):
        folder_path = os.path.join(db_dir, folder)
        if os.path.isdir(folder_path):
            # Try to read metadata file first
            metadata_file = os.path.join(folder_path, "query_metadata.json")
            if os.path.exists(metadata_file):
                try:
                    with open(metadata_file, 'r', encoding='utf-8') as f:
                        metadata = json.load(f)
                        queries.append(metadata.get("original_query", folder))
                except Exception:
                    # Fallback: convert slug back to readable format
                    queries.append(folder.replace("_", " "))
            else:
                # Legacy: convert slug back to readable format
                queries.append(folder.replace("_", " "))
    
    return sorted(queries, reverse=True)  # Most recent first
