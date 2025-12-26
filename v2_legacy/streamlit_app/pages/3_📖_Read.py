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
from core.generators.content_extractor import ContentExtractor
from core.generators.ppt_generator import PPTGenerator
from core.chatbot.gemini_embeddings import GeminiEmbeddings
import chromadb
from chromadb.config import Settings
from config import VECTOR_DB_DIR


st.set_page_config(
    page_title="Read - Lit-Miner",
    page_icon="📖",
    layout="wide"
)


# Sidebar Configuration
with st.sidebar:
    st.header("⚙️ Settings")
    api_key = st.text_input("DeepSeek API Key", type="password", help="Required for PPT content analysis")
    if api_key:
        os.environ["DEEPSEEK_API_KEY"] = api_key
    
    st.divider()
    st.markdown("### 🛠️ Functionality")
    st.info("Upload a PDF to start.")

# Main Layout
st.title("📖 Read - PDF Intelligent Extraction")
st.markdown("""
Upload a PDF to extract text, figures, and generate a PowerPoint report.
""")

uploaded_file = st.file_uploader("Upload PDF", type=['pdf'], label_visibility="collapsed")

if uploaded_file:
    # Display file info in a concise way
    st.info(f"📄 **{uploaded_file.name}** ({uploaded_file.size / 1024:.1f} KB)")
    
    # Process button
    if st.button("🤖 Start AI Extraction", type="primary", use_container_width=True):
        try:
            with st.spinner("AI model processing... This may take a minute."):
                result = process_local_pdf(uploaded_file)
            
            st.success(f"✅ Extraction complete! Processed {result.num_pages} pages")
            st.session_state['processed_result'] = result
            
        except Exception as e:
            st.error(f"❌ Processing failed: {str(e)}")


if 'processed_result' in st.session_state:
    result = st.session_state['processed_result']
    
    st.divider()
    
    # --- Top Control Bar: Report Generation ---
    col_kpi1, col_kpi2 = st.columns([3, 1])
    with col_kpi1:
        st.markdown(f"### 📊 Analysis Results ({len(result.markdown)} chars, {len(result.figures)+len(result.tables)} images)")
    with col_kpi2:
        if st.button("🚀 Generate PPT", type="primary", use_container_width=True, help="Convert to PowerPoint"):
             # Logic for PPT generation (will implement inside a function or check session state trigger to avoid re-run issues)
             # Ideally we set a flag here or run it immediately
             st.session_state['trigger_ppt'] = True

    # Handle PPT Trigger
    if st.session_state.get('trigger_ppt'):
        try:
            if not os.environ.get("DEEPSEEK_API_KEY"):
                st.warning("⚠️ Please enter your DeepSeek API Key in the sidebar first!")
            else:
                with st.spinner("🤖 Analyzing & Generating PPT..."):
                    extractor = ContentExtractor()
                    paper_data = extractor.extract_from_text(result.markdown)
                    paper_data["title"] = paper_data.get("title", uploaded_file.name.replace(".pdf", ""))
                    
                    all_images = result.figures + result.tables
                    ppt_gen = PPTGenerator()
                    
                    output_dir = "data/reports"
                    os.makedirs(output_dir, exist_ok=True)
                    output_path = os.path.join(output_dir, f"Report_{uploaded_file.name.replace('.pdf', '')}.pptx")
                    
                    ppt_gen.create_report(paper_data, output_path, images=all_images)
                    
                    st.success("✅ PPT Ready!")
                    with open(output_path, "rb") as f:
                        st.download_button(
                            label="📥 Download .pptx",
                            data=f,
                            file_name=os.path.basename(output_path),
                            mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
                            use_container_width=True
                        )
                    # Reset trigger to avoid loop? Or keep it to show download button
                    # st.session_state['trigger_ppt'] = False 
        except Exception as e:
             st.error(f"PPT Generation failed: {e}")

    st.divider()
    
    # Layout: left for text, right for images/tables
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("#### 📝 Extracted Text")
        # Collapsed by default
        with st.expander("📄 View Markdown Content", expanded=False):
            st.markdown(result.markdown)
            st.download_button("💾 Save MD", result.markdown, f"{result.pdf_id}.md")
    
    with col2:
        # Figures & Tables
        images = result.figures + result.tables
        if images:
             st.markdown(f"#### 🖼️ Figures & Tables ({len(images)})")
             
             # Batch download button
             import zipfile
             import io
             
             zip_buffer = io.BytesIO()
             with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                 for idx, img_path in enumerate(images):
                     if os.path.exists(img_path):
                         zip_file.write(img_path, os.path.basename(img_path))
             
             st.download_button(
                 "📦 Download All Images (ZIP)",
                 data=zip_buffer.getvalue(),
                 file_name=f"{result.pdf_id}_images.zip",
                 mime="application/zip",
                 use_container_width=True
             )
             
             st.divider()
             
             # Show mini grid
             img_cols = st.columns(2)
             for idx, img_path in enumerate(images):
                 if os.path.exists(img_path):
                     img_cols[idx % 2].image(img_path, caption=f"Img {idx+1}", use_container_width=True)
        else:
             st.info("No images detected")

    
    # --- Add to Knowledge Base Section ---
    st.divider()
    st.markdown("#### 🧠 Knowledge Base Integration")
    
    col_kb1, col_kb2 = st.columns([3, 1])
    with col_kb1:
        st.markdown("""
        Add this document to the **Chatbot Knowledge Base** to ask questions about it.
        *Creates embeddings and stores in vector database.*
        """)
    with col_kb2:
        if st.button("📥 Add to Knowledge Base", type="secondary", use_container_width=True):
            try:
                with st.spinner("Chunking and Embedding..."):
                    # 1. Chunking Logic (Simplified)
                    text = result.markdown
                    chunk_size = 500
                    overlap = 50
                    chunks = []
                    start = 0
                    chunk_id = 0
                    
                    base_metadata = {
                        "filename": os.path.basename(result.pdf_path),
                        "pdf_id": result.pdf_id,
                        "title": result.pdf_id, # Fallback title
                        "source": "Read_Page_Upload"
                    }

                    while start < len(text):
                        end = start + chunk_size
                        chunk_text = text[start:end]
                        if end < len(text):
                            last_period = chunk_text.rfind('。')
                            if last_period == -1: last_period = chunk_text.rfind('.')
                            if last_period > chunk_size * 0.5:
                                end = start + last_period + 1
                                chunk_text = text[start:end]
                        
                        chunks.append({
                            "id": f"{result.pdf_id}_chunk_{chunk_id}",
                            "text": chunk_text.strip(),
                            "metadata": {**base_metadata, "chunk_id": chunk_id}
                        })
                        chunk_id += 1
                        start = end - overlap
                    
                    if not chunks:
                        st.warning("No text extracted to embed.")
                    else:
                         # 2. Embedding & Storage
                         embeddings_client = GeminiEmbeddings()
                         chroma_client = chromadb.PersistentClient(
                             path=str(VECTOR_DB_DIR / "chatbot"),
                             settings=Settings(anonymized_telemetry=False)
                         )
                         collection = chroma_client.get_or_create_collection(
                             name="periodontal_core",
                             metadata={"description": "Periodontal disease core literature (Gemini embeddings)"}
                         )
                         
                         texts = [c["text"] for c in chunks]
                         embeddings = embeddings_client.embed_documents(texts)
                         
                         collection.add(
                             documents=texts,
                             embeddings=embeddings,
                             metadatas=[c["metadata"] for c in chunks],
                             ids=[c["id"] for c in chunks]
                         )
                         
                         st.success(f"✅ Added {len(chunks)} chunks to Knowledge Base!")
                         st.balloons()
                         
            except Exception as e:
                st.error(f"Failed to add to Knowledge Base: {e}")


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
