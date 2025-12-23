"""
Reusable UI Components for Streamlit
"""

import streamlit as st
from typing import Dict, List


def display_paper_card(paper: Dict, index: int):
    """
    Display a paper as an expandable card.
    
    Args:
        paper: Paper dictionary with metadata
        index: Paper index (for display order)
    """
    # Color-code by category
    category = paper.get("category", "general")
    category_colors = {
        "high_impact": "🔴",
        "recent": "🟢", 
        "data_rich": "🔵",
        "general": "⚪"
    }
    
    category_icon = category_colors.get(category, "⚪")
    score = paper.get("score", 0)
    
    with st.expander(f"{category_icon} **[{index+1}] {paper['title']}** (Score: {score})"):
        # Metadata row
        col1, col2, col3 = st.columns(3)
        with col1:
            st.caption(f"**Journal:** {paper.get('journal', 'Unknown')}")
        with col2:
            st.caption(f"**Year:** {paper.get('year', 'N/A')}")
        with col3:
            st.caption(f"**Citations:** {paper.get('citations', 0)}")
        
        # DOI link
        if paper.get("doi"):
            st.caption(f"**DOI:** [{paper['doi']}](https://doi.org/{paper['doi']})")
        
        # Authors
        authors = paper.get("authors", [])
        if authors:
            st.caption(f"**Authors:** {', '.join(authors[:3])}{'...' if len(authors) > 3 else ''}")
        
        # Tags
        tags = paper.get("tags", [])
        if tags:
            tag_html = " ".join([f"<span style='background-color: #e0e0e0; padding: 2px 6px; border-radius: 3px; margin-right: 4px;'>{tag}</span>" for tag in tags])
            st.markdown(f"**Tags:** {tag_html}", unsafe_allow_html=True)
        
        # Abstract
        st.markdown("**Abstract:**")
        st.write(paper.get("abstract", "No abstract available."))
        
        # Category badge
        st.caption(f"**Category:** `{category}`")


def log_container():
    """
    Create a real-time log display container.
    
    Returns:
        Streamlit container for log updates
    """
    return st.empty()


def progress_tracker(steps: List[str], current_step: int = 0):
    """
    Display multi-step progress indicator.
    
    Args:
        steps: List of step descriptions
        current_step: Index of current step (0-indexed)
    """
    progress = (current_step + 1) / len(steps)
    st.progress(progress, text=f"Step {current_step + 1}/{len(steps)}: {steps[current_step]}")


def sidebar_settings():
    """
    Render shared sidebar settings and return configuration.
    
    Returns:
        Dict with 'email' and 'api_key' keys
    """
    with st.sidebar:
        st.header("⚙️ Settings")
        
        # Email for PubMed
        email = st.text_input(
            "PubMed Email",
            value=st.session_state.get("user_email", "your_email@example.com"),
            help="Required for PubMed API access"
        )
        st.session_state["user_email"] = email
        
        # API Key for DeepSeek
        api_key = st.text_input(
            "DeepSeek API Key",
            value=st.session_state.get("api_key", ""),
            type="password",
            help="Load from .env or enter manually"
        )
        st.session_state["api_key"] = api_key
        
        st.divider()
        
        # Database status
        st.header("📊 Status")
        from utils.backend import get_available_queries
        queries = get_available_queries()
        st.metric("Stored Queries", len(queries))
        
        if queries:
            st.caption("Recent searches:")
            for q in queries[-5:]:
                st.caption(f"• {q}")
        
    return {"email": email, "api_key": api_key}


def error_display(error: Exception):
    """
    Display error message in a consistent format.
    
    Args:
        error: Exception to display
    """
    st.error(f"❌ **Error:** {str(error)}")
    with st.expander("Details"):
        st.code(str(error))
