
"""
Report Page - Generate PPT from Papers
"""

import streamlit as st
import os
import sys
import tempfile
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from utils import sidebar_settings, error_display
from core.generators.content_extractor import ContentExtractor
from core.generators.ppt_generator import PPTGenerator

# Simple PDF text extractor for now (if not reusing others)
import fitz # PyMuPDF

def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract text from PDF using PyMuPDF"""
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text

# Page config
st.set_page_config(
    page_title="Report - Lit-Miner",
    page_icon="📊",
    layout="wide"
)

# Render sidebar
config = sidebar_settings()

# Main content
st.title("📊 Research Report Generator")
st.markdown("Upload a research paper (PDF) to auto-generate a **PowerPoint presentation**.")

# 1. Upload PDF
st.subheader("1. Upload Paper")
uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

if uploaded_file is not None:
    # Save uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        tmp_file.write(uploaded_file.getbuffer())
        tmp_path = tmp_file.name
    
    st.info(f"📄 File uploaded: **{uploaded_file.name}**")
    
    # 2. Extract & Analyze
    st.subheader("2. Analyze Content")
    
    if st.button("🚀 Analyze & Generate PPT", type="primary"):
        progress = st.progress(0, text="Starting analysis...")
        
        try:
            # Step 1: Extract Text
            progress.progress(20, text="Extracting text from PDF...")
            raw_text = extract_text_from_pdf(tmp_path)
            
            if len(raw_text) < 100:
                st.error("⚠️ Failed to extract text. The PDF might be scanned/image-based.")
                st.stop()
                
            # Step 2: AI Extraction
            progress.progress(40, text="AI analyzing content (DeepSeek)...")
            extractor = ContentExtractor()
            
            # Add metadata from filename as fallback
            paper_data = extractor.extract_from_text(raw_text)
            paper_data["title"] = paper_data.get("title", uploaded_file.name.replace(".pdf", ""))
            
            # Step 3: Generate PPT
            progress.progress(80, text="Generating PowerPoint slides...")
            ppt_gen = PPTGenerator()
            
            # Create output path
            output_dir = "data/reports"
            os.makedirs(output_dir, exist_ok=True)
            output_path = os.path.join(output_dir, f"Report_{uploaded_file.name.replace('.pdf', '')}.pptx")
            
            ppt_gen.create_report(paper_data, output_path)
            
            progress.progress(100, text="Done!")
            
            # Step 4: Display & Download
            st.success("✅ PPT Generated Successfully!")
            
            # Preview Content
            with st.expander("👀 View Extracted Content", expanded=True):
                st.json(paper_data)
                
            # Download Button
            with open(output_path, "rb") as f:
                st.download_button(
                    label="📥 Download PPT",
                    data=f,
                    file_name=os.path.basename(output_path),
                    mime="application/vnd.openxmlformats-officedocument.presentationml.presentation"
                )
                
        except Exception as e:
            st.error(f"Error: {e}")
            import traceback
            st.code(traceback.format_exc())
            
        finally:
            # Cleanup temp file
            os.unlink(tmp_path)

else:
    st.info("👆 Upload a PDF to get started")

# Tips
st.divider()
st.markdown("""
### 💡 How it works
1. **Upload**: Select a medical research PDF
2. **Analyze**: DeepSeek AI extracts structure (Background, Methods, Results, Conclusion)
3. **Generate**: Creates a clean, standard 5-slide PowerPoint presentation
""")
