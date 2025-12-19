"""
🔧 Tools - PMID Information Lookup
Quick utility to get paper information from PMID
"""

import streamlit as st
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from utils.pmid_tools import lookup_pmid

st.set_page_config(
    page_title="Tools - Lit-Miner",
    page_icon="🔧",
    layout="wide"
)

st.title("🔧 Tools - PMID Information Lookup")
st.markdown("""
Quick tool to look up paper information from PubMed ID.  
Get DOI, title, and direct links without downloading the full paper.
""")

# Input section
st.divider()
col1, col2 = st.columns([3, 1])

with col1:
    pmid = st.text_input(
        "Enter PubMed ID (PMID)",
        placeholder="e.g., 36054302",
        help="Enter the numerical PubMed ID"
    )

with col2:
    st.markdown("<br>", unsafe_allow_html=True)
    search_button = st.button("🔍 Lookup", type="primary", use_container_width=True)

# Process lookup
if search_button and pmid:
    if not pmid.strip().isdigit():
        st.error("❌ Please enter a valid numerical PMID")
    else:
        try:
            with st.spinner(f"Looking up PMID {pmid}..."):
                result = lookup_pmid(pmid.strip())
            
            st.success("✅ Information retrieved successfully!")
            
            # Display results
            st.divider()
            
            # Basic info
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown("### 📄 Paper Information")
                st.markdown(f"**Title**: {result['title']}")
                st.markdown(f"**Journal**: {result['journal']} ({result['year']})")
                
                with st.expander("📝 Show Abstract"):
                    st.write(result['abstract'])
            
            with col2:
                st.markdown("### 🔑 Identifiers")
                st.metric("PMID", result['pmid'])
                
                if result['doi'] != "Not available":
                    st.code(result['doi'], language=None)
                    if st.button("📋 Copy DOI"):
                        st.toast("DOI copied to clipboard!")
                else:
                    st.info("DOI not available")
            
            # Links section
            st.divider()
            st.markdown("### 🔗 Quick Access Links")
            
            link_col1, link_col2, link_col3 = st.columns(3)
            
            with link_col1:
                st.markdown(f"""
                <a href="{result['pubmed_url']}" target="_blank">
                    <button style="width:100%; padding:10px; background:#0066cc; color:white; border:none; border-radius:5px; cursor:pointer;">
                        📚 Open in PubMed
                    </button>
                </a>
                """, unsafe_allow_html=True)
            
            with link_col2:
                if result['doi_url']:
                    st.markdown(f"""
                    <a href="{result['doi_url']}" target="_blank">
                        <button style="width:100%; padding:10px; background:#28a745; color:white; border:none; border-radius:5px; cursor:pointer;">
                            🔓 Open DOI Link
                        </button>
                    </a>
                    """, unsafe_allow_html=True)
                else:
                    st.button("🔓 DOI Link", disabled=True, use_container_width=True)
            
            with link_col3:
                if result['scihub_url']:
                    st.markdown(f"""
                    <a href="{result['scihub_url']}" target="_blank">
                        <button style="width:100%; padding:10px; background:#6c757d; color:white; border:none; border-radius:5px; cursor:pointer;">
                            🦅 Sci-Hub Access
                        </button>
                    </a>
                    """, unsafe_allow_html=True)
                else:
                    st.button("🦅 Sci-Hub", disabled=True, use_container_width=True)
            
        except Exception as e:
            st.error(f"❌ Lookup failed: {str(e)}")
            st.info("💡 Please check the PMID and try again")

elif search_button:
    st.warning("⚠️ Please enter a PMID")

# Usage tips
st.divider()
with st.expander("💡 Usage Tips"):
    st.markdown("""
    **How to use:**
    1. Enter a PubMed ID (PMID) - the numerical identifier for papers in PubMed
    2. Click "Lookup" to retrieve information
    3. Use the quick access links to open the paper in different sources
    
    **Where to find PMID:**
    - On PubMed search results page
    - In paper citations (usually listed as "PMID: 12345678")
    - From Search results in this app
    
    **What you get:**
    - DOI (Digital Object Identifier)
    - Paper title and abstract
    - Direct links to PubMed, DOI resolver, and Sci-Hub
    """)

# Footer
st.divider()
st.caption("🔧 Tools | Lit-Miner | Quick PMID Lookup Utility")
