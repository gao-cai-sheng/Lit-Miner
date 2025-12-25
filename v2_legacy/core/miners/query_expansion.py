"""
Query Expansion Module v2.0
AI-powered dynamic query expansion using DeepSeek API
"""

import re
import json
import requests
from typing import Dict, Optional
from config import DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL, PROMPTS, QUERY_EXPANSION_CONFIG

# ...


# Simple cache to avoid repeated API calls for same queries
_expansion_cache: Dict[str, str] = {}


def expand_query(user_query: str, use_ai: bool = True) -> str:
    """
    Expand user query using AI-powered intelligent expansion.
    
    Args:
        user_query: Raw search query (any language)
        use_ai: If True, use DeepSeek API; if False, use legacy config-based expansion
        
    Returns:
        Expanded PubMed search query
    """
    q = user_query.strip()
    if not q:
        return ""
    
    # Check cache first
    if q in _expansion_cache:
        return _expansion_cache[q]
    
    # Detect if query contains Chinese characters
    has_chinese = bool(re.search(r"[\u4e00-\u9fff]", q))
    
    # Try AI expansion first (if enabled and API key available)
    if use_ai and DEEPSEEK_API_KEY:
        try:
            expanded = _expand_with_ai(q, has_chinese=has_chinese)
            if expanded and expanded != q:
                # Cache successful expansion
                _expansion_cache[q] = expanded
                return expanded
        except Exception as e:
            print(f"[Warning] AI expansion failed: {e}, falling back to legacy method")
    
    # Fallback to legacy config-based expansion
    if has_chinese:
        expanded = _expand_chinese_query_legacy(q)
    else:
        expanded = _expand_generic_query(q)
    
    _expansion_cache[q] = expanded
    return expanded


def _expand_with_ai(query: str, has_chinese: bool = False) -> str:
    """
    Use DeepSeek API to intelligently expand query.
    """
    if has_chinese:
        template = PROMPTS.get("query_expansion", {}).get("chinese_to_pubmed", "")
        # Fallback if empty (omitted for brevity, reliable config assumed from previous step)
        prompt = template.format(query=query)
    else:
        template = PROMPTS.get("query_expansion", {}).get("english_optimization", "")
        prompt = template.format(query=query)
    
    try:
        headers = {
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.3,  # Lower temperature for more consistent results
            "max_tokens": 300
        }
        
        response = requests.post(
            f"{DEEPSEEK_BASE_URL}/chat/completions",
            json=data,
            headers=headers,
            timeout=10  # 10 second timeout
        )
        
        if response.status_code == 200:
            result = response.json()
            expanded_query = result["choices"][0]["message"]["content"].strip()
            
            # Clean up the response (remove any markdown formatting, extra quotes, etc.)
            expanded_query = expanded_query.strip('`"\'')
            
            # Validate that we got a reasonable query back
            if len(expanded_query) > 0 and len(expanded_query) < 1000:
                return expanded_query
            else:
                print(f"[Warning] AI returned invalid query length: {len(expanded_query)}")
                return query
        else:
            print(f"[Error] API returned status {response.status_code}: {response.text}")
            return query
            
    except requests.exceptions.Timeout:
        print("[Error] AI expansion timeout")
        return query
    except Exception as e:
        print(f"[Error] AI expansion failed: {e}")
        return query


def _expand_chinese_query_legacy(query: str) -> str:
    """
    Legacy config-based Chinese query expansion (fallback).
    """
    core_clauses = []
    modifier_clauses = []
    
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
    
    # If no matches found, return original
    return query


def _expand_generic_query(query: str) -> str:
    """
    Generic expansion for English queries without AI.
    Adds Title/Abstract field restrictions.
    """
    # Check for common patterns first
    q_lower = query.lower()
    
    # Socket preservation pattern (legacy)
    if "socket" in q_lower and "preserv" in q_lower:
        return '("socket preservation" OR "alveolar ridge preservation" OR "extraction socket management" OR "ridge preservation")'
    
    # Generic field restriction
    tokens = re.split(r"(\s+AND\s+|\s+OR\s+)", query, flags=re.IGNORECASE)
    expanded_parts = []
    
    for t in tokens:
        t_strip = t.strip()
        if not t_strip:
            continue
        if t_strip.upper() in {"AND", "OR"}:
            expanded_parts.append(t_strip.upper())
            continue
        # Add field restriction
        expanded_parts.append(f'({t_strip}[Title/Abstract])')
    
    return " ".join(expanded_parts)


def clear_cache():
    """Clear the expansion cache (useful for testing)"""
    global _expansion_cache
    _expansion_cache.clear()


def get_cache_stats() -> Dict[str, int]:
    """Get cache statistics"""
    return {
        "cached_queries": len(_expansion_cache),
        "cache_size_bytes": len(str(_expansion_cache))
    }
