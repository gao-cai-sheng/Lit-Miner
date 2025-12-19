"""
Lit-Miner Configuration
Centralized configuration management for all paths and settings
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Project root directory
PROJECT_ROOT = Path(__file__).parent.absolute()

# Data directories
DATA_DIR = PROJECT_ROOT / "data"
VECTOR_DB_DIR = DATA_DIR / "vector_dbs"
PDF_DIR = DATA_DIR / "raw_pdfs"
FIGURES_DIR = DATA_DIR / "processed_figures"

# Ensure directories exist
for dir_path in [DATA_DIR, VECTOR_DB_DIR, PDF_DIR, FIGURES_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)

# API Configuration
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
DEEPSEEK_BASE_URL = "https://api.deepseek.com/v1"
PUBMED_EMAIL = os.getenv("PUBMED_EMAIL", "your_email@example.com")

# AI Query Expansion (v2.0)
USE_AI_EXPANSION = True  # Set to False to use legacy config-based expansion
AI_EXPANSION_TIMEOUT = 10  # seconds
AI_EXPANSION_CACHE_ENABLED = True

# Mining Configuration - Rubric Scoring System
RUBRIC_CONFIG = {
    # Top journals and their score weights
    # Multi-domain support: Dentistry, Neuroscience, Cardiology, Oncology, General Medicine
    "top_journals": {
        # === Dentistry / Periodontology (Original) ===
        "Periodontology 2000": 10,
        "Journal of clinical periodontology": 8,
        "Journal of periodontology": 6,
        "Clinical oral implants research": 5,
        "International journal of oral implantology": 5,
        
        # === Neuroscience (High Impact) ===
        "Nature Neuroscience": 15,
        "Neuron": 15,
        "Nature Reviews Neuroscience": 15,
        "Brain": 12,
        "Lancet Neurology": 12,
        "JAMA Neurology": 12,
        "Annals of Neurology": 12,
        "Biological Psychiatry": 10,
        "Journal of Neuroscience": 8,
        "Molecular Psychiatry": 8,
        "Trends in Neurosciences": 8,
        "Cerebral Cortex": 7,
        "NeuroImage": 7,
        "Journal of Neurophysiology": 6,
        
        # === Cardiology ===
        "Circulation": 15,
        "European Heart Journal": 15,
        "Journal of the American College of Cardiology": 14,
        "JAMA Cardiology": 12,
        "Circulation Research": 10,
        "Cardiovascular Research": 8,
        
        # === Oncology ===
        "CA: A Cancer Journal for Clinicians": 15,
        "Nature Reviews Cancer": 15,
        "The Lancet Oncology": 14,
        "Journal of Clinical Oncology": 12,
        "Cancer Cell": 12,
        "Annals of Oncology": 10,
        
        # === General Medicine (Top Tier) ===
        "Nature": 16,
        "Science": 16,
        "The New England Journal of Medicine": 16,
        "The Lancet": 15,
        "JAMA": 15,
        "Nature Medicine": 15,
        "BMJ": 12,
        "PLOS Medicine": 10,
        
        # === Psychiatry / Mental Health ===
        "American Journal of Psychiatry": 10,
        "JAMA Psychiatry": 10,
        "Schizophrenia Bulletin": 8,
        
        # === Immunology / Infectious Disease ===
        "Nature Immunology": 14,
        "Immunity": 14,
        "The Lancet Infectious Diseases": 12,
    },
    
    # Citation score rules: [(threshold, score), ...]
    # Papers with citations >= threshold get the corresponding score
    "citation_rules": [
        (200, 4),  # >= 200 citations: +4
        (100, 3),  # 100-199 citations: +3
        (50, 2),   # 50-99 citations: +2
        (10, 1),   # 10-49 citations: +1
        # < 10 citations: +0
    ],
    
    # Recency scoring: current year +5, each year back -1, min 0
    "recency_max_score": 5,
    
    # Data quality bonus
    "data_quality_bonus": 2,  # Papers with mm measurements
}

# Query Expansion - Chinese to English Mappings
QUERY_EXPANSION_CONFIG = {
    # Core disease terms
    "diseases": {
        "牙周炎": '("periodontitis" OR "chronic periodontitis" OR "aggressive periodontitis")',
        "慢性牙周炎": '("chronic periodontitis")',
        "侵袭性牙周炎": '("aggressive periodontitis")',
        "牙龈炎": '("gingivitis")',
        "牙周袋": '("periodontal pocket")',
        "牙周再生": '("periodontal regeneration" OR "regenerative periodontal therapy")',
        "引导组织再生": '("guided tissue regeneration" OR "GTR")',
        "引导骨再生": '("guided bone regeneration" OR "GBR")',
        "骨内缺损": '("intrabony defect" OR "intra-bony defect")',
        "分叉病变": '("furcation involvement" OR "furcation defect")',
    },
    
    # Treatment procedures
    "procedures": {
        "位点保存": '("socket preservation" OR "alveolar ridge preservation" OR "ridge preservation" OR "extraction socket management")',
        "牙槽嵴保存": '("socket preservation" OR "alveolar ridge preservation" OR "ridge preservation" OR "extraction socket management")',
        "上颌窦提升": '("sinus floor elevation" OR "sinus augmentation" OR "sinus lift")',
        "植骨": '("bone graft" OR "bone grafting" OR "bone substitute")',
        "异种骨": '("xenograft" OR "deproteinized bovine bone" OR "DBBM")',
        "自体骨": '("autograft" OR "autogenous bone")',
    },
    
    # Outcome measures
    "outcomes": {
        "骨高度": '("bone height" OR "vertical dimension" OR "alveolar bone")',
        "骨增量": '("bone augmentation" OR "ridge augmentation")',
        "边缘骨吸收": '("marginal bone loss" OR "crestal bone loss")',
        "探诊深度": '("probing pocket depth" OR "PPD")',
        "临床附着水平": '("clinical attachment level" OR "CAL")',
        "牙龈退缩": '("gingival recession" OR "recession depth")',
    }
}

# Model Configuration
EMBEDDING_MODEL = "all-MiniLM-L6-v2"  # Sentence transformer model

# Logging
LOG_LEVEL = "INFO"
