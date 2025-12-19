# Journal Impact Factor Database
# Data source: 2023 Journal Citation Reports (Web of Science)
# Last updated: 2025-12-19

JOURNAL_IMPACT_FACTORS = {
    # General Medicine (Top Tier)
    "Nature": 64.8,
    "Science": 56.9,
    "The New England Journal of Medicine": 158.5,
    "The Lancet": 168.9,
    "JAMA": 120.7,
    "Nature Medicine": 87.2,
    "BMJ": 93.6,
    "PLOS Medicine": 11.0,
    
    # Neuroscience
    "Nature Neuroscience": 28.8,
    "Neuron": 16.2,
    "Nature Reviews Neuroscience": 38.1,
    "Brain": 15.0,
    "Lancet Neurology": 59.9,
    "JAMA Neurology": 30.4,
    "Annals of Neurology": 11.2,
    "Biological Psychiatry": 12.8,
    "Journal of Neuroscience": 6.2,
    "Molecular Psychiatry": 11.0,
    "Trends in Neurosciences": 15.2,
    "Cerebral Cortex": 4.3,
    "NeuroImage": 5.7,
    "Journal of Neurophysiology": 2.5,
    
    # Cardiology
    "Circulation": 37.8,
    "European Heart Journal": 39.3,
    "Journal of the American College of Cardiology": 24.0,
    "JAMA Cardiology": 18.3,
    "Circulation Research": 20.1,
    "Cardiovascular Research": 10.9,
    
    # Oncology
    "CA: A Cancer Journal for Clinicians": 254.7,
    "Nature Reviews Cancer": 69.8,
    "The Lancet Oncology": 54.4,
    "Journal of Clinical Oncology": 45.3,
    "Cancer Cell": 38.6,
    "Annals of Oncology": 51.8,
    
    # Psychiatry
    "American Journal of Psychiatry": 19.6,
    "JAMA Psychiatry": 22.5,
    "Schizophrenia Bulletin": 9.3,
    
    # Immunology
    "Nature Immunology": 30.5,
    "Immunity": 32.4,
    "The Lancet Infectious Diseases": 36.4,
    
    # Dentistry / Periodontology
    "Periodontology 2000": 17.2,
    "Journal of clinical periodontology": 6.5,
    "Journal of periodontology": 4.1,
    "Clinical oral implants research": 5.0,
    "International journal of oral implantology": 2.3,
}


def get_impact_factor(journal_name: str) -> float:
    """
    Get impact factor for a journal by name (case-insensitive partial match)
    
    Args:
        journal_name: Journal name (can be partial)
        
    Returns:
        Impact factor (0.0 if not found)
    """
    if not journal_name:
        return 0.0
    
    journal_lower = journal_name.lower()
    
    # Try exact match first
    for key, if_value in JOURNAL_IMPACT_FACTORS.items():
        if key.lower() == journal_lower:
            return if_value
    
    # Try partial match
    for key, if_value in JOURNAL_IMPACT_FACTORS.items():
        if key.lower() in journal_lower or journal_lower in key.lower():
            return if_value
    
    return 0.0


def calculate_if_score(impact_factor: float) -> int:
    """
    Convert impact factor to score points
    
    Rules:
    - IF >= 50: +5 points (exceptional)
    - IF >= 20: +4 points (excellent)
    - IF >= 10: +3 points (very good)
    - IF >= 5: +2 points (good)
    - IF >= 2: +1 point (decent)
    - IF < 2: 0 points
    
    Args:
        impact_factor: Journal impact factor
        
    Returns:
        Score bonus (0-5 points)
    """
    if impact_factor >= 50:
        return 5
    elif impact_factor >= 20:
        return 4
    elif impact_factor >= 10:
        return 3
    elif impact_factor >= 5:
        return 2
    elif impact_factor >= 2:
        return 1
    else:
        return 0
