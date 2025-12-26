
import sys
import os
import traceback
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from streamlit_app.utils.local_pdf_processor import extract_structured_content

def debug_extraction():
    pdf_path = "v2_legacy/data/pdfs/chatbot_knowledge/J Clinic Periodontology - 2019 - Donos - The adjunctive use of host modulators in non‐surgical periodontal therapy  A.pdf"
    
    if not os.path.exists(pdf_path):
        print(f"File not found: {pdf_path}")
        return

    print(f"Testing extraction on: {pdf_path}")
    
    try:
        pdf_id = "debug_test"
        result = extract_structured_content(pdf_path, pdf_id)
        print("✅ Extraction successful!")
        print(f"Markdown length: {len(result.markdown)}")
    except Exception:
        print("❌ Extraction failed!")
        traceback.print_exc()

if __name__ == "__main__":
    debug_extraction()
