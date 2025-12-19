"""Utilities package for Streamlit app"""

from .backend import (
    run_smart_mining,
    generate_ai_review,
    get_available_queries
)

# Read functionality from local_pdf_processor
from .local_pdf_processor import process_local_pdf

# Tools functionality
from .pmid_tools import lookup_pmid

from .ui_components import (
    display_paper_card,
    log_container,
    progress_tracker,
    sidebar_settings,
    error_display
)

__all__ = [
    'run_smart_mining',
    'generate_ai_review',
    'get_available_queries',
    'process_local_pdf',
    'lookup_pmid',
    'display_paper_card',
    'log_container',
    'progress_tracker',
    'sidebar_settings',
    'error_display'
]
