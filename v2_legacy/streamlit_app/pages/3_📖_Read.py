"""
📖 Read - Local PDF Intelligent Extraction
Upload PDF and extract structured content using AI
"""

import streamlit as st
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from utils.local_pdf_processor import process_local_pdf

st.set_page_config(
    page_title="Read - Lit-Miner",
    page_icon="📖",
    layout="wide"
)

st.title("📖 Read - PDF Intelligent Extraction")
st.markdown("""
Upload a PDF and let AI extract structured content:
- 📝 Text → Markdown file
- 🖼️ Figures → Separate images
- 📊 Tables → Separate images
""")

# Upload section
st.divider()
st.markdown("### 📤 Upload PDF")

uploaded_file = st.file_uploader(
    "Choose a PDF file",
    type=['pdf'],
    help="Upload an academic paper or document for AI-powered extraction"
)

if uploaded_file:
    # Display file info
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Filename", uploaded_file.name)
    with col2:
        st.metric("Size", f"{uploaded_file.size / 1024:.1f} KB")
    with col3:
        st.metric("Type", uploaded_file.type)
    
    # Process button
    st.divider()
    if st.button("🤖 Start AI Extraction", type="primary", use_container_width=True):
        try:
            with st.spinner("AI model processing... This may take a minute."):
                result = process_local_pdf(uploaded_file)
            
            st.success(f"✅ Extraction complete! Processed {result.num_pages} pages")
            
            # Store in session state
            st.session_state['processed_result'] = result
            
        except Exception as e:
            st.error(f"❌ Processing failed: {str(e)}")
            st.info("💡 Please check the PDF and try again")

# Display results if available
if 'processed_result' in st.session_state:
    result = st.session_state['processed_result']
    
    st.divider()
    st.markdown("### 📊 Extraction Results")
    
    # Layout: left for text, right for images/tables
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("#### 📝 Extracted Text")
        
        # Show preview
        with st.expander("📄 Preview Markdown", expanded=True):
            st.markdown(result.markdown)
        
        # Download markdown
        st.download_button(
            "💾 Download Markdown",
            data=result.markdown,
            file_name=f"{result.pdf_id}_content.md",
            mime="text/markdown",
            use_container_width=True
        )
        
        # Show stats
        st.caption(f"📊 Stats: {len(result.markdown)} characters, {result.num_pages} pages")
    
    with col2:
        # Figures
        if result.figures:
            st.markdown(f"#### 🖼️ Figures ({len(result.figures)})")
            for idx, fig_path in enumerate(result.figures):
                if os.path.exists(fig_path):
                    try:
                        st.image(fig_path, caption=f"Figure {idx+1}", use_container_width=True)
                        with open(fig_path, "rb") as f:
                            st.download_button(
                                f"💾 Download Fig {idx+1}",
                                data=f.read(),
                                file_name=os.path.basename(fig_path),
                                mime="image/png",
                                key=f"fig_{idx}",
                                use_container_width=True
                            )
                    except Exception as e:
                        st.error(f"Error displaying figure {idx+1}: {str(e)}")
                        st.caption(f"Path: {fig_path}")
                else:
                    st.warning(f"Figure {idx+1} file not found: {fig_path}")
        else:
            st.info("🖼️ No figures detected")
        
        # Tables
        if result.tables:
            st.markdown(f"#### 📊 Tables ({len(result.tables)})")
            for idx, tbl_path in enumerate(result.tables):
                if os.path.exists(tbl_path):
                    try:
                        st.image(tbl_path, caption=f"Table {idx+1}", use_container_width=True)
                        with open(tbl_path, "rb") as f:
                            st.download_button(
                                f"💾 Download Table {idx+1}",
                                data=f.read(),
                                file_name=os.path.basename(tbl_path),
                                mime="image/png",
                                key=f"tbl_{idx}",
                                use_container_width=True
                            )
                    except Exception as e:
                        st.error(f"Error displaying table {idx+1}: {str(e)}")
                        st.caption(f"Path: {tbl_path}")
                else:
                    st.warning(f"Table {idx+1} file not found: {tbl_path}")
        else:
            st.info("📊 No tables detected")

# Usage tips
st.divider()
with st.expander("💡 Usage Tips"):
    st.markdown("""
    **How it works:**
    1. Upload a PDF file (academic papers work best)
    2. AI model (LayoutParser) analyzes each page
    3. Extracts text, figures, and tables separately
    
    **What you get:**
    - **Markdown file**: All text content in readable format
    - **Figure images**: Each figure as a separate PNG file
    - **Table images**: Each table as a separate PNG file
    
    **Tips:**
    - Best results with clearly formatted academic papers
    - Processing may take 30-60 seconds depending on PDF size
    - All extracted content can be downloaded individually
    
    **Note:** This is completely local - no data is sent to external servers.
    """)

# Footer
st.divider()
st.caption("📖 Read | Lit-Miner | Local PDF Processing with AI")
