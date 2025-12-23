"""
Local PDF Processor
Upload and extract structured content from PDFs using AI
"""

import os
import fitz  # PyMuPDF
from typing import Dict, List
from datetime import datetime
from dataclasses import dataclass


@dataclass
class ProcessedContent:
    """Structured content from PDF"""
    pdf_id: str
    markdown: str
    figures: List[str]  # paths to figure images
    tables: List[str]   # paths to table images
    pdf_path: str
    num_pages: int


def save_uploaded_pdf(uploaded_file, pdf_id: str) -> str:
    """
    Save uploaded PDF file to disk.
    
    Args:
        uploaded_file: Streamlit UploadedFile object
        pdf_id: Unique identifier for this PDF
        
    Returns:
        Path to saved PDF
    """
    from config import PDF_DIR
    
    os.makedirs(PDF_DIR, exist_ok=True)
    pdf_path = os.path.join(PDF_DIR, f"{pdf_id}.pdf")
    
    # Save uploaded file
    with open(pdf_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    return pdf_path


def extract_text_to_markdown(pdf_path: str) -> str:
    """
    Extract text from PDF and format as Markdown.
    
    Args:
        pdf_path: Path to PDF file
        
    Returns:
        Markdown-formatted text
    """
    doc = fitz.open(pdf_path)
    markdown_lines = []
    
    # Add metadata
    markdown_lines.append(f"# PDF Document Analysis\n\n")
    markdown_lines.append(f"**Pages**: {len(doc)}\n\n")
    markdown_lines.append("---\n\n")
    
    for page_num in range(len(doc)):
        page = doc[page_num]
        
        # Add page header
        markdown_lines.append(f"## Page {page_num + 1}\n\n")
        
        # Extract text blocks
        blocks = page.get_text("blocks")
        
        for block in blocks:
            if len(block) >= 5:
                text = block[4].strip()
                
                if not text:
                    continue
                
                # Simple heuristic for formatting
                if len(text) < 100 and text.isupper():
                    # Likely a heading
                    markdown_lines.append(f"### {text}\n\n")
                else:
                    # Regular paragraph
                    markdown_lines.append(f"{text}\n\n")
        
        markdown_lines.append("\n")
    
    doc.close()
    return "".join(markdown_lines)


def extract_structured_content(pdf_path: str, pdf_id: str) -> ProcessedContent:
    """
    Extract structured content from PDF using AI.
    
    Separates:
    - Text → Markdown file
    - Figures → figures/
    - Tables → tables/
    
    Args:
        pdf_path: Path to PDF
        pdf_id: Unique ID for this PDF
        
    Returns:
        ProcessedContent with all extracted data
    """
    from config import PROJECT_ROOT
    
    # Create output directories
    output_base = os.path.join(PROJECT_ROOT, "data/processed", pdf_id)
    figures_dir = os.path.join(output_base, "figures")
    tables_dir = os.path.join(output_base, "tables")
    
    for dir_path in [output_base, figures_dir, tables_dir]:
        os.makedirs(dir_path, exist_ok=True)
    
    # Extract text to markdown
    print(f"[*] Extracting text from PDF...")
    markdown = extract_text_to_markdown(pdf_path)
    
    # Save markdown
    md_path = os.path.join(output_base, "content.md")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(markdown)
    
    # Extract figures and tables using LayoutParser AI
    figures = []
    tables = []
    
    try:
        import layoutparser as lp
        import cv2
        import numpy as np
        from pdf2image import convert_from_path
        
        print(f"[*] Initializing AI Layout Model...")
        
        # Load local model
        home_dir = os.path.expanduser("~")
        local_weights = os.path.join(home_dir, ".layoutparser", "model_final.pth")
        
        if os.path.exists(local_weights):
            model = lp.Detectron2LayoutModel(
                config_path='lp://PubLayNet/mask_rcnn_X_101_32x8d_FPN_3x/config',
                model_path=local_weights,
                extra_config=["MODEL.ROI_HEADS.SCORE_THRESH_TEST", 0.5],
                label_map={0: "Text", 1: "Title", 2: "List", 3: "Table", 4: "Figure"}
            )
            
            print(f"[*] Converting PDF to images...")
            images = convert_from_path(pdf_path, dpi=200)
            
            for page_num, image in enumerate(images):
                print(f"    [AI] Analyzing Page {page_num + 1}...")
                
                image_np = np.array(image)
                layout = model.detect(image_np)
                
                # Extract figures
                figure_blocks = lp.Layout([b for b in layout if b.type == 'Figure'])
                for fig_idx, block in enumerate(figure_blocks):
                    try:
                        segment = block.crop_image(image_np)
                        
                        if segment.size == 0 or segment.shape[0] < 50 or segment.shape[1] < 50:
                            continue
                        
                        filename = f"page{page_num+1}_fig{fig_idx+1}.png"
                        filepath = os.path.join(figures_dir, filename)
                        
                        segment_bgr = cv2.cvtColor(segment, cv2.COLOR_RGB2BGR)
                        cv2.imwrite(filepath, segment_bgr)
                        figures.append(filepath)
                        print(f"          -> Saved figure: {filename}")
                    except Exception as e:
                        print(f"          [Skip] Figure extraction error: {e}")
                
                # Extract tables
                table_blocks = lp.Layout([b for b in layout if b.type == 'Table'])
                for tbl_idx, block in enumerate(table_blocks):
                    try:
                        segment = block.crop_image(image_np)
                        
                        if segment.size == 0 or segment.shape[0] < 50 or segment.shape[1] < 50:
                            continue
                        
                        filename = f"page{page_num+1}_table{tbl_idx+1}.png"
                        filepath = os.path.join(tables_dir, filename)
                        
                        segment_bgr = cv2.cvtColor(segment, cv2.COLOR_RGB2BGR)
                        cv2.imwrite(filepath, segment_bgr)
                        tables.append(filepath)
                        print(f"          -> Saved table: {filename}")
                    except Exception as e:
                        print(f"          [Skip] Table extraction error: {e}")
            
            print(f"[*] AI extraction complete: {len(figures)} figures, {len(tables)} tables")
        else:
            print(f"[!] AI model not found, skipping figure/table extraction")
            
    except Exception as e:
        print(f"[!] AI extraction error: {e}")
    
    # Get page count
    doc = fitz.open(pdf_path)
    num_pages = len(doc)
    doc.close()
    
    return ProcessedContent(
        pdf_id=pdf_id,
        markdown=markdown,
        figures=figures,
        tables=tables,
        pdf_path=pdf_path,
        num_pages=num_pages
    )


def process_local_pdf(uploaded_file) -> ProcessedContent:
    """
    Main entry point for processing uploaded PDF.
    
    Args:
        uploaded_file: Streamlit UploadedFile object
        
    Returns:
        ProcessedContent with all extracted data
    """
    # Generate unique ID
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    original_name = uploaded_file.name.replace('.pdf', '').replace(' ', '_')
    pdf_id = f"{original_name}_{timestamp}"
    
    # Save uploaded file
    pdf_path = save_uploaded_pdf(uploaded_file, pdf_id)
    print(f"[*] PDF saved: {pdf_path}")
    
    # Extract structured content
    result = extract_structured_content(pdf_path, pdf_id)
    
    return result
