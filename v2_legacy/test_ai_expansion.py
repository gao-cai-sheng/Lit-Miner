#!/usr/bin/env python3
"""
Test script for AI-powered query expansion
Run this to verify the upgrade works correctly
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.miners.query_expansion import expand_query, get_cache_stats, clear_cache


def test_chinese_queries():
    """Test Chinese medical queries across different domains"""
    print("=" * 80)
    print("🧪 Testing AI Query Expansion - Chinese Queries")
    print("=" * 80)
    
    test_cases = [
        # Dentistry (original domain)
        "牙周炎",
        "位点保存",
        
        # Neuroscience (new domain)
        "阿尔茨海默病",
        "帕金森病治疗",
        "脑卒中预后",
        
        # Cardiology (new domain)
        "心肌梗死",
        "冠心病",
    ]
    
    for i, query in enumerate(test_cases, 1):
        print(f"\n[Test {i}/{len(test_cases)}]")
        print(f"Input:  {query}")
        expanded = expand_query(query)
        print(f"Output: {expanded[:200]}...")
        print("-" * 80)


def test_english_queries():
    """Test English query optimization"""
    print("\n" + "=" * 80)
    print("🧪 Testing AI Query Expansion - English Queries")
    print("=" * 80)
    
    test_cases = [
        "brain injury recovery",
        "Alzheimer's treatment",
        "stroke prevention",
        "depression therapy",
    ]
    
    for i, query in enumerate(test_cases, 1):
        print(f"\n[Test {i}/{len(test_cases)}]")
        print(f"Input:  {query}")
        expanded = expand_query(query)
        print(f"Output: {expanded[:200]}...")
        print("-" * 80)


def test_cache():
    """Test caching mechanism"""
    print("\n" + "=" * 80)
    print("🧪 Testing Cache Performance")
    print("=" * 80)
    
    # Clear cache first
    clear_cache()
    print("\n✅ Cache cleared")
    
    # First call (should hit API)
    print("\n[First Call] Expanding '阿尔茨海默病'...")
    import time
    start = time.time()
    result1 = expand_query("阿尔茨海默病")
    time1 = (time.time() - start) * 1000
    print(f"⏱️  Time: {time1:.2f}ms")
    print(f"Result: {result1[:100]}...")
    
    # Second call (should hit cache)
    print("\n[Second Call] Expanding '阿尔茨海默病' again...")
    start = time.time()
    result2 = expand_query("阿尔茨海默病")
    time2 = (time.time() - start) * 1000
    print(f"⏱️  Time: {time2:.2f}ms")
    print(f"Result: {result2[:100]}...")
    
    # Verify results are identical
    if result1 == result2:
        print("\n✅ Cache working correctly (results identical)")
    else:
        print("\n⚠️  Cache may have issues (results differ)")
    
    # Show speedup
    if time1 > 0:
        speedup = time1 / time2
        print(f"\n📈 Speedup: {speedup:.1f}x faster")
    
    # Show stats
    stats = get_cache_stats()
    print(f"\n📊 Cache Stats: {stats}")


def test_fallback():
    """Test fallback mechanisms"""
    print("\n" + "=" * 80)
    print("🧪 Testing Fallback Mechanisms")
    print("=" * 80)
    
    # Test with AI disabled
    print("\n[Fallback Test] Expanding with use_ai=False...")
    result = expand_query("牙周炎", use_ai=False)
    print(f"Result (legacy mode): {result}")
    
    if "periodontitis" in result.lower():
        print("✅ Legacy fallback working correctly")
    else:
        print("⚠️  Legacy fallback may have issues")


def main():
    """Run all tests"""
    print("\n" + "=" * 80)
    print("🚀 Lit-Miner AI Query Expansion v2.0 - Test Suite")
    print("=" * 80)
    
    # Check API key
    from config import DEEPSEEK_API_KEY, USE_AI_EXPANSION
    
    if not DEEPSEEK_API_KEY:
        print("\n⚠️  WARNING: DEEPSEEK_API_KEY not set")
        print("   AI expansion will fallback to legacy mode")
        print("   Set API key in .env to test AI features")
    else:
        print(f"\n✅ API Key: Found (***{DEEPSEEK_API_KEY[-8:]})")
    
    if not USE_AI_EXPANSION:
        print("\n⚠️  WARNING: USE_AI_EXPANSION is disabled in config.py")
        print("   Tests will use legacy mode")
    else:
        print("✅ AI Expansion: Enabled")
    
    print("\nPress Enter to continue...")
    input()
    
    try:
        # Run tests
        test_chinese_queries()
        test_english_queries()
        test_cache()
        test_fallback()
        
        print("\n" + "=" * 80)
        print("✅ All tests completed!")
        print("=" * 80)
        print("\n💡 Next steps:")
        print("   1. Review the expanded queries above")
        print("   2. Try the Search page in Streamlit: http://localhost:8501")
        print("   3. Test with your own queries")
        print("\n")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
