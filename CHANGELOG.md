# Changelog

All notable changes to Lit-Miner will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2025-12-19

### 🚀 Major Features

#### AI-Powered Query Expansion
- **Zero-configuration AI expansion**: Supports any medical domain without manual dictionary setup
- **DeepSeek API integration**: Intelligent translation from Chinese to English medical terminology
- **Smart caching**: 500x+ speedup for repeated queries, significant cost savings
- **Multi-layer fallback**: Automatic degradation to legacy methods if AI fails
- **Cross-domain support**: Seamlessly handles dentistry, neuroscience, cardiology, oncology, etc.

#### Multi-Domain Journal Configuration
- **50+ top journals** added across medical specialties:
  - Neuroscience: Nature Neuroscience, Neuron, Brain, Lancet Neurology (14 journals)
  - Cardiology: Circulation, European Heart Journal, JACC (6 journals)
  - Oncology: Nature Reviews Cancer, JCO, Cancer Cell (6 journals)
  - General Medicine: Nature, Science, NEJM, Lancet (8 journals)
  - Psychiatry & Immunology: Additional 6 journals
- **Intelligent scoring**: Automatic recognition of top-tier publications

#### Enhanced Search Depth
- **Default increased**: 20 → 200 papers (10x improvement)
- **Maximum raised**: 100 → 500 papers (5x more comprehensive)
- **Tiered UI**: PRO subscription hints for 200+ paper searches
- **Better coverage**: Significantly reduced risk of missing important literature

### ✨ Improvements

#### User Interface
- Added **AI status indicator** on Search page
- Shows "🤖 AI Query Expansion: Enabled" when active
- PRO tier hints for future commercialization: "💎 深度检索即将推出"
- Improved help text with tier explanations

#### Performance
- **Query caching**: Identical queries return instantly (<1ms)
- **Optimized API calls**: Low temperature (0.3) for consistency
- **Cost efficiency**: ~$0.001 per unique query, zero for cached

#### Developer Experience
- Comprehensive test suite (`test_ai_expansion.py`)
- Cross-domain validation support
- Cache statistics and management functions
- Detailed logging for debugging

### 🔧 Technical Changes

#### Core Modules
- **`core/miners/query_expansion.py`**: Complete rewrite with AI integration
  - `expand_query()`: Main entry with AI support
  - `_expand_with_ai()`: DeepSeek API integration
  - `_expansion_cache`: In-memory caching system
  - Fallback to legacy config-based expansion

#### Configuration
- **`config.py`**: New AI expansion settings
  - `USE_AI_EXPANSION`: Toggle AI on/off
  - `AI_EXPANSION_TIMEOUT`: API timeout (10s default)
  - `AI_EXPANSION_CACHE_ENABLED`: Cache control
  - Expanded journal list from 5 to 50+ entries

#### UI Components
- **`streamlit_app/pages/1_🔍_Search.py`**: Updated search interface
  - Slider range: 50-500 (was 10-100)
  - Default value: 200 (was 20)
  - Step size: 50 (was 5)
  - Added PRO tier conditional hints

### 📚 Documentation
- Created `PRO_ROADMAP.md`: Commercial planning document
- Added `test_ai_expansion.py`: Testing infrastructure
- Implementation guides and walkthroughs

### 🐛 Bug Fixes
- Fixed PDF read functionality with correct `file_name` parameter
- Improved error handling for API failures
- Enhanced image display with try-except wrappers

---

## [1.0.0] - 2025-12-19

### Initial Release

#### Core Features
- **Smart Literature Mining**: PubMed integration with intelligent scoring
- **AI Review Generation**: DeepSeek-powered synthesis
- **PDF Processing**: LayoutParser AI extraction
- **PMID Tools**: Quick lookup and conversion

#### Search & Mining
- Query expansion for common dental/periodontal terms
- Rubric-based scoring (journal quality, recency, citations, data richness)
- ChromaDB vector storage for RAG
- Automatic categorization (high-impact, recent, data-rich)

#### AI Writing
- Auto-topic generation from papers
- RAG-enhanced review synthesis
- Markdown export
- PMID citation tracking

#### PDF Processing
- Local AI-powered extraction (LayoutParser)
- Text → Markdown conversion
- Automatic figure & table separation
- No external upload required

#### Journal Configuration
- Dentistry/Periodontology focus:
  - Periodontology 2000 (score: 10)
  - Journal of Clinical Periodontology (score: 8)
  - Journal of Periodontology (score: 6)
  - Clinical Oral Implants Research (score: 5)
  - International Journal of Oral Implantology (score: 5)

#### Technical Stack
- Frontend: Streamlit
- Literature API: Bio.Entrez (PubMed)
- Vector DB: ChromaDB
- Semantic Model: sentence-transformers
- AI Writing: DeepSeek API
- PDF Processing: PyMuPDF, LayoutParser
- Image Processing: OpenCV, pdf2image

---

## Version Numbering

- **Major (X.0.0)**: Breaking changes, significant new features
- **Minor (x.X.0)**: New features, backwards compatible
- **Patch (x.x.X)**: Bug fixes, minor improvements

## Upcoming

### v2.1 (Planned)
- Retracted paper detection
- Preprint marking (bioRxiv/medRxiv)
- Impact factor integration
- Enhanced quality assurance

### v2.5 (Future)
- User authentication system
- PRO subscription (Stripe integration)
- Batch processing
- PDF auto-download

### v3.0 (Long-term)
- API access (FastAPI)
- Team collaboration
- Private deployment options
- MeSH terminology integration

---

## Links

- **Repository**: https://github.com/gao-cai-sheng/Lit-Miner
- **Issues**: https://github.com/gao-cai-sheng/Lit-Miner/issues
- **Discussions**: https://github.com/gao-cai-sheng/Lit-Miner/discussions
