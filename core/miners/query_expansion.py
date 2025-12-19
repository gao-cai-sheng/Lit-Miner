"""
Query Expansion Module
Handles Chinese-to-English translation and query expansion for PubMed searches
"""

import re
from typing import List, Tuple
from config import QUERY_EXPANSION_CONFIG


def expand_query(user_query: str) -> str:
    """
    Expand user query with synonyms and related terms.
    
    For Chinese queries: translates to English with medical synonyms
    For English queries: adds Boolean operators and field restrictions
    
    Args:
        user_query: Raw search query (Chinese or English)
        
    Returns:
        Expanded PubMed search query
    """
    q = user_query.strip()
    if not q:
        return ""
    
    q_lower = q.lower()
    
    # Check if query contains Chinese characters
    has_chinese = bool(re.search(r"[\u4e00-\u9fff]", q))
    
    if has_chinese:
        return _expand_chinese_query(q)
    
    # English-specific patterns
    if "socket" in q_lower and "preserv" in q_lower:
        return '("socket preservation" OR "alveolar ridge preservation" OR "extraction socket management" OR "ridge preservation") AND ("bone height" OR "vertical dimension" OR "alveolar bone")'
    
    # Generic expansion: add Title/Abstract restrictions
    return _expand_generic_query(q)


def _expand_chinese_query(query: str) -> str:
    """Expand Chinese medical query to English Boolean query"""
    core_clauses: List[str] = []
    modifier_clauses: List[str] = []
    
    # Combine all term mappings from config
    all_terms = {}
    for category in ["diseases", "procedures", "outcomes"]:
        all_terms.update(QUERY_EXPANSION_CONFIG.get(category, {}))
    
    # Find matching terms
    for zh_term, en_clause in all_terms.items():
        if zh_term in query:
            # Determine if it's a core term or modifier
            if zh_term in QUERY_EXPANSION_CONFIG.get("diseases", {}) or \
               zh_term in QUERY_EXPANSION_CONFIG.get("procedures", {}):
                core_clauses.append(en_clause)
            else:
                modifier_clauses.append(en_clause)
    
    # Build final query
    if core_clauses:
        core_part = " OR ".join(set(core_clauses))
        if modifier_clauses:
            mod_part = " OR ".join(set(modifier_clauses))
            return f"({core_part}) AND ({mod_part})"
        return core_part
    
    # Fallback: if no matches, use original query
    return query


def _expand_generic_query(query: str) -> str:
    """Generic expansion with Title/Abstract field restrictions"""
    tokens = re.split(r"(\s+AND\s+|\s+OR\s+)", query, flags=re.IGNORECASE)
    expanded_parts: List[str] = []
    
    for t in tokens:
        t_strip = t.strip()
        if not t_strip:
            continue
        if t_strip.upper() in {"AND", "OR"}:
            expanded_parts.append(t_strip.upper())
            continue
        # Add field restriction
        expanded_parts.append(f'({t_strip} OR "{t_strip}"[Title/Abstract])')
    
    return " ".join(expanded_parts)
