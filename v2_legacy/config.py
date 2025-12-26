# Lit-Miner Configuration
# Core system configuration for literature mining and AI writing

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# === API Configuration ===
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
DEEPSEEK_BASE_URL = "https://api.deepseek.com"
PUBMED_EMAIL = os.getenv("PUBMED_EMAIL", "your_email@example.com")

# === Directory Configuration ===
BASE_DIR = Path(__file__).parent
PROJECT_ROOT = BASE_DIR
DATA_DIR = BASE_DIR / "data"
VECTOR_DB_DIR = DATA_DIR / "vector_dbs"
PDF_DIR = DATA_DIR / "pdfs"
PROCESSED_DIR = DATA_DIR / "processed"

# Create directories if they don't exist
for dir_path in [DATA_DIR, VECTOR_DB_DIR, PDF_DIR, PROCESSED_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)

# === AI Query Expansion Configuration ===
USE_AI_EXPANSION = True  # Enable/disable AI-powered query expansion
AI_EXPANSION_TIMEOUT = 10  # Timeout for AI API calls (seconds)
AI_EXPANSION_CACHE_ENABLED = True  # Enable caching for repeated queries

# === Query Expansion Rules (Legacy) ===
QUERY_EXPANSION_CONFIG = {
    "diseases": {
        "牙周炎": '("periodontitis"[MeSH Terms] OR "periodontitis"[Title/Abstract] OR "periodontal disease"[Title/Abstract])',
        "种植体周围炎": '("peri-implantitis"[MeSH Terms] OR "peri-implantitis"[Title/Abstract])',
        "骨缺损": '("bone defects"[MeSH Terms] OR "alveolar bone loss"[Title/Abstract] OR "bony defect"[Title/Abstract])',
    },
    "procedures": {
        "位点保存": '("socket preservation"[Title/Abstract] OR "alveolar ridge preservation"[Title/Abstract] OR "extraction socket"[Title/Abstract])',
        "GBR": '("guided bone regeneration"[Title/Abstract] OR "GBR"[Title/Abstract] OR "bone regeneration"[MeSH Terms])',
        "种植": '("dental implants"[MeSH Terms] OR "dental implantation"[MeSH Terms] OR "implant"[Title/Abstract])',
    },
    "outcomes": {
        "骨结合": '("osseointegration"[MeSH Terms] OR "bone-implant interaction"[Title/Abstract])',
        "成功率": '("survival rate"[Title/Abstract] OR "success rate"[Title/Abstract] OR "failure"[Title/Abstract])',
    }
}

# === Mining Configuration - Rubric Scoring System ===
# Journal rankings and scoring weights moved to private file for security
try:
    from core.journal_rankings import TOP_JOURNALS, SCORING_WEIGHTS
    
    RUBRIC_CONFIG = {
        "top_journals": TOP_JOURNALS,
        "citation_rules": SCORING_WEIGHTS["citation_rules"],
        "recency_max_score": SCORING_WEIGHTS["recency_max_score"],
        "data_quality_bonus": SCORING_WEIGHTS["data_quality_bonus"],
    }
    # raise ImportError("Debugging: Force fallback")
except ImportError:
    # Fallback if private file is missing (e.g., fresh clone)
    print("⚠️  Warning: core/journal_rankings.py not found. Using minimal fallback configuration.")
    print("   Please copy journal_rankings.py from your backup or contact the developer.")
    RUBRIC_CONFIG = {
        "top_journals": {
            "Nature": 16,
            "Science": 16,
            "The New England Journal of Medicine": 16,
        },
        "citation_rules": [(200, 4), (100, 3), (50, 2), (10, 1)],
        "recency_max_score": 5,
        "data_quality_bonus": 2,
    }

# === Embedding Model Configuration ===
# Upgraded to multilingual model for better Chinese-English cross-lingual retrieval
# EMBEDDING_MODEL = "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"
EMBEDDING_MODEL = "Gemini text-embedding-004" # Now using Gemini (via core.chatbot.gemini_embeddings)

# === ChromaDB Configuration ===
CHROMA_PERSIST_DIR = str(VECTOR_DB_DIR)

# === PDF Processing Configuration ===
LAYOUTPARSER_MODEL = "lp://PubLayNet/faster_rcnn_R_50_FPN_3x/config"
LAYOUTPARSER_DEVICE = "cpu"  # or "cuda" if GPU available

# === Writing Configuration ===
WRITING_MODEL = "deepseek-chat"
WRITING_TEMPERATURE = 0.7
WRITING_MAX_TOKENS = 4000

# === Search Configuration ===
DEFAULT_SEARCH_LIMIT = 200  # Default number of papers to retrieve
MAX_SEARCH_LIMIT = 500  # Maximum allowed search limit

# === Logging Configuration ===
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# === Prompt Configuration ===
try:
    import yaml
    with open(BASE_DIR / "config/prompts.yaml", "r", encoding="utf-8") as f:
        PROMPTS = yaml.safe_load(f)
except Exception as e:
    print(f"⚠️ Warning: Failed to load config/prompts.yaml: {e}")
    PROMPTS = {}
