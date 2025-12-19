"""
Lit-Miner: AI-Powered Literature Mining & Review Generation
Home Page
"""

import streamlit as st
import os
import sys

# Page config (must be first Streamlit command)
st.set_page_config(
    page_title="Lit-Miner",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils import sidebar_settings, get_available_queries

# Render sidebar settings
config = sidebar_settings()

# Main content
st.title("📚 Lit-Miner")
st.subheader("AI-Powered Literature Mining & Review Generation")

st.markdown("""
Welcome to **Lit-Miner**, an intelligent literature research assistant that combines:
- 🔍 **Smart Mining**: Advanced PubMed search with query expansion and intelligent scoring
- ✍️ **AI Writing**: Automated literature review generation powered by DeepSeek
- 📖 **Read**: Local PDF processing with AI-powered extraction
- 🔧 **Tools**: Quick PMID information lookup
""")

st.divider()

# Feature cards
st.header("🚀 Features")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("""
    ### 🔍 Search
    
    **Smart Literature Mining**
    - Query expansion (CN→EN, synonyms)
    - Rubric-based scoring (impact, recency, data quality)
    - Automatic categorization
    - ChromaDB storage for RAG
    
    [Go to Search →](Search)
    """)

with col2:
    st.markdown("""
    ### ✍️ Write
    
    **AI Review Generation**
    - Auto-topic generation from papers
    - DeepSeek-powered synthesis
    - RAG-enhanced accuracy
    - Markdown export
    
    [Go to Write →](Write)
    """)

with col3:
    st.markdown("""
    ### 📖 Read
    
    **Local PDF Processing**
    - Upload PDF files
    - AI extraction (LayoutParser)
    - Text → Markdown
    - Auto-separate figures & tables
    
    [Go to Read →](Read)
    """)

with col4:
    st.markdown("""
    ### 🔧 Tools
    
    **PMID Quick Lookup**
    - PMID → DOI conversion
    - Paper metadata
    - Quick access links
    - No download needed
    
    [Go to Tools →](Tools)
    """)

st.divider()

# Quick stats
st.header("📊 Quick Stats")

queries = get_available_queries()
num_queries = len(queries)

metric_col1, metric_col2, metric_col3 = st.columns(3)

with metric_col1:
    st.metric("Stored Queries", num_queries)

with metric_col2:
    # Count total papers (approximate by counting ChromaDB documents)
    total_papers = 0
    db_dir = "data/vector_dbs"
    if os.path.exists(db_dir):
        for folder in os.listdir(db_dir):
            folder_path = os.path.join(db_dir, folder)
            if os.path.isdir(folder_path):
                # Rough estimate - ChromaDB stores metadata in chroma.sqlite3
                chroma_db = os.path.join(folder_path, "chroma.sqlite3")
                if os.path.exists(chroma_db):
                    total_papers += 1  # Placeholder - could parse actual count
    
    st.metric("Database Collections", total_papers)

with metric_col3:
    # Count downloaded PDFs
    pdf_dir = "data/raw_pdfs"
    num_pdfs = 0
    if os.path.exists(pdf_dir):
        num_pdfs = len([f for f in os.listdir(pdf_dir) if f.endswith('.pdf')])
    
    st.metric("Downloaded PDFs", num_pdfs)

# Recent searches
if queries:
    st.divider()
    st.header("🕐 Recent Searches")
    
    recent = queries[-5:][::-1]  # Last 5, reversed
    for q in recent:
        st.caption(f"• {q}")

# Footer
st.divider()
st.caption("Built with Streamlit | Powered by DeepSeek & PubMed")
