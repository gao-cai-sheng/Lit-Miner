"""
Search Page - Smart Literature Mining
"""

import streamlit as st
import os
import sys
import json
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from utils import (
    sidebar_settings,
    run_smart_mining,
    display_paper_card,
    error_display
)

# Page config
st.set_page_config(
    page_title="Search - Lit-Miner",
    page_icon="🔍",
    layout="wide"
)

# Render sidebar
config = sidebar_settings()

# Main content
st.title("🔍 Literature Search")
st.markdown("Smart mining with **AI-powered query expansion**, scoring, and ChromaDB storage")

# Show AI expansion status
from config import USE_AI_EXPANSION, DEEPSEEK_API_KEY
if USE_AI_EXPANSION and DEEPSEEK_API_KEY:
    st.success("🤖 AI Query Expansion: **Enabled** (Supports any medical domain)")
else:
    st.info("📝 Query Expansion: Legacy config-based mode")

# Search form
with st.form("search_form"):
    query = st.text_input(
        "Search Query",
        placeholder="e.g., socket preservation, alveolar ridge augmentation",
        help="Enter a medical/scientific topic. Chinese terms will be auto-translated."
    )
    
    limit = st.slider(
        "Maximum Papers",
        min_value=50,
        max_value=500,
        value=200,
        step=50,
        help="检索深度：50-200篇（免费），201-500篇（PRO功能，即将推出）"
    )
    
    # VIP tier hint
    if limit > 200:
        st.info("💎 深度检索（200+篇）即将推出PRO订阅功能，敬请期待！")
    
    submitted = st.form_submit_button("🔍 Search", type="primary")

# Handle search
if submitted:
    if not query.strip():
        st.warning("⚠️ Please enter a search query")
    elif not config["email"] or config["email"] == "your_email@example.com":
        st.warning("⚠️ Please set your PubMed email in the sidebar settings")
    else:
        # Initialize log container
        log_container = st.empty()
        logs = []
        
        def log_callback(message: str):
            """Callback to capture logs"""
            logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")
            log_container.code("\n".join(logs), language="log")
        
        # Progress container
        progress = st.progress(0, text="Starting search...")
        
        try:
            # Run mining
            st.info("🔍 Starting smart mining...")
            progress.progress(10, text="Expanding query...")
            
            papers = run_smart_mining(
                query=query,
                limit=limit,
                email=config["email"],
                log_callback=log_callback
            )
            
            progress.progress(100, text="Complete!")
            
            # Store in session state
            st.session_state["search_results"] = papers
            st.session_state["current_query"] = query
            
            # Success message
            st.success(f"✅ Found and stored {len(papers)} papers!")
            
            # Clear progress
            progress.empty()
            
        except Exception as e:
            progress.empty()
            error_display(e)

# Display results
if "search_results" in st.session_state and st.session_state["search_results"]:
    st.divider()
    st.header(f"📚 Results ({len(st.session_state['search_results'])} papers)")
    
    papers = st.session_state["search_results"]
    
    # Export options
    col1, col2 = st.columns([1, 5])
    with col1:
        # Export as JSON
        json_data = json.dumps(papers, indent=2, ensure_ascii=False)
        st.download_button(
            "📥 Export JSON",
            data=json_data,
            file_name=f"search_results_{st.session_state['current_query'][:30]}.json",
            mime="application/json"
        )
    
    st.divider()
    
    # Category filter
    categories = list(set(p.get("category", "general") for p in papers))
    selected_category = st.selectbox(
        "Filter by Category",
        ["All"] + categories,
        key="category_filter"
    )
    
    # Filter papers
    if selected_category != "All":
        filtered_papers = [p for p in papers if p.get("category") == selected_category]
    else:
        filtered_papers = papers
    
    st.caption(f"Showing {len(filtered_papers)} of {len(papers)} papers")
    
    # Display papers
    for idx, paper in enumerate(filtered_papers):
        display_paper_card(paper, idx)
    
    # Navigation hint
    st.divider()
    st.info("💡 **Next step:** Go to the [Write](Write) page to generate an AI-powered review from these papers!")

else:
    st.info("👆 Enter a search query above to get started")
